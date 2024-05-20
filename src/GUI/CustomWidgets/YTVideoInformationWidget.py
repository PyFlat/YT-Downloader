from datetime import datetime

from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from qfluentwidgets import Flyout, FlyoutView, PushButton, isDarkTheme

from src.Config.Config import cfg
from src.DownloaderCore.Downloader import Downloader
from src.GUI.CustomWidgets.InformationWidget import InformationWidget
from src.GUI.CustomWidgets.VideoDownloadWidget import VideoDownloadWidget
from src.GUI.Icons.Icons import CustomIcons


class YTVideoInformationWidget(InformationWidget):
    def __init__(self, parent=None, info_dict:dict=None, downloader:Downloader=None):
        super().__init__(parent)
        self.downloader = downloader
        self._parent = parent
        self.info = info_dict
        self.url = self.info["original_url"]

        self.thumbnail_url = f"https://i.ytimg.com/vi/{self.info['display_id']}/mqdefault.jpg"

        if cfg.get(cfg.thumbnail_streaming):
            self.fetchThumbnailFromUrl(self.thumbnail_url)
        else:
            self.setDefaultThumbnail()

        # with open("data.json", "w") as f:
        #     json.dump(self.info, f)

        self.setIcons()

        self.setTexts()

        self.stackedWidget.setCurrentIndex(0)

        self.best_video_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.best_audio_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.quick_dl_btn.clicked.connect(self.showFlyout)

        self.PushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

    def download_video(self):
        # Erstelle ein neues Widget für den Download
        download_widget = VideoDownloadWidget(self._parent.download_interface, self.info["display_id"], self.info["title"], self.info['channel'])
        self._parent.download_interface.verticalLayout.addWidget(download_widget, 0, Qt.AlignTop | Qt.AlignCenter)

        # Definiere die Funktionen für den Downloadprozess
        def start():
            print("Download started")

        def progress(result: dict):
            if result.get("postprocessing"):
                download_widget.updatePostProcessStatus(result)
            else:
                download_widget.updateStatus(result)

        def finish(success):
            download_widget.finishStatus(success)

        self.downloader.downloadVideo(self.url, cfg.get(cfg.download_folder), cfg.get(cfg.ffmpeg_path), "bv*+ba[ext=m4a]/b", start, progress, finish)

    def setIcons(self):

        self.youtube_icon.setIcon(CustomIcons.YOUTUBE)
        self.author_icon.setIcon(CustomIcons.PERSON)
        self.duration_icon.setIcon(CustomIcons.TIME)
        self.calender_icon.setIcon(CustomIcons.CALENDER)

        self.best_video_btn.setIcon(CustomIcons.VIDEO)
        self.best_audio_btn.setIcon(CustomIcons.AUDIO)
        self.quick_dl_btn.setIcon(CustomIcons.DOWNLOAD)
        self.custom_dl_btn.setIcon(CustomIcons.WRITE)

    def setTexts(self):
        self.TitleLabel.setText(self.info["title"])

        self.HyperlinkLabel.setUrl(self.url)
        self.StrongBodyLabel_2.setText(f"by {self.info['channel']}")

        upload_date = datetime.strptime(self.info["upload_date"], "%Y%m%d").strftime("%d.%m.%Y")

        minutes, seconds = divmod(self.info["duration"], 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            duration = f"{hours:02} hours, {minutes:02} minutes, {seconds:02} seconds"
        elif minutes > 0:
            duration = f"{minutes:02} minutes, {seconds:02} seconds"
        else:
            duration = f"{seconds:02} seconds"

        self.BodyLabel_3.setText(duration)

        self.BodyLabel_4.setText(upload_date)


    def fetchThumbnailFromUrl(self, url):
        manager = QNetworkAccessManager(self)
        manager.finished.connect(lambda: self.setThumbnail(response))
        request = QNetworkRequest(QUrl(url))
        response = manager.get(request)

    def setDefaultThumbnail(self):
        color = "black" if isDarkTheme() else "white"
        pixmap = QPixmap(f"src/GUI/Images/thumbnail_streaming_{color}")
        pixmap = self.round_pixmap_corners(pixmap, 10)
        self.updateDropShadow()
        self.PixmapLabel_2.setPixmap(pixmap)

    def setThumbnail(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            image_data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            pixmap = pixmap.scaled(QSize(400, 225), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap = self.round_pixmap_corners(pixmap, 10)
            self.updateDropShadow()

            self.PixmapLabel_2.setPixmap(pixmap)
        else:
            print("Failed to download image. Error:", reply.errorString())

    def updateDropShadow(self):
        shadow_effect = QGraphicsDropShadowEffect(self.widget_8)
        shadow_effect.setBlurRadius(30)
        color = QColor(Qt.white) if isDarkTheme() else QColor(Qt.black)
        shadow_effect.setColor(color)
        shadow_effect.setOffset(0,0)
        self.widget_8.setGraphicsEffect(shadow_effect)

    def showFlyout(self):
        self.view = FlyoutView(
            title = "",
            content="",
        )

        button = PushButton('Video')
        button.setIcon(self.best_video_btn.icon())
        button.setFixedWidth(120)

        button1 = PushButton('Audio')
        button1.setIcon(self.best_audio_btn.icon())
        button1.setFixedWidth(120)

        self.view.addWidget(button, align=Qt.AlignRight)
        self.view.addWidget(button1, align=Qt.AlignRight)

        flyout = Flyout.make(
            target=self.quick_dl_btn,
            view=self.view,
            parent=self.parent()
        )

        button.clicked.connect(lambda: [self.download_video(), flyout.close()])


    def round_pixmap_corners(self, pixmap, radius):
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(pixmap)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pixmap.rect(), radius, radius)
        painter.end()
        return rounded
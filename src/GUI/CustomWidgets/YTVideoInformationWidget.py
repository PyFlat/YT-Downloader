from src.GUI.CustomWidgets.InformationWidget import InformationWidget
from datetime import datetime
from src.GUI.Icons.Icons import CustomIcons
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QPixmap, QImage, QColor, QPainter
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qfluentwidgets import TeachingTip, TeachingTipTailPosition, isDarkTheme, TeachingTipView, PushButton
from src.DownloaderCore.Downloader import Downloader
from src.Config.Config import cfg
import json

class YTVideoInformationWidget(InformationWidget):
    def __init__(self, parent=None, info_dict:dict=None, downloader:Downloader=None):
        super().__init__(parent)
        self.downloader = downloader
        self.info = info_dict
        self.url = self.info["original_url"]

        for thumbnail in self.info["thumbnails"]:
            if thumbnail["url"].endswith("mqdefault.jpg"):
                self.thumbnail_url = thumbnail["url"]

        self.fetchThumbnailFromUrl(self.thumbnail_url)

        with open("data.json", "w") as f:
            json.dump(self.info, f)

        self.setIcons()

        self.setTexts()

        self.stackedWidget.setCurrentIndex(0)

        self.best_video_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.best_audio_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.quick_dl_btn.clicked.connect(self.showFlyout)

        self.PushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))


        print(self.size())

    def download_video(self):
        self.downloader.downloadVideo(self.url, cfg.get(cfg.download_folder), cfg.get(cfg.ffmpeg_path), "bv*+ba[ext=m4a]/b")

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

    def setThumbnail(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            image_data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            pixmap = pixmap.scaled(QSize(400, 225), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap = self.round_pixmap_corners(pixmap, 10)

            self.PixmapLabel_2.setPixmap(pixmap)

            shadow_effect = QGraphicsDropShadowEffect(self.widget_8)
            shadow_effect.setBlurRadius(30)
            color = QColor(Qt.white) if isDarkTheme() else QColor(Qt.black)
            shadow_effect.setColor(color)
            shadow_effect.setOffset(0,0)
            self.widget_8.setGraphicsEffect(shadow_effect)
        else:
            print("Failed to download image. Error:", reply.errorString())

    def showFlyout(self):
        position = TeachingTipTailPosition.BOTTOM
        view = TeachingTipView(
            title = "",
            content="",
            isClosable=True
        )

        button = PushButton('Video')
        button.setIcon(self.best_video_btn.icon())
        button.setFixedWidth(120)

        button1 = PushButton('Audio')
        button1.setIcon(self.best_audio_btn.icon())
        button1.setFixedWidth(120)

        view.addWidget(button, align=Qt.AlignRight)
        view.addWidget(button1, align=Qt.AlignRight)

        button.clicked.connect(self.download_video)

        w = TeachingTip.make(
            target=self.quick_dl_btn,
            view=view,
            duration=-1,
            tailPosition=position,
            parent=self.parent()
        )
        view.closed.connect(w.close)

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
import re
from datetime import datetime

from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QListWidget
from qfluentwidgets import Flyout, FlyoutView, PushButton, isDarkTheme

from src.Config.Config import cfg
from src.DownloaderCore.Downloader import Downloader
from src.DownloaderCore.formats import YOUTUBE_VIDEO
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

        self.back_to_all_formats = False
        self.button_type_clicked = None

        self.thumbnail_url = f"https://i.ytimg.com/vi/{self.info['display_id']}/mqdefault.jpg"

        self.video_formats = [x["extension"] for x in YOUTUBE_VIDEO.get("video_formats", [])]
        self.best_video_formats = [x["extension"] for x in YOUTUBE_VIDEO.get("video_formats", []) if x.get("best_format")]

        self.audio_formats = [x["extension"] for x in YOUTUBE_VIDEO.get("audio_formats", [])]
        self.best_audio_formats = [x["extension"] for x in YOUTUBE_VIDEO.get("audio_formats", []) if x.get("best_format")]

        if cfg.get(cfg.thumbnail_streaming):
            self.fetchThumbnailFromUrl(self.thumbnail_url)
        else:
            self.setDefaultThumbnail()

        # with open("data.json", "w") as f:
        #     json.dump(self.info, f)

        self.setIcons()

        self.setTexts()

        self.stackedWidget.setCurrentIndex(0)

        self.best_video_btn.clicked.connect(lambda: self.setFormatOptions())
        self.best_audio_btn.clicked.connect(lambda: self.setFormatOptions(video = False))
        self.quick_dl_btn.clicked.connect(self.showFlyout)
        self.custom_dl_btn.clicked.connect(self.setAllFormatOptions)
        self.custom_dl_next_btn.clicked.connect(self.setResolutionOptions)
        self.custom_dl_back_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.custom_dl_list_widget.itemSelectionChanged.connect(self.changeBtnVisibility)

        self.custom_dl_next_btn.setVisible(False)
        self.custom_dl_dl_btn.setVisible(False)

        self.PushButton.clicked.connect(self.goBack)
        self.PrimaryPushButton_4.clicked.connect(self.perform_download)

        self.SearchLineEdit.textChanged.connect(lambda text: self.filter_list(text, self.ListWidget))
        self.custom_dl_line_edit.textChanged.connect(lambda text: self.filter_list(text, self.custom_dl_list_widget))

    def filter_list(self, text:str, list_widget: QListWidget):
        text = text.lower()
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            item.setHidden(text not in item.text().lower())

    def perform_download(self):
        match self.button_type_clicked:
            case "best_video":
                type = "video"
                ext = self.ListWidget.currentItem().text().lower()
            case "best_audio":
                type = "audio"
                ext = self.ListWidget.currentItem().text().lower()
            case "custom":
                pass
            case other:
                return

        download_widget = VideoDownloadWidget(self._parent.download_interface, self.info["display_id"], self.info["title"], self.info['channel'])
        self._parent.download_interface.verticalLayout.addWidget(download_widget, 0, Qt.AlignTop | Qt.AlignCenter)

        def start():
            print("Download started")

        def progress(result: dict):
            if result.get("postprocessing"):
                download_widget.updatePostProcessStatus(result)
            else:
                download_widget.updateStatus(result)

        def finish(success):
            download_widget.finishStatus(success)

        options = {
            "ID": f"{type}/{ext}/best",
            "ffmpeg_path": cfg.get(cfg.ffmpeg_path),
            "outtmpl": cfg.get(cfg.download_folder),
            "overwrites": True
        }

        self.downloader.downloadVideo(self.url, start, progress, finish, **options)

    def download_video(self):
        download_widget = VideoDownloadWidget(self._parent.download_interface, self.info["display_id"], self.info["title"], self.info['channel'])
        self._parent.download_interface.verticalLayout.addWidget(download_widget, 0, Qt.AlignTop | Qt.AlignCenter)

        def start():
            print("Download started")

        def progress(result: dict):
            if result.get("postprocessing"):
                download_widget.updatePostProcessStatus(result)
            else:
                download_widget.updateStatus(result)

        def finish(success):
            download_widget.finishStatus(success)

        options = {
            "ID": "video/mp4/best",
            "ffmpeg_path": cfg.get(cfg.ffmpeg_path),
            "outtmpl": cfg.get(cfg.download_folder),
            "overwrites": True
        }

        self.downloader.downloadVideo(self.url, start, progress, finish, **options)

    def download_audio(self):
        download_widget = VideoDownloadWidget(self._parent.download_interface, self.info["display_id"], self.info["title"], self.info['channel'])
        self._parent.download_interface.verticalLayout.addWidget(download_widget, 0, Qt.AlignTop | Qt.AlignCenter)

        def start():
            print("Download started")

        def progress(result: dict):
            if result.get("postprocessing"):
                download_widget.updatePostProcessStatus(result)
            else:
                download_widget.updateStatus(result)

        def finish(success):
            download_widget.finishStatus(success)

        options = {
            "ID": "audio/mp3/best",
            "ffmpeg_path": cfg.get(cfg.ffmpeg_path),
            "outtmpl": cfg.get(cfg.download_folder),
            "overwrites": True
        }

        self.downloader.downloadVideo(self.url, start, progress, finish, **options)

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

    def changeBtnVisibility(self):
        selectedItems = self.custom_dl_list_widget.selectedItems()
        if len(selectedItems) == 0:
            self.custom_dl_next_btn.setVisible(False)
            self.custom_dl_dl_btn.setVisible(False)
            return

        if "video" in selectedItems[0].text().lower():
            self.custom_dl_next_btn.setVisible(True)
            self.custom_dl_dl_btn.setVisible(False)
        else:
            self.custom_dl_next_btn.setVisible(False)
            self.custom_dl_dl_btn.setVisible(True)

    def goBack(self):
        if self.back_to_all_formats:
            self.setAllFormatOptions()
        else:
            self.stackedWidget.setCurrentIndex(0)

    def setFormatOptions(self, video=True):
        self.ListWidget.clear()
        self.ListWidget.clearSelection()
        self.stackedWidget.setCurrentIndex(1)
        self.SearchLineEdit.clear()
        self.back_to_all_formats = False

        if video:
            self.button_type_clicked = "best_video"
            self.ListWidget.addItems(self.best_video_formats)
        else:
            self.button_type_clicked = "best_audio"
            self.ListWidget.addItems(self.best_audio_formats)

    def setAllFormatOptions(self):
        self.custom_dl_list_widget.clear()
        self.custom_dl_list_widget.clearSelection()
        self.stackedWidget.setCurrentIndex(2)
        self.custom_dl_line_edit.clear()
        self.back_to_all_formats = True
        self.button_type_clicked = "custom"
        self.custom_dl_list_widget.addItems([f"{x} (Video)" for x in self.video_formats])
        self.custom_dl_list_widget.addItems([f"{x} (Audio)" for x in self.audio_formats])

    def setResolutionOptions(self):
        self.ListWidget.clear()
        self.ListWidget.clearSelection()
        self.stackedWidget.setCurrentIndex(1)
        self.SearchLineEdit.clear()
        self.ListWidget.addItems(self.get_available_resolutions())

    def get_available_resolutions(self):
        resolution = []
        for stream in self.info["formats"]:
            if stream["video_ext"] != "none":
                stre = f"{stream['resolution'].split('x')[1]}p"
                if stre not in resolution:
                    resolution.append(stre)
        resolution = sorted(resolution, key=lambda s: int(re.compile(r'\d+').search(s).group()), reverse=True)
        return resolution

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

        # button.clicked.connect(lambda: [self.download_video(), flyout.close()])
        # button1.clicked.connect(lambda: [self.download_audio(), flyout.close()])

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
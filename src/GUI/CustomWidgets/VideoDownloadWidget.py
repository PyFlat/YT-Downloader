import json

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QPainter, QPalette, QPixmap, QResizeEvent
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import isDarkTheme

from src.GUI.CustomWidgets.DownloadWidget import DownloadWidget
from src.GUI.Interfaces.DownloadInterface import DownloadInterface


class VideoDownloadWidget(DownloadWidget):
    def __init__(self, parent:DownloadInterface=None, display_id:str=None, title:str=None, uploader:str=None):
        super().__init__(parent)
        self.__parent = parent
        self.display_id = display_id
        self.setFixedWidth(self.__parent.size().width()-50)
        self.setFixedHeight(245)
        self.image_data = None
        self.last_eta = 0
        self.last_speed =  ""
        self.total_size  = ""

        self.title_label.setText(title)
        self.channel_label.setText(uploader)

        self.cancel_btn.setIcon(FIF.CANCEL_MEDIUM)

        self.pause_btn.setIcon(FIF.PAUSE)
        self.icon = False
        self.pause_btn.clicked.connect(self.switch)

        self.fetchThumbnails()

    def switch(self):

        if not self.icon:
            self.pause_btn.setIcon(FIF.PLAY)
        else:
            self.pause_btn.setIcon(FIF.PAUSE)
        self.icon = not self.icon

    def fetchThumbnails(self):
        manager = QNetworkAccessManager(self)
        manager.finished.connect(lambda: self.handle_response(response))
        request = QNetworkRequest(QUrl(f"https://i.ytimg.com/vi/{self.display_id}/mqdefault.jpg"))
        response = manager.get(request)

    def handle_response(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            self.image_data = reply.readAll()
            self.update_pixmap()

    def update_pixmap(self):
        if self.image_data is None: return
        pixmap = QPixmap()
        pixmap.loadFromData(self.image_data)

        pixmap = pixmap.scaledToWidth(self.width(), Qt.SmoothTransformation)

        transparent_pixmap = QPixmap(self.size())
        color = QColor(Qt.black if isDarkTheme() else Qt.white)
        color.setAlpha(150)
        transparent_pixmap.fill(color)

        painter = QPainter(transparent_pixmap)
        painter.setOpacity(0.1)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        final_pixmap = self.round_pixmap_corners(transparent_pixmap, 15)

        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QPixmap(final_pixmap))
        self.setPalette(palette)

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

    def updateStatus(self, status_dict: dict, progress: int):
        self.progress_bar.setValue(progress)

        eta = status_dict.get("_eta_str", self.last_eta)
        if eta != "Unknown":
            self.last_eta = eta
        else:
            eta  = self.last_eta

        speed = status_dict.get("_speed_str", self.last_speed).lstrip()
        if "Unknown" not in speed:
            self.last_speed = speed
        else:
            speed = self.last_speed

        total_size = status_dict.get('_total_bytes_str', self.total_size).lstrip()
        if not self.total_size:
            self.total_size = total_size

        self.progress_label.setText(f"{progress}% / {total_size} - {eta} left ({speed})")


    def finishStatus(self, success):
        if success:
            self.progress_bar.setValue(100)
            self.progress_label.setText(f"100% / {self.total_size}")
            self.status_label.setText("Status: Download finished")
        else:
            self.progress_bar.setValue(0)
            self.status_label.setText("Status: Download failed")

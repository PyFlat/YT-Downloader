from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QPainter, QPalette, QPixmap, QResizeEvent
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import isDarkTheme

from src.GUI.CustomWidgets.DownloadWidget import DownloadWidget
from src.GUI.Interfaces.DownloadInterface import DownloadInterface


class VideoDownloadWidget(DownloadWidget):
    def __init__(self, parent:DownloadInterface=None, display_id:str=None):
        super().__init__(parent)
        self.__parent = parent
        self.display_id = display_id
        self.setFixedWidth(self.__parent.size().width()-50)
        self.setFixedHeight(215)
        self.image_data = None
        self.last_eta = 0

        self.PushButton.setIcon(FIF.CANCEL_MEDIUM)

        self.PushButton_2.setIcon(FIF.PAUSE)
        self.icon = False
        self.PushButton_2.clicked.connect(self.switch)

        self.fetchThumbnails()

    def switch(self):

        if not self.icon:
            self.PushButton_2.setIcon(FIF.PLAY)
        else:
            self.PushButton_2.setIcon(FIF.PAUSE)
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

    def updateStatus(self, status_dict:dict, progress:int):
        self.ProgressBar.setValue(progress)
        if "_eta_str" in status_dict and status_dict["_eta_str"]:
            eta = status_dict["_eta_str"]
            if eta == "Unknown":
                eta = self.last_eta
            else:
                self.last_eta = eta

            self.BodyLabel.setText(f"{progress}% / {status_dict['_total_bytes_str']} - {eta} left")
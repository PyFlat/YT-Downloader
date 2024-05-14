from src.GUI.CustomWidgets.DownloadWidget import DownloadWidget
from src.GUI.Interfaces.DownloadInterface import DownloadInterface
from PySide6.QtGui import QPixmap, QPainter, QColor, QPalette, QResizeEvent
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl, Qt

class VideoDownloadWidget(DownloadWidget):
    def __init__(self, parent:DownloadInterface=None):
        super().__init__(parent)
        self.__parent = parent
        self.setFixedWidth(self.__parent.size().width()-50)
        self.setFixedHeight(215)

    def fetchThumbnails(self):
        manager = QNetworkAccessManager(self)
        manager.finished.connect(lambda: self.handle_response(response))
        request = QNetworkRequest(QUrl("https://i.ytimg.com/vi/JSuWJoDWoJI/mqdefault.jpg"))
        response = manager.get(request)

    def handle_response(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            image_data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            pixmap = pixmap.scaledToWidth(self.width(), Qt.SmoothTransformation)

            transparent_pixmap = QPixmap(self.size())
            transparent_pixmap.fill(QColor(0, 0, 0, 150))

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
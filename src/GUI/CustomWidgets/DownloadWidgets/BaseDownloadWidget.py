from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QColor, QPainter, QPalette, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import isDarkTheme

from src.Config.Config import cfg
from src.GUI.CustomWidgets.DownloadWidget import DownloadWidget
from src.GUI.CustomWidgets.PLSmallDownloadWidget import PLSmallDownloadWidget
from src.GUI.Icons.Icons import CustomIcons
from src.GUI.Interfaces.DownloadInterface import DownloadInterface


class BaseDownloadWidget(DownloadWidget):
    def __init__(
        self,
        parent: DownloadInterface = None,
        widget_information: dict = {},
        is_playlist: bool = False,
    ):
        super().__init__(parent)

        self.__parent = parent

        self.widget_information = widget_information

        self.playlist_widgets_folded = False

        self.__initWidget()

        self.__setPlaylist(is_playlist)

        self.image_data = None

        self.icon = False

    def __initWidget(self):
        self.setFixedWidth(self.__parent.size().width() - 50)
        self.SingleDirectionScrollArea.setVisible(False)

        if cfg.get(cfg.thumbnail_streaming):
            self.fetchThumbnails()
        else:
            color = "202020" if isDarkTheme() else "eeeeee"
            self.setStyleSheet(f"background: #{color}; border-radius: 10px")

        self.__setTexts()
        self.__setIcons()
        self.__connectSignalsToSlots()

    def __setPlaylist(self, is_playlist: bool):
        self.IconWidget.setVisible(is_playlist)
        self.SingleDirectionScrollArea.setVisible(is_playlist)
        self.__setVideoListVisibility(self.playlist_widgets_folded)

    def __setVideoListVisibility(self, visible: bool):
        self.playlist_widgets_folded = visible
        if visible:
            self.SingleDirectionScrollArea.setVisible(True)
            self.IconWidget.setIcon(CustomIcons.CHEVRON_UP)
        else:
            self.SingleDirectionScrollArea.setVisible(False)
            self.IconWidget.setIcon(CustomIcons.CHEVRON_DOWN)

    def __setTexts(self):
        self.title_label.setText(self.widget_information.get("title"))
        self.channel_label.setText(self.widget_information.get("uploader"))

        format_str: str = self.widget_information.get("format-id")

        parts = format_str.split("/")
        format_str = "Format: " + parts[0].capitalize() + "/" + parts[1].upper()

        if parts[0] == "video":
            if parts[2] == "best":
                quality_str = "Quality: Best Video/Best Audio"
            else:
                quality_str = "Quality: " + parts[2].capitalize() + "p/Best Audio"
        elif parts[0] == "audio":
            quality_str = "Quality: Best Audio"

        self.format_label.setText(format_str)
        self.quality_label.setText(quality_str)

    def __setIcons(self):
        self.cancel_btn.setIcon(FIF.CANCEL_MEDIUM)

        self.pause_btn.setIcon(FIF.PAUSE)

        self.IconWidget.setIcon(CustomIcons.CHEVRON_DOWN)
        self.IconWidget.setFixedSize(40, 40)

    def __connectSignalsToSlots(self):
        self.pause_btn.clicked.connect(self.switch)
        self.IconWidget.mousePressEvent = lambda _: [
            self.__setVideoListVisibility(not self.playlist_widgets_folded),
            self.update_pixmap(),
        ]

    def addDownloadLabel(self, title: str = "", uploader: str = ""):
        smallDLWidget = PLSmallDownloadWidget(self.__parent, title, uploader)
        self.verticalLayout_4.insertWidget(
            self.verticalLayout_4.count() - 1,
            smallDLWidget,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        return smallDLWidget

    def switch(self):
        if not self.icon:
            self.pause_btn.setIcon(FIF.PLAY)
        else:
            self.pause_btn.setIcon(FIF.PAUSE)
        self.icon = not self.icon

    def fetchThumbnails(self):
        manager = QNetworkAccessManager(self)
        manager.finished.connect(lambda: self.handle_response(response))
        request = QNetworkRequest(QUrl(self.widget_information.get("thumbnail-url")))
        response = manager.get(request)

    def handle_response(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            self.image_data = reply.readAll()
            self.update_pixmap()

    def update_pixmap(self):
        if self.image_data is None:
            return
        pixmap = QPixmap()
        pixmap.loadFromData(self.image_data)

        pixmap = pixmap.scaledToWidth(self.width(), Qt.SmoothTransformation)

        transparent_pixmap = QPixmap(QSize(self.width(), self.sizeHint().height()))
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

    def updateStatus(
        self,
        progress: int = 0,
        progress_text: str = None,
        status_text: str = "",
    ):

        self.status_label.setText(status_text)

        if self.progress_bar.value() != progress:
            self.progress_bar.setValue(progress)

        if self.progress_label.text() != progress_text:
            self.progress_label.setText(progress_text)

    def updatePostProcessStatus(self, status_dict: dict):
        if status_dict.get("postprocessing") == "started":
            self.status_label.setText("Status: Converting...")
        else:
            self.status_label.setText("Status: Converting finished")

    def finishStatus(self, success, url):
        if success:
            self.progress_bar.setValue(100)
            self.progress_label.setText("100%")
            self.status_label.setText("Status: Download finished")
        else:
            self.progress_bar.setValue(0)
            self.status_label.setText("Status: Download failed")

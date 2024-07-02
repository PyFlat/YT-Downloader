from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QListWidget,
    QListWidgetItem,
    QStyle,
)
from qfluentwidgets import Flyout, FlyoutView, PushButton, isDarkTheme

from src.Config.Config import cfg
from src.GUI.CustomWidgets.InformationWidget import InformationWidget
from src.GUI.CustomWidgets.PlaylistSelectionDialog import VideoSelectDialog
from src.GUI.DownloadWidgetManager import download_widget_manager
from src.GUI.Icons.Icons import CustomIcons
from src.Logger import logger


class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, text: str, item_id: str):
        super().__init__(text)
        self.item_id = item_id


class BaseInformationWidget(InformationWidget):
    def __init__(
        self,
        parent=None,
        widget_information: dict = {},
        video_type: dict = {},
        is_playlist: bool = False,
    ):
        super().__init__(parent)

        self.widget_information = widget_information

        self._parent = parent
        self.back_to_all_formats = False
        self.button_type_clicked = None
        self.image_data = None

        self.selected_ids = []

        self.custom_video_formats = [
            x for x in video_type.get("video_formats", []) if not x.get("best_format")
        ]
        self.best_video_formats = [
            x for x in video_type.get("video_formats", []) if x.get("best_format")
        ]

        self.best_audio_formats = [x for x in video_type.get("audio_formats", [])]

        self.setIcons()

        self.setTexts()

        self.connectSignalsToSlots()

        thumbnail_url = self.widget_information.get("thumbnail-url")

        if cfg.get(cfg.thumbnail_streaming) and thumbnail_url:
            self.fetchThumbnailFromUrl(thumbnail_url)
        else:
            self.setDefaultThumbnail()

        self.stackedWidget.setCurrentIndex(0)

        if is_playlist:
            self.enablePlaylist()
        else:
            self.back_btn.setVisible(False)

    def enablePlaylist(self):
        self.stackedWidget.setCurrentIndex(3)
        playlist_length = self.widget_information.get("playlist-length")
        self.start_range_label.setText(str(1))
        self.end_range_label.setText(str(playlist_length))
        self.SubtitleLabel.setText(f"{playlist_length} Videos")
        self.range_selection_slider.setRange(1, playlist_length)

        self.updateDownloadRange()

    def has_clear_range(self, numbers: list[int]):
        numbers.sort()

        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] != 1:
                return False
        self.range_selection_slider.setValue(numbers[0], numbers[-1])
        return True

    def updateDownloadRange(self):
        start, stop = self.range_selection_slider.value()
        self.selected_ids = []
        for num in range(start, stop + 1):
            self.selected_ids.append(num)

    def showPlaylistSelectionDialog(self):
        self.dialog = VideoSelectDialog(
            self.window(),
            self.widget_information.get("playlist-entries"),
            self.selected_ids,
        )
        result = self.dialog.exec()
        if result:
            self.selected_ids = self.dialog.get_selected()

            if self.selected_ids == [] or self.has_clear_range(self.selected_ids):
                self.range_selection_slider.setEnabled(True)
            else:
                self.range_selection_slider.setEnabled(False)

    def connectSignalsToSlots(self):
        self.best_video_btn.clicked.connect(lambda: self.setFormatOptions())
        self.best_audio_btn.clicked.connect(lambda: self.setFormatOptions(video=False))
        self.quick_dl_btn.clicked.connect(self.showFlyout)
        self.custom_dl_btn.clicked.connect(self.setAllFormatOptions)
        self.custom_dl_next_btn.clicked.connect(self.setResolutionOptions)
        self.custom_dl_back_btn.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0)
        )
        self.custom_dl_list_widget.itemSelectionChanged.connect(
            self.changeBtnVisibility
        )

        self.ListWidget.itemSelectionChanged.connect(self.setDownloadBtnVisible)

        self.custom_dl_next_btn.setVisible(False)
        self.custom_dl_dl_btn.setVisible(False)
        self.PrimaryPushButton_4.setVisible(False)

        self.PushButton.clicked.connect(self.goBack)
        self.PrimaryPushButton_4.clicked.connect(self.perform_download)

        self.SearchLineEdit.textChanged.connect(
            lambda text: self.filter_list(text, self.ListWidget)
        )
        self.custom_dl_line_edit.textChanged.connect(
            lambda text: self.filter_list(text, self.custom_dl_list_widget)
        )

        self.pl_next_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.back_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))

        self.PrimaryPushButton.clicked.connect(self.showPlaylistSelectionDialog)

        self.range_selection_slider.lowerValueChanged.connect(self.updateDownloadRange)
        self.range_selection_slider.upperValueChanged.connect(self.updateDownloadRange)

    def setIcons(self):
        url_type_icon = self.widget_information.get("url-type-icon")

        self.youtube_icon.setIcon(url_type_icon)
        self.author_icon.setIcon(CustomIcons.PERSON)
        self.duration_icon.setIcon(CustomIcons.TIME)
        self.calender_icon.setIcon(CustomIcons.CALENDER)
        self.playlist_length_icon.setIcon(CustomIcons.PLAYLIST)

        self.best_video_btn.setIcon(CustomIcons.VIDEO)
        self.best_audio_btn.setIcon(CustomIcons.AUDIO)
        self.quick_dl_btn.setIcon(CustomIcons.DOWNLOAD)
        self.custom_dl_btn.setIcon(CustomIcons.WRITE)

    def setTexts(self):
        url_type = self.widget_information.get("url-type")
        self.HyperlinkLabel.setText(url_type)

        title = self.widget_information.get("title")
        self.TitleLabel.setText(title)

        url = self.widget_information.get("url")
        self.HyperlinkLabel.setUrl(url)

        channel = self.widget_information.get("channel")
        self.StrongBodyLabel_2.setText(f"by {channel}")

        video_duration = self.widget_information.get("video-duration")
        self.BodyLabel_3.setText(video_duration)

        upload_date = self.widget_information.get("upload-date")
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

    def updateDropShadow(self):
        shadow_effect = QGraphicsDropShadowEffect(self.widget_8)
        shadow_effect.setBlurRadius(30)
        color = QColor(Qt.white) if isDarkTheme() else QColor(Qt.black)
        shadow_effect.setColor(color)
        shadow_effect.setOffset(0, 0)
        self.widget_8.setGraphicsEffect(shadow_effect)

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

    def setThumbnail(self, reply: QNetworkReply = None):
        if reply is None or reply.error() == QNetworkReply.NoError:
            if self.image_data == None:
                self.image_data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(self.image_data)

            scaled_pixmap = pixmap.scaled(
                QSize(400, 225), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            final_pixmap = QPixmap(400, 225)
            final_pixmap.fill(QColor("#202020") if isDarkTheme() else QColor("#F3F3F3"))

            painter = QPainter(final_pixmap)
            x_offset = (final_pixmap.width() - scaled_pixmap.width()) // 2
            y_offset = (final_pixmap.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
            painter.end()

            final_pixmap = self.round_pixmap_corners(final_pixmap, 10)
            self.updateDropShadow()

            self.PixmapLabel_2.setPixmap(final_pixmap)
        else:
            logger.error("Failed to download image. Error: %s", reply.errorString())

    def showFlyout(self):
        self.view = FlyoutView(
            title="",
            content="",
        )

        vid_button = PushButton("Video")
        vid_button.setIcon(self.best_video_btn.icon())
        vid_button.setFixedWidth(120)

        audio_button = PushButton("Audio")
        audio_button.setIcon(self.best_audio_btn.icon())
        audio_button.setFixedWidth(120)

        self.view.addWidget(vid_button, align=Qt.AlignRight)
        self.view.addWidget(audio_button, align=Qt.AlignRight)

        flyout = Flyout.make(
            target=self.quick_dl_btn, view=self.view, parent=self.parent()
        )

        vid_button.clicked.connect(
            lambda: [self.perform_download(quickdl=True, video=True), flyout.close()]
        )
        audio_button.clicked.connect(
            lambda: [self.perform_download(quickdl=True, video=False), flyout.close()]
        )

    def perform_download(self, quickdl: bool = False, video: bool = None):
        item = None
        format_id = ""

        if not quickdl:
            item = self.ListWidget.currentItem()
            if not isinstance(item, CustomListWidgetItem):
                item = self.custom_dl_list_widget.currentItem()
                if not isinstance(item, CustomListWidgetItem):
                    return

            format_id = item.item_id
        else:
            format_id = cfg.get(
                cfg.yt_video_quick_dl if video else cfg.yt_audio_quick_dl
            )
            if not format_id:
                return

            format, resolution = format_id.rsplit("/", 1)
            if resolution != "best":
                format_id = f"{format}/custom_res"
                resolution = resolution[:-1]

        options = {
            "ID": format_id,
            "ffmpeg_path": cfg.get(cfg.ffmpeg_path),
            "outtmpl": cfg.get(cfg.download_folder),
            "overwrites": True,
        }

        if "custom_res" in format_id:
            resolution_text = (
                self.ListWidget.currentItem().text() if not quickdl else None
            )
            resolution = resolution_text[:-1] if item and not quickdl else resolution
            options["format"] = resolution
            format_id = f"{format_id.rsplit('/', 1)[0]}/{resolution}"

        download_widget_manager.addVideoDownloadWidget(
            self.widget_information.get("thumbnail-url"),
            self.widget_information.get("title"),
            self.widget_information.get("channel"),
            format_id,
            self.widget_information.get("url"),
            **options,
        )

    def changeBtnVisibility(self):
        selectedItems = self.custom_dl_list_widget.selectedItems()
        if len(selectedItems) == 0:
            self.custom_dl_next_btn.setVisible(False)
            self.custom_dl_dl_btn.setVisible(False)
            return

        self.custom_dl_next_btn.setVisible(True)
        self.custom_dl_dl_btn.setVisible(False)

    def setDownloadBtnVisible(self):
        selectedItems = self.ListWidget.selectedItems()
        if len(selectedItems) == 0:
            self.PrimaryPushButton_4.setVisible(False)
        else:
            self.PrimaryPushButton_4.setVisible(True)

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

        for item in self.best_video_formats if video else self.best_audio_formats:
            list_item = CustomListWidgetItem(item["extension"], item["ID"])
            self.ListWidget.addItem(list_item)

        if self.ListWidget.count() > 0:
            self.ListWidget.setCurrentRow(0)

    def setAllFormatOptions(self):
        self.custom_dl_list_widget.clear()
        self.custom_dl_list_widget.clearSelection()
        self.stackedWidget.setCurrentIndex(2)
        self.custom_dl_line_edit.clear()
        self.back_to_all_formats = True

        for item in self.custom_video_formats:
            list_item = CustomListWidgetItem(item["extension"], item["ID"])
            self.custom_dl_list_widget.addItem(list_item)

        if self.custom_dl_list_widget.count() > 0:
            self.custom_dl_list_widget.setCurrentRow(0)

    def setResolutionOptions(self):
        self.ListWidget.clear()
        self.ListWidget.clearSelection()
        self.stackedWidget.setCurrentIndex(1)
        self.SearchLineEdit.clear()
        self.ListWidget.addItems(self.widget_information.get("available-resolutions"))

        if self.ListWidget.count() > 0:
            self.ListWidget.setCurrentRow(0)

    def filter_list(self, text: str, list_widget: QListWidget):
        text = text.lower()
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            item.setHidden(text not in item.text().lower())

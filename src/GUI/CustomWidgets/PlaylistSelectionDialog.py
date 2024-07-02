from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
)
from qfluentwidgets import (
    CheckBox,
    FluentStyleSheet,
    PrimaryPushButton,
    PushButton,
    SearchLineEdit,
    TableWidget,
)
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase


class VideoSelectDialog(MaskDialogBase):
    def __init__(self, parent=None, videos=None, selected_ids: list[int] = []):
        super().__init__(parent)

        self.setWindowTitle("Video Selection")

        self.videos = videos

        self.selected_ids = selected_ids

        self.search_title = True
        self.search_uploader = True

        self.buttonGroup = QFrame(self.widget)
        self.yesButton = PrimaryPushButton(self.tr("OK"), self.widget)
        self.cancelButton = QPushButton(self.tr("Cancel"), self.widget)

        self.search_title_checkbox = CheckBox("Search Title", self.widget)
        self.search_uploader_checkbox = CheckBox("Search Uploader", self.widget)
        self.search_index_checkbox = CheckBox("Search Index", self.widget)

        self.video_table = TableWidget(self.widget)

        self.search_input = SearchLineEdit(self.widget)

        self.select_all_button = PushButton("Select all", self.widget)
        self.deselect_all_button = PushButton("Deselect all", self.widget)

        self.main_layout = QVBoxLayout(self.widget)

        self.__initWidget()

        self.__loadData(self.videos)

    def __initWidget(self):
        self.search_title_checkbox.setChecked(True)
        self.search_uploader_checkbox.setChecked(True)
        self.search_index_checkbox.setChecked(False)

        self.video_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.video_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.video_table.setSortingEnabled(True)
        self.video_table.setColumnCount(3)
        self.video_table.setHorizontalHeaderLabels(
            ["Title", "Uploader", "Playlist Index"]
        )
        self.video_table.verticalHeader().setVisible(False)
        self.video_table.horizontalHeader().setSortIndicatorShown(True)
        self.video_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.video_table.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )

        self.search_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__setQss()
        self.__initLayout()
        self.__connectSignalsToSlots()

    def __initLayout(self):
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(12, 12, 12, 0)
        search_layout.addWidget(self.search_input)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(12, 0, 12, 0)
        button_layout.addWidget(self.search_title_checkbox)
        button_layout.addWidget(self.search_uploader_checkbox)
        button_layout.addWidget(self.search_index_checkbox)
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.deselect_all_button)

        table_layout = QHBoxLayout()
        table_layout.setContentsMargins(12, 0, 12, 0)
        table_layout.addWidget(self.video_table)

        button_layout2 = QHBoxLayout(self.buttonGroup)
        button_layout2.setSpacing(50)
        button_layout2.setContentsMargins(50, 9, 50, 9)
        button_layout2.addWidget(self.cancelButton)
        button_layout2.addWidget(self.yesButton)

        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addLayout(search_layout)
        self.main_layout.addLayout(button_layout)
        self.main_layout.addLayout(table_layout)
        self.main_layout.addWidget(self.buttonGroup)

    def __onYesButtonClicked(self):
        self.accept()
        # Accept logic here

    def __connectSignalsToSlots(self):
        self.cancelButton.clicked.connect(self.reject)
        self.yesButton.clicked.connect(self.__onYesButtonClicked)

        self.search_input.textChanged.connect(self.filter_videos)
        self.select_all_button.clicked.connect(self.video_table.selectAll)
        self.deselect_all_button.clicked.connect(self.video_table.clearSelection)
        self.search_title_checkbox.stateChanged.connect(self.filter_videos)
        self.search_uploader_checkbox.stateChanged.connect(self.filter_videos)
        self.search_index_checkbox.stateChanged.connect(self.filter_videos)

    def __setQss(self):
        FluentStyleSheet.COLOR_DIALOG.apply(self)
        self.yesButton.setObjectName("yesButton")
        self.cancelButton.setObjectName("cancelButton")
        self.buttonGroup.setObjectName("buttonGroup")

    def __loadData(self, videos=None):
        self.video_table.setRowCount(len(videos))
        for row, video in enumerate(videos):
            title_item = QTableWidgetItem(video["title"])
            uploader_item = QTableWidgetItem(video["uploader"])
            playlist_index_item = PlaylistIndexTableWidgetItem(
                str(video["playlist_index"] + 1)
            )

            self.video_table.setItem(row, 0, title_item)
            self.video_table.setItem(row, 1, uploader_item)
            self.video_table.setItem(row, 2, playlist_index_item)

            for col in range(self.video_table.columnCount()):
                self.video_table.item(row, col).setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                )

        for index in self.selected_ids:
            self.video_table.delegate.selectedRows.add(index - 1)

    def filter_videos(self):
        self.video_table.keyboardSearch
        text = self.search_input.text().lower()
        self.video_table.setUpdatesEnabled(False)
        for row in range(self.video_table.rowCount()):
            title_item = self.video_table.item(row, 0)
            uploader_item = self.video_table.item(row, 1)
            index_item = self.video_table.item(row, 2)

            title_contains_text = (
                self.search_title_checkbox.isChecked()
                and text in title_item.text().lower()
            )
            uploader_contains_text = (
                self.search_uploader_checkbox.isChecked()
                and text in uploader_item.text().lower()
            )
            index_contains_text = (
                self.search_index_checkbox.isChecked() and text in index_item.text()
            )

            if title_contains_text or uploader_contains_text or index_contains_text:
                self.video_table.showRow(row)
            else:
                self.video_table.hideRow(row)
        self.video_table.setUpdatesEnabled(True)

    def get_selected(self) -> list[int]:
        return [index + 1 for index in self.video_table.delegate.selectedRows]


class PlaylistIndexTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other: QTableWidgetItem):
        if self.column() == 2 and other.column() == 2:
            return int(self.text()) < int(other.text())
        return super().__lt__(other)

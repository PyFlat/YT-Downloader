from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from src.CustomWidgets.CustomTableWidget import CustomTableWidget

class VideoSelectDialog(QDialog):
    def __init__(self, parent=None, dl=None, videos=None):
        super().__init__(parent)
        self.setMinimumSize(1150, 550)
        self.setWindowTitle(dl.tm.get_inline_string("video-selector"))

        self.search_title_checkbox = QCheckBox(dl.tm.get_inline_string("search-title"))
        self.search_title_checkbox.setChecked(True)
        self.search_uploader_checkbox = QCheckBox(dl.tm.get_inline_string("search-uploader"))
        self.search_uploader_checkbox.setChecked(True)
        self.search_index_checkbox = QCheckBox(dl.tm.get_inline_string("search-index"))
        self.search_index_checkbox.setChecked(False)

        self.video_table = CustomTableWidget()
        self.video_table.setSortingEnabled(True)
        self.video_table.setColumnCount(4)
        self.video_table.setHorizontalHeaderLabels([dl.tm.get_inline_string("Auswählen"),
                                                    dl.tm.get_inline_string("title2"),
                                                    dl.tm.get_inline_string("uploader2"),
                                                    dl.tm.get_inline_string("playlist-index")])
        self.video_table.verticalHeader().setVisible(False)
        self.video_table.horizontalHeader().setSortIndicatorShown(False)
        self.video_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.video_table.setSelectionMode(QAbstractItemView.NoSelection)

        self.search_input = QLineEdit()
        self.search_input.setAlignment(Qt.AlignCenter)
        self.search_input.textChanged.connect(self.delayed_filter_videos)

        self.load_videos(videos)

        self.select_all_button = QPushButton(dl.tm.get_inline_string("select-all"))
        self.select_all_button.clicked.connect(self.select_all_videos)

        self.deselect_all_button = QPushButton(dl.tm.get_inline_string("deselect-all"))
        self.deselect_all_button.clicked.connect(self.deselect_all_videos)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.deselect_all_button)

        search_criteria_group = QGroupBox(dl.tm.get_inline_string("search-criteria"))
        search_criteria_layout = QHBoxLayout()
        search_criteria_layout.setSpacing(24)
        search_criteria_layout.setAlignment(Qt.AlignLeft)
        search_criteria_layout.addWidget(self.search_title_checkbox)
        search_criteria_layout.addWidget(self.search_uploader_checkbox)
        search_criteria_layout.addWidget(self.search_index_checkbox)
        search_criteria_group.setLayout(search_criteria_layout)

        search_layout = QFormLayout()
        search_layout.addRow(dl.tm.get_inline_string("search"), self.search_input)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(search_criteria_group)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.video_table)

        self.setLayout(main_layout)

        for i in range(4):
            self.video_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch if i > 0 else QHeaderView.ResizeToContents)

        self.search_title_checkbox.stateChanged.connect(self.delayed_filter_videos)
        self.search_uploader_checkbox.stateChanged.connect(self.delayed_filter_videos)

        self.search_title = True
        self.search_uploader = True

        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.filter_videos)
        self.filter_delay = 300

    def load_videos(self, videos=None):
        self.video_table.setRowCount(len(videos))
        for row, video in enumerate(videos):
            title_item = QTableWidgetItem(video["title"])
            uploader_item = QTableWidgetItem(video["uploader"])
            playlist_index_item = PlaylistIndexTableWidgetItem(str(video["playlist_index"]+1))
            checkBoxWidget = QWidget()
            checkBoxWidget.setObjectName("widget")
            checkBox = QCheckBox()
            checkBox.setObjectName("checkbox")
            checkBox.setChecked(video["selected"])

            layoutCheckBox = QHBoxLayout(checkBoxWidget)

            layoutCheckBox.addWidget(checkBox)

            checkBoxWidget.setStyleSheet("QWidget#widget{border-left: 2px solid white;}QCheckBox{padding: 2px}")

            layoutCheckBox.setContentsMargins(7,0,0,0)

            self.video_table.setCellWidget(row, 0, checkBoxWidget)
            self.video_table.setItem(row, 1, title_item)
            self.video_table.setItem(row, 2, uploader_item)
            self.video_table.setItem(row, 3, playlist_index_item)

            for col in range(1, self.video_table.columnCount()):
                self.video_table.item(row, col).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    def delayed_filter_videos(self):
        self.filter_timer.start(self.filter_delay)

    def filter_videos(self):
        text = self.search_input.text().lower()
        for row in range(self.video_table.rowCount()):
            title_item = self.video_table.item(row, 1)
            uploader_item = self.video_table.item(row, 2)
            index_item  = self.video_table.item(row, 3)
            title_contains_text = self.search_title_checkbox.isChecked() and text in title_item.text().lower()
            uploader_contains_text = self.search_uploader_checkbox.isChecked() and text in uploader_item.text().lower()
            index_contains_text = self.search_index_checkbox.isChecked() and text in index_item.text()
            if title_contains_text or uploader_contains_text or index_contains_text:
                self.video_table.setRowHidden(row, False)
            else:
                self.video_table.setRowHidden(row, True)

    def get_selected(self):
        ids = []
        for row in range(self.video_table.rowCount()):
            checkbox_widget = self.video_table.cellWidget(row, 0)
            checkbox_item = checkbox_widget.findChild(QCheckBox, "checkbox")
            if checkbox_item.isChecked():
                index_item = self.video_table.item(row, 3)
                ids.append(int(index_item.text()))

        return ids

    def select_all_videos(self):
        for row in range(self.video_table.rowCount()):
            checkbox_widget = self.video_table.cellWidget(row, 0)
            checkbox_item = checkbox_widget.findChild(QCheckBox, "checkbox")
            checkbox_item.setChecked(True)

    def deselect_all_videos(self):
        for row in range(self.video_table.rowCount()):
            checkbox_widget = self.video_table.cellWidget(row, 0)
            checkbox_item = checkbox_widget.findChild(QCheckBox, "checkbox")
            checkbox_item.setChecked(False)

class PlaylistIndexTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if (self.column() == 3 and other.column() == 3):
            return int(self.text()) < int(other.text())
        return super().__lt__(other)
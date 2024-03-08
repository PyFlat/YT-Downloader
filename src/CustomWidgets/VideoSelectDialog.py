from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from src.CustomWidgets.CustomTableWidget import CustomTableWidget

class VideoSelectDialog(QDialog):
    def __init__(self, parent=None, videos=None):
        super().__init__(parent)
        self.setMinimumSize(1150, 550)
        self.setWindowTitle("Video Selector")

        # Search Criteria
        self.search_title_checkbox = QCheckBox("Search Title")
        self.search_title_checkbox.setChecked(True)
        self.search_uploader_checkbox = QCheckBox("Search Uploader")
        self.search_uploader_checkbox.setChecked(True)
        self.search_index_checkbox = QCheckBox("Search Index")
        self.search_index_checkbox.setChecked(False)

        # Video Table
        self.video_table = CustomTableWidget()
        self.video_table.setSortingEnabled(True)
        self.video_table.setColumnCount(4)
        self.video_table.setHorizontalHeaderLabels(["Select", "Title", "Uploader", "Playlist Index"])
        self.video_table.verticalHeader().setVisible(False)
        self.video_table.horizontalHeader().setSortIndicatorShown(False)
        self.video_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.video_table.setSelectionMode(QAbstractItemView.NoSelection)

        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setAlignment(Qt.AlignCenter)
        self.search_input.textChanged.connect(self.delayed_filter_videos)

        # Load Videos
        self.load_videos(videos)

        # Select/Deselect Buttons
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_videos)

        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_videos)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.deselect_all_button)

        # Search Criteria Group
        search_criteria_group = QGroupBox("Search Criteria")
        search_criteria_layout = QHBoxLayout()
        search_criteria_layout.setSpacing(24)
        search_criteria_layout.setAlignment(Qt.AlignLeft)
        search_criteria_layout.addWidget(self.search_title_checkbox)
        search_criteria_layout.addWidget(self.search_uploader_checkbox)
        search_criteria_layout.addWidget(self.search_index_checkbox)
        search_criteria_group.setLayout(search_criteria_layout)

        # Search Layout
        search_layout = QFormLayout()
        search_layout.addRow("Search:", self.search_input)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(search_criteria_group)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.video_table)

        self.setLayout(main_layout)

        # Set Section Resize Modes
        for i in range(4):
            self.video_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch if i > 0 else QHeaderView.ResizeToContents)

        # Connect Checkbox Signals
        self.search_title_checkbox.stateChanged.connect(self.delayed_filter_videos)
        self.search_uploader_checkbox.stateChanged.connect(self.delayed_filter_videos)

        # Set Default Values
        self.search_title = True
        self.search_uploader = True

        # Timer for Delayed Filtering
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
            checkbox_item = QCheckBox()

            self.video_table.setCellWidget(row, 0, checkbox_item)
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

    def select_all_videos(self):
        for row in range(self.video_table.rowCount()):
            checkbox_item = self.video_table.cellWidget(row, 0)
            checkbox_item.setChecked(True)

    def deselect_all_videos(self):
        for row in range(self.video_table.rowCount()):
            checkbox_item = self.video_table.cellWidget(row, 0)
            checkbox_item.setChecked(False)

class PlaylistIndexTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if (self.column() == 3 and other.column() == 3):  # Check if sorting the playlist index column
            return int(self.text()) < int(other.text())
        return super().__lt__(other)  # For other columns, use default sorting behavior
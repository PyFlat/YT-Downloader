from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class VideoSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Selector")

        self.video_table = QTableWidget()
        self.video_table.setColumnCount(3)  # Title, Uploader, Checkbox
        self.video_table.setHorizontalHeaderLabels(["", "Uploader", "Title"])
        self.video_table.verticalHeader().setVisible(False)
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_videos)

        self.load_videos()

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_videos)

        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_videos)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.deselect_all_button)

        self.select_range_slider = QSlider(Qt.Horizontal)
        self.select_range_slider.setMinimum(0)
        self.select_range_slider.setMaximum(self.video_table.rowCount() - 1)
        self.select_range_slider.setTickInterval(1)
        self.select_range_slider.setTickPosition(QSlider.TicksBelow)

        self.select_range_slider.sliderReleased.connect(self.select_range)

        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addLayout(button_layout)
        layout.addWidget(self.select_range_slider)
        layout.addWidget(self.video_table)

        self.setLayout(layout)

        self.selected_rows = []

    def load_videos(self):
        videos = [
            {"title": "Video 1", "uploader": "Uploader A"},
            {"title": "Video 2", "uploader": "Uploader B"},
            {"title": "Video 3", "uploader": "Uploader C"},
            {"title": "Video 4", "uploader": "Uploader D"}
        ]

        self.video_table.setRowCount(len(videos))
        for row, video in enumerate(videos):
            title_item = QTableWidgetItem(video["title"])
            uploader_item = QTableWidgetItem(video["uploader"])
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.Unchecked)

            self.video_table.setItem(row, 0, checkbox_item)
            self.video_table.setItem(row, 1, title_item)
            self.video_table.setItem(row, 2, uploader_item)

    def filter_videos(self, text):
        for row in range(self.video_table.rowCount()):
            title_item = self.video_table.item(row, 1)
            if title_item.text().lower().startswith(text.lower()):
                self.video_table.setRowHidden(row, False)
            else:
                self.video_table.setRowHidden(row, True)

    def select_all_videos(self):
        for row in range(self.video_table.rowCount()):
            checkbox_item = self.video_table.item(row, 0)
            checkbox_item.setCheckState(Qt.Checked)

    def deselect_all_videos(self):
        for row in range(self.video_table.rowCount()):
            checkbox_item = self.video_table.item(row, 0)
            checkbox_item.setCheckState(Qt.Unchecked)

    def select_range(self):
        slider_value = self.select_range_slider.value()
        for row in range(self.video_table.rowCount()):
            checkbox_item = self.video_table.item(row, 0)
            if row <= slider_value:
                checkbox_item.setCheckState(Qt.Checked)
            else:
                checkbox_item.setCheckState(Qt.Unchecked)
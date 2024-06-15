from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from qfluentwidgets import *

from src.Config.Config import cfg


class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, text: str = "", format_id: str = ""):
        super().__init__(text)
        self.format_id = format_id


class FormatSelectDialog(MessageBoxBase):
    def __init__(
        self,
        parent=None,
        subtitle: str = None,
        data: list[list[str]] = None,
        resolutions: list[str] = None,
        config_key: str = None,
        alignment: Qt.AlignmentFlag = Qt.AlignCenter,
    ):
        super().__init__(parent=parent)
        self.resolutions = resolutions
        self.config_key = config_key
        self.data = data or []
        self.alignment = alignment

        self.current_step = "formats"

        self.current_extension = None

        self.init_ui(subtitle)
        self.populate_list(self.data)

    def init_ui(self, subtitle):
        self.search = LineEdit()
        self.search.setAlignment(Qt.AlignCenter)
        self.search.setPlaceholderText("Search ...")
        self.search.textChanged.connect(self.filter_list)

        self.listWidget = ListWidget(self)
        self.listWidget.currentItemChanged.connect(self.update_button_visibility)
        self.listWidget.setMaximumHeight(160)

        title_label = SubtitleLabel(subtitle)
        self.viewLayout.addWidget(title_label)
        self.viewLayout.addWidget(self.search)
        self.viewLayout.addWidget(self.listWidget)

        self.hideCancelButton = self.cancelButton.hide
        self.hideYesButton = self.yesButton.hide

        self.cancel_btn = PushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        self.back_btn = PushButton("Back")
        self.back_btn.clicked.connect(self.last_step)

        self.yes_btn = PrimaryPushButton("Ok")
        self.yes_btn.clicked.connect(self.finish)

        self.next_btn = PushButton("Next")
        self.next_btn.clicked.connect(self.next_step)

        self.buttonLayout.addWidget(self.cancel_btn)
        self.buttonLayout.addWidget(self.back_btn)
        self.buttonLayout.addWidget(self.yes_btn)
        self.buttonLayout.addWidget(self.next_btn)

        self.hideCancelButton()
        self.hideYesButton()
        self.update_button_visibility()

    def populate_list(self, data):
        self.listWidget.clear()
        for format in data:
            item = CustomListWidgetItem(*format)
            item.setTextAlignment(self.alignment)
            self.listWidget.addItem(item)
        self.listWidget.clearSelection()

    def update_button_visibility(self):
        if self.current_step == "formats":
            self.back_btn.setVisible(False)
            self.next_btn.setVisible(False)
            self.yes_btn.setVisible(False)
            current_item = self.listWidget.currentItem()
            if current_item and "custom" in current_item.text().lower():
                self.next_btn.setVisible(True)
            else:
                self.yes_btn.setVisible(current_item is not None)
        elif self.current_step == "resolutions":
            self.back_btn.setVisible(True)
            self.next_btn.setVisible(False)
            current_item = self.listWidget.currentItem()
            self.yes_btn.setVisible(current_item is not None)

    def last_step(self):
        self.current_step = "formats"
        self.populate_list(self.data)
        self.update_button_visibility()

    def next_step(self):
        self.current_step = "resolutions"
        self.current_extension: CustomListWidgetItem = self.listWidget.selectedItems()[
            0
        ]
        self.populate_list([[res] for res in self.resolutions])
        self.update_button_visibility()

    def finish(self):
        current_item: CustomListWidgetItem = self.listWidget.selectedItems()[0]
        format_id = (
            self.current_extension.format_id
            if self.current_extension
            else current_item.format_id
        ).lower()

        if self.current_extension and "custom" in format_id:
            resulting_id = self.current_extension.format_id.replace(
                "custom_res", current_item.text()
            )
        else:
            resulting_id = format_id

        cfg.set(self.config_key, resulting_id)

        self.accept()

    def filter_list(self, text: str):
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

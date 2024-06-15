from PySide6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import BodyLabel, ExpandGroupSettingCard, FluentIcon, PushButton

from src.Config.Config import cfg
from src.GUI.Dialogs.FormatSelectDialog import FormatSelectDialog


class BaseSettingCard(ExpandGroupSettingCard):
    def __init__(
        self,
        icon: FluentIcon,
        title: str,
        description: str,
        parent=None,
        settingInterface=None,
    ):
        super().__init__(icon, title, description, parent)
        self.settingInterface = settingInterface
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)
        self.audio_label = None
        self.video_label = None

    def add_setting(
        self, config_key: object, is_video: bool = True, format_dict: dict = None
    ):
        download_type = "video" if is_video else "audio"
        label = BodyLabel(
            f"Quick {download_type} download options: {self.format_formatId_string(cfg.get(config_key))}"
        )

        if is_video:
            self.video_label = label
        else:
            self.audio_label = label

        button = PushButton("Change")
        button.clicked.connect(
            lambda: self.showOptionsDialog(is_video, format_dict, config_key)
        )
        button.setFixedWidth(135)

        widget = QWidget()
        widget.setFixedHeight(60)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(48, 12, 48, 12)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(button)

        self.addGroupWidget(widget)

    def format_formatId_string(self, formatId: str) -> str:
        _, part1, part2 = formatId.split("/")
        return f"{part1.upper()} ({part2.capitalize()})"

    def showOptionsDialog(
        self, is_video: bool = True, format_dict: dict = None, config_key=None
    ):
        formats = (
            format_dict.get("video_formats")
            if is_video
            else format_dict.get("audio_formats")
        )

        selectable_formats = [
            [
                f"{format.get('extension')} ({'Best' if format.get('best_format') else 'Custom'})",
                format.get("ID"),
            ]
            for format in formats
        ]

        dialog = FormatSelectDialog(
            self.settingInterface,
            "Select file extension",
            selectable_formats,
            format_dict.get("resolutions"),
        )
        dialog.exec()

        download_type = "video" if is_video else "audio"
        config_key = cfg.yt_video_quick_dl if is_video else cfg.yt_audio_quick_dl
        format_str = self.format_formatId_string(cfg.get(config_key))

        label = self.video_label if is_video else self.audio_label
        label.setText(f"Quick {download_type} download options: {format_str}")

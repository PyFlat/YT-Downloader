from PySide6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import BodyLabel, ExpandGroupSettingCard, PushButton

from src.GUI.Icons.Icons import CustomIcons


class YouTubeSettingCard(ExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(
            CustomIcons.YOUTUBE,
            "YouTube options",
            "Set default download parameters for youtube.com",
            parent,
        )

        self.quick_dl_video_btn = PushButton("Change")
        self.quick_dl_video_label = BodyLabel(
            "Quick Video Download Options: MP4 / 1080p"
        )
        self.quick_dl_video_btn.setFixedWidth(135)

        self.quick_dl_audio_btn = PushButton("Change")
        self.quick_dl_audio_label = BodyLabel("Quick Audio Download Options: MP3")
        self.quick_dl_audio_btn.setFixedWidth(135)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add(self.quick_dl_video_label, self.quick_dl_video_btn)
        self.add(self.quick_dl_audio_label, self.quick_dl_audio_btn)

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        self.addGroupWidget(w)

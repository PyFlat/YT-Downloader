from src.Config.Config import cfg
from src.DownloaderCore.formats import YOUTUBE_VIDEO
from src.GUI.CustomWidgets.BaseSettingCard import BaseSettingCard
from src.GUI.Icons.Icons import CustomIcons


class YouTubeSettingCard(BaseSettingCard):
    def __init__(self, parent=None, settingInterface=None):
        super().__init__(
            CustomIcons.YOUTUBE,
            "YouTube options",
            "Set default download parameters for youtube.com",
            parent,
            settingInterface,
        )

        self.add_setting(cfg.yt_video_quick_dl, True, YOUTUBE_VIDEO)
        self.add_setting(cfg.yt_audio_quick_dl, False, YOUTUBE_VIDEO)

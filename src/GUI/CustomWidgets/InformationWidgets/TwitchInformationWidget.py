from datetime import datetime

from src.DownloaderCore.Downloader import Downloader
from src.GUI.CustomWidgets.InformationWidgets.BaseInformationWidget import (
    BaseInformationWidget,
)
from src.GUI.Icons.Icons import CustomIcons
from src.utils import transformVideoDuration


class TwitchInformationWidget(BaseInformationWidget):
    def __init__(
        self,
        parent=None,
        info_dict: dict = None,
        downloader: Downloader = None,
        video_type: dict = {},
    ):

        self.info = info_dict

        thumbnail_url = self.info.get("thumbnail")

        widget_information = {
            "downloader": downloader,
            "url": self.info["original_url"],
            "thumbnail-url": thumbnail_url,
            "title": self.info["title"],
            "channel": self.info["uploader"],
            "url-type": "Twitch Video",
            "url-type-icon": CustomIcons.TWITCH,
            "video-duration": transformVideoDuration(self.info["duration"]),
            "upload-date": datetime.strptime(
                self.info["upload_date"], "%Y%m%d"
            ).strftime("%d.%m.%Y"),
        }

        super().__init__(parent, widget_information, video_type)

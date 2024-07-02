import re
from datetime import datetime

from src.DownloaderCore.Downloader import Downloader
from src.GUI.CustomWidgets.BaseInformationWidget import BaseInformationWidget
from src.GUI.Icons.Icons import CustomIcons
from src.utils import transformVideoDuration


class TikTokInformationWidget(BaseInformationWidget):
    def __init__(
        self,
        parent=None,
        info_dict: dict = None,
        downloader: Downloader = None,
        video_type: dict = {},
    ):

        self.info = info_dict

        small_thumbnail_url = None

        for thumbnail in self.info.get("thumbnails", []):
            if thumbnail.get("id") == "0":
                small_thumbnail_url = thumbnail.get("url")
                break

        widget_information = {
            "downloader": downloader,
            "url": self.info["original_url"],
            "thumbnail-url": small_thumbnail_url,
            "title": self.info["title"],
            "channel": self.info["uploader"],
            "url-type": "TikTok Video",
            "url-type-icon": CustomIcons.TIKTOK,
            "video-duration": transformVideoDuration(),
            "upload-date": datetime.strptime(
                self.info["upload_date"], "%Y%m%d"
            ).strftime("%d.%m.%Y"),
        }

        super().__init__(parent, widget_information, video_type)

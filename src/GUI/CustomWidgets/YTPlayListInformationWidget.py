import json
from datetime import datetime

from src.DownloaderCore.Downloader import Downloader
from src.GUI.CustomWidgets.BaseInformationWidget import BaseInformationWidget
from src.GUI.Icons.Icons import CustomIcons
from src.utils import getPlaylistSum, transformVideoDuration


class YTPlayListInformationWidget(BaseInformationWidget):
    def __init__(
        self,
        parent=None,
        info_dict: dict = None,
        downloader: Downloader = None,
        video_type: dict = {},
    ):
        self.info = info_dict

        thumbnail_url = None

        for thumbnail in self.info.get("thumbnails", []):
            if thumbnail.get("id") == "3":
                thumbnail_url = thumbnail.get("url")
                break

        widget_information = {
            "downloader": downloader,
            "url": self.info["original_url"],
            "thumbnail-url": thumbnail_url,
            "title": self.info["title"],
            "channel": self.info["channel"],
            "url-type": "YouTube Video",
            "url-type-icon": CustomIcons.YOUTUBE,
            "video-duration": transformVideoDuration(
                getPlaylistSum(self.info["entries"])
            ),
            "upload-date": datetime.strptime(
                self.info["modified_date"], "%Y%m%d"
            ).strftime("%d.%m.%Y"),
            "playlist-length": self.info["playlist_count"],
            "playlist-entries": self.info["entries"],
        }

        super().__init__(parent, widget_information, video_type, is_playlist=True)

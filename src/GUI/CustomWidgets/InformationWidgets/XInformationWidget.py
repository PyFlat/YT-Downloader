import re
from datetime import datetime

from src.DownloaderCore.Downloader import Downloader
from src.GUI.CustomWidgets.InformationWidgets.BaseInformationWidget import (
    BaseInformationWidget,
)
from src.GUI.Icons.Icons import CustomIcons
from src.utils import transformVideoDuration


class XInformationWidget(BaseInformationWidget):

    def __init__(
        self,
        parent=None,
        setting_interface=None,
        info_dict: dict = None,
        downloader: Downloader = None,
        video_type: dict = {},
    ):
        self.info = info_dict

        small_thumbnail_url = None

        for thumbnail in self.info.get("thumbnails", []):
            if thumbnail.get("id") == "small":
                small_thumbnail_url = thumbnail.get("url")
                break

        widget_information = {
            "downloader": downloader,
            "url": self.info["original_url"],
            "thumbnail-url": small_thumbnail_url,
            "title": self.info["title"],
            "channel": self.info["uploader"],
            "url-type": "X Video",
            "url-type-icon": CustomIcons.X,
            "video-duration": transformVideoDuration(self.info["duration"]),
            "upload-date": datetime.strptime(
                self.info["upload_date"], "%Y%m%d"
            ).strftime("%d.%m.%Y"),
            "available-resolutions": self.get_available_resolutions(),
        }

        super().__init__(parent, setting_interface, widget_information, video_type)

    def get_available_resolutions(self) -> list[str]:
        resolution = []
        for stream in self.info["formats"]:
            if stream["video_ext"] != "none":
                stre = f"{stream['resolution'].split('x')[1]}p"
                if stre not in resolution:
                    resolution.append(stre)
        resolution = sorted(
            resolution,
            key=lambda s: int(re.compile(r"\d+").search(s).group()),
            reverse=True,
        )
        return resolution

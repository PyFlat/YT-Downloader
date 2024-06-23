import re
from datetime import datetime

from src.DownloaderCore.Downloader import Downloader
from src.DownloaderCore.formats import YOUTUBE_VIDEO
from src.GUI.CustomWidgets.BaseInformationWidget import BaseInformationWidget
from src.GUI.Icons.Icons import CustomIcons


class YTInformationWidget(BaseInformationWidget):
    def __init__(
        self, parent=None, info_dict: dict = None, downloader: Downloader = None
    ):

        custom_video_formats = [
            x
            for x in YOUTUBE_VIDEO.get("video_formats", [])
            if not x.get("best_format")
        ]
        best_video_formats = [
            x for x in YOUTUBE_VIDEO.get("video_formats", []) if x.get("best_format")
        ]

        best_audio_formats = [x for x in YOUTUBE_VIDEO.get("audio_formats", [])]

        self.info = info_dict

        widget_information = {
            "downloader": downloader,
            "url": self.info["original_url"],
            "thumbnail-url": f"https://i.ytimg.com/vi/{self.info['display_id']}/mqdefault.jpg",
            "title": self.info["title"],
            "channel": self.info["channel"],
            "url-type-icon": CustomIcons.YOUTUBE,
            "video-duration": self.getVideoDuration(),
            "upload-date": datetime.strptime(
                self.info["upload_date"], "%Y%m%d"
            ).strftime("%d.%m.%Y"),
            "custom-vid-formats": custom_video_formats,
            "best-vid-formats": best_video_formats,
            "best-audio-formats": best_audio_formats,
            "available-resolutions": self.get_available_resolutions(),
        }

        super().__init__(parent, widget_information)

    def getVideoDuration(self) -> str:
        minutes, seconds = divmod(self.info["duration"], 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            duration = f"{hours:02} hours, {minutes:02} minutes, {seconds:02} seconds"
        elif minutes > 0:
            duration = f"{minutes:02} minutes, {seconds:02} seconds"
        else:
            duration = f"{seconds:02} seconds"

        return duration

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

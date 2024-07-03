from enum import Enum

from qfluentwidgets import FluentIconBase, Theme, getIconColor


class CustomIcons(FluentIconBase, Enum):
    AUDIO = "audio"
    CALENDER = "calender"
    DOWNLOAD = "download"
    FFMPEG = "ffmpeg"
    PERSON = "person"
    TIME = "time"
    VIDEO = "video"
    WRITE = "write"
    YOUTUBE = "youtube"
    YOUTUBE2 = "youtube2"
    X = "x"
    TIKTOK = "tiktok"
    PLAYLIST = "playlist_length"
    CHEVRON_DOWN = "chevron_down"
    CHEVRON_UP = "chevron_up"

    def path(self, theme=Theme.AUTO):
        return f"src/GUI/Icons/icons_{getIconColor(theme)}/{self.value}_{getIconColor(theme)}.svg"

    def toString(self):
        return self.value

    @classmethod
    def generate_mapping(cls, icon_name):
        mapping = {icon.value: icon for icon in cls}
        return mapping.get(icon_name, None)

from enum import Enum
from qfluentwidgets import getIconColor, Theme, FluentIconBase

class CustomIcons(FluentIconBase, Enum):
    AUDIO = "audio"
    CALENDER = "calender"
    DOWNLOAD = "download"
    PERSON = "person"
    TIME = "time"
    VIDEO = "video"
    WRITE = "write"
    YOUTUBE = "youtube"

    def path(self, theme=Theme.AUTO):
        return f'src/GUI/Icons/icons_{getIconColor(theme)}/{self.value}_{getIconColor(theme)}.svg'

    def toString(self):
        return self.value

    @classmethod
    def generate_mapping(cls, icon_name):
        mapping = {icon.value: icon for icon in cls}
        return mapping.get(icon_name, None)
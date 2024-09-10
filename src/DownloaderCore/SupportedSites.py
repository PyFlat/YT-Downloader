from src.DownloaderCore.formats import *
from src.GUI.CustomWidgets.InformationWidgets.TikTokInformationWidget import (
    TikTokInformationWidget,
)
from src.GUI.CustomWidgets.InformationWidgets.TwitchInformationWidget import (
    TwitchInformationWidget,
)
from src.GUI.CustomWidgets.InformationWidgets.XInformationWidget import (
    XInformationWidget,
)
from src.GUI.CustomWidgets.InformationWidgets.YTInformationWidget import (
    YTInformationWidget,
)
from src.GUI.CustomWidgets.InformationWidgets.YTPlayListInformationWidget import (
    YTPlayListInformationWidget,
)

VIDEO_SITES = {
    "youtube.com": {
        "data": YOUTUBE_VIDEO,
        "widget": YTInformationWidget,
        "playlist-widget": YTPlayListInformationWidget,
    },
    "x.com": {"data": X_VIDEO, "widget": XInformationWidget},
    "tiktok.com": {"data": TIKTOK_VIDEO, "widget": TikTokInformationWidget},
    "twitch.tv": {"data": TWITCH_VIDEO, "widget": TwitchInformationWidget},
}

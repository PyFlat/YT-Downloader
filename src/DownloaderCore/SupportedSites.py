from src.DownloaderCore.formats import *
from src.GUI.CustomWidgets.TikTokInformationWidget import TikTokInformationWidget
from src.GUI.CustomWidgets.XInformationWidget import XInformationWidget
from src.GUI.CustomWidgets.YTInformationWidget import YTInformationWidget

VIDEO_SITES = {
    "youtube.com": {
        "data": YOUTUBE_VIDEO,
        "widget": YTInformationWidget,
    },
    "x.com": {"data": X_VIDEO, "widget": XInformationWidget},
    "tiktok.com": {"data": TIKTOK_VIDEO, "widget": TikTokInformationWidget},
}

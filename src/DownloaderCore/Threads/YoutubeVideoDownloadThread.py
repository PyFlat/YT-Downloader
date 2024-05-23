try:
    from src.DownloaderCore.formats import YOUTUBE_VIDEO
    from src.DownloaderCore.Threads.VideoDownloadThread import VideoDownloadThread
except ModuleNotFoundError:
    from Threads.VideoDownloadThread import VideoDownloadThread
class YoutubeVideoDownloadThread(VideoDownloadThread):
    def __init__(self, yt_dlp: object, url: str, finished_callback: object | None = None, progress_callback: object | None = None, **options) -> None:

        new_options = {}
        for option in YOUTUBE_VIDEO.get("video_formats"):
            if "ID" in options and options["ID"] == option["ID"]:
                new_options = option["yt_dlp_options"]

        if new_options == {}:
            raise ValueError("Invalid or missing ID")

        new_options["progress_hooks"] = [super()._progress_hook]
        new_options["postprocessor_hooks"] = [super()._finish_hook]

        for key in options:
            if key in new_options:
                new_options[key] = options[key]

        super().__init__(yt_dlp, url, new_options, finished_callback, progress_callback)
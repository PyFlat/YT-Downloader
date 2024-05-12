from PySide6.QtCore import QRunnable
try:
    from src.DownloaderCore.Threads.Signal import Signal
except ModuleNotFoundError:
    from Threads.Signal import Signal

class InformationLoadThread(QRunnable):
    def __init__(self, url: str, all_playlist: bool, finished_callback: object) -> None:
        super().__init__()
        self.__on_finish = Signal(dict, str)
        self.__url = url
        self.__all_playlist = all_playlist
        self.__on_finish.connect(finished_callback)
    def run(self):
        options = {"quiet": True,
                        "noprogress": True,
                        "extract_flat": "in_playlist"
                    }
        if not self.__all_playlist:
            options["playlist_items"] = "0"
        try:
            from yt_dlp import YoutubeDL
            from yt_dlp.utils import DownloadError
        except ModuleNotFoundError:
            print("Youtube-dlp has not been found. Have you forgot to install it?")
            self.__on_finish.emit({"error":"yt-dl-not-found"}, self.__url)
            return
        ydl = YoutubeDL(options)
        try:
            inf = ydl.extract_info(self.__url, False)
            result = ydl.sanitize_info(inf)
        except DownloadError as e:
            result = {}
            if "urlopen error" in e.msg:
                #connection error
                result = {"error":"connection-error"}
            elif "ytsearch" in e.msg:
                result = {"error":"ytsearch"}
            else:
                result = {"error":e.msg}
        except Exception as e:
            if e.__class__.__name__ == "NoSupportingHandlers":
                result = {"error": "NoSupportingHandlers"}
                #NoSupportingHandler
            else:
                result = {"error": str(e)} 
        self.__on_finish.emit(result, self.__url)
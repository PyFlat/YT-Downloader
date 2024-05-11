from PySide6.QtCore import QThread, Signal
class VideoDownloadThread(QThread):
    __on_finish = Signal(bool)
    __on_progress = Signal(str, str)
    def __init__(self, url: str = "https://www.youtube.com/watch?v=HBEsr0MfdmQ", options : dict[str, object] = {}, finished_callback: object| None = None, progress_callback: object | None = None) -> None:
        super().__init__()
        if finished_callback != None:
            self.__on_finish.connect(finished_callback)
        if progress_callback != None:
            self.__on_progress.connect(progress_callback)

        self.url = url
        self.download_options = options
    def _finish_hook(self, d):
        pass
    def _progress_hook(self, d):
        pass
    def run(self):
        try:
            from yt_dlp import YoutubeDL
            from yt_dlp.utils import DownloadError
        except ModuleNotFoundError:
            print("Youtube-dlp has not been found. Have you forgot to install it?")
            self.__on_finish.emit(False)
            return
        try:
            YoutubeDL(self.download_options).download(self.url)
        except DownloadError as download_error:
            if "urlopen error" in download_error.msg or "The read operation timed out" in download_error.msg:
                pass#Network error
            elif "Cancelled by user" in download_error.msg:
                pass#User cancle
            else:
                pass #Unknown error
            self.__on_finish.emit(False)
        else:
            self.__on_finish.emit(True) #All okay
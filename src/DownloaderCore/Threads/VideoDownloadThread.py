from PySide6.QtCore import QObject, QRunnable, Signal


class VideoDownloadThread(QObject, QRunnable):
    __on_finish = Signal(bool)
    __on_progress = Signal(dict)
    def __init__(self, yt_dlp: object, url: str = "https://www.youtube.com/watch?v=HBEsr0MfdmQ", options : dict[str, object] = {}, finished_callback: object| None = None, progress_callback: object | None = None) -> None:
        super().__init__()
        self.yt_dlp = yt_dlp
        if finished_callback != None:
            self.__on_finish.connect(finished_callback)
        if progress_callback != None:
            self.__on_progress.connect(progress_callback)
        self.__is_cancled = False
        self.__progress_counter = 0
        self.__url = url
        self.__download_options = options
    def _finish_hook(self, result):
        if result["status"] == "started":
            self.__on_progress.emit({"postprocessing": "started"})
        else:
            self.__on_progress.emit({"postprocessing": "finished"})
    def _progress_hook(self, result):
        if self.__is_cancled:
            raise self.yt_dlp.utils.DownloadError("Cancelled by user")

        self.__progress_counter += 1
        if self.__progress_counter % 20 != 0:
            return

        self.__on_progress.emit(result)
    def run(self):
        try:
            self.yt_dlp.YoutubeDL(self.__download_options).download(self.__url)
        except self.yt_dlp.DownloadError as download_error:
            if "urlopen error" in download_error.msg or "The read operation timed out" in download_error.msg:
                pass#Network error
            elif "Cancelled by user" in download_error.msg:
                pass#User cancle
            else:
                pass #Unknown error
            self.__on_finish.emit(False)
        else:
            self.__on_finish.emit(True) #All okay
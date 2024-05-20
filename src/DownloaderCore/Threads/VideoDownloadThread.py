from PySide6.QtCore import QObject, QRunnable, Signal


class VideoDownloadThread(QObject, QRunnable):
    __on_finish = Signal(bool)
    __on_progress = Signal(dict, int, object)
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
            self.__on_progress.emit({}, "Postprocessing started", "")
        else:
            self.__on_progress.emit({}, "Postprocessing finished", "")
    def _progress_hook(self, result):
        if self.__is_cancled:
            raise self.yt_dlp.utils.DownloadError("Cancelled by user")

        self.__progress_counter += 1
        if self.__progress_counter % 20 != 0:
            return

        match(result["status"]):
            case "downloading":
                downloaded_bytes = float(result["downloaded_bytes"])
                total_bytes = 0
                if "total_bytes" in result:
                    total_bytes = float(result["total_bytes"])
                elif "total_bytes_estimate" in result:
                    total_bytes = float(result["total_bytes_estimate"])
                else:
                    return
                percent_progress = round(100*downloaded_bytes/total_bytes)
                eta = "unknown"
                if "eta" in result and result["eta"]:
                    eta = result["eta"]
                self.__on_progress.emit(result, percent_progress, eta)
            case "finished":
                self.__on_progress.emit(result, "","")
            case other:
                self.__on_progress.emit(result, f"Unknown status {result['status']}","")
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
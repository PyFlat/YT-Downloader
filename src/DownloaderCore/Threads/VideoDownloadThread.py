from PySide6.QtCore import QThread, Signal, QRunnable
class VideoDownloadThread(QRunnable):
    def __init__(self, url: str = "https://www.youtube.com/watch?v=HBEsr0MfdmQ", options : dict[str, object] = {}, finished_callback: object| None = None, progress_callback: object | None = None) -> None:
        super().__init__()
        self.__on_finish = finished_callback
        self.__on_progress = progress_callback
        self.__is_cancled = False
        self.__progress_counter = 0
        self.__url = url
        self.__download_options = options
    def _finish_hook(self, result):
        if self.__on_finish == None:
            return
        if result["status"] == "started":
            self.__on_finish("Postprocessing started", "")
        else:
            self.__on_finish("Postprocessing finished", "")
    def _progress_hook(self, result):
        if self.__on_progress == None:
            return
        if self.__is_cancled:
            from yt_dlp.utils import DownloadError
            raise DownloadError("Cancelled by user")
        
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
                    eta = round(float(result["eta"]))
                self.__on_progress(f"{percent_progress}%", eta)
            case "finished":
                self.__on_progress("","")
            case other:
                self.__on_progress(f"Unknown status {result['status']}","")
    def run(self):
        try:
            from yt_dlp import YoutubeDL
            from yt_dlp.utils import DownloadError
        except ModuleNotFoundError:
            print("Youtube-dlp has not been found. Have you forgot to install it?")
            if self.__on_finish != None:
                self.__on_finish(False)
            return
        try:
            YoutubeDL(self.__download_options).download(self.__url)
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
from PySide6.QtCore import QRunnable
from urllib.request import urlopen
from urllib.error import URLError
import requests
try:
    from src.DownloaderCore.Threads.Signal import Signal
except ModuleNotFoundError:
    from Signal import Signal

VERSION = '2.0.0'
class UpdateCheckerThread(QRunnable):
    def __init__(self):
        super().__init__()
        self.on_update_avaliable = Signal(bool, str)
    def run(self):
        try:
            f = urlopen("https://github.com/PyFlat/YT-Downloader/releases/latest").url
        except URLError:
            self.update_available.emit(False, "no_connection")
            return
        tag = f.split("/")[-1]
        if VERSION < tag[1:]:
            self.update_available.emit(True, tag[1:])

class GithubDownloaderThread(QRunnable):
    

    def __init__(self, url: str, save_path: str, progress_callback: object | None = None, finished_callback: object | None = None):
        super().__init__()
        self.on_progress = Signal(float)
        self.on_finished = Signal(bool)
        self.url = url
        self.save_path = save_path
        if progress_callback != None:
            self.on_progress.connect(progress_callback)
        if finished_callback != None:
            self.on_progress.connect(finished_callback)

    def run(self):
        self.on_progress.emit(0)
        try:
            response = requests.get(self.url, stream=True, timeout=15)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(self.save_path, 'wb') as file:
                for data in response.iter_content(chunk_size=4096):
                    file.write(data)
                    downloaded_size += len(data)
                    progress = downloaded_size / total_size * 100
                    self.on_progress.emit(progress)
            self.on_finished.emit(True if progress == 100.0 else False)

        except requests.exceptions.ConnectionError:
            self.on_progress.emit(-1.0)
            self.on_finished.emit(False)
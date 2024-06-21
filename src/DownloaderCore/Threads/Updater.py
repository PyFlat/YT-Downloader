import os
import time
from urllib.error import URLError
from urllib.request import urlopen

import requests
from PySide6.QtCore import QObject, QRunnable, Signal

from src.version import VERSION


class UpdateCheckerThread(QObject, QRunnable):
    on_update_available = Signal(bool, str)

    def __init__(self, callback):
        super().__init__()
        self.on_update_available.connect(callback)

    def run(self):
        try:
            f = urlopen("https://github.com/PyFlat/YT-Downloader/releases/latest").url
        except URLError:
            self.on_update_available.emit(False, "no_connection")
            return
        tag = f.split("/")[-1]
        if VERSION < tag[1:]:
            self.on_update_available.emit(True, tag[1:])
        elif VERSION == tag[1:]:
            self.on_update_available.emit(False, "already_up_to_date")
        else:
            self.on_update_available.emit(False, "no_release_version")


class GithubDownloaderThread(QObject, QRunnable):
    on_progress = Signal(int)
    on_finished = Signal(bool)

    def __init__(
        self,
        url: str,
        save_path: str,
        progress_callback: object | None = None,
        finished_callback: object | None = None,
    ):
        super().__init__()
        self.url = url
        self.save_path = save_path
        if progress_callback != None:
            self.on_progress.connect(progress_callback)
        if finished_callback != None:
            self.on_finished.connect(finished_callback)

    def run(self):
        self.on_progress.emit(0)
        try:
            response = requests.get(self.url, stream=True, timeout=15)
            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            with open(self.save_path, "wb") as file:
                for data in response.iter_content(chunk_size=4096):
                    file.write(data)
                    downloaded_size += len(data)
                    progress = 100 * downloaded_size / total_size
                    self.on_progress.emit(int(progress))
            self.on_finished.emit(True if progress == 100.0 else False)

        except requests.exceptions.ConnectionError:
            self.on_progress.emit(-1.0)
            self.on_finished.emit(False)

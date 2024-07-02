import os
import shutil
import sys
import zipfile
import zipimport

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QWidget

import src.DownloaderCore.Constants as CONST
from src.Config.Config import cfg
from src.DownloaderCore.Threads.InformationLoadThread import InformationLoadThread
from src.DownloaderCore.Threads.ThreadManager import ThreadManager
from src.DownloaderCore.Threads.Updater import (
    GithubDownloaderThread,
    UpdateCheckerThread,
)
from src.DownloaderCore.Threads.YoutubeVideoDownloadThread import (
    YoutubeVideoDownloadThread,
)

TM = ThreadManager(10)


class Downloader:
    def __init__(
        self, thread_manager: ThreadManager, yt_dlp_path: str = "appdata/yt_dlp"
    ) -> None:
        self.thread_manager = thread_manager
        self.yt_dlp_path = yt_dlp_path
        self.yt_dlp = None
        # try:
        #     pass
        #     self.yt_dlp = __import__("yt_dlp")
        # except ModuleNotFoundError:
        if os.path.isfile(self.yt_dlp_path):
            self.importYtldp(self.yt_dlp_path)

    def getPlaylistInfo(self, url: str, callback: callable) -> None:
        self.thread_manager.runTask(
            InformationLoadThread(self.yt_dlp, url, True, callback), force=True
        )

    def getVideoInfo(self, url: str, callback: callable) -> None:
        self.thread_manager.runTask(
            InformationLoadThread(self.yt_dlp, url, False, callback), force=True
        )

    def downloadVideo(
        self,
        url: str,
        start_callback: object | None = None,
        progress_callback: object | None = None,
        finish_callback: object | None = None,
        **options,
    ):
        self.thread_manager.runTask(
            YoutubeVideoDownloadThread(
                self.yt_dlp, url, finish_callback, progress_callback, **options
            ),
            False,
            start_callback,
        )

    def download_playlist(
        self,
        url: str,
        start_callback: object | None = None,
        progress_callback: object | None = None,
        finish_callback: object | None = None,
        playlist_items: list[int] | None = None,
        **options,
    ):
        def on_info_recieve(data, url):
            if data == {}:
                return

            for i, entry in enumerate(data["entries"]):
                if playlist_items != None:
                    print(playlist_items, i + 1)
                    if i + 1 not in playlist_items:
                        continue
                self.downloadVideo(
                    entry["url"],
                    start_callback,
                    progress_callback,
                    finish_callback,
                    **options,
                )

        self.getPlaylistInfo(url, on_info_recieve)

    def updateFFmpeg(
        self,
        progress_callback: object | None = None,
        finish_callback: object | None = None,
    ):
        def on_finish(ok):
            if not ok:
                if finish_callback != None:
                    finish_callback(ok)
                return
            zip = zipfile.ZipFile("appdata/ffmpeg.zip")
            names = [
                name
                for name in zip.namelist()
                if name.startswith("ffmpeg-master-latest-win64-gpl/")
            ]
            for file in names:
                zip.extract(file)
            zip.close()
            os.rename("ffmpeg-master-latest-win64-gpl", "appdata/FFmpeg")
            os.remove("appdata/ffmpeg.zip")
            if finish_callback != None:
                finish_callback(ok)

        if os.path.isdir("appdata/FFmpeg"):
            shutil.rmtree("appdata/FFmpeg")

        self.thread_manager.runTask(
            GithubDownloaderThread(
                "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
                "appdata/ffmpeg.zip",
                progress_callback,
                on_finish,
            ),
            True,
        )

    def importYtldp(self, path: str):
        yt_dlp_zipimporter = zipimport.zipimporter(path)
        self.yt_dlp = yt_dlp_zipimporter.load_module("yt_dlp")

    def updateYtdlp(
        self,
        progress_callback: object | None = None,
        finish_callback: object | None = None,
    ):
        channel_url_map = {
            "nightly": CONST.NIGHTLY_CHANNEL_URL,
            "master": CONST.MASTER_CHANNEL_URL,
        }

        channel: str = cfg.get(cfg.ytDlpUpdateChannel)
        channel_url = channel_url_map.get(channel.lower(), CONST.STABLE_CHANNEL_URL)

        def on_finish_(ok):
            if not ok:
                if finish_callback != None:
                    finish_callback(ok)
                return
            if finish_callback != None:
                finish_callback(ok)
            cfg.appRestartSig.emit()

        if os.path.isfile("appdata/yt_dlp"):
            os.remove("appdata/yt_dlp")

        self.thread_manager.runTask(
            GithubDownloaderThread(
                f"{channel_url}/releases/latest/download/yt-dlp",
                self.yt_dlp_path,
                progress_callback,
                on_finish_,
            ),
            True,
        )

    # update_check_callback: (bool, str) -> bool dowload_finish_callback: (bool) -> any downlaod_progress_callback: (int) -> None
    def updateApplication(
        self,
        download_progress_callback=None,
        download_finish_callback=None,
        update_check_callback=None,
        main_window: QWidget = None,
    ):
        def on_update_check(available, tag):
            if update_check_callback != None:
                response = update_check_callback(available, tag)
                if not response:
                    return
            if not available:
                return

            def on_download_finish(success):
                if download_finish_callback != None:
                    wait = download_finish_callback(success)
                file = r"C:\Users\Johannes\Documents\Github\YT-Downloader\appdata\win_installer_v1.3.3.exe"
                QProcess.startDetached(file)
                main_window.close()

            self.thread_manager.runTask(
                GithubDownloaderThread(
                    f"https://github.com/PyFlat-Studios-JR/YT-Downloader/releases/latest/download/win_installer_v{tag}.exe",
                    f"appdata/win_installer_v{tag}.exe",
                    download_progress_callback,
                    on_download_finish,
                ),
                True,
            )

        self.thread_manager.runTask(UpdateCheckerThread(on_update_check), True)


if __name__ == "__main__":
    import sys

    from PySide6.QtCore import QCoreApplication, QThread, QTimer

    # download https://www.youtube.com/watch?v=HBEsr0MfdmQ mp4 C:/Users/jonas/AppData/Local/Programs/PyFlat Youtube Downloader(2)/appdata/FFmpeg/bin bv[height<=720]+ba[ext=m4a]/b (%(height)sp).%(ext)s
    def cb(*args):
        print(*args)

    __app__ = QCoreApplication()
    DL = Downloader(TM)
    DL.download_playlist(
        "https://www.youtube.com/playlist?list=PLE1nXFFhjpTFyTf6Gp7M7M17MeIz8QYr4",
        "./",
        "C:/Users/jonas/AppData/Local/Programs/PyFlat Youtube Downloader(2)/appdata/FFmpeg/bin",
        720,
    )
    sys.exit(__app__.exec())

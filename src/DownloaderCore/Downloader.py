try:
    from src.DownloaderCore.Threads.VideoDownloadThread import VideoDownloadThread
    from src.DownloaderCore.Threads.YoutubeVideoDownloadThread import YoutubeVideoDownloadThread
    from src.DownloaderCore.Threads.InformationLoadThread import InformationLoadThread
    from src.DownloaderCore.Threads.ThreadManager import ThreadManager
    from src.DownloaderCore.Threads.Container import Container
    from src.DownloaderCore.Threads.Signal import Signal
    from src.DownloaderCore.Threads.Updater import GithubDownloaderThread, UpdateCheckerThread
except:
    from Threads.VideoDownloadThread import VideoDownloadThread
    from Threads.YoutubeVideoDownloadThread import YoutubeVideoDownloadThread
    from Threads.InformationLoadThread import InformationLoadThread
    from Threads.ThreadManager import ThreadManager
    from Threads.Container import Container
    from Threads.Updater import GithubDownloaderThread, UpdateCheckerThread

import sys, os, zipfile, zipimport
TM = ThreadManager(10)

class Downloader():
    def __init__(self, thread_manager: ThreadManager, yt_dlp_path: str = "appdata/yt_dlp") -> None:
        self.thread_manager = thread_manager
        self.yt_dlp_path = yt_dlp_path
        self.yt_dlp = None
        try:
            self.yt_dlp = __import__("yt_dlp")
        except ModuleNotFoundError:
            if os.path.isfile(self.yt_dlp_path):
                self.importYtldp(self.yt_dlp_path)

    def get_playlist_info(self, url: str, callback: callable) -> None:
        self.thread_manager.runTask(InformationLoadThread(self.yt_dlp, url, True, callback), force=True)
    def get_video_info(self, url: str, callback: callable) -> None:
        self.thread_manager.runTask(InformationLoadThread(self.yt_dlp, url, False, callback), force=True)
    def download_video(self, url: str, outfile_path: str, ffmpeg_path: str, resolution: int):
        self.thread_manager.runTask(YoutubeVideoDownloadThread(self.yt_dlp, url,f"bv[height<={resolution}]+ba[ext=m4a]/b",ffmpeg_path,f"{outfile_path}/%(title)s(%(height)sp).%(ext)s","mp4"))
    def download_playlist(self, url: str, outfile_path: str, ffmpeg_path: str, resolution: int, playlist_range: tuple[int, int] | None = None):
        def on_info_recieve(data, url):
            if data == {}:
                return
            import os
            if not os.path.isdir(f"{outfile_path}{data['title']}"):
                os.mkdir(f"{outfile_path}{data['title']}")
            for i, entry in enumerate(data["entries"]):
                if playlist_range != None:
                    lower, upper = playlist_range
                    if i < lower or i > upper:
                        continue
                self.download_video(entry["url"],f"{outfile_path}{data['title']}/",ffmpeg_path, resolution)
        self.get_playlist_info(url, on_info_recieve)
    def updateFFmpeg(self, progress_callback: object | None = None, finish_callback: object | None = None):
        def on_finish(ok):
            if not ok:
                if finish_callback != None:
                    finish_callback(ok)
                return
            zip = zipfile.ZipFile("appdata/ffmpeg.zip")
            names = [name for name in zip.namelist() if name.startswith("ffmpeg-master-latest-win64-gpl/")]
            for file in names:
                zip.extract(file)
            zip.close()
            os.rename("ffmpeg-master-latest-win64-gpl", "appdata/FFmpeg")
            os.remove("appdata/ffmpeg.zip")
            if finish_callback != None:
                finish_callback(ok)
        self.thread_manager.runTask(
            GithubDownloaderThread("https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip", "appdata/ffmpeg.zip", progress_callback, on_finish), True)
    def importYtldp(self, path: str):
        yt_dlp_zipimporter = zipimport.zipimporter(path)
        self.yt_dlp = yt_dlp_zipimporter.load_module('yt_dlp')
    def updateYtdlp(self, progress_callback: object | None = None, finish_callback: object | None = None):
        def on_finish_(ok):
            if not ok:
                if finish_callback != None:
                    finish_callback(ok)
                return
            self.importYtldp(self.yt_dlp_path)
            if finish_callback != None:
                finish_callback(ok)
        self.thread_manager.runTask(GithubDownloaderThread("https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt-dlp", self.yt_dlp_path,progress_callback,on_finish_),True)
    #update_check_callback: (bool, str) -> bool dowload_finish_callback: (bool) -> any downlaod_progress_callback: (int) -> None
    def updateApplication(self, download_finish_callback = None, download_progress_callback = None, update_check_callback = None):
        def on_update_check(success, tag):
            if update_check_callback != None:
                response = update_check_callback(success, tag)
                if not response:
                    return
            if not success:
                return
            def on_download_finish(success):
                if download_finish_callback != None:
                    wait = download_finish_callback(success)
                os.popen(f"start appdata/win_installer_v{tag}.exe")
                sys.exit(0)
            self.thread_manager.runTask(GithubDownloaderThread(f"https://github.com/PyFlat-Studios-JR/YT-Downloader/releases/latest/download/win_installer_v{tag}.exe", f"appdata/win_installer_v{tag}.exe",download_progress_callback,on_download_finish),True)
        self.thread_manager.runTask(UpdateCheckerThread(on_update_check),True)
                
                

            
if __name__ == "__main__":
    import sys
    from PySide6.QtCore import QCoreApplication, QTimer, QThread
    #download https://www.youtube.com/watch?v=HBEsr0MfdmQ mp4 C:/Users/jonas/AppData/Local/Programs/PyFlat Youtube Downloader(2)/appdata/FFmpeg/bin bv[height<=720]+ba[ext=m4a]/b (%(height)sp).%(ext)s
    def cb(*args):
        print(*args)
    __app__ = QCoreApplication()
    DL = Downloader(TM)
    DL.download_playlist("https://www.youtube.com/playlist?list=PLE1nXFFhjpTFyTf6Gp7M7M17MeIz8QYr4","./","C:/Users/jonas/AppData/Local/Programs/PyFlat Youtube Downloader(2)/appdata/FFmpeg/bin",720)
    sys.exit(__app__.exec())
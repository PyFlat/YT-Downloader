try:
    from src.DownloaderCore.Threads.VideoDownloadThread import VideoDownloadThread
    from src.DownloaderCore.Threads.YoutubeVideoDownloadThread import YoutubeVideoDownloadThread
    from src.DownloaderCore.Threads.InformationLoadThread import InformationLoadThread
    from src.DownloaderCore.Threads.ThreadManager import ThreadManager
    from src.DownloaderCore.Threads.Container import Container
    from src.DownloaderCore.Threads.Signal import Signal
except:
    from Threads.VideoDownloadThread import VideoDownloadThread
    from Threads.YoutubeVideoDownloadThread import YoutubeVideoDownloadThread
    from Threads.InformationLoadThread import InformationLoadThread
    from Threads.ThreadManager import ThreadManager
    from Threads.Container import Container
TM = ThreadManager(10)

class Downloader():
    def __init__(self, thread_manager: ThreadManager) -> None:
        self.thread_manager = thread_manager
    def get_playlist_info(self, url: str, callback: callable) -> None:
        self.thread_manager.runTask(InformationLoadThread(url, True, callback), force=True)
    def get_video_info(self, url: str, callback: callable) -> None:
        self.thread_manager.runTask(InformationLoadThread(url, False, callback), force=True)
    def download_video(self, url: str, outfile_path: str, ffmpeg_path: str, resolution: int):
        self.thread_manager.runTask(YoutubeVideoDownloadThread(url,f"bv[height<={resolution}]+ba[ext=m4a]/b",ffmpeg_path,f"{outfile_path}/%(title)s(%(height)sp).%(ext)s","mp4"))
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
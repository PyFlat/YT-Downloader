from qfluentwidgets import *
from PySide6.QtCore import QStandardPaths

class Config(QConfig):

    #Downloader Group
    download_folder = ConfigItem("Downloader", "files-download-directory", QStandardPaths.writableLocation(QStandardPaths.DownloadLocation), FolderValidator())
    ffmpeg_path = ConfigItem("Downloader", "ffmpeg-location-path", "", FolderValidator())
    maximum_download_threads = RangeConfigItem("Downloader", "max-download-threads", 1, RangeValidator(1, 10))
    thumbnail_streaming = ConfigItem("Downloader", "thumbnail-streaming", True, BoolValidator())

    #Application Group

    check_for_updates = ConfigItem("Application", "check-for-updates", True, BoolValidator())
    log_level = OptionsConfigItem("Application", "log-level", "Info", OptionsValidator(["Info", "Debug"]))


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('src/Config/config.json', cfg)
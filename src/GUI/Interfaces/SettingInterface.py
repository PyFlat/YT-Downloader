from src.GUI.Icons.Icons import CustomIcons
from src.Config.Config import cfg
from qfluentwidgets import (ScrollArea, ExpandLayout, SettingCardGroup,
                            OptionsSettingCard, PushSettingCard,
                            InfoBar, SwitchSettingCard,
                            setTheme, RangeSettingCard,
                            ComboBoxSettingCard, StateToolTip)
from qfluentwidgets import FluentIcon as FIF
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog
from src.GUI.Stylesheet.StyleSheet import StyleSheet
from src.GUI.CustomWidgets.DownloadMessageBox import DownloadMessageBox
from src.DownloaderCore.Downloader import Downloader
import os
from yt_dlp import version

class SettingInterface(ScrollArea):

    def __init__(self, parent=None, downloader:Downloader=None):
        super().__init__(parent=parent)
        self.downloader = downloader
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel("Settings", self)

        self.personalGroup = SettingCardGroup("Personalization", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "Application theme",
            "Change the appearance of the application",
            texts=[
                "Light", "Dark",
                "Use system setting"
            ],
            parent = self.personalGroup
        )
        self.downloaderGroup = SettingCardGroup("Downloader", self.scrollWidget)
        self.downloadFolderCard = PushSettingCard(
            "Choose Folder",
            FIF.DOWNLOAD,
            "Download directory",
            cfg.get(cfg.download_folder),
            self.downloaderGroup
        )

        self.ffmpegPathCard = PushSettingCard(
            "Choose Folder",
            CustomIcons.FFMPEG,
            "FFmpeg location",
            cfg.get(cfg.ffmpeg_path),
            self.downloaderGroup
        )

        self.downloadFFmpegCard = PushSettingCard(
            "Download",
            CustomIcons.FFMPEG,
            "Download the latest FFmpeg version",
            parent = self.downloaderGroup
        )

        self.updateYtDlpCard = PushSettingCard(
            "Update",
            CustomIcons.YOUTUBE2,
            "Download the latest version of yt-dlp",
            f"Current version: {version.__version__}",
            parent = self.downloaderGroup
        )

        self.maxDlThreads = RangeSettingCard(
            cfg.maximum_download_threads,
            FIF.SPEED_HIGH,
            "Maximum Download Threads",
            parent=self.downloaderGroup
        )

        self.thumbnailStreamingCard = SwitchSettingCard(
            FIF.PHOTO,
            "Stream Thumbnails",
            configItem=cfg.thumbnail_streaming,
            parent=self.downloaderGroup
        )

        self.applicationGroup = SettingCardGroup("Application", self.scrollWidget)

        self.updateOnStartCard = SwitchSettingCard(
            FIF.UPDATE,
            "Check for updates when the application starts",
            "The new version will fix known bugs and have more features",
            configItem=cfg.check_for_updates,
            parent=self.applicationGroup
        )

        self.logLevelCard = ComboBoxSettingCard(
            cfg.log_level,
            FIF.QUICK_NOTE,
            "Log Level",
            "Set your preferred log-level",
            texts = ["Info", "Debug"],
            parent = self.applicationGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("settingInterface")

        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")

        StyleSheet.SETTING_INTERFACE.apply(self)

        self.initLayout()
        self.connectSignalToSlot()

    def initLayout(self):
        self.settingLabel.move(36, 30)

        self.personalGroup.addSettingCard(self.themeCard)

        self.downloaderGroup.addSettingCard(self.downloadFolderCard)
        self.downloaderGroup.addSettingCard(self.ffmpegPathCard)
        self.downloaderGroup.addSettingCard(self.downloadFFmpegCard)
        self.downloaderGroup.addSettingCard(self.updateYtDlpCard)
        self.downloaderGroup.addSettingCard(self.maxDlThreads)
        self.downloaderGroup.addSettingCard(self.thumbnailStreamingCard)

        self.applicationGroup.addSettingCard(self.updateOnStartCard)
        self.applicationGroup.addSettingCard(self.logLevelCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)

        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.downloaderGroup)
        self.expandLayout.addWidget(self.applicationGroup)

    def __showDownloadTooltip(self):
        msg = DownloadMessageBox(self)
        def finish(success):
            msg.accept()
        msg.show()
        def cb(*args):
            print(*args)
        self.downloader.updateFFmpeg(self, cb, cb)


    def __showNoFFmpegTooltip(self):
        InfoBar.error(
            'Error:',
            'FFmpeg Not Found in Specified Path',
            duration=2500,
            parent=self
        )

    def __onDownloadFolderCardClicked(self, ffmpeg=False):
        folder = QFileDialog.getExistingDirectory(self, "Choose folder", "./")

        current_path =  cfg.ffmpeg_path if ffmpeg else cfg.download_folder

        if not folder or cfg.get(current_path) == folder:
            return

        if ffmpeg and not (os.path.isfile(f"{folder}/ffmpeg.exe") and os.path.isfile(f"{folder}/ffprobe.exe")):
            self.__showNoFFmpegTooltip()
            return

        cfg.set(current_path, folder)

        if not ffmpeg:
            self.downloadFolderCard.setContent(folder)
        else:
            self.ffmpegPathCard.setContent(folder)

    def connectSignalToSlot(self):

        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))

        self.downloadFolderCard.clicked.connect(
            self.__onDownloadFolderCardClicked
        )

        self.ffmpegPathCard.clicked.connect(
            lambda: self.__onDownloadFolderCardClicked(True)
        )

        self.downloadFFmpegCard.clicked.connect(
            self.__showDownloadTooltip
        )
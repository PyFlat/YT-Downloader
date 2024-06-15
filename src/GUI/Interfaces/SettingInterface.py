import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QLabel, QWidget
from qfluentwidgets import ComboBoxSettingCard, ExpandLayout
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    FluentWindow,
    HyperlinkCard,
    InfoBar,
    MessageBox,
    OptionsSettingCard,
    PrimaryPushSettingCard,
    PushSettingCard,
    RangeSettingCard,
    ScrollArea,
    SettingCardGroup,
    SwitchSettingCard,
    setTheme,
)

from src.Config.Config import cfg
from src.DownloaderCore.Downloader import Downloader
from src.GUI.CustomWidgets.DownloadMessageBox import DownloadMessageBox
from src.GUI.CustomWidgets.YouTubeSettingCard import YouTubeSettingCard
from src.GUI.Icons.Icons import CustomIcons
from src.GUI.Stylesheet.StyleSheet import StyleSheet
from src.version import VERSION


class SettingInterface(ScrollArea):

    def __init__(self, parent: FluentWindow = None, downloader: Downloader = None):
        super().__init__(parent=parent)
        self.downloader = downloader
        self.__parent = parent
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel("Settings", self)

        self.personalGroup = SettingCardGroup("Personalization", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "Application theme",
            "Change the appearance of the application",
            texts=["Light", "Dark", "Use system setting"],
            parent=self.personalGroup,
        )
        self.downloaderGroup = SettingCardGroup("Downloader", self.scrollWidget)
        self.downloadFolderCard = PushSettingCard(
            "Choose Folder",
            FIF.DOWNLOAD,
            "Download directory",
            cfg.get(cfg.download_folder),
            self.downloaderGroup,
        )

        self.ffmpegPathCard = PushSettingCard(
            "Choose Folder",
            CustomIcons.FFMPEG,
            "FFmpeg location",
            cfg.get(cfg.ffmpeg_path),
            self.downloaderGroup,
        )

        self.downloadFFmpegCard = PushSettingCard(
            "Download",
            CustomIcons.FFMPEG,
            "Download the latest FFmpeg version",
            parent=self.downloaderGroup,
        )

        self.updateYtDlpCard = PushSettingCard(
            "Update",
            CustomIcons.YOUTUBE2,
            "Download the latest version of yt-dlp",
            f"Current version: ",
            parent=self.downloaderGroup,
        )

        self.maxDlThreads = RangeSettingCard(
            cfg.maximum_download_threads,
            FIF.SPEED_HIGH,
            "Maximum Download Threads",
            parent=self.downloaderGroup,
        )
        self.maxDlThreads.slider.setPageStep(1)

        self.thumbnailStreamingCard = SwitchSettingCard(
            FIF.PHOTO,
            "Stream Thumbnails",
            configItem=cfg.thumbnail_streaming,
            parent=self.downloaderGroup,
        )

        self.youtubeCard = YouTubeSettingCard(self.downloaderGroup, self)

        self.applicationGroup = SettingCardGroup("Application", self.scrollWidget)

        self.updateOnStartCard = SwitchSettingCard(
            FIF.UPDATE,
            "Check for updates when the application starts",
            "The new version will fix known bugs and have more features",
            configItem=cfg.check_for_updates,
            parent=self.applicationGroup,
        )

        self.logLevelCard = ComboBoxSettingCard(
            cfg.log_level,
            FIF.LABEL,
            "Log Level",
            "Set your preferred log-level",
            texts=["Info", "Debug"],
            parent=self.applicationGroup,
        )

        self.helpCard = HyperlinkCard(
            "https://github.com/PyFlat/YT-Downloader",
            "Open help page",
            FIF.HELP,
            "Help",
            "Find help and discover new features about PyFlat YouTube Downloader",
            self.applicationGroup,
        )

        self.feedbackCard = PrimaryPushSettingCard(
            "Provide feedback",
            FIF.FEEDBACK,
            "Provide feedback",
            "Help us improve PyFlat YouTube Downloader by providing feedback",
            self.applicationGroup,
        )

        self.aboutCard = PrimaryPushSettingCard(
            "Check update",
            FIF.INFO,
            "About",
            f"©2024, PyFlat, Version {VERSION}",
            self.applicationGroup,
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
        self.downloaderGroup.addSettingCard(self.youtubeCard)

        self.applicationGroup.addSettingCard(self.updateOnStartCard)
        self.applicationGroup.addSettingCard(self.logLevelCard)
        self.applicationGroup.addSettingCard(self.helpCard)
        self.applicationGroup.addSettingCard(self.feedbackCard)
        self.applicationGroup.addSettingCard(self.aboutCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)

        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.downloaderGroup)
        self.expandLayout.addWidget(self.applicationGroup)

    def update_ytdlp_version(self):
        if self.downloader.yt_dlp:
            self.updateYtDlpCard.setContent(
                f"Current version: {self.downloader.yt_dlp.version.__version__}"
            )

    def __showDownloadDialog(self, ffmpeg: bool = True):
        msg = DownloadMessageBox(self)

        def updateProgress(progress):
            msg.ProgressRing.setValue(progress)

        def finish(success):
            msg.hide()
            if ffmpeg:
                text = "FFmpeg"
                cfg.set(cfg.ffmpeg_path, "appdata/FFmpeg/bin")
                self.ffmpegPathCard.setContent(cfg.get(cfg.ffmpeg_path))
            else:
                text = "yt-dlp"
                self.update_ytdlp_version()
            if success:
                InfoBar.success(
                    "Succes:",
                    f"{text} was downloaded and installed succesfully",
                    duration=2500,
                    parent=self,
                )
            else:
                InfoBar.error(
                    "Error:",
                    f"Some error occured when downloading {text}. Download not succesfull.",
                    duration=2500,
                    parent=self,
                )

        msg.show()
        if ffmpeg:
            self.downloader.updateFFmpeg(updateProgress, finish)
        else:
            self.downloader.updateYtdlp(updateProgress, finish)

    def __showNoFFmpegTooltip(self):
        InfoBar.error(
            "Error:", "FFmpeg Not Found in Specified Path", duration=2500, parent=self
        )

    def __onDownloadFolderCardClicked(self, ffmpeg=False):
        folder = QFileDialog.getExistingDirectory(self, "Choose folder", "./")

        current_path = cfg.ffmpeg_path if ffmpeg else cfg.download_folder

        if not folder or cfg.get(current_path) == folder:
            return

        if ffmpeg and not (
            os.path.isfile(f"{folder}/ffmpeg.exe")
            and os.path.isfile(f"{folder}/ffprobe.exe")
        ):
            self.__showNoFFmpegTooltip()
            return

        cfg.set(current_path, folder)

        if not ffmpeg:
            self.downloadFolderCard.setContent(folder)
        else:
            self.ffmpegPathCard.setContent(folder)

    def updateApplication(self, automatic_call: bool = False):
        # Ensure the current widget is this instance before proceeding
        if self.__parent.stackedWidget.currentWidget() != self:
            self.__parent.switchTo(self)

        # Create a message box for displaying download progress
        download_msg_box = DownloadMessageBox(self)

        def handle_update_dialog(available, tag):
            # Skip update dialog for automatic calls if no update is available
            if automatic_call and not available:
                return False

            # Create a message box for update notifications
            update_msg_box = MessageBox("Search for updates", "", self)
            update_msg_box.cancelButton.hide()

            # Customize message based on update status
            if tag == "no_release_version":
                message = "You are already on a non-released beta version!"
            elif tag == "already_up_to_date":
                message = "You are already on the latest version!"
            else:
                update_msg_box.titleLabel.setText("New update available!")
                message = f"Current version: {VERSION}\nNew version: {tag}\nInstall it?"
                update_msg_box.cancelButton.show()

            # Set message content and prompt user
            update_msg_box.contentLabel.setText(message)
            if update_msg_box.exec():
                if available:
                    download_msg_box.show()
                return True
            else:
                return False

        def update_progress(progress):
            download_msg_box.ProgressRing.setValue(progress)

        def handle_download_completion(success):
            MessageBox(
                "Download completed",
                "The app has to close to perform the update!",
                self,
            ).exec()

        self.downloader.updateApplication(
            update_progress,
            handle_download_completion,
            handle_update_dialog,
            self.__parent,
        )

    def connectSignalToSlot(self):

        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))

        self.downloadFolderCard.clicked.connect(self.__onDownloadFolderCardClicked)

        self.ffmpegPathCard.clicked.connect(
            lambda: self.__onDownloadFolderCardClicked(True)
        )

        self.downloadFFmpegCard.clicked.connect(self.__showDownloadDialog)
        self.updateYtDlpCard.clicked.connect(lambda: self.__showDownloadDialog(False))

        self.maxDlThreads.slider.valueChanged.connect(
            self.downloader.thread_manager.setMaxThreadCount
        )

        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/PyFlat/YT-Downloader/issues")
            )
        )

        self.aboutCard.clicked.connect(self.updateApplication)

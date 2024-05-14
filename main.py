from src.Logger import Logger
import logging, sys

if __name__ == "__main__":
    logger_object = Logger(logs_folder="logs")
    logger = logger_object.logger
    logger.info("Logging Started")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import *

from qfluentwidgets import FluentWindow, SplashScreen, setTheme, Theme, NavigationItemPosition, MessageBox, HorizontalSeparator
from qfluentwidgets import FluentIcon as FIF

from src.GUI.Interfaces.MainInterface import MainInterface
from src.GUI.Interfaces.DownloadInterface import DownloadInterface
from src.GUI.Interfaces.SettingInterface import SettingInterface

from src.GUI.CustomWidgets.YTVideoInformationWidget import YTVideoInformationWidget
from src.GUI.CustomWidgets.VideoDownloadWidget import VideoDownloadWidget

from src.Config.Config import cfg

from src.DownloaderCore.Threads.ThreadManager import ThreadManager
from src.DownloaderCore.Downloader import Downloader


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.info_widget = None

        self.main_interface = MainInterface(self)
        self.main_interface.stackedWidget.setCurrentIndex(0)
        self.main_interface.PushButton.setShortcut(QKeySequence(Qt.Key_Return))
        self.main_interface.PushButton.clicked.connect(self.searchByUrl)

        self.download_interface = DownloadInterface(self)
        self.download_interface.setStyleSheet("background: transparent; border: none")

        self.setting_interface = SettingInterface(self, downloader)

        self.setting_interface.themeCard.optionChanged.connect(self.updateVideoWidget)
        self.setting_interface.themeCard.optionChanged.connect(self.updateDownloadWidget)

        self.initNavigation()

        self.checkForYtdlp()

        if getattr(sys, 'frozen', False) and cfg.get(cfg.check_for_updates):
            self.setting_interface.updateApplication(True)

        self.doATest()

        self.splashScreen.finish()

    def doATest(self):
        self.download_widget = VideoDownloadWidget(self.download_interface)
        self.download_interface.verticalLayout.addWidget(self.download_widget, 0, Qt.AlignTop | Qt.AlignCenter)
        self.download_widget.fetchThumbnails()
        newWidget2 = HorizontalSeparator(self.download_interface)
        self.download_interface.verticalLayout.addWidget(newWidget2, 0, Qt.AlignTop)

    def updateDownloadWidget(self):
        if self.download_widget:
            self.download_widget.update_pixmap()

    def updateVideoWidget(self):
        if self.info_widget:
            self.info_widget.updateDropShadow()

    def videoInformationCallback(self, result, url):
        if self.info_widget:
            self.info_widget.deleteLater()
            self.info_widget = None

        self.info_widget = YTVideoInformationWidget(self, result, downloader)
        self.main_interface.page.layout().addWidget(self.info_widget, 0, Qt.AlignTop)
        self.main_interface.stackedWidget.setCurrentIndex(0)

    def searchByUrl(self):
        self.main_interface.stackedWidget.setCurrentIndex(1)
        downloader.getVideoInfo(self.main_interface.LineEdit.text(), self.videoInformationCallback)

    def showDialog(self):
        title = "yt-dlp not found"
        content = "Yt-dlp isn't installed without it the downloader can't work. Download it?"
        msgb = MessageBox(title, content, self)
        if msgb.exec():
            self.switchTo(self.setting_interface)
            self.setting_interface.updateYtDlpCard.button.click()
        else:
            self.close()
            sys.exit()

    def checkForYtdlp(self):
        if downloader.yt_dlp == None:
            self.showDialog()
        else:
            self.setting_interface.update_ytdlp_version()

    def initNavigation(self):
        self.addSubInterface(self.main_interface, FIF.HOME, 'Home')
        self.addSubInterface(self.download_interface, FIF.DOWNLOAD, 'Download')
        self.navigationInterface.addSeparator()

        self.addSubInterface(self.setting_interface, FIF.SETTING, "Settings", NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(800, 550)
        self.setMinimumSize(800, 550)

        self.setWindowIcon(QIcon("src/GUI/app-icon.ico"))
        self.setWindowTitle('PyFlat YouTube Downloader')

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    thread_manager = ThreadManager(10)
    downloader = Downloader(thread_manager)
    MainWindow()
    sys.exit(app.exec())
from src.Logger import Logger
import logging, sys

if __name__ == "__main__":
    logger_object = Logger(logs_folder="logs")
    logger = logger_object.logger
    logger.info("Logging Started")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import *

from qfluentwidgets import FluentWindow, SplashScreen, setTheme, Theme, NavigationItemPosition, MessageBox
from qfluentwidgets import FluentIcon as FIF

from src.GUI.Interfaces.MainInterface import MainInterface
from src.GUI.Interfaces.SettingInterface import SettingInterface

from src.DownloaderCore.Threads.ThreadManager import ThreadManager
from src.DownloaderCore.Downloader import Downloader

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

        self.main_interface = MainInterface(self)

        self.setting_interface = SettingInterface(self, downloader)

        self.initNavigation()

        self.splashScreen.finish()

        self.checkForYtdlp()

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
        self.navigationInterface.addSeparator()

        self.addSubInterface(self.setting_interface, FIF.SETTING, "Settings", NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(800, 500)
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
    setTheme(Theme.DARK)
    sys.exit(app.exec())
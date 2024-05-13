from src.Logger import Logger
import logging, sys

if __name__ == "__main__":
    logger_object = Logger(logs_folder="logs")
    logger = logger_object.logger
    logger.info("Logging Started")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import *

from qfluentwidgets import FluentWindow, SplashScreen, setTheme, Theme, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF

from src.GUI.Interfaces.MainInterface import MainInterface
from src.GUI.Interfaces.SettingInterface import SettingInterface

from src.DownloaderCore.Threads.ThreadManager import ThreadManager
from src.DownloaderCore.Downloader import Downloader

thread_manager = ThreadManager(10)
downloader = Downloader(thread_manager)

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

        self.main_interface = MainInterface(self)

        self.setting_interface = SettingInterface(self, downloader)

        self.initNavigation()

        self.splashScreen.finish()

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
    MainWindow()
    setTheme(Theme.DARK)
    sys.exit(app.exec())
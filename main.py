from src.Logger import Logger
import logging, sys

if __name__ == "__main__":
    logger_object = Logger(logs_folder="logs")
    logger = logger_object.logger
    logger.info("Logging Started")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import *

from qfluentwidgets import FluentWindow, SplashScreen, setTheme, Theme
from qfluentwidgets import FluentIcon as FIF

from src.GUI.Interfaces.MainInterface import MainInterface

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

        self.main_interface = MainInterface(self)

        self.initNavigation()

        self.splashScreen.finish()

    def initNavigation(self):
        self.addSubInterface(self.main_interface, FIF.HOME, 'Home')

    def initWindow(self):
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
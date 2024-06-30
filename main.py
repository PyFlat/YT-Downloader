import os
import sys

from src.Logger import logger

logger.info("Logging Started")

from PySide6.QtCore import QSize, QUrl
from PySide6.QtGui import *
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    FluentWindow,
    InfoBadge,
    InfoBadgePosition,
    MessageBox,
    NavigationItemPosition,
    SplashScreen,
)

from src.Config.Config import cfg
from src.DownloaderCore.Downloader import Downloader
from src.DownloaderCore.SupportedSites import VIDEO_SITES
from src.DownloaderCore.Threads.ThreadManager import ThreadManager
from src.GUI.CustomWidgets.BaseInformationWidget import BaseInformationWidget
from src.GUI.DownloadWidgetManager import download_widget_manager
from src.GUI.Interfaces.DownloadInterface import DownloadInterface
from src.GUI.Interfaces.MainInterface import MainInterface
from src.GUI.Interfaces.SettingInterface import SettingInterface


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.info_widget: BaseInformationWidget = None

        self.main_interface = MainInterface(self)
        self.main_interface.stackedWidget.setCurrentIndex(0)
        self.main_interface.LineEdit.searchButton.setShortcut(
            QKeySequence(Qt.Key_Return)
        )
        self.main_interface.LineEdit.searchButton.clicked.connect(self.searchByUrl)

        self.download_interface = DownloadInterface(self)
        self.download_interface.setStyleSheet("background: transparent; border: none")

        self.setting_interface = SettingInterface(self, downloader)

        self.setting_interface.themeCard.optionChanged.connect(self.updateVideoWidget)

        self.initNavigation()

        if getattr(sys, "frozen", False) and cfg.get(cfg.check_for_updates):
            self.setting_interface.updateApplication(True)

        cfg.appRestartSig.connect(self.restartApplication)

        self.splashScreen.finish()

        self.checkForYtdlp()

    def updateVideoWidget(self):
        if not cfg.get(cfg.thumbnail_streaming):
            self.info_widget.setDefaultThumbnail()
            return

        if self.info_widget:
            self.info_widget.updateDropShadow()
            self.info_widget.setThumbnail()

    def videoInformationCallback(self, result: dict, url: str):
        if self.info_widget:
            self.info_widget.deleteLater()
            self.info_widget = None

        webpage_url: str = result.get("webpage_url_domain")

        if webpage_url in VIDEO_SITES:
            site: dict = VIDEO_SITES.get(webpage_url)
            info_widget_class: BaseInformationWidget = site.get("widget")

            self.info_widget = info_widget_class(
                self, result, downloader, site.get("data")
            )
            self.main_interface.page.layout().addWidget(
                self.info_widget, 0, Qt.AlignTop
            )

        self.main_interface.stackedWidget.setCurrentIndex(0)

    def searchByUrl(self):
        search_text = self.main_interface.LineEdit.text().replace(" ", "")
        if search_text == "":
            return
        self.main_interface.stackedWidget.setCurrentIndex(1)
        downloader.getVideoInfo(search_text, self.videoInformationCallback)

    def showDialog(self):
        title = "yt-dlp not found"
        content = (
            "Yt-dlp isn't installed without it the downloader can't work. Download it?"
        )
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

    def restartApplication(self):
        self.closeEvent(QCloseEvent())
        if getattr(sys, "frozen", False):
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def initNavigation(self):
        self.addSubInterface(self.main_interface, FIF.HOME, "Home")
        self.download_interface_nav_item = self.addSubInterface(
            self.download_interface, FIF.DOWNLOAD, "Download"
        )
        InfoBadge.attension(
            text=0,
            parent=self.download_interface_nav_item.parent(),
            target=self.download_interface_nav_item,
            position=InfoBadgePosition.NAVIGATION_ITEM,
        )

        self.navigationInterface.addSeparator()

        self.navigationInterface.addItem(
            routeKey="price",
            icon=FIF.HEART,
            text="Donate",
            onClick=lambda: QDesktopServices.openUrl(QUrl("https://ko-fi.com/pyflat")),
            selectable=False,
            tooltip="Donate",
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(
            self.setting_interface,
            FIF.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM,
        )

    def initWindow(self):
        self.resize(800, 550)
        self.setMinimumSize(800, 550)

        self.setWindowIcon(QIcon("src/GUI/app-icon.ico"))
        self.setWindowTitle("PyFlat YouTube Downloader")

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    thread_manager = ThreadManager(10)
    thread_manager.setMaxThreadCount(cfg.get(cfg.maximum_download_threads))
    downloader = Downloader(thread_manager)
    main_window = MainWindow()
    download_widget_manager.setInterface(main_window.download_interface, downloader)
    sys.exit(app.exec())

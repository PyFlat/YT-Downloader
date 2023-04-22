import threading, datetime, re, os, configparser,sys,subprocess, requests, shutil, wget

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from superqt import QLabeledRangeSlider #https://pyapp-kit.github.io/superqt/widgets/qlabeledrangeslider/
from urllib.request import urlopen
from zipfile import ZipFile

#MainWindow.setStyleSheet(open(get_abs_path("appdata/style.qss"), "r").read())
#self.playlist_range_slider.setOrientation(Qt.Orientation.Horizontal)
#https://www.youtube.com/watch?v=dQw4w9WgXcQ

class loggerout:
    def error(msg):
        print(msg)
    def warning(msg):
        print(msg)
    def debug(msg):
        pass

def get_abs_path(relative_path):
    base_path = getattr(sys,'_MEIPASS',os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_path, relative_path).replace("\\", "/")
    return path

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.toggle_sidebar_btn.clicked.connect(lambda: self.toggle_menu())
        self.ui.top_label.hide()
        self.ui.download_btn.setEnabled(False)
        self.ui.url_search_btn.setVisible(False)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(300)

        self.timer2 = QTimer()
        self.timer2.setSingleShot(True)

        self.bind_keys()

        self.threadpool = QThreadPool()

        self.ui.search_btn.setChecked(True)
        self.show()

    def bind_keys(self):
        self.ui.search_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(0)])
        self.ui.download_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(1)])
        self.ui.settings_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(2)])
        self.ui.exit_btn.clicked.connect(lambda: [self.close()])

    def toggle_menu(self):
        width = self.ui.sidebar.width()
        maxExtend = 190
        standard = 70
        if width == standard:
            widthExtended = maxExtend
        else:
            widthExtended = standard
        self.animation = QPropertyAnimation(self.ui.sidebar, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.start()

    @Slot(int, int)
    def setWidg2Range(self, max: int, min:int):
        self.ui.playlist_range_slider.setRange(max, min)

    @Slot(int, int)
    def setWidg2Value(self, max: int, min:int):
        self.ui.playlist_range_slider.setValue((max, min))

    @Slot(bool)
    def import_yt_dlp(self, t):
        global YoutubeDL, DownloadError
        try:
            from appdata.yt_dlp import YoutubeDL
            from appdata.yt_dlp.utils import DownloadError
        except ImportError:
            sys.path.insert(0, get_abs_path("appdata/"))
            from yt_dlp import YoutubeDL
            from yt_dlp.utils import DownloadError
            
    def invokeFunc(self, widget, func, connection, arg):
        QMetaObject.invokeMethod(widget, func, connection, arg)

    def invokeFunc2(self, widget, func, connection, arg, arg2):
        QMetaObject.invokeMethod(widget, func, connection, arg, arg2)

    def connect_wid(self, widget ,func):
        widget.connect(lambda: func())

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1100, 550)
        MainWindow.setMinimumSize(QSize(1100, 550))
        MainWindow.setStyleSheet(open(get_abs_path("appdata/style.qss"), "r").read())
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.topbar = QFrame(self.centralwidget)
        self.topbar.setObjectName(u"topbar")
        self.topbar.setMinimumSize(QSize(0, 50))
        self.topbar.setMaximumSize(QSize(16777215, 50))
        self.topbar.setStyleSheet(u"")
        self.topbar.setFrameShape(QFrame.NoFrame)
        self.topbar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.topbar)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.toggle_sidebar_btn = QPushButton(self.topbar)
        self.toggle_sidebar_btn.setObjectName(u"toggle_sidebar_btn")
        self.toggle_sidebar_btn.setMaximumSize(QSize(70, 50))
        icon = QIcon()
        icon.addFile(u"appdata/images/menu.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toggle_sidebar_btn.setIcon(icon)
        self.toggle_sidebar_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.toggle_sidebar_btn)

        self.topframe = QFrame(self.topbar)
        self.topframe.setObjectName(u"topframe")
        self.topframe.setFrameShape(QFrame.StyledPanel)
        self.topframe.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.topframe)
        self.horizontalLayout_7.setSpacing(10)
        self.horizontalLayout_7.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.top_label = QLabel(self.topframe)
        self.top_label.setObjectName(u"top_label")

        self.horizontalLayout_7.addWidget(self.top_label, 0, Qt.AlignHCenter)


        self.horizontalLayout.addWidget(self.topframe)


        self.verticalLayout.addWidget(self.topbar)

        self.main_frame = QFrame(self.centralwidget)
        self.main_frame.setObjectName(u"main_frame")
        self.main_frame.setFrameShape(QFrame.NoFrame)
        self.main_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.main_frame)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.sidebar = QFrame(self.main_frame)
        self.sidebar.setObjectName(u"sidebar")
        self.sidebar.setMaximumSize(QSize(70, 16777214))
        self.sidebar.setStyleSheet(u"")
        self.sidebar.setFrameShape(QFrame.NoFrame)
        self.sidebar.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.sidebar)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.sb_top_frame = QFrame(self.sidebar)
        self.sb_top_frame.setObjectName(u"sb_top_frame")
        self.sb_top_frame.setFrameShape(QFrame.NoFrame)
        self.sb_top_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.sb_top_frame)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 25, 0, 0)
        self.search_btn = QPushButton(self.sb_top_frame)
        self.search_btn.setObjectName(u"search_btn")
        self.search_btn.setMinimumSize(QSize(0, 50))
        icon1 = QIcon()
        icon1.addFile(u"appdata/images/search.png", QSize(), QIcon.Normal, QIcon.Off)
        self.search_btn.setIcon(icon1)
        self.search_btn.setIconSize(QSize(30, 30))
        self.search_btn.setCheckable(True)
        self.search_btn.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.search_btn)

        self.download_btn = QPushButton(self.sb_top_frame)
        self.download_btn.setObjectName(u"download_btn")
        self.download_btn.setMinimumSize(QSize(0, 50))
        icon2 = QIcon()
        icon2.addFile(u"appdata/images/download.png", QSize(), QIcon.Normal, QIcon.Off)
        self.download_btn.setIcon(icon2)
        self.download_btn.setIconSize(QSize(30, 30))
        self.download_btn.setCheckable(True)
        self.download_btn.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.download_btn)

        self.settings_btn = QPushButton(self.sb_top_frame)
        self.settings_btn.setObjectName(u"settings_btn")
        self.settings_btn.setMinimumSize(QSize(0, 50))
        icon3 = QIcon()
        icon3.addFile(u"appdata/images/settings.png", QSize(), QIcon.Normal, QIcon.Off)
        self.settings_btn.setIcon(icon3)
        self.settings_btn.setIconSize(QSize(30, 30))
        self.settings_btn.setCheckable(True)
        self.settings_btn.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.settings_btn)


        self.verticalLayout_3.addWidget(self.sb_top_frame, 0, Qt.AlignTop)

        self.sb_bottom_frame = QFrame(self.sidebar)
        self.sb_bottom_frame.setObjectName(u"sb_bottom_frame")
        self.sb_bottom_frame.setFrameShape(QFrame.NoFrame)
        self.sb_bottom_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.sb_bottom_frame)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.exit_btn = QPushButton(self.sb_bottom_frame)
        self.exit_btn.setObjectName(u"exit_btn")
        self.exit_btn.setMinimumSize(QSize(70, 50))
        icon4 = QIcon()
        icon4.addFile(u"appdata/images/exit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.exit_btn.setIcon(icon4)
        self.exit_btn.setIconSize(QSize(30, 30))

        self.verticalLayout_4.addWidget(self.exit_btn)


        self.verticalLayout_3.addWidget(self.sb_bottom_frame, 0, Qt.AlignBottom)


        self.horizontalLayout_2.addWidget(self.sidebar)

        self.frame_5 = QFrame(self.main_frame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.mainpages = QStackedWidget(self.frame_5)
        self.mainpages.setObjectName(u"mainpages")
        self.mpage1 = QWidget()
        self.mpage1.setObjectName(u"mpage1")
        self.verticalLayout_9 = QVBoxLayout(self.mpage1)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.mpage1)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(15)
        self.gridLayout.setVerticalSpacing(25)
        self.gridLayout.setContentsMargins(25, 25, 25, 0)
        self.url_entry = QLineEdit(self.frame)
        self.url_entry.setObjectName(u"url_entry")
        self.url_entry.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.url_entry, 0, 0, 1, 1)

        self.url_search_btn = QPushButton(self.frame)
        self.url_search_btn.setObjectName(u"url_search_btn")

        self.gridLayout.addWidget(self.url_search_btn, 0, 1, 1, 1)

        self.search_stack_widg = QStackedWidget(self.frame)
        self.search_stack_widg.setObjectName(u"search_stack_widg")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_10 = QVBoxLayout(self.page)
        self.verticalLayout_10.setSpacing(10)
        self.verticalLayout_10.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.info_start_label = QLabel(self.page)
        self.info_start_label.setObjectName(u"info_start_label")
        self.info_start_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.info_start_label, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.search_stack_widg.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_12 = QVBoxLayout(self.page_2)
        self.verticalLayout_12.setSpacing(10)
        self.verticalLayout_12.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.scrollArea = QScrollArea(self.page_2)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Plain)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 814, 1500))
        self.verticalLayout_13 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.scrollAreaWidgetContents)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 1500))
        self.gridLayout_2 = QGridLayout(self.widget)
        self.gridLayout_2.setSpacing(10)
        self.gridLayout_2.setContentsMargins(10, 10, 10, 10)
        self.gridLayout_2.setObjectName(u"gridLayout_2")

        self.verticalLayout_13.addWidget(self.widget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_12.addWidget(self.scrollArea)

        self.search_stack_widg.addWidget(self.page_2)

        self.gridLayout.addWidget(self.search_stack_widg, 1, 0, 1, 1)


        self.verticalLayout_9.addWidget(self.frame)

        self.mainpages.addWidget(self.mpage1)
        self.mpage2 = QWidget()
        self.mpage2.setObjectName(u"mpage2")
        self.verticalLayout_6 = QVBoxLayout(self.mpage2)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(10, 0, 10, 0)
        self.download_1 = QFrame(self.mpage2)
        self.download_1.setObjectName(u"download_1")
        self.download_1.setFrameShape(QFrame.StyledPanel)
        self.download_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.download_1)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.image_frame = QFrame(self.download_1)
        self.image_frame.setObjectName(u"image_frame")
        self.image_frame.setMinimumSize(QSize(480, 270))
        self.image_frame.setFrameShape(QFrame.StyledPanel)
        self.image_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.image_frame)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 10, 0, 0)
        self.image_label = QLabel(self.image_frame)
        self.image_label.setObjectName(u"image_label")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_label.sizePolicy().hasHeightForWidth())
        self.image_label.setSizePolicy(sizePolicy)
        self.image_label.setMinimumSize(QSize(480, 270))
        self.image_label.setMaximumSize(QSize(480, 270))
        self.image_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_9.addWidget(self.image_label)


        self.horizontalLayout_4.addWidget(self.image_frame)

        self.label_frame = QFrame(self.download_1)
        self.label_frame.setObjectName(u"label_frame")
        self.label_frame.setFrameShape(QFrame.StyledPanel)
        self.label_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.label_frame)
        self.verticalLayout_2.setSpacing(25)
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 9, 0, 0)
        self.name_label = QLabel(self.label_frame)
        self.name_label.setObjectName(u"name_label")
        self.name_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.name_label)

        self.artist_label = QLabel(self.label_frame)
        self.artist_label.setObjectName(u"artist_label")
        self.artist_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.artist_label)

        self.date_label = QLabel(self.label_frame)
        self.date_label.setObjectName(u"date_label")

        self.verticalLayout_2.addWidget(self.date_label)


        self.horizontalLayout_4.addWidget(self.label_frame, 0, Qt.AlignTop)


        self.verticalLayout_6.addWidget(self.download_1)

        self.download_2 = QStackedWidget(self.mpage2)
        self.download_2.setObjectName(u"download_2")
        self.download_2.setFrameShape(QFrame.StyledPanel)
        self.download_2.setFrameShadow(QFrame.Raised)
        self.download_bar_page1 = QWidget()
        self.download_bar_page1.setObjectName(u"download_bar_page1")
        self.verticalLayout_7 = QVBoxLayout(self.download_bar_page1)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.selection_frame = QFrame(self.download_bar_page1)
        self.selection_frame.setObjectName(u"selection_frame")
        self.selection_frame.setFrameShape(QFrame.StyledPanel)
        self.selection_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.selection_frame)
        self.horizontalLayout_5.setSpacing(15)
        self.horizontalLayout_5.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.format_selection = QComboBox(self.selection_frame)
        self.format_selection.setObjectName(u"format_selection")

        self.horizontalLayout_5.addWidget(self.format_selection)

        self.resolution_selection = QComboBox(self.selection_frame)
        self.resolution_selection.setObjectName(u"resolution_selection")

        self.horizontalLayout_5.addWidget(self.resolution_selection)

        self.change_location_btn = QPushButton(self.selection_frame)
        self.change_location_btn.setObjectName(u"change_location_btn")

        self.horizontalLayout_5.addWidget(self.change_location_btn)

        self.show_folder_btn = QPushButton(self.selection_frame)
        self.show_folder_btn.setObjectName(u"show_folder_btn")

        self.horizontalLayout_5.addWidget(self.show_folder_btn)


        self.verticalLayout_7.addWidget(self.selection_frame)

        self.download_btn_frame = QFrame(self.download_bar_page1)
        self.download_btn_frame.setObjectName(u"download_btn_frame")
        self.download_btn_frame.setFrameShape(QFrame.StyledPanel)
        self.download_btn_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.download_btn_frame)
        self.horizontalLayout_6.setSpacing(25)
        self.horizontalLayout_6.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.last_page_btn = QPushButton(self.download_btn_frame)
        self.last_page_btn.setObjectName(u"last_page_btn")

        self.horizontalLayout_6.addWidget(self.last_page_btn, 0, Qt.AlignLeft)

        self.download_button = QPushButton(self.download_btn_frame)
        self.download_button.setObjectName(u"download_button")

        self.horizontalLayout_6.addWidget(self.download_button)


        self.verticalLayout_7.addWidget(self.download_btn_frame, 0, Qt.AlignHCenter)

        self.download_2.addWidget(self.download_bar_page1)
        self.download_bar_page2 = QWidget()
        self.download_bar_page2.setObjectName(u"download_bar_page2")
        self.horizontalLayout_8 = QHBoxLayout(self.download_bar_page2)
        self.horizontalLayout_8.setSpacing(10)
        self.horizontalLayout_8.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.progress_frame = QFrame(self.download_bar_page2)
        self.progress_frame.setObjectName(u"progress_frame")
        self.progress_frame.setFrameShape(QFrame.StyledPanel)
        self.progress_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.progress_frame)
        self.verticalLayout_8.setSpacing(10)
        self.verticalLayout_8.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.progress_eta_label = QLabel(self.progress_frame)
        self.progress_eta_label.setObjectName(u"progress_eta_label")

        self.verticalLayout_8.addWidget(self.progress_eta_label, 0, Qt.AlignHCenter)

        self.progressbar = QProgressBar(self.progress_frame)
        self.progressbar.setObjectName(u"progressbar")
        sizePolicy.setHeightForWidth(self.progressbar.sizePolicy().hasHeightForWidth())
        self.progressbar.setSizePolicy(sizePolicy)
        self.progressbar.setMinimumSize(QSize(250, 0))
        self.progressbar.setValue(0)
        self.progressbar.setTextVisible(True)
        self.progressbar.setInvertedAppearance(False)

        self.verticalLayout_8.addWidget(self.progressbar, 0, Qt.AlignHCenter)


        self.horizontalLayout_8.addWidget(self.progress_frame)

        self.download_2.addWidget(self.download_bar_page2)
        self.download_bar_page3 = QWidget()
        self.download_bar_page3.setObjectName(u"download_bar_page3")
        self.verticalLayout_14 = QVBoxLayout(self.download_bar_page3)
        self.verticalLayout_14.setSpacing(10)
        self.verticalLayout_14.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(20, 10, 20, 15)
        self.info_range_slider_label = QLabel(self.download_bar_page3)
        self.info_range_slider_label.setObjectName(u"info_range_slider_label")
        self.info_range_slider_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_14.addWidget(self.info_range_slider_label, 0, Qt.AlignTop)

        self.playlist_range_slider = QLabeledRangeSlider(self.download_bar_page3)
        self.playlist_range_slider.setObjectName(u"playlist_range_slider")
        self.playlist_range_slider.setOrientation(Qt.Orientation.Horizontal)
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.playlist_range_slider.sizePolicy().hasHeightForWidth())
        self.playlist_range_slider.setSizePolicy(sizePolicy1)
        self.playlist_range_slider.setMinimumSize(QSize(0, 81))

        self.verticalLayout_14.addWidget(self.playlist_range_slider)

        self.next_page_btn = QPushButton(self.download_bar_page3)
        self.next_page_btn.setObjectName(u"next_page_btn")

        self.verticalLayout_14.addWidget(self.next_page_btn, 0, Qt.AlignHCenter)

        self.download_2.addWidget(self.download_bar_page3)

        self.verticalLayout_6.addWidget(self.download_2)

        self.mainpages.addWidget(self.mpage2)
        self.mpage3 = QWidget()
        self.mpage3.setObjectName(u"mpage3")
        self.verticalLayout_11 = QVBoxLayout(self.mpage3)
        self.verticalLayout_11.setSpacing(10)
        self.verticalLayout_11.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.selection_frame_2 = QFrame(self.mpage3)
        self.selection_frame_2.setObjectName(u"selection_frame_2")
        self.selection_frame_2.setFrameShape(QFrame.StyledPanel)
        self.selection_frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.selection_frame_2)
        self.horizontalLayout_11.setSpacing(15)
        self.horizontalLayout_11.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.change_ffmpeg_path_btn = QPushButton(self.selection_frame_2)
        self.change_ffmpeg_path_btn.setObjectName(u"change_ffmpeg_path_btn")

        self.horizontalLayout_11.addWidget(self.change_ffmpeg_path_btn)

        self.download_ffmpeg_btn = QPushButton(self.selection_frame_2)
        self.download_ffmpeg_btn.setObjectName(u"download_ffmpeg_btn")

        self.horizontalLayout_11.addWidget(self.download_ffmpeg_btn)


        self.verticalLayout_11.addWidget(self.selection_frame_2, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_3 = QFrame(self.mpage3)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)

        self.verticalLayout_11.addWidget(self.frame_3)

        self.mainpages.addWidget(self.mpage3)

        self.horizontalLayout_3.addWidget(self.mainpages)


        self.horizontalLayout_2.addWidget(self.frame_5)


        self.verticalLayout.addWidget(self.main_frame)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.mainpages.setCurrentIndex(0)
        self.search_stack_widg.setCurrentIndex(0)
        self.download_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Youtube Downloader v1.0.0", None))
        self.toggle_sidebar_btn.setText("")
        self.top_label.setText("")
        self.search_btn.setText(QCoreApplication.translate("MainWindow", u"   Search", None))
        self.download_btn.setText(QCoreApplication.translate("MainWindow", u"   Download", None))
        self.settings_btn.setText(QCoreApplication.translate("MainWindow", u"   Settings", None))
        self.exit_btn.setText(QCoreApplication.translate("MainWindow", u"   Exit", None))
        self.url_entry.setText("")
        self.url_entry.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Insert Video or Playlist URL", None))
        self.url_search_btn.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.info_start_label.setText("")
        self.image_label.setText(QCoreApplication.translate("MainWindow", u"Thumbnail", None))
        self.name_label.setText("")
        self.artist_label.setText("")
        self.date_label.setText("")
        self.change_location_btn.setText(QCoreApplication.translate("MainWindow", u"Change Download Folder", None))
        self.show_folder_btn.setText(QCoreApplication.translate("MainWindow", u"Show Folder in Explorer", None))
        self.last_page_btn.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.download_button.setText(QCoreApplication.translate("MainWindow", u"Download", None))
        self.progress_eta_label.setText("")
        self.info_range_slider_label.setText("")
        self.next_page_btn.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.change_ffmpeg_path_btn.setText(QCoreApplication.translate("MainWindow", u"Change FFmpeg Path", None))
        self.download_ffmpeg_btn.setText(QCoreApplication.translate("MainWindow", u"Download FFmpeg", None))
    # retranslateUi

class Downloader():
    def __init__(self, window, app):
        self.win = window
        self.app = app
        self.win.connect_wid(self.win.timer.timeout, self.start_load_video)
        self.win.connect_wid(self.win.ui.url_entry.textChanged, self.win.timer.start)
        self.win.connect_wid(self.win.ui.format_selection.currentIndexChanged, self.update_file_box)
        self.win.connect_wid(self.win.ui.download_button.clicked, self.start_download)
        self.win.connect_wid(self.win.ui.change_location_btn.clicked, self.change_location)
        self.win.connect_wid(self.win.ui.show_folder_btn.clicked, self.show_in_explorer)
        self.win.connect_wid(self.win.ui.download_ffmpeg_btn.clicked, self.download_ffmpeg)
        self.win.connect_wid(self.win.ui.change_ffmpeg_path_btn.clicked, self.change_ffmpeg_location)
        self.win.connect_wid(self.win.ui.next_page_btn.clicked, lambda: self.win.ui.download_2.setCurrentIndex(0))
        self.win.connect_wid(self.win.ui.last_page_btn.clicked, lambda: self.win.ui.download_2.setCurrentIndex(2))
        self.file_formats = ["Mp4", "Mp3"]
        if not os.path.isfile(get_abs_path("appdata/config.ini")):
            y = threading.Thread(target=self.create_ini)
            y.start()
            y.join()
        self.load_config()
        self.win.invokeFunc(self.win, "import_yt_dlp", Qt.QueuedConnection, Q_ARG(bool, True))

    def update_file_box(self):
        if self.win.ui.format_selection.currentText() == "Mp4":
            self.win.ui.resolution_selection.setEnabled(True)
        else:
            self.win.ui.resolution_selection.setEnabled(False)
            self.win.ui.resolution_selection.setCurrentIndex(0)

    def start_load_video(self):
        self.win.invokeFunc(self.win.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, "Searching..."))
        threading.Thread(target=self.load_video).start()

    def create_ini(self):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"download_path": "~/Downloads/",
                             "ffmpeg_path": "None",
                             "yt-dlp-installed": "False",
                             "yt-dlp-date": "False",}
        with open(get_abs_path("appdata/config.ini"), "w+") as file:
            config.write(file)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(get_abs_path("appdata/config.ini"))
        self.ffmpeg = config["DEFAULT"]["ffmpeg_path"]
        self.file = config["DEFAULT"]["download_path"]
        self.yt_dlp_installed = config["DEFAULT"]["yt-dlp-installed"]
        if self.yt_dlp_installed == "False":
            self.install_yt_dlp()
        if self.ffmpeg == "None":
            self.user_info_no_ffmpeg()
        
    def update_config(self, section, key, new_val):
        config = configparser.ConfigParser()
        config.read(get_abs_path("appdata/config.ini"))
        config[section][key] = str(new_val)
        with open(get_abs_path("appdata/config.ini"), "w") as file:
            config.write(file)

    def load_playlist(self, info):
        self.title = info["title"]
        self.author = info["channel"]
        self.playlist_count = info["playlist_count"]
        self.url = self.get_thumbnail_url(info)
        self.image_byt = urlopen(self.url).read()
        self.update_main_frame()

    def load_video(self):
        cur_link = self.win.ui.url_entry.text()
        if cur_link == "":
            self.win.invokeFunc(self.win.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, ""))
            return
        if "&list=" in cur_link and "?v=" in cur_link:
            cur_link = cur_link.split("&list=")[0]
        info = self.get_video_information(cur_link)
        if info != None and info["webpage_url_domain"] != None and info["webpage_url_domain"] == "youtube.com":
            self.cur_link = cur_link
            if "?list=" in cur_link and ("&list=" not in cur_link and "?v=" not in cur_link):
                self.playlist = True
                self.load_playlist(info)
                return
            self.playlist = False
            self.title = self.windows_file_title = str(info["title"])
            char_remov = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
            for char in char_remov:
                self.windows_file_title = self.windows_file_title.replace(char, "#")
            self.author = info["channel"]
            self.upload_date = datetime.datetime.strptime(info["upload_date"], "%Y%m%d").strftime("%d.%m.%Y")
            self.formats = self.check_formats(info)
            self.url = self.get_thumbnail_url(info)
            self.image_byt = urlopen(self.url).read()
            self.update_main_frame()
            
        else:
            if len(cur_link) >= 20:
                cur_link = f"{cur_link[0:13]}..."
                #\n(If you want to search for '{cur_link}' press Search.) <- Not possible yet! (implement later)
            if info == None or info["webpage_url_domain"] == None:
                text = f"No video found!"
            else:
                text = f"No valid video url!"
            self.win.invokeFunc(self.win.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, text))
            self.win.invokeFunc(self.win.ui.download_btn, "setEnabled", Qt.QueuedConnection, Q_ARG(bool, False))

    def get_thumbnail_url(self, info):
        x = []
        for thumbnail in info["thumbnails"]:
            if "resolution" in thumbnail:
                if int(thumbnail["width"]) >= 300 and int(thumbnail["width"]) <= 640:
                    x.append(thumbnail["url"])
        return x[-1]

    def get_video_information(self, url):
        yt_dlp_opts = {"quiet": True,
                       "noprogress": True,
                       "logger": loggerout,
                       "playlist_items": "0",
                       "extract_flat": True,
                       }
        ydl = YoutubeDL(yt_dlp_opts)
        try:
            inf = ydl.extract_info(url, False)
            info = ydl.sanitize_info(inf)
        except DownloadError:
            info = None
        return info

    def check_formats(self, info):
        resolution = []
        for stream in info["formats"]:
            if stream["video_ext"] != "none":
                stre = f"{stream['resolution'].split('x')[1]}p"
                if stre not in resolution:
                    resolution.append(stre)
        resolution = sorted(resolution, key=lambda s: int(re.compile(r'\d+').search(s).group()), reverse=True)
        resolution.insert(0, "Best Quality")
        return resolution

    def update_main_frame(self):
        self.win.ui.download_btn.setEnabled(True)
        self.win.ui.download_btn.click()
        self.win.invokeFunc(self.win.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, ""))
        img = QImage()
        img.loadFromData(self.image_byt)
        pixmap = QPixmap.fromImage(img.scaled(480, 360))
        self.win.ui.image_label.setPixmap(pixmap)
        self.win.ui.name_label.setText(f"Title: {self.title}")
        self.win.ui.artist_label.setText(f"Uploader: {self.author}")
        self.win.invokeFunc(self.win.ui.format_selection, "setVisible", Qt.QueuedConnection, Q_ARG(bool, True))
        self.win.ui.format_selection.addItems(self.file_formats)
        if not self.playlist:
            self.win.ui.date_label.setText(f"Upload Date: {self.upload_date}")
            self.win.ui.resolution_selection.addItems(self.formats)
            self.win.invokeFunc(self.win.ui.resolution_selection, "setVisible", Qt.QueuedConnection, Q_ARG(bool, True))
            self.win.invokeFunc(self.win.ui.last_page_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
        else:
            self.win.invokeFunc(self.win.ui.download_2, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 2))
            self.win.invokeFunc(self.win.ui.info_range_slider_label, "setText", Qt.QueuedConnection, Q_ARG(str, "Select the Range you want to Download"))
            self.win.ui.date_label.setText(f"Playlist Count: {self.playlist_count} Videos")
            self.win.invokeFunc2(self.win, "setWidg2Range", Qt.QueuedConnection, Q_ARG(int, 1), Q_ARG(int, self.playlist_count))
            self.win.invokeFunc2(self.win, "setWidg2Value", Qt.QueuedConnection, Q_ARG(int, 1), Q_ARG(int, self.playlist_count))
            self.win.invokeFunc(self.win.ui.resolution_selection, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
        
    def change_location(self):
        new_dir = QFileDialog.getExistingDirectory(None, "Select a folder", os.path.expanduser(self.file))
        if new_dir == "":
            return
        self.file = f"{new_dir}/"
        threading.Thread(target = lambda: self.update_config("DEFAULT", "download_path", self.file)).start()

    def change_ffmpeg_location(self):
        new_dir = QFileDialog.getExistingDirectory(None, "Select the '/bin' Folder of your FFmpeg installation", os.path.expanduser(self.ffmpeg))
        if new_dir == "":
            return
        self.ffmpeg = f"{new_dir}/"
        self.update_config("DEFAULT", "ffmpeg_path", self.ffmpeg)

    def show_in_explorer(self):
        f = os.path.expanduser(self.file).replace('/', '\\')
        command = f"explorer.exe {f}"
        subprocess.Popen(command)

    def update_to(self, d):
        #print(d["status"])
        if d["status"] == "started":
            self.win.invokeFunc(self.win.ui.progressbar, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
            if self.playlist:
                self.win.ui.progress_eta_label.setText(f"Download Finished, Postprocessing Started\nVideo: {d['info_dict']['playlist_autonumber']}/{d['info_dict']['n_entries']}")
        elif d["status"] == "finished":
            if (self.playlist and int(d['info_dict']['playlist_autonumber']) == d['info_dict']['n_entries']) or not self.playlist:
                self.win.invokeFunc(self.win.ui.download_2, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 0))
            self.win.invokeFunc(self.win.ui.progressbar, "setVisible", Qt.QueuedConnection, Q_ARG(bool, True))
            self.win.invokeFunc(self.win.ui.progressbar, "setValue", Qt.QueuedConnection, Q_ARG(int, 0))

    def update_progress(self, d):
        if not self.win.ui.progressbar.isVisible():
            self.win.invokeFunc(self.win.ui.progressbar, "setVisible", Qt.QueuedConnection, Q_ARG(bool, True))
        if d['status'] == 'downloading':
            pr = int(round(round(float(d['downloaded_bytes'])/float(d["total_bytes"]),2)*100, 0))
            if d["eta"] == None:
                eta = "Unknown"
            else:
                eta = int(round(float(d['eta']),ndigits=0))
            if self.playlist:
                add = f"| Video: {d['info_dict']['playlist_autonumber']}/{d['info_dict']['n_entries']}"
            else:
                add = ""
            label_text = f"Time Elapsed: {int(round(float(d['elapsed']),ndigits=0))}s| Estimated Time: {eta}s{add}"
            self.win.invokeFunc(self.win.ui.progressbar, "setValue", Qt.QueuedConnection, Q_ARG(int, pr))
            self.win.invokeFunc(self.win.ui.progress_eta_label, "setText", Qt.QueuedConnection, Q_ARG(str, label_text))
        elif d["status"] == "finished":
            self.win.invokeFunc(self.win.ui.progress_eta_label, "setText", Qt.QueuedConnection, Q_ARG(str, "Download Finished"))
                    
    def yes_no_messagebox(self, text, icon, title, options, hide = True):
        qms = QMessageBox(icon, title, text, options, self.win)
        qms.setModal(True)
        if hide:
            qms.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        reply = qms.exec()
        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def user_info_no_ffmpeg(self):
        self.yes_no_messagebox("\"FFmpeg\" path is not defined.\nYou can't download Videos without it!\nDownload it or set the path to your installation.", QMessageBox.Warning, "Warning", QMessageBox.Ok)
        self.win.ui.settings_btn.click()

    def start_playlist_download(self):
        path = f"{os.path.expanduser(self.file)}/yt_playlist_{self.title}_{self.author}/"
        if os.path.isdir(path):
            num = 1
            pat = path
            while os.path.isdir(pat):
                pat = path[:-1]
                pat = f"{pat}({num})"
                num += 1
                if not os.path.isdir(pat):
                    path = pat + "/"
        os.makedirs(path)
        self.temp_file = path
        vid_ext = self.win.ui.format_selection.currentText().lower()
        if vid_ext == "mp4":
            self.outtmpl = f"{self.temp_file}%(title)s(%(height)sp).%(ext)s"
        else:
            self.outtmpl = f"{self.temp_file}%(title)s.%(ext)s"
        min, max = self.win.ui.playlist_range_slider.value()
        self.pl_range = f"{min}:{max}"
        threading.Thread(target=self.download).start()

    def start_download(self):
        self.win.invokeFunc(self.win.ui.progressbar, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
        if self.playlist:
            self.start_playlist_download()
            return
        self.pl_range = ""
        vid_ext = self.win.ui.format_selection.currentText().lower()
        vid_res = self.win.ui.resolution_selection.currentText()
        if vid_ext  == "mp4":
            self.outtmpl = f"{self.file}{self.title}(%(height)sp).%(ext)s"
            if vid_res != "Best Quality":
                ext = f"({vid_res})"
            else:
                ext = f"({self.formats[1]})"
        else:
            self.outtmpl = f"{self.file}{self.title}.%(ext)s"
            ext = ""
        path = os.path.expandvars(f"{os.path.expanduser(self.file)}{self.windows_file_title}{ext}.{self.win.ui.format_selection.currentText().lower()}")
        if os.path.isfile(path):
            if not self.yes_no_messagebox("This file already exists.\nDo you want to overwrite it?", QMessageBox.Warning, "Warning", QMessageBox.Yes | QMessageBox.No):
                return
        if not os.path.isfile(self.ffmpeg + "/ffmpeg.exe"):
            self.user_info_no_ffmpeg()
            return
        threading.Thread(target=self.download).start()

    def install_yt_dlp(self):
        if self.yes_no_messagebox("\"yt-dlp\" isn't downloaded! \nDownload it?", QMessageBox.Warning, "Warning", QMessageBox.Yes |QMessageBox.No):
            self.download_yt_dlp()
        else:
            self.win.close()
            sys.exit()

    def download_from_github(self, url, filename, progress):
        def bar_progress(current, total, width=80):
            progress_message = int(round(current / total * 100, ndigits=0))
            if progress.value() != progress_message:
                progress.setValue(progress_message)
        wget.download(url, out=filename, bar=bar_progress)

    def download_yt_dlp(self):
        if os.path.isdir("appdata/yt_dlp"):
            shutil.rmtree("appdata/yt_dlp")
        progress = QProgressDialog('Downloading yt-dlp', '', 0, 100, self.win)
        progress.setFixedWidth(250)
        progress.setWindowTitle("Download Window")
        progress.setModal(True)
        progress.setCancelButton(None)
        progress.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.download_from_github("https://github.com/yt-dlp/yt-dlp/archive/refs/heads/master.zip", "appdata/yt-dlp.zip", progress)
        zp = ZipFile("appdata/yt-dlp.zip")
        names_foo = [i for i in zp.namelist() if i.startswith("yt-dlp-master/yt_dlp/")]
        for file in names_foo:
            zp.extract(file)
        zp.close()
        shutil.move("yt-dlp-master/yt_dlp", "appdata/yt_dlp")
        shutil.rmtree("yt-dlp-master")
        os.remove("appdata/yt-dlp.zip")
        self.update_config("DEFAULT", "yt-dlp-installed", "True")
        self.update_config("DEFAULT", "yt-dlp-date", str(datetime.datetime.now()))
        self.yes_no_messagebox("Download Finished", QMessageBox.Information, "Info", QMessageBox.Ok)

    def download_ffmpeg(self):
        if os.path.isdir("appdata/FFmpeg"):
            shutil.rmtree("appdata/FFmpeg")
        progress = QProgressDialog('Downloading FFmpeg', '', 0, 100, self.win)
        progress.setFixedWidth(250)
        progress.setWindowTitle("Download Window")
        progress.setModal(True)
        progress.setCancelButton(None)
        progress.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.download_from_github("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip", "appdata/ffmpeg.zip", progress)
        zp = ZipFile("appdata/ffmpeg.zip")
        names_foo = [i for i in zp.namelist() if i.startswith("ffmpeg-master-latest-win64-gpl/")]
        for file in names_foo:
            zp.extract(file)
        zp.close()
        os.rename("ffmpeg-master-latest-win64-gpl", "appdata/FFmpeg")
        os.remove("appdata/ffmpeg.zip")
        self.yes_no_messagebox("Download Finished", QMessageBox.Information, "Info", QMessageBox.Ok)
        self.ffmpeg = get_abs_path("appdata/FFmpeg/bin")
        self.update_config("DEFAULT", "ffmpeg_path", self.ffmpeg)

    def download(self):
        self.win.invokeFunc(self.win.ui.download_2, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 1))
        self.win.ui.progress_eta_label.setText("Download Started")
        vid_format = self.win.ui.format_selection.currentText().lower()
        vid_quality = self.win.ui.resolution_selection.currentText().split("p")[0]
        if ((vid_quality != "Best Quality") and (vid_format != "mp3")) and not self.playlist:
            format_ = "bv[height="+str(vid_quality)+"]+ba[ext=m4a]/b"
        else:
            format_ = "bv*+ba[ext=m4a]/b"
        if vid_format == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "ffmpeg_location": self.ffmpeg,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
                "outtmpl": self.outtmpl,
                "quiet": True,
                "noprogress": True,
                'progress_hooks': [self.update_progress],
                "playlist_items": self.pl_range,
                "overwrites": True,
                "postprocessor_hooks": [self.update_to],
                }
        else:
            ydl_opts = {
                "format": format_,
                "ffmpeg_location": self.ffmpeg,
                "outtmpl": self.outtmpl,
                "merge_output_format": "mp4",
                "quiet": True,
                "noprogress": True,
                'progress_hooks': [self.update_progress],
                "concurrent_fragments": 2,
                "playlist_items": self.pl_range,
                "overwrites": True,
                "postprocessor_hooks": [self.update_to],
                }
        YoutubeDL(ydl_opts).download(self.cur_link)

#https://www.youtube.com/watch?v=dQw4w9WgXcQ

if __name__ == "__main__":
    app = QApplication([])
    Downloader(MainWindow(), app)
    sys.exit(app.exec())
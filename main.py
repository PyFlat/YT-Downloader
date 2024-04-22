from src.Logger import Logger
import sys, logging, os

class Utils():
    @staticmethod
    def get_abs_path(relative_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = getattr(sys, '_MEIPASS', current_dir)
        path = os.path.join(base_path, relative_path).replace("\\", "/")
        return path

if __name__ == "__main__":
    logger_object = Logger(logs_folder=Utils.get_abs_path("logs"))
    logger = logger_object.logger
    logger.info("Logging Started")

import threading, datetime, os, configparser, shutil, requests, re, copy

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from zipfile import ZipFile
from src.CustomWidgets.ProgressDialog import ProgressDialog
from src.Ui_MainWindow import Ui_MainWindow
from src.CustomWidgets.SLabel import SLabel
from src.CustomWidgets.VideoSelectDialog import VideoSelectDialog
from src.TranslationManager import TranslationManager
from appdata.changelogs.changelogFiles import CHANGELOG_FILES

from urllib.request import urlopen
from urllib.error import URLError

VERSION = "1.3.3"

class noLogger:
    def error(msg):
        pass
    def warning(msg):
        pass
    def debug(msg):
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.toggle_sidebar_btn.clicked.connect(lambda: self.toggle_menu())
        self.ui.download_btn.setEnabled(False)
        self.ui.tableWidget.horizontalHeader().setVisible(True)
        self.ui.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch)
        self.ui.tableWidget.setWordWrap(True)

        self.setStyleSheet(open(Utils.get_abs_path("appdata/style.qss"), "r").read())

        self.ui.mainpages.setCurrentIndex(0)
        self.ui.search_stack_widg.setCurrentIndex(0)
        self.ui.download_2.setCurrentIndex(0)

        self.ui.tableWidget.focusOutEvent = self.on_focus_out

        self.bind_keys()

        self.search_shortcut = QShortcut(QKeySequence("Return"), self)

        self.actiongroup_change_log_level = QActionGroup(self)
        self.actiongroup_change_log_level.addAction(self.ui.actionLog_Level_Debug)
        self.actiongroup_change_log_level.addAction(self.ui.actionLog_Level_Info)

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(5)

        self.ui.search_btn.setChecked(True)

        self.show()

    def on_focus_out(self, event):
        selection_model = self.ui.tableWidget.selectionModel()
        selection_model.clearSelection()
        event.accept()
        timer = QTimer()
        timer.singleShot(250, lambda: self.set_enabled(False, False, False))

    def set_enabled(self, enabled1:bool, enabled2:bool, enabled3:bool, enabled4:bool=False):
        self.ui.download_delete_btn.setEnabled(enabled1)
        self.ui.download_open_btn.setEnabled(enabled2)
        self.ui.download_download_btn.setEnabled(enabled3)
        self.ui.download_cancel_btn.setEnabled(enabled4)

    def bind_keys(self):
        self.ui.search_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(0)])
        self.ui.download_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(1)])
        self.ui.file_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(2)])
        self.ui.exit_btn.clicked.connect(lambda: [self.close()])

    def toggle_menu(self):
        width = self.ui.sidebar.width()
        maxExtend = 190
        standard = 70
        widthExtended = maxExtend if width == standard else standard
        self.animation = QPropertyAnimation(self.ui.sidebar, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.start()

    @Slot(int, int)
    def setWidg2Range(self, min: int, max:int):
        self.ui.playlist_range_slider.setRange(min, max)

    @Slot(int, int)
    def setWidg2Value(self, min: int, max:int):
        self.ui.playlist_range_slider.setValue((min, max))


    def invokeFunc(self, widget, func, connection, arg):
        QMetaObject.invokeMethod(widget, func, connection, arg)

    def invokeFunc2(self, widget, func, connection, arg, arg2):
        QMetaObject.invokeMethod(widget, func, connection, arg, arg2)

    def create_search_widges(self, more = False):
        if not more:
            self.search_labels = []
            self.column = 0
        else:
            if not dl.search_activated or dl.new_widget_thread_running: return
            if not self.ui.scrollArea.verticalScrollBar().value() == self.ui.scrollArea.verticalScrollBar().maximum(): return
        for _ in range(0,10):
            for i in range(0,3):
                label = SLabel(self.ui.searching_button, dl, self.ui.scrollAreaWidgetContents)
                self.search_labels.append(label)
                self.ui.gridLayout_2.addWidget(label, self.column, i)
                self.ui.gridLayout_2.setAlignment(label, Qt.AlignTop | Qt.AlignCenter)
            self.column += 1

    def restartApplication(self):
        if getattr(sys, 'frozen', False):
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def closeEvent(self, event: QCloseEvent):
        dl.cleanup()
        logger.info("Closing the application")
        return super().closeEvent(event)

    def paintEvent(self, event: QPaintEvent):
        self.ui.scrollArea.setMinimumHeight(self.geometry().height()-150)
        return super().paintEvent(event)

class Downloader():
    def __init__(self):
        mw.ui.searching_button.clicked.connect(lambda:[self.load_url(), mw.ui.searching_button.setEnabled(False)])
        mw.ui.format_selection.currentIndexChanged.connect(lambda:self.update_file_box())
        mw.ui.download_button.clicked.connect(self.prepare_for_download)
        mw.ui.next_page_btn.clicked.connect(lambda: mw.ui.download_2.setCurrentIndex(0))
        mw.ui.last_page_btn.clicked.connect(lambda: mw.ui.download_2.setCurrentIndex(1))
        mw.ui.select_videos_btn.clicked.connect(lambda: self.show_video_select())
        mw.ui.playlist_range_slider.valueChanged.connect(lambda: self.change_download_range())
        mw.ui.scrollArea.verticalScrollBar().valueChanged.connect(lambda: [self.fill_new_widgs()])
        mw.search_shortcut.activated.connect(self.enter_pressed)
        mw.ui.tableWidget.cellClicked.connect(self.handle_clicked)
        self.file_formats = ["Mp4", "Mp3"]
        self.resolutions = ['Best Quality', '4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
        self.search_activated = True
        self.new_widget_thread_running = False
        self.update_thread = None
        self.downloads = []
        self.cur_process = []
        self.selected_ids = []
        self.loading = False
        self.delete_exe_files()
        self.connect_menu_actions()
        self.tm = TranslationManager(Utils.get_abs_path("languages/"), mw)
        self.update_language_action()
        if not os.path.isfile(Utils.get_abs_path("appdata/config.ini")):
            y = threading.Thread(target=self.create_ini)
            y.start()
            y.join()
        self.load_config()
        if getattr(sys, 'frozen', False) and self.update_check:
            self.search_for_updates()

    def cleanup(self):
        path = os.path.dirname(self.file)
        for file in os.listdir(path):
            if file.endswith('.part') or file.endswith('.ytdl'):
                os.remove(os.path.join(path, file))

    def prepare_for_download(self):
        ext = mw.ui.format_selection.currentText().lower()
        res = mw.ui.resolution_selection.currentText()
        copy.copy(self.data).prepare_for_download(ext, res)

    def update_language_action(self):
        keys = self.tm.languages.keys()
        mw.ui.actionDefault.deleteLater()
        icon = mw.ui.actionLog_Level_Debug.icon()

        mw.ui.menuChange_Language.clear()

        action_group = QActionGroup(mw)

        for key in keys:
            action = QAction(key, mw, checkable=True)
            action.setIcon(icon)
            action.setObjectName(key)
            action_group.addAction(action)
            action.triggered.connect(lambda checked=False, k=key: self.change_language(k))

            mw.ui.menuChange_Language.addAction(action)

    def change_language(self, language:str, force=False):
        if language == self.default_language:
            force = True
        if not force:
            result = self.yes_no_messagebox(self.tm.get_inline_string("change-language-dialog"), QMessageBox.Warning, self.tm.get_inline_string("warning"), QMessageBox.No | QMessageBox.Yes)
            if not result:
                child = mw.findChild(QAction, self.default_language)
                child.setChecked(True)
                return

        self.tm.change_language(language)

        self.default_language = language
        self.update_config("DEFAULT", "default-language", str(self.default_language))
        self.resolutions[0] = self.tm.get_inline_string("best-quality")

        if not force:
            if getattr(sys, 'frozen', False):
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                python = sys.executable
                os.execl(python, python, *sys.argv)

    def show_video_select(self):
        videos = []
        for index, playlist_object in enumerate(self.data.playlist_data_objects):
            videos.append({"title": playlist_object.title,
                "uploader": playlist_object.author,
                "playlist_index": index,
                "selected": True if index + 1 in self.selected_ids else False
        })
        self.video_select_dialog = VideoSelectDialog(mw, dl, videos)
        self.video_select_dialog.exec()
        self.selected_ids = self.video_select_dialog.get_selected()
        if self.selected_ids == [] or self.has_clear_range(self.selected_ids):
            mw.ui.playlist_range_slider.setEnabled(True)
        else:
            mw.ui.playlist_range_slider.setEnabled(False)

    def change_download_range(self):
        start, stop = mw.ui.playlist_range_slider.value()
        self.selected_ids = []
        for num in range(start, stop + 1):
            self.selected_ids.append(num)

    def has_clear_range(self, numbers):
        numbers.sort()

        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] != 1:
                return False
        mw.ui.playlist_range_slider.setValue((numbers[0], numbers[-1]))
        return True

    def enter_pressed(self):
        if mw.ui.mainpages.currentIndex() == 0:
            mw.ui.searching_button.click()

    def connect_menu_actions(self):
        mw.ui.actionChange_Download_Folder.triggered.connect(lambda: self.change_location())
        mw.ui.actionReveal_in_File_Explorer.triggered.connect(lambda: self.show_in_explorer())
        mw.ui.actionAutomatic_Update_Check.triggered.connect(lambda ev:[setattr(self, "update_check", ev), self.update_config("DEFAULT", "check-for-updates", str(ev))])
        mw.ui.actionShow_Thumbnails.triggered.connect(lambda ev:[setattr(self, "stream_thumbnails", ev), self.update_config("DEFAULT", "thumbnail-streaming", str(ev))])
        mw.ui.actionSet_FFmpeg_Path.triggered.connect(lambda: self.change_ffmpeg_location())
        mw.ui.actionDownload_FFmpeg.triggered.connect(lambda: self.download_ffmpeg())
        mw.ui.actionUpdate_Yt_dlp.triggered.connect(lambda: self.download_yt_dlp())
        mw.ui.actionSearch_For_Updates.triggered.connect(lambda: self.search_for_updates(False))
        mw.ui.actionMaximum_Threads.triggered.connect(lambda: self.change_max_threads())
        mw.ui.actionShow_Changelog.triggered.connect(lambda: self.show_changelog())
        mw.ui.actionShow_on_Github.triggered.connect(lambda: self.show_on_github())
        mw.ui.actionDefault_Resolution.triggered.connect(lambda: self.change_default_resolution())
        mw.ui.actionOpen_Log_Files_Folder.triggered.connect(lambda: self.open_log_files_folder())
        mw.ui.actionLog_Level_Debug.triggered.connect(lambda: self.update_log_level("debug"))
        mw.ui.actionLog_Level_Info.triggered.connect(lambda: self.update_log_level("info"))

    def open_log_files_folder(self):
        path = Utils.get_abs_path('logs').replace('/', '\\')
        os.popen(f"explorer.exe \"{path}\"")

    def change_max_threads(self):
        dialog = QDialog(mw)

        layout = QVBoxLayout()

        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(25)
        label = QLabel(self.tm.get_inline_string("max-dl-threads").format(self.max_download_threads))
        layout.addWidget(label)

        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(10)
        slider.setValue(self.max_download_threads)
        slider.valueChanged.connect(lambda value: label.setText(self.tm.get_inline_string("max-dl-threads").format(value)))
        layout.addWidget(slider)

        apply_button = QPushButton(self.tm.get_inline_string("apply"))
        apply_button.clicked.connect(lambda: save_maximum_download_threads())

        def save_maximum_download_threads():
            mw.threadpool.setMaxThreadCount(slider.value())
            self.update_config("DEFAULT", "max-download-threads", str(slider.value()))
            self.max_download_threads = slider.value()
            dialog.accept()

        layout.addWidget(apply_button)

        dialog.setLayout(layout)

        dialog.setWindowTitle(self.tm.get_inline_string("max-dl-threads-title"))
        dialog.setFixedSize(375, 175)

        dialog.exec()

    def change_default_resolution(self):
        dialog = QDialog(mw)

        layout = QVBoxLayout()

        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(25)

        combobox = QComboBox()
        combobox.clear()
        combobox.addItems(self.resolutions)
        if self.default_resolution in self.resolutions:
            combobox.setCurrentIndex(self.resolutions.index(self.default_resolution))

        layout.addWidget(combobox)

        apply_button = QPushButton(self.tm.get_inline_string("apply"))
        apply_button.clicked.connect(lambda: save_default_resolution())

        def save_default_resolution():
            self.default_resolution = combobox.currentText()
            self.update_config("DEFAULT", "default-resolution", self.default_resolution)
            dialog.accept()

        layout.addWidget(apply_button, 0, Qt.AlignCenter)

        dialog.setLayout(layout)

        dialog.setWindowTitle(self.tm.get_inline_string("default-res-title"))
        dialog.setFixedSize(300, 125)

        dialog.exec()

    def delete_exe_files(self, folder_path="appdata"):
        for filename in os.listdir(folder_path):
            if filename.endswith(".exe"):
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)

    def update_file_box(self):
        if mw.ui.format_selection.currentText() == "Mp4":
            mw.ui.resolution_selection.setEnabled(True)
            if self.default_resolution != None:
                if self.default_resolution in self.data.resolutions:
                    mw.ui.resolution_selection.setCurrentIndex(self.data.resolutions.index(self.default_resolution))
        else:
            mw.ui.resolution_selection.setEnabled(False)
            mw.ui.resolution_selection.setCurrentIndex(0)

    def create_ini(self):
        logger.info("Creating new configuration file")
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"download_path": "~/Downloads/",
                            "ffmpeg_path": "None",
                            "yt-dlp-installed": "False",
                            "yt-dlp-date": "False",
                            "check-for-updates": "True",
                            "max-download-threads": "1",
                            "thumbnail-streaming": "True",
                            "log-level": "info",
                            "default-resolution": "None",
                            "default-language": "English"}
        with open(Utils.get_abs_path("appdata/config.ini"), "w+") as file:
            config.write(file)

    def load_config(self):
        logger.info("Loading configuration file")
        config = configparser.ConfigParser()
        config.read(Utils.get_abs_path("appdata/config.ini"))
        self.ffmpeg = config["DEFAULT"]["ffmpeg_path"]
        self.file = config["DEFAULT"]["download_path"]
        expanded_path = os.path.expanduser(self.file)
        self.file = os.path.join(os.path.normpath(expanded_path), '').replace("\\", "/")
        self.update_config("DEFAULT", "download_path", self.file)
        self.yt_dlp_installed = config["DEFAULT"]["yt-dlp-installed"]
        self.first_use = config["DEFAULT"].getboolean("first-use-since-update", fallback=True)
        self.update_config_version(config)
        if self.first_use: self.show_changelog()
        if self.yt_dlp_installed == "False":
            self.user_info_no_yt_dlp()
        else:
            self.import_yt_dl()

    def user_info_no_yt_dlp(self):
        if self.yes_no_messagebox(self.tm.get_inline_string("yt-dlp-not-exists"), QMessageBox.Warning, "Warning", QMessageBox.Yes |QMessageBox.No):
            self.download_yt_dlp()
        else:
            mw.close()
            sys.exit()

    def import_yt_dl(self):
        logger.info("Importing yt-dlp")
        self.import_yt_dl_thread = ImportYTDLP()
        self.import_yt_dl_thread.finished.connect(lambda: [mw.ui.searching_button.setEnabled(True)])
        self.import_yt_dl_thread.result.connect(lambda e: self.user_info_no_yt_dlp() if not e else self.check_ffmpeg_installed())
        self.import_yt_dl_thread.start()

    def check_ffmpeg_installed(self):
        if not os.path.isfile(f"{self.ffmpeg}/ffmpeg.exe"):
            self.user_info_no_ffmpeg()

    def update_config_version(self, config):
        self.update_check = config["DEFAULT"].getboolean("check-for-updates", fallback=True)
        mw.ui.actionAutomatic_Update_Check.setChecked(self.update_check)
        self.update_config("DEFAULT", "check-for-updates", str(self.update_check))

        self.max_download_threads = int(config["DEFAULT"].get("max-download-threads", fallback=1))
        mw.threadpool.setMaxThreadCount(self.max_download_threads)
        self.update_config("DEFAULT", "max-download-threads", str(self.max_download_threads))

        self.stream_thumbnails = config["DEFAULT"].getboolean("thumbnail-streaming", fallback=True)
        mw.ui.actionShow_Thumbnails.setChecked(self.stream_thumbnails)
        self.update_config("DEFAULT", "thumbnail-streaming", str(self.stream_thumbnails))

        self.log_level = config["DEFAULT"].get("log-level", fallback="info")
        self.update_log_level(self.log_level)

        self.default_resolution = config["DEFAULT"].get("default-resolution", fallback=None)
        self.update_config("DEFAULT", "default-resolution", str(self.default_resolution))

        self.default_language = config["DEFAULT"].get("default-language", fallback="English")
        self.update_config("DEFAULT", "default-language", str(self.default_language))
        self.change_language(self.default_language, force=True)
        child = mw.findChild(QAction, self.default_language)
        child.setChecked(True)

    def update_log_level(self, level):
        self.update_config("DEFAULT", "log-level", level)
        if level == "debug":
            logger_object.set_log_level(logging.DEBUG)
            mw.ui.actionLog_Level_Debug.setChecked(True)
        else:
            logger_object.set_log_level(logging.INFO)
            mw.ui.actionLog_Level_Info.setChecked(True)

    def update_config(self, section, key, new_val):
        logger.debug("Updating configuration file")
        config = configparser.ConfigParser()
        config.read(Utils.get_abs_path("appdata/config.ini"))
        config[section][key] = str(new_val)
        with open(Utils.get_abs_path("appdata/config.ini"), "w") as file:
            config.write(file)

    def show_changelog(self):
        self.update_config("DEFAULT", "first-use-since-update", "False")
        changelog_file = CHANGELOG_FILES.get(self.default_language, "changelog_en.md")
        text = open(f"appdata/changelogs/{changelog_file}", "r", encoding="utf-8").read()

        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(text)

        text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        text_browser.setMinimumSize(600, 300)

        msg_box = QMessageBox(mw)
        msg_box.setWindowTitle(self.tm.get_inline_string("changelog-dialog-title").format(VERSION))
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.setEscapeButton(QMessageBox.Ok)
        msg_box.setText(self.tm.get_inline_string("changelog-dialog-text").format(VERSION))
        msg_box.layout().addWidget(text_browser, 1, 0, 1, msg_box.layout().columnCount())
        msg_box.exec()

    def yt_search(self, text, pl_items, req):
        logger.info("Started YouTube search")
        opts = {"quiet": True,
                "noprogress": True,
                "playlist_items": pl_items,
                "logger": noLogger,
                "skip_download": True,
                "extract_flat": True,
                "list_thumbnails": True}
        try:
            ydl = YoutubeDL(opts)
            vid = ydl.extract_info(f"ytsearch{req}:{text}")["entries"]
            logger.info("Succesfully ended YouTube search")
            return vid
        except DownloadError as e:
            if "urlopen error" in e.msg:
                logger.error("Internet connection error")
                return "Connection Error"
            else:
                logger.error(f"An unknown error occurred: {e.msg}")
        except Exception as e:
            logger.error(f"An unknown error occurred: {e}")

    def use_info(self, info, cur_link):
        self.loading = False
        if not info:
            info = {}
        if info != {} and info["webpage_url_domain"] != None and info["webpage_url_domain"] == "youtube.com" and info["channel"] != None and info != False:
            self.cur_link = cur_link
            if "?list=" in cur_link and ("&list=" not in cur_link and "?v=" not in cur_link):
                self.playlist = True
            else:
                self.playlist = False
            self.data = DataHandler(self.cur_link, info, self.playlist)
            self.update_main_frame()
        else:
            if info == {} or info["webpage_url_domain"] == None:
                self.search_thread.start()
                text = self.tm.get_inline_string("searching-text")
            else:
                text = self.tm.get_inline_string("no-video-found")
            mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, text))
            mw.invokeFunc(mw.ui.download_btn, "setEnabled", Qt.QueuedConnection, Q_ARG(bool, False))
        self.info_thread = None

    def load_url(self, cur_link = None):
        if not cur_link:
            mw.invokeFunc(mw.ui.search_stack_widg, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 0))
        mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, self.tm.get_inline_string("searching-text")))
        if cur_link==None: cur_link = mw.ui.url_entry.text()
        if cur_link == "":
            mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, ""))
            mw.invokeFunc(mw.ui.searching_button, "setDisabled", Qt.QueuedConnection, Q_ARG(bool, False))
            return

        self.search_thread = YoutubeSearch(cur_link,"0:30", 30, self)
        self.search_thread.result.connect(self.store_result)

        if "&list=" in cur_link and "?v=" in cur_link:
            cur_link = cur_link.split("&list=")[0]
        if self.loading: return
        self.loading = True
        self.info_thread = LoadVideo(cur_link, self)
        self.info_thread.finished.connect(self.use_info)
        self.info_thread.start()

    def store_result(self, data):
        logger.info("Searching finished, received data")
        self.search_thread = None
        self.search = 30
        while len(mw.search_labels) > 0:
            mw.search_labels.pop().deleteLater()
        mw.create_search_widges()
        mw.invokeFunc(mw.ui.scrollArea.verticalScrollBar(), "setValue", Qt.QueuedConnection, Q_ARG(int, 0))
        if data == []:
            mw.ui.searching_button.setEnabled(True)
            mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, self.tm.get_inline_string("no-video-found2")))
            return
        self.fill_widget_thread = FillWidgetThread(data)
        self.fill_widget_thread.finished.connect(lambda: mw.ui.searching_button.setEnabled(True))
        self.fill_widget_thread.start()
        mw.invokeFunc(mw.ui.search_stack_widg, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 1))

    def custom_event(self, event, url, channel, title):
        if event.button() == Qt.LeftButton:
            self.load_url(url)
        elif event.button() == Qt.RightButton:
            self.yes_no_messagebox(f"""<p style="font-weight: bold;">{self.tm.get_inline_string("uploader2")}:</p> {channel}
                                    <p style="font-weight: bold;">{self.tm.get_inline_string("title2")}:</p> {title}
                                    <p style="font-weight: bold;">URL:</p>
                                    <a style="color: white; font-weight: bold;" href='{url}'>{url}</a>""", QMessageBox.Information, "Video", QMessageBox.Ok)

    def fill_new_widgs(self):
        if self.new_widget_thread_running or not self.search_activated: return
        if mw.ui.scrollArea.verticalScrollBar().value() == mw.ui.scrollArea.verticalScrollBar().maximum():
            mw.ui.searching_button.setEnabled(False)
            mw.create_search_widges(True)
            self.fill_new_widgs_thread = FillWidgetThread()
            self.fill_new_widgs_thread.finished.connect(lambda: mw.ui.searching_button.setEnabled(True))
            self.fill_new_widgs_thread.start()
        else:
            return

    def get_video_information(self, url, all_playlist = False):
        logger.info(f"Getting video information")
        yt_dlp_opts = {"quiet": True,
                        "noprogress": True,
                        "logger": noLogger,
                        "extract_flat": "in_playlist"
        }
        if not all_playlist: yt_dlp_opts["playlist_items"] = "0"
        ydl = YoutubeDL(yt_dlp_opts)
        try:
            inf = ydl.extract_info(url, False)
            info = ydl.sanitize_info(inf)
        except DownloadError as e:
            info = None
            if "urlopen error" in e.msg:
                logger.error("Internet connection error")
                info = False
            elif "ytsearch" in e.msg:
                pass
            else:
                logger.error(f"An unknown error occurred: {e}")
        except Exception as e:
            if e.__class__.__name__ == "NoSupportingHandlers":
                info = None
                logger.error(f"NoSupportingHandlerError occured")
            else:
                logger.error(f"An unknown error occurred: {e}")
        self.info  = info
        return info

    def update_main_frame(self):
        mw.ui.download_btn.setEnabled(True)
        mw.ui.download_btn.click()
        mw.ui.searching_button.setEnabled(True)
        mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, ""))
        mw.ui.image_label.clear()
        if self.stream_thumbnails:
            img = QImage()
            img.loadFromData(self.data.image_byt)
            pixmap = QPixmap.fromImage(img.scaled(480, 360))
            mw.ui.image_label.setPixmap(pixmap)
        else:
            mw.ui.image_label.setText("")
        mw.ui.name_label.setText(self.tm.get_inline_string("title").format(self.data.title))
        mw.ui.artist_label.setText(self.tm.get_inline_string("uploader").format(self.data.uploader))
        mw.ui.format_selection.clear()
        mw.ui.resolution_selection.clear()
        mw.ui.format_selection.addItems(self.file_formats)
        mw.ui.resolution_selection.addItems(self.data.resolutions)
        if self.default_resolution != None:
            if self.default_resolution in self.data.resolutions:
                mw.ui.resolution_selection.setCurrentIndex(self.data.resolutions.index(self.default_resolution))
        if not self.playlist:
            mw.ui.date_label.setText(self.tm.get_inline_string("upload-date").format(self.data.upload_date))
            mw.ui.duration_label.setText(self.tm.get_inline_string("video-length").format(self.data.duration))
            mw.invokeFunc(mw.ui.last_page_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
        else:
            mw.ui.duration_label.clear()
            mw.invokeFunc(mw.ui.download_2, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 1))
            mw.invokeFunc(mw.ui.info_range_slider_label, "setText", Qt.QueuedConnection, Q_ARG(str, self.tm.get_inline_string("select-range-info")))
            mw.ui.date_label.setText(self.tm.get_inline_string("playlist-count").format(self.data.playlist_count))
            mw.ui.last_page_btn.setVisible(True)
            mw.invokeFunc2(mw, "setWidg2Range", Qt.QueuedConnection, Q_ARG(int, 1), Q_ARG(int, self.data.playlist_count))
            mw.invokeFunc2(mw, "setWidg2Value", Qt.QueuedConnection, Q_ARG(int, 1), Q_ARG(int, self.data.playlist_count))

    def change_location(self):
        new_dir = QFileDialog.getExistingDirectory(None, self.tm.get_inline_string("select-folder"), os.path.expanduser(self.file))
        if new_dir == "":
            return
        self.file = f"{new_dir}/"
        self.update_config("DEFAULT", "download_path", self.file)

    def change_ffmpeg_location(self):
        new_dir = QFileDialog.getExistingDirectory(None, self.tm.get_inline_string("select-ffmpeg-bin"), os.path.expanduser(self.ffmpeg))
        if new_dir == "":
            return
        if not os.path.isfile(f"{new_dir}/ffmpeg.exe"):
            self.yes_no_messagebox(self.tm.get_inline_string("no-valid-path"), QMessageBox.Warning, "Warning", QMessageBox.Ok)
            self.change_ffmpeg_location()
            return
        self.ffmpeg = f"{new_dir}/"
        self.update_config("DEFAULT", "ffmpeg_path", self.ffmpeg)

    def show_in_explorer(self):
        f = os.path.expanduser(self.file).replace('/', '\\')
        command = f"explorer.exe {f}"
        os.popen(command)

    def yes_no_messagebox(self, text, icon, title, options, hide = True):
        qms = QMessageBox(icon, title, text, options, mw)
        qms.setModal(True)
        if hide:
            qms.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        for option in options:
            btn = qms.button(option)
            btn.setText(self.tm.get_inline_string(str(option)))

        return qms.exec() == QMessageBox.Yes


    def user_info_no_ffmpeg(self):
        msg_box = QMessageBox(mw)
        msg_box.setText(self.tm.get_inline_string("missing-ffmpeg-path"))
        msg_box.setWindowTitle(self.tm.get_inline_string("error"))

        msg_box.layout().setContentsMargins(10, 0, 0, 10)

        install = QPushButton(self.tm.get_inline_string("install-ffmpeg"))
        msg_box.addButton(install, QMessageBox.ActionRole)
        set = QPushButton(self.tm.get_inline_string("set-ffmpeg-path"))
        msg_box.addButton(set, QMessageBox.ActionRole)
        ignore = QPushButton(self.tm.get_inline_string("ok"))
        msg_box.addButton(ignore, QMessageBox.ActionRole)

        msg_box.setStyleSheet("QPushButton{margin-right: 8px;}")
        msg_box.layout().setAlignment(Qt.AlignmentFlag.AlignHCenter)

        res = msg_box.exec()
        if res == 0:
            self.download_ffmpeg()
        elif res == 1:
            self.change_ffmpeg_location()

    def handle_update_available(self, update_available, tag, auto):
        self.update_thread = None
        if update_available:
            msg_box = QMessageBox(mw)
            msg_box.setText(self.tm.get_inline_string("update-available").format(VERSION, tag))
            msg_box.setWindowTitle("Update found")
            msg_box.setIcon(QMessageBox.Information)
            download_and_install = QPushButton(self.tm.get_inline_string("install-update"))
            msg_box.addButton(download_and_install, QMessageBox.ActionRole)

            skip = QPushButton(self.tm.get_inline_string("skip-update"))
            msg_box.addButton(skip, QMessageBox.ActionRole)
            res = msg_box.exec()
            if res == 0: self.update_self(tag)
        elif not update_available and tag == "no_connection":
            self.yes_no_messagebox(self.tm.get_inline_string("error-no-internet"), QMessageBox.Warning, self.tm.get_inline_string("no-internet"), QMessageBox.Ok)
        elif not update_available and not auto:
            self.yes_no_messagebox(self.tm.get_inline_string("no-update-found"), QMessageBox.Information, self.tm.get_inline_string("no-update-found"), QMessageBox.Ok)

    def search_for_updates(self, auto = True):
        if self.update_thread != None:
            return
        logger.info("Started searching for updates")
        self.update_thread = UpdateThread(auto)
        self.update_thread.update_available.connect(self.handle_update_available)
        self.update_thread.start()

    def show_on_github(self):
        os.popen("start https://github.com/PyFlat/YT-Downloader")

    def update_self(self, tag):
        logger.info("Update download started")
        self.self_download_thread = GithubDownloader(f"https://github.com/PyFlat-Studios-JR/YT-Downloader/releases/latest/download/win_installer_v{tag}.exe", f"appdata/win_installer_v{tag}.exe")
        self.self_download_thread.progress.connect(self.update_progress_self)
        self.self_download_thread.finished.connect(lambda success: self.download_finished_self(success, tag))

        self.self_download_progress_dialog = ProgressDialog(self.tm.get_inline_string("update"), mw, dl)
        self.self_download_progress_dialog.show()

        self.self_download_thread.start()

    def update_progress_self(self, progress):
        if progress < 0:
            self.self_download_progress_dialog.close()
            logger.error("Internet connection error")
            self.yes_no_messagebox(self.tm.get_inline_string("error-no-internet"), QMessageBox.Warning, self.tm.get_inline_string("no-internet"), QMessageBox.Ok)
        if self.self_download_progress_dialog:
            self.self_download_progress_dialog.update_progress(progress)

    def download_finished_self(self, success, tag):
        self.self_download_progress_dialog.close()
        self.self_download_progress_dialog = None
        if not success:
            logger.warning("Update download failed")
            self.yes_no_messagebox(self.tm.get_inline_string("download-failed"), QMessageBox.Warning, self.tm.get_inline_string("download-failed"), QMessageBox.Ok)
            return
        if self.yes_no_messagebox(self.tm.get_inline_string("download-finished"), QMessageBox.Question, " ", QMessageBox.Yes | QMessageBox.No):
            logger.info("Update download finished, updating now")
            os.popen(f"start appdata/win_installer_v{tag}.exe")
            mw.close()
            sys.exit(0)

    def download_yt_dlp(self):
        logger.info("Download yt-dlp started")
        self.yt_dlp_download_thread = GithubDownloader("https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt-dlp", "appdata/yt_dlp")
        self.yt_dlp_download_thread.progress.connect(self.update_progress_yt_dlp)
        self.yt_dlp_download_thread.finished.connect(self.download_finished_yt_dlp)

        self.yt_dlp_progress_dialog = ProgressDialog("yt-dlp", mw, dl)
        self.yt_dlp_progress_dialog.show()

        self.yt_dlp_download_thread.start()

    def update_progress_yt_dlp(self, progress):
        if progress < 0:
            self.yt_dlp_progress_dialog.close()
            logger.error("Internet connection error")
            self.yes_no_messagebox(self.tm.get_inline_string("error-no-internet"), QMessageBox.Warning, self.tm.get_inline_string("no-internet"), QMessageBox.Ok)
        if self.yt_dlp_progress_dialog:
            self.yt_dlp_progress_dialog.update_progress(progress)

    def download_finished_yt_dlp(self, success):
        self.yt_dlp_progress_dialog.close()
        self.yt_dlp_progress_dialog = None
        if not success:
            logger.warning("yt-dlp download failed")
            self.yes_no_messagebox(self.tm.get_inline_string("download-failed"), QMessageBox.Warning, self.tm.get_inline_string("download-failed"), QMessageBox.Ok)
            return
        logger.info("yt-dlp download and installation finished")
        self.update_config("DEFAULT", "yt-dlp-installed", "True")
        self.update_config("DEFAULT", "yt-dlp-date", str(datetime.datetime.now()))
        self.yes_no_messagebox(self.tm.get_inline_string("installation-finished").format("yt-dlp"), QMessageBox.Information, self.tm.get_inline_string("info"), QMessageBox.Ok)
        self.import_yt_dl()

    def download_ffmpeg(self):
        logger.info("Download FFmpeg started")
        if os.path.isdir("appdata/FFmpeg"):
            shutil.rmtree("appdata/FFmpeg")
        self.ffmpeg_download_thread = GithubDownloader("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip", "appdata/ffmpeg.zip")
        self.ffmpeg_download_thread.progress.connect(self.update_progress_ffmpeg)
        self.ffmpeg_download_thread.finished.connect(self.download_finished_ffmpeg)

        self.ffmpeg_progress_dialog = ProgressDialog("ffmpeg", mw, dl)
        self.ffmpeg_progress_dialog.show()

        self.ffmpeg_download_thread.start()

    def update_progress_ffmpeg(self, progress):
        if progress < 0:
            self.ffmpeg_progress_dialog.close()
            logger.error("Internet connection error")
            self.yes_no_messagebox(self.tm.get_inline_string("error-no-internet"), QMessageBox.Warning, self.tm.get_inline_string("no-internet"), QMessageBox.Ok)
        if self.ffmpeg_progress_dialog:
            self.ffmpeg_progress_dialog.update_progress(progress)

    def download_finished_ffmpeg(self, success):
        if not success:
            logger.warning("FFmpeg download failed")
            self.ffmpeg_progress_dialog.close()
            self.ffmpeg_progress_dialog = None
            self.yes_no_messagebox(self.tm.get_inline_string("download-failed"), QMessageBox.Warning, self.tm.get_inline_string("download-failed"), QMessageBox.Ok)
            return
        logger.info("FFmpeg download finished, starting installation")
        zp = ZipFile("appdata/ffmpeg.zip")
        names_foo = [i for i in zp.namelist() if i.startswith("ffmpeg-master-latest-win64-gpl/")]
        for file in names_foo:
            zp.extract(file)
        zp.close()
        os.rename("ffmpeg-master-latest-win64-gpl", "appdata/FFmpeg")
        os.remove("appdata/ffmpeg.zip")
        self.ffmpeg_progress_dialog.close()
        self.ffmpeg_progress_dialog = None
        self.yes_no_messagebox(self.tm.get_inline_string("installation-finished").format("ffmpeg"), QMessageBox.Information, self.tm.get_inline_string("info"), QMessageBox.Ok)
        self.ffmpeg = Utils.get_abs_path("appdata/FFmpeg/bin")
        self.update_config("DEFAULT", "ffmpeg_path", self.ffmpeg)
        logger.info("FFmpeg installation finished")

    def add_row(self, row_count, data):
        mw.ui.tableWidget.insertRow(row_count)
        for column, string in enumerate(data):
            item = QTableWidgetItem(str(string))
            item.setTextAlignment(Qt.AlignCenter)
            mw.ui.tableWidget.setItem(row_count, column, item)

    def handle_clicked(self, row, column):
        selection_model = mw.ui.tableWidget.selectionModel()
        selection_model.clearSelection()
        mw.set_enabled(False, False, False, False)
        index = mw.ui.tableWidget.model().index(row, 0)
        selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        try:
            mw.ui.download_delete_btn.disconnect(self.delete_btn_connection)
            mw.ui.download_open_btn.disconnect(self.play_file_btn_connection)
            mw.ui.download_cancel_btn.disconnect(self.cancel_btn_connection)
            mw.ui.download_download_btn.disconnect(self.re_download_file_btn_connection)
        except AttributeError:
            pass
        status = mw.ui.tableWidget.item(row, 4).text()
        if not os.path.isfile(self.downloads[row].filename) and status == self.tm.get_inline_string("finished"):
            item = QTableWidgetItem(self.tm.get_inline_string("deleted"))
            item.setTextAlignment(Qt.AlignCenter)
            mw.ui.tableWidget.setItem(row, 4, item)
            status = self.tm.get_inline_string("deleted")

        if status == self.tm.get_inline_string("finished"):
            mw.set_enabled(True, True, True, False)
        elif status == self.tm.get_inline_string("deleted") or status == self.tm.get_inline_string("download-failed"):
            mw.set_enabled(False, False, True, False)
        else:
            mw.set_enabled(False, False, False, True)

        self.delete_btn_connection = mw.ui.download_delete_btn.clicked.connect(lambda ev: self.downloads[row].delete(row))
        self.play_file_btn_connection = mw.ui.download_open_btn.clicked.connect(lambda ev: self.downloads[row].play())
        self.cancel_btn_connection = mw.ui.download_cancel_btn.clicked.connect(lambda ev: self.downloads[row].cancel())
        ext = mw.ui.tableWidget.item(row, 2).text().lower()
        res = mw.ui.tableWidget.item(row, 3).text()
        self.re_download_file_btn_connection = mw.ui.download_download_btn.clicked.connect(lambda ev: self.downloads[row].prepare_for_download(ext, res, row))

class DataHandler():
    def __init__(self, url, info, playlist = False, skip=False):
        self.playlist = playlist
        self.url = url
        self.title = str(info["title"])
        self.uploader = info["channel"]
        self.author = info["channel"]
        self.info = info
        self.file_name_threads = []

        if skip:return
        if dl.stream_thumbnails:
            self.thumbnail_url = self.get_thumbnail_url()
            self.image_byt = urlopen(self.thumbnail_url,timeout=15).read()
        if self.playlist:
            self.playlist_count = info["playlist_count"]
            mw.ui.download_button.setDisabled(True)
            self.resolutions = dl.resolutions
            self.playlist_url_thread = LoadPlaylistURLS(info["webpage_url"])
            self.playlist_url_thread.finished.connect(self.store_playlist_urls)
            self.playlist_url_thread.start()
        else:
            self.upload_date = datetime.datetime.strptime(info["upload_date"], "%Y%m%d").strftime("%d.%m.%Y")
            minutes, seconds = divmod(info["duration"], 60)
            hours, minutes = divmod(minutes, 60)
            self.duration = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.resolutions = self.get_available_resolutions()

    def store_playlist_urls(self, data):
        self.playlist_data_await = True
        self.playlist_data_objects = [None]*len(data["entries"])
        for i, entrie in enumerate(data["entries"]):
            self.create_data_objects(entrie["url"], entrie, i)
        self.playlist_data_await = False

    def create_data_objects(self, url, info, index):
        x = DataHandler(url, info, skip=True)
        self.playlist_data_objects[index] = x
        if not None in self.playlist_data_objects:
            mw.ui.download_button.setEnabled(True)
            mw.ui.select_videos_btn.setEnabled(True)

    def get_thumbnail_url(self):
        x = []
        for thumbnail in self.info["thumbnails"]:
            if "resolution" in thumbnail:
                if int(thumbnail["width"]) >= 300 and int(thumbnail["width"]) <= 640:
                    x.append(thumbnail["url"])
        return x[-1]

    def get_available_resolutions(self):
        resolution = []
        for stream in self.info["formats"]:
            if stream["video_ext"] != "none":
                stre = f"{stream['resolution'].split('x')[1]}p"
                if stre not in resolution:
                    resolution.append(stre)
        resolution = sorted(resolution, key=lambda s: int(re.compile(r'\d+').search(s).group()), reverse=True)
        resolution.insert(0, dl.tm.get_inline_string("best-quality"))
        return resolution

    def prepare_for_download(self, vid_ext, vid_res, row = None):
        mw.set_enabled(False, False, False)
        self.vid_ext = vid_ext
        self.vid_res = vid_res
        self.vid_res = dl.tm.get_inline_string("best-quality") if self.vid_res == "" else self.vid_res

        if self.playlist: self.download_playlist();return

        temp_vid_res = self.vid_res.split("p")[0]
        if ((temp_vid_res != dl.tm.get_inline_string("best-quality")) and (self.vid_ext != "mp3")) and not self.playlist:
            self.download_format = f"bv[height<={temp_vid_res}]+ba[ext=m4a]/b"
        else:
            self.download_format = "bv*+ba[ext=m4a]/b"
        if self.vid_ext  == "mp4":
            self.outtmpl = f"{dl.file}{self.title}(%(height)sp).%(ext)s"
        else:
            self.outtmpl = f"{dl.file}{self.title}.%(ext)s"
        if not os.path.isfile(dl.ffmpeg + "/ffmpeg.exe"):
            dl.user_info_no_ffmpeg()
            return

        currently_processing = [self.vid_ext, temp_vid_res, self.url]
        if currently_processing in dl.cur_process:
            dl.yes_no_messagebox(dl.tm.get_inline_string("no-same-files"), QMessageBox.Warning, dl.tm.get_inline_string("warning"), QMessageBox.Ok)
            return

        self.process = currently_processing
        dl.cur_process.append(currently_processing)
        if row != None:
            self.download(row)
            return
        file_name_thread = FileNameThread(self.outtmpl, self.download_format, self.url, self.vid_ext, dl.file)
        file_name_thread.ret_filename.connect(lambda x: self.check_if_exists(x))
        file_name_thread.start()
        self.file_name_threads.append(file_name_thread)

    def check_if_exists(self, filename):
        if filename == "Connection Error":
            logger.error("Internet connection error")
            dl.yes_no_messagebox(dl.tm.get_inline_string("error-no-internet"), QMessageBox.Warning, dl.tm.get_inline_string("no-internet"), QMessageBox.Ok)
            dl.cur_process.remove(self.process)
            return
        if os.path.isfile(filename):
            if not dl.yes_no_messagebox(dl.tm.get_inline_string("file-already-exists"), QMessageBox.Warning, dl.tm.get_inline_string("warning"), QMessageBox.Yes | QMessageBox.No):
                dl.cur_process.remove(self.process)
                return
        if filename[-3:] == "mp4":
            self.vid_res = filename.split("(")[-1].split(")")[0]
        else:
            self.vid_res = ""
        self.filename = filename
        for i, download in enumerate(dl.downloads):
            if download.filename == self.filename:
                download.download(i)
                return
        self.download()

    def download_playlist(self):
        if dl.selected_ids  == []:
            dl.yes_no_messagebox(dl.tm.get_inline_string("no-video-chosen"), QMessageBox.Warning, dl.tm.get_inline_string("warning"), QMessageBox.Ok)
            return
        def download_next(index):
            if index < len(dl.selected_ids):
                video_id = dl.selected_ids[index]-1
                self.playlist_data_objects[video_id].prepare_for_download()
                QTimer.singleShot(1000, lambda: download_next(index + 1))

        download_next(0)

    def download(self, row=None):
        if row == None:
            data = [self.author, self.title, self.vid_ext.upper(), self.vid_res, dl.tm.get_inline_string("started"), ""]
            row_count = mw.ui.tableWidget.rowCount()
            dl.add_row(row_count, data)
        else:
            item  = QTableWidgetItem(dl.tm.get_inline_string("started"))
            item.setTextAlignment(Qt.AlignCenter)
            mw.ui.tableWidget.setItem(row, 4, item)
            row_count = row

        dl_thread = VideoDownloadThread(self.url, self.download_format, self.vid_ext, dl.ffmpeg, self.filename, row_count)
        dl_thread.finished.connect(self.handle_download_finished)
        dl_thread.progress.connect(self.update_progress)
        self.x = dl_thread
        thread_worker = ThreadWorker(dl_thread)
        mw.threadpool.start(thread_worker)
        if row == None: dl.downloads.append(self)

    def handle_download_finished(self, success, row):
        if mw.ui.tableWidget.item(row, 0).isSelected():
            mw.set_enabled(True, True, True)
        dl.cur_process.remove(dl.downloads[row].process)

        if success:
            item  = QTableWidgetItem(dl.tm.get_inline_string("finished"))
            item.setTextAlignment(Qt.AlignCenter)
            mw.ui.tableWidget.setItem(row, 4, item)
            logger.info("Video download finished successfully")
        else:
            item  = QTableWidgetItem(dl.tm.get_inline_string("download-failed"))
            item.setTextAlignment(Qt.AlignCenter)
            mw.ui.tableWidget.setItem(row, 4, item)
            logger.warning("Video download failed")

    def update_progress(self, progress, row, eta):
        item  = QTableWidgetItem(progress)
        item.setTextAlignment(Qt.AlignCenter)
        mw.ui.tableWidget.setItem(row, 4, item)
        if dl.tm.get_inline_string("unknown") in eta: return
        item2 = QTableWidgetItem(eta)
        item2.setTextAlignment(Qt.AlignCenter)
        mw.ui.tableWidget.setItem(row, 5, item2)

    def delete(self, row):
        mw.set_enabled(False, False, False)
        if not dl.yes_no_messagebox(dl.tm.get_inline_string("delete-file"), QMessageBox.Question, dl.tm.get_inline_string("question"), QMessageBox.Yes | QMessageBox.No):return
        item  = QTableWidgetItem(dl.tm.get_inline_string("deleted"))
        item.setTextAlignment(Qt.AlignCenter)
        mw.ui.tableWidget.setItem(row, 4, item)
        if os.path.isfile(self.filename):
            logger.info("Deleting file")
            logger.debug(f"Filename: \"{self.filename}\"")

            os.remove(self.filename)

    def cancel(self):
        self.x.cancel()

    def play(self):
        mw.set_enabled(False, False, False)
        logger.info(f"Opening file with cmd, file-extension: {self.vid_ext}")
        logger.debug(f"Filename: \"{self.filename}\"")
        os.popen(f"\"{self.filename}\"")

class FileNameThread(QThread):
    ret_filename = Signal(str)
    def __init__(self, template, download_format, url, ext, file):
        super().__init__()
        self.template = template
        self.file = file.replace("/", "\\")
        self.download_format = download_format
        self.url = url
        self.ext = ext
    def run(self):
        ydl_opts = {
            'quiet': True,
            'simulate': True,
            "forcefilename": True,
            'outtmpl': self.template,
            'format': self.download_format,
            'merge_output_format': self.ext,
        }
        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(self.url, download=False)
                filename = ydl.prepare_filename(info, warn = True)
                filename = filename.split(self.file)[1]
                compat_filename = re.sub(r'[\\/:"*?<>|&]+', '#', filename)
                self.ret_filename.emit(self.file + compat_filename)
            except DownloadError as e:
                if "urlopen error" in e.msg:
                    self.ret_filename.emit("Connection Error")

class CreatePlaylistData(QThread):
    def __init__(self, info):
        super().__init__()
        self.info = info
    def run(self):
        self.playlist_urls = []
        for entrie in self.info["entries"]:
            x = dl.get_video_information(entrie["url"])
            y = DataHandler(entrie["url"], x, False)

class FillWidgetThread(QThread):
    finished = Signal(bool)
    def __init__(self, data=None):
        super().__init__()
        self.data = data

    def run(self):
        if self.data == "Connection Error":
            mw.invokeFunc(mw.ui.search_stack_widg, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 0))
            mw.ui.info_start_label.setText(dl.tm.get_inline_string("error-no-internet"))
            mw.ui.searching_button.setEnabled(True)
            return

        new_widgs = not bool(self.data)

        if new_widgs:
            dl.new_widget_thread_running = True
            cur_link = mw.ui.url_entry.text()
            self.data = dl.yt_search(cur_link, f"{dl.search+1}:{dl.search+30}", dl.search + 30)

            if self.data == "Connection Error":
                mw.search_labels = mw.search_labels[:dl.search]
                mw.invokeFunc(mw.ui.search_stack_widg, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 0))
                mw.ui.info_start_label.setText(dl.tm.get_inline_string("error-no-internet"))
                mw.ui.searching_button.setEnabled(True)
                dl.new_widget_thread_running = False
                return

        search_len = len(self.data)
        remaining_labels = len(mw.search_labels[search_len:])

        dl.search_activated = not (search_len % 30)

        if search_len % 30:
            if new_widgs:
                for _ in range(30 - search_len % 30):
                    mw.search_labels.pop().deleteLater()
            else:
                for _ in range(remaining_labels):
                    mw.search_labels.pop().deleteLater()

        for i, entry in enumerate(self.data, dl.search if new_widgs else 0):
            mw.search_labels[i].mousePressEvent = lambda ev, x=entry["url"], y=entry["channel"], z=entry["title"]: dl.custom_event(ev, x, y, z)
            if dl.stream_thumbnails:
                thumbnail_url = entry['thumbnails'][0]['url']
                if entry["thumbnails"][0]["height"] >= entry["thumbnails"][0]["width"]:
                    thumbnail_url = f"{thumbnail_url.replace('vi_webp', 'vi').rsplit('/',1)[0]}/mqdefault.jpg"
                try:
                    image_byt = urlopen(thumbnail_url, timeout=15).read()
                except Exception:
                    mw.invokeFunc(mw.ui.search_stack_widg, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 0))
                    mw.ui.info_start_label.setText(dl.tm.get_inline_string("error-no-internet"))
                    mw.ui.searching_button.setEnabled(True)
                    return

                img = QImage.fromData(image_byt)
                pixmap = QPixmap.fromImage(img.scaled(325, 183))
                mw.search_labels[i].setPixmap(pixmap)
            else:
                if len(entry["title"])>15:
                    mw.search_labels[i].setText(f"{entry['title'][:15]}...")
                else:
                    mw.search_labels[i].setText(entry["title"])

        if new_widgs:
            dl.search += search_len
            dl.new_widget_thread_running = False
        self.finished.emit(True)

class GithubDownloader(QThread):
    progress = Signal(float)
    finished = Signal(bool)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        logger.info(f"Download started for {self.url}")
        self.progress.emit(0)
        try:
            response = requests.get(self.url, stream=True, timeout=15)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(self.save_path, 'wb') as file:
                for data in response.iter_content(chunk_size=4096):
                    file.write(data)
                    downloaded_size += len(data)
                    progress = downloaded_size / total_size * 100
                    self.progress.emit(progress)
            logger.info(f"Download of {self.url} finished")
            self.finished.emit(True if progress == 100.0 else False)

        except requests.exceptions.ConnectionError:
            logger.error(f"Internet connection error when trying to download {self.url}")
            self.progress.emit(-1.0)
            self.finished.emit(False)

class LoadPlaylistURLS(QThread):
    finished = Signal(dict)
    def __init__(self, url:str):
        super().__init__()
        self.url = url
    def run(self):
        result = dl.get_video_information(self.url, True)
        if result != None:
            self.finished.emit(result)

class LoadVideo(QThread):
    finished = Signal(dict, str)
    def __init__(self, url:str, dl):
        super().__init__()
        self.url = url
        self.dl = dl
    def run(self):
        result = self.dl.get_video_information(self.url)
        self.finished.emit(result, self.url)

class ThreadWorker(QRunnable):
    def __init__(self, thread):
        super().__init__()
        self.thread = thread

    def run(self):
        self.thread.run()

class UpdateThread(QThread):
    update_available = Signal(bool, str, bool)
    def __init__(self, auto):
        super().__init__()
        self.auto = auto
    def run(self):
        from main import VERSION
        try:
            f = urlopen("https://github.com/PyFlat/YT-Downloader/releases/latest").url
        except URLError:
            logger.error("Internet connection error")
            self.update_available.emit(None, "no_connection", None)
            return
        tag = f.split("/")[-1]
        if VERSION < tag[1:]:
            self.update_available.emit(True, tag[1:], self.auto)
        else:
            self.update_available.emit(False, "", self.auto)

class VideoDownloadThread(QThread):
    finished = Signal(bool, int)
    progress = Signal(str, int, str)

    def __init__(self, url:str, format:str, ext:str, ffmpeg:str, file_template:str, row:int):
        super().__init__()
        self.url = url
        self.format = format
        self.extension = ext
        self.ffmpeg = ffmpeg
        self.file_template = file_template
        self.update_eta = 0
        self.is_cancelled = False
        self.row = row

    def run(self):
        if self.extension == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "ffmpeg_location": self.ffmpeg,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
                "outtmpl": self.file_template[:-4],
                "quiet": True,
                "noprogress": True,
                'progress_hooks': [self._hook],
                "overwrites": True,
                "postprocessor_hooks": [self._hook_postprocess],
                "socket_timeout": 15,
                }
        else:
            ydl_opts = {
                "format": self.format,
                "ffmpeg_location": self.ffmpeg,
                "outtmpl": self.file_template,
                "merge_output_format": "mp4",
                "quiet": True,
                "noprogress": True,
                'progress_hooks': [self._hook],
                "concurrent_fragments": 2,
                "overwrites": True,
                "postprocessor_hooks": [self._hook_postprocess],
                "socket_timeout": 15,
                }
        try:
            logger.info(f"Video download started")
            logger.debug(f"Video url: {self.url}")
            YoutubeDL(ydl_opts).download(self.url)

        except DownloadError as e:
            if "urlopen error" in e.msg or "The read operation timed out" in e.msg:
                logger.error(f"A network error occured: {e.msg}")
                self.finished.emit(False, self.row)
            elif "Cancelled by user" in e.msg:
                logger.info("Download cancelled by user")
                self.finished.emit(False, self.row)
            else:
                logger.error(f"An unnokwn download error occured: {e.msg}")

        else:
            logger.info(f"Video downloaded successfully")
            self.finished.emit(True, self.row)

    def _hook(self, d):
        if self.is_cancelled:
            raise DownloadError("Cancelled by user")
        self.update_eta += 1
        if not (self.update_eta % 20 == 0):
            return
        if d['status'] == 'downloading':
            try:
                pr = int(round(round(float(d['downloaded_bytes'])/float(d["total_bytes"]),2)*100, 0))
            except KeyError:
                pr = int(round(round(float(d['downloaded_bytes'])/float(d["total_bytes_estimate"]),2)*100, 0))
            eta = int(round(float(d['eta']),ndigits=0)) if d["eta"] else dl.tm.get_inline_string("unknown")
            self.progress.emit(f"{pr}%", self.row, dl.tm.get_inline_string("1-second") if eta==1 else dl.tm.get_inline_string("seconds").format(eta))
        elif d["status"] == "finished":
            self.progress.emit("", self.row, "")

    def _hook_postprocess(self, d):
        if d["status"] == "started":
            self.progress.emit(dl.tm.get_inline_string("postp-started"), self.row, "")
        else:
            self.progress.emit(dl.tm.get_inline_string("postp-finished"), self.row, "")

    def cancel(self):
        self.is_cancelled = True

class YoutubeSearch(QThread):
    result = Signal(object)
    def __init__(self, url:str, range:str, amount:int, dl):
        super().__init__()
        self.url = url
        self.range = range
        self.amount = amount
        self.dl = dl
    def run(self):
        result = self.dl.yt_search(self.url,self.range, self.amount)
        self.result.emit(result)

class ImportYTDLP(QThread):
    result = Signal(bool)
    def __init__(self):
        super().__init__()
    def run(self):
        global YoutubeDL, DownloadError
        if Utils.get_abs_path("appdata/yt_dlp") in sys.path:
            sys.path.remove(Utils.get_abs_path("appdata/yt_dlp"))
        if os.path.isfile(Utils.get_abs_path("appdata/yt_dlp")):
            sys.path.insert(0, Utils.get_abs_path("appdata/yt_dlp"))
        try:
            from yt_dlp import YoutubeDL
            from yt_dlp.utils import DownloadError
            logger.info("Imported yt-dlp succesfully")
            self.result.emit(True)
        except ModuleNotFoundError as e:
            logger.error(f"An error occured, that yt-dlp doesn't exist. Probably it isn't downloaded! Error: {e}")
            self.result.emit(False)
        except Exception as e:
            logger.error(f"An unnokwn error occured when trying to import yt-dlp: {e}")
            self.result.emit(True)

class ScreenShot(QThread):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
    def run(self):
        if os.path.isfile(f"{dl.file}Rick Astley - Never Gonna Give You Up (Official Music Video)(1080p).mp4"):
            os.remove(f"{dl.file}Rick Astley - Never Gonna Give You Up (Official Music Video)(1080p).mp4")
        screenshot = mw.grab()
        screenshot.save('showcase/Startpage.png', 'png')


        mw.ui.url_entry.setText("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.msleep(3000)
        mw.ui.searching_button.click()

        self.msleep(5000)

        screenshot = mw.grab()
        screenshot.save('showcase/Download_Video.png', 'png')

        mw.ui.download_button.click()

        self.msleep(6000)

        mw.ui.file_btn.click()

        self.msleep(1000)

        screenshot = mw.grab()
        screenshot.save('showcase/Download_Overview.png', 'png')

        mw.ui.url_entry.setText("Rick Astley")
        mw.ui.searching_button.click()
        mw.ui.search_btn.click()
        self.msleep(5000)
        screenshot = mw.grab()
        screenshot.save("showcase/Search.png", "png")

        mw.ui.url_entry.setText("https://www.youtube.com/playlist?list=PL7oy-W4T92tJuncyNL2xk8F4PGzz0jvtb")
        mw.ui.searching_button.click()
        self.msleep(5000)
        screenshot = mw.grab()
        screenshot.save("showcase/Select_Playlist_Range.png", "png")

        mw.ui.select_videos_btn.click()
        self.msleep(1000)

        screenshot = dl.video_select_dialog.grab()
        screenshot.save("showcase/Select_Playlist_Precise.png", "png")

        mw.ui.next_page_btn.click()

        self.msleep(1000)

        screenshot = mw.grab()
        screenshot.save("showcase/Download_Playlist.png", "png")

def qt_message_handler(mode, context, message):
    if mode == QtMsgType.QtInfoMsg:
        mode = logging.INFO
    elif mode == QtMsgType.QtWarningMsg:
        mode = logging.WARNING
    elif mode == QtMsgType.QtCriticalMsg:
        mode = logging.CRITICAL
    elif mode == QtMsgType.QtFatalMsg:
        mode = logging.ERROR
    else:
        mode = logging.DEBUG
    logger.log(mode, message)


if __name__ == "__main__":
    app = QApplication([])
    qInstallMessageHandler(qt_message_handler)
    mw = MainWindow()
    dl = Downloader()
    mw.create_search_widges()
    # thread = ScreenShot(mw)
    # thread.start()
    sys.exit(app.exec())

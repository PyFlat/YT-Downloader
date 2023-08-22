import threading, datetime, os, configparser, sys, shutil, requests, re, copy

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from zipfile import ZipFile
from src.CustomWidgets.ProgressDialog import ProgressDialog
from src.Ui_MainWindow import Ui_MainWindow
from src.CustomWidgets.SLabel import SLabel

from urllib.request import urlopen
from urllib.error import URLError

VERSION = "1.2.1"

class Logger:
    def error(msg):
        pass
    def warning(msg):
        pass
    def debug(msg):
        pass

class Utils():
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
        self.ui.tableWidget.horizontalHeader().setVisible(True)

        self.setStyleSheet(open(Utils.get_abs_path("appdata/style.qss"), "r").read())
        
        
        self.ui.mainpages.setCurrentIndex(0)
        self.ui.search_stack_widg.setCurrentIndex(0)
        self.ui.download_2.setCurrentIndex(0)
        
        self.ui.tableWidget.focusOutEvent = self.on_focus_out
        
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(750)

        self.timer2 = QTimer()
        self.timer2.setSingleShot(True)

        self.bind_keys()

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(5)
        
        self.ui.search_btn.setChecked(True)
        
        self.create_search_widges()

        self.show()
    
    def on_focus_out(self, event):
        selection_model = self.ui.tableWidget.selectionModel()
        selection_model.clearSelection()
        event.accept()
        timer = QTimer()
        timer.singleShot(250, lambda: self.set_enabled(False, False, False))
        
    def set_enabled(self, enabled1:bool, enabled2:bool, enabled3:bool):
        self.ui.download_delete_btn.setEnabled(enabled1)
        self.ui.download_open_btn.setEnabled(enabled2)
        self.ui.download_download_btn.setEnabled(enabled3)
        
    def bind_keys(self):
        self.ui.search_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(0)])
        self.ui.download_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(1)])
        self.ui.file_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(2)])
        self.ui.settings_btn.clicked.connect(lambda: [self.ui.mainpages.setCurrentIndex(3)])
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
                label = SLabel(self.ui.url_entry, self.ui.scrollAreaWidgetContents)
                self.search_labels.append(label)
                self.ui.gridLayout_2.addWidget(label, self.column, i)
                self.ui.gridLayout_2.setAlignment(label, Qt.AlignTop | Qt.AlignLeft)
            self.column += 1

    def paintEvent(self, event: QPaintEvent):
        self.ui.scrollArea.setMinimumHeight(self.geometry().height()-175)
        return super().paintEvent(event)

class Downloader():
    def __init__(self):
        mw.timer.timeout.connect(lambda:[self.load_url(), mw.ui.url_entry.setEnabled(False)])
        mw.ui.url_entry.textChanged.connect(lambda:mw.timer.start())
        mw.ui.format_selection.currentIndexChanged.connect(lambda:self.update_file_box())
        mw.ui.download_button.clicked.connect(lambda: self.data.prepare_for_download())
        mw.ui.change_location_btn.clicked.connect(lambda: self.change_location())
        mw.ui.show_folder_btn.clicked.connect(lambda: self.show_in_explorer())
        mw.ui.download_ffmpeg_btn.clicked.connect(lambda:self.download_ffmpeg())
        mw.ui.change_ffmpeg_path_btn.clicked.connect(lambda: self.change_ffmpeg_location())
        mw.ui.next_page_btn.clicked.connect(lambda: mw.ui.download_2.setCurrentIndex(0))
        mw.ui.last_page_btn.clicked.connect(lambda: mw.ui.download_2.setCurrentIndex(1))
        mw.ui.update_yt_dlp_btn.clicked.connect(lambda: [self.download_yt_dlp()])
        mw.ui.scrollArea.verticalScrollBar().valueChanged.connect(lambda: [self.fill_new_widgs()])
        mw.ui.search_for_update_btn.clicked.connect(lambda: self.search_for_updates(False))
        mw.ui.tableWidget.cellClicked.connect(self.handle_clicked)
        mw.ui.max_thread_slider.valueChanged.connect(lambda ev:[mw.threadpool.setMaxThreadCount(ev), self.update_config("DEFAULT", "max-download-threads", str(ev))])
        mw.ui.thumbnail_check_box.clicked.connect(lambda ev:[setattr(self, "stream_thumbnails", ev), self.update_config("DEFAULT", "thumbnail-streaming", str(ev))])
        mw.ui.update_check_box.clicked.connect(lambda ev:[setattr(self, "update_check", ev), self.update_config("DEFAULT", "check-for-updates", str(ev))])
        self.file_formats = ["Mp4", "Mp3"]
        self.search_activated = True
        self.new_widget_thread_running = False
        self.downloads = []
        self.cur_process = []
        self.loading = False
        self.delete_exe_files()
        if not os.path.isfile(Utils.get_abs_path("appdata/config.ini")):
            y = threading.Thread(target=self.create_ini)
            y.start()
            y.join()
        self.load_config()
        if getattr(sys, 'frozen', False) and self.update_check:
            self.search_for_updates()
        
    def delete_exe_files(self, folder_path="appdata"):
        for filename in os.listdir(folder_path):
            if filename.endswith(".exe"):
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)

    def update_file_box(self):
        if mw.ui.format_selection.currentText() == "Mp4":
            mw.ui.resolution_selection.setEnabled(True)
        else:
            mw.ui.resolution_selection.setEnabled(False)
            mw.ui.resolution_selection.setCurrentIndex(0)

    def create_ini(self):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"download_path": "~/Downloads/",
                            "ffmpeg_path": "None",
                            "yt-dlp-installed": "False",
                            "yt-dlp-date": "False",
                            "check-for-updates": "True",
                            "max-download-threads": "1",
                            "thumbnail-streaming": "True"}
        with open(Utils.get_abs_path("appdata/config.ini"), "w+") as file:
            config.write(file)

    def load_config(self):
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
            if self.yes_no_messagebox("\"yt-dlp\" isn't downloaded! \nDownload it?", QMessageBox.Warning, "Warning", QMessageBox.Yes |QMessageBox.No):
                self.download_yt_dlp()
            else:
                mw.close()
                sys.exit()
        else:
            self.import_yt_dl()

    def import_yt_dl(self):
        self.import_yt_dl_thread = ImportYTDLP()
        self.import_yt_dl_thread.finished.connect(lambda: [mw.ui.url_entry.setEnabled(True), self.user_info_no_ffmpeg() if self.ffmpeg == "None" else None])
        self.import_yt_dl_thread.start()
        
    def update_config_version(self, config):
        self.update_check = config["DEFAULT"].getboolean("check-for-updates", fallback=True)
        mw.ui.update_check_box.setChecked(self.update_check)
        self.update_config("DEFAULT", "check-for-updates", str(self.update_check))

        max_download_threads = int(config["DEFAULT"].get("max-download-threads", fallback=1))
        mw.threadpool.setMaxThreadCount(max_download_threads)
        mw.ui.max_thread_slider.setValue(max_download_threads)
        self.update_config("DEFAULT", "max-download-threads", str(max_download_threads))

        self.stream_thumbnails = config["DEFAULT"].getboolean("thumbnail-streaming", fallback=True)
        mw.ui.thumbnail_check_box.setChecked(self.stream_thumbnails)
        self.update_config("DEFAULT", "thumbnail-streaming", str(self.stream_thumbnails))
        
    def update_config(self, section, key, new_val):
        config = configparser.ConfigParser()
        config.read(Utils.get_abs_path("appdata/config.ini"))
        config[section][key] = str(new_val)
        with open(Utils.get_abs_path("appdata/config.ini"), "w") as file:
            config.write(file)

    def show_changelog(self):
        self.update_config("DEFAULT", "first-use-since-update", "False")
        text = open("appdata/changelog.md", "r").read()
        msg_box = QMessageBox(mw)
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setWindowTitle(f"Changelog - {VERSION}")
        
        msg_box.setText(text)
        msg_box.exec()
        
    def yt_search(self, text, pl_items, req):
        opts = {"quiet": True,
                "noprogress": True,
                "playlist_items": pl_items,
                "logger": Logger,
                "skip_download": True,
                "extract_flat": True,
                "list_thumbnails": True}
        try:
            ydl = YoutubeDL(opts)
            vid = ydl.extract_info(f"ytsearch{req}:{text}")["entries"]
            return vid
        except DownloadError as e:
            if "urlopen error" in e.msg:
                return "Connection Error"

    def use_info(self, info, cur_link):
        self.loading = False
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
                text = "Searching..."                
            else:
                text = f"No valid video or playlist url!"
            mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, text))
            mw.invokeFunc(mw.ui.download_btn, "setEnabled", Qt.QueuedConnection, Q_ARG(bool, False))
        self.info_thread = None
        
    def load_url(self, cur_link = None):
        if cur_link:
            if mw.timer.isActive():
                return
        
        if not cur_link: 
            mw.invokeFunc(mw.ui.search_stack_widg, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 0))
        mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, "Searching..."))
        if cur_link==None: cur_link = mw.ui.url_entry.text()   
        if cur_link == "":
            mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, ""))
            return
        
        self.search_thread = YoutubeSearch(cur_link,"0:30", 30, self)
        self.search_thread.result.connect(self.store_result)
        
        if "&list=" in cur_link and "?v=" in cur_link:
            cur_link = cur_link.split("&list=")[0]
        if self.loading:return
        self.loading = True
        self.info_thread = LoadVideo(cur_link, self)
        self.info_thread.finished.connect(self.use_info)
        self.info_thread.start()

    def store_result(self, data):
        self.search_thread = None
        self.search = 30
        while len(mw.search_labels) > 0:
            mw.search_labels.pop().deleteLater()
        mw.create_search_widges()
        mw.invokeFunc(mw.ui.scrollArea.verticalScrollBar(), "setValue", Qt.QueuedConnection, Q_ARG(int, 0))
        if data == []:
            mw.ui.url_entry.setEnabled(True)
            mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, "No video found"))
            return
        self.fill_widget_thread = FillWidgetThread(data)
        self.fill_widget_thread.finished.connect(lambda: mw.ui.url_entry.setEnabled(True))
        self.fill_widget_thread.start()
        mw.invokeFunc(mw.ui.search_stack_widg, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 1))

    def custom_event(self, event, url, channel, title):
        if event.button() == Qt.LeftButton:
            self.load_url(url)
        elif event.button() == Qt.RightButton:
            self.yes_no_messagebox(f"""<p style="font-weight: bold;">Uploader:</p> {channel}
                                    <p style="font-weight: bold;">Title:</p> {title}
                                    <p style="font-weight: bold;">URL:</p> 
                                    <a style="color: white; font-weight: bold;" href='{url}'>{url}</a>""", QMessageBox.Information, "Video", QMessageBox.Ok)

    def fill_new_widgs(self):
        if self.new_widget_thread_running or not self.search_activated: return
        if mw.ui.scrollArea.verticalScrollBar().value() == mw.ui.scrollArea.verticalScrollBar().maximum():
            mw.ui.url_entry.setEnabled(False)
            mw.create_search_widges(True)
            self.fill_new_widgs_thread = FillWidgetThread()
            self.fill_new_widgs_thread.finished.connect(lambda: mw.ui.url_entry.setEnabled(True))
            self.fill_new_widgs_thread.start()
        else:
            return

    def get_video_information(self, url, all_playlist = False):
        yt_dlp_opts = {"quiet": True,
                        "noprogress": True,
                        "logger": Logger,
                        "extract_flat": "in_playlist"
        }
        if not all_playlist: yt_dlp_opts["playlist_items"] = "0"
        ydl = YoutubeDL(yt_dlp_opts)
        try:
            inf = ydl.extract_info(url, False)
            info = ydl.sanitize_info(inf)
        except DownloadError as e:
            if "urlopen error" in e.msg:
                info = False
            info = None
        self.info  = info
        return info

    def update_main_frame(self):
        mw.ui.download_btn.setEnabled(True)
        mw.ui.download_btn.click()
        mw.ui.url_entry.setEnabled(True)
        mw.invokeFunc(mw.ui.info_start_label, "setText", Qt.QueuedConnection, Q_ARG(str, ""))
        if self.stream_thumbnails:
            img = QImage()
            img.loadFromData(self.data.image_byt)
            pixmap = QPixmap.fromImage(img.scaled(480, 360))
            mw.ui.image_label.setPixmap(pixmap)
        else:
            mw.ui.image_label.setText("")
        mw.ui.name_label.setText(f"Title: {self.data.title}")
        mw.ui.artist_label.setText(f"Uploader: {self.data.uploader}")
        mw.ui.format_selection.clear()
        mw.ui.resolution_selection.clear()
        mw.ui.format_selection.addItems(self.file_formats)
        mw.ui.resolution_selection.addItems(self.data.resolutions)
        if not self.playlist:
            mw.ui.date_label.setText(f"Upload Date: {self.data.upload_date}")
            mw.ui.duration_label.setText(f"Video Length: {self.data.duration}")
            mw.invokeFunc(mw.ui.last_page_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
        else:
            mw.ui.duration_label.clear()
            mw.invokeFunc(mw.ui.download_2, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 1))
            mw.invokeFunc(mw.ui.info_range_slider_label, "setText", Qt.QueuedConnection, Q_ARG(str, "Select the Range you want to Download"))
            mw.ui.date_label.setText(f"Playlist Count: {self.data.playlist_count} Videos")
            mw.invokeFunc2(mw, "setWidg2Range", Qt.QueuedConnection, Q_ARG(int, 1), Q_ARG(int, self.data.playlist_count))
            mw.invokeFunc2(mw, "setWidg2Value", Qt.QueuedConnection, Q_ARG(int, 1), Q_ARG(int, self.data.playlist_count))

    def change_location(self):
        new_dir = QFileDialog.getExistingDirectory(None, "Select a folder", os.path.expanduser(self.file))
        if new_dir == "":
            return
        self.file = f"{new_dir}/"
        self.update_config("DEFAULT", "download_path", self.file)

    def change_ffmpeg_location(self):
        new_dir = QFileDialog.getExistingDirectory(None, "Select the '/bin' Folder of your FFmpeg installation", os.path.expanduser(self.ffmpeg))
        if new_dir == "":
            return
        if not os.path.isfile(f"{new_dir}/ffmpeg.exe"):
            self.yes_no_messagebox("This is not a valid path", QMessageBox.Warning, "Warning", QMessageBox.Ok)
            self.change_ffmpeg_location()
            return
        self.ffmpeg = f"{new_dir}/"
        self.update_config("DEFAULT", "ffmpeg_path", self.ffmpeg)

    def show_in_explorer(self):
        f = os.path.expanduser(self.file).replace('/', '\\')
        command = f"explorer.exe {f}"
        os.system(command)

    def yes_no_messagebox(self, text, icon, title, options, hide = True):
        qms = QMessageBox(icon, title, text, options, mw)
        qms.setModal(True)
        if hide:
            qms.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        reply = qms.exec()
        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def user_info_no_ffmpeg(self):
        self.yes_no_messagebox("\"FFmpeg\" path is not defined.\nYou can't download Videos without it!\nDownload it or set the path to your installation in the settings.", QMessageBox.Warning, "Warning", QMessageBox.Ok)
        mw.invokeFunc(mw.ui.mainpages, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 3))
        mw.ui.settings_btn.click()

    def handle_update_available(self, update_available, tag, auto):
        if update_available:
            msg_box = QMessageBox(mw)
            msg_box.setText(f"""Current version: {VERSION} <br> 
                                New version: {tag} <br> 
                                Download and install? <br>
                                Not working with portable version""")
            msg_box.setWindowTitle("Update found")
            msg_box.setIcon(QMessageBox.Information)
            download_and_install = QPushButton("Install Update")
            msg_box.addButton(download_and_install, QMessageBox.ActionRole)
            
            skip = QPushButton("Skip Update")
            msg_box.addButton(skip, QMessageBox.ActionRole)
            res = msg_box.exec()
            if res == 0: self.update_self(tag)
        elif not update_available and tag == "no_connection":
            self.yes_no_messagebox("ERROR: No internet connection", QMessageBox.Warning, "No internet", QMessageBox.Ok)
        elif not update_available and not auto:
            self.yes_no_messagebox("No update available.", QMessageBox.Information, "No update found", QMessageBox.Ok)

    def search_for_updates(self, auto = True):
        self.update_thread = UpdateThread(auto)
        self.update_thread.update_available.connect(self.handle_update_available)
        self.update_thread.start()

    def update_self(self, tag):
        self.self_download_thread = GithubDownloader(f"https://github.com/PyFlat-Studios-JR/YT-Downloader/releases/latest/download/win_installer_v{tag}.exe", f"appdata/win_installer_v{tag}.exe")
        self.self_download_thread.progress.connect(self.update_progress_self)
        self.self_download_thread.finished.connect(lambda success: self.download_finished_self(success, tag))

        self.self_download_progress_dialog = ProgressDialog("update", mw)
        self.self_download_progress_dialog.show()

        self.self_download_thread.start()

    def update_progress_self(self, progress):
        if progress < 0:
            self.self_download_progress_dialog.close()
            self.yes_no_messagebox("ERROR: No internet connection", QMessageBox.Warning, "No internet", QMessageBox.Ok)
        if self.self_download_progress_dialog:
            self.self_download_progress_dialog.update_progress(progress)

    def download_finished_self(self, success, tag):
        self.self_download_progress_dialog.close()
        self.self_download_thread = None
        self.self_download_progress_dialog = None
        if not success: self.yes_no_messagebox("Download Failed", QMessageBox.Warning, "Download Fail", QMessageBox.Ok); return
        if self.yes_no_messagebox("Download Finished\nStart installation?", QMessageBox.Question, " ", QMessageBox.Yes | QMessageBox.No):
            os.system(f"start appdata/win_installer_v{tag}.exe")
            mw.close()
            sys.exit(0)

    def download_yt_dlp(self):
        self.yt_dlp_download_thread = GithubDownloader("https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt-dlp", "appdata/yt_dlp")
        self.yt_dlp_download_thread.progress.connect(self.update_progress_yt_dlp)
        self.yt_dlp_download_thread.finished.connect(self.download_finished_yt_dlp)

        self.yt_dlp_progress_dialog = ProgressDialog("yt-dlp", mw)
        self.yt_dlp_progress_dialog.show()

        self.yt_dlp_download_thread.start()

    def update_progress_yt_dlp(self, progress):
        if progress < 0:
            self.yt_dlp_progress_dialog.close()
            self.yes_no_messagebox("ERROR: No internet connection", QMessageBox.Warning, "No internet", QMessageBox.Ok)
        if self.yt_dlp_progress_dialog:
            self.yt_dlp_progress_dialog.update_progress(progress)

    def download_finished_yt_dlp(self, success):
        self.yt_dlp_progress_dialog.close()
        self.yt_dlp_download_thread = None
        self.yt_dlp_progress_dialog = None
        if not success: self.yes_no_messagebox("Download Failed", QMessageBox.Warning, "Download Fail", QMessageBox.Ok); return
        self.update_config("DEFAULT", "yt-dlp-installed", "True")
        self.update_config("DEFAULT", "yt-dlp-date", str(datetime.datetime.now()))
        self.yes_no_messagebox("Installation Finished", QMessageBox.Information, "Info", QMessageBox.Ok)
        self.import_yt_dl()

    def download_ffmpeg(self):
        if os.path.isdir("appdata/FFmpeg"):
            shutil.rmtree("appdata/FFmpeg")
        self.ffmpeg_download_thread = GithubDownloader("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip", "appdata/ffmpeg.zip")
        self.ffmpeg_download_thread.progress.connect(self.update_progress_ffmpeg)
        self.ffmpeg_download_thread.finished.connect(self.download_finished_ffmpeg)

        self.ffmpeg_progress_dialog = ProgressDialog("ffmpeg", mw)
        self.ffmpeg_progress_dialog.show()

        self.ffmpeg_download_thread.start()

    def update_progress_ffmpeg(self, progress):
        if progress < 0:
            self.ffmpeg_progress_dialog.close()
            self.yes_no_messagebox("ERROR: No internet connection", QMessageBox.Warning, "No internet", QMessageBox.Ok)
        if self.ffmpeg_progress_dialog:
            self.ffmpeg_progress_dialog.update_progress(progress)

    def download_finished_ffmpeg(self, success):
        self.ffmpeg_download_thread = None
        if  not success: 
            self.ffmpeg_progress_dialog.close()
            self.ffmpeg_progress_dialog = None
            self.yes_no_messagebox("Download Failed", QMessageBox.Warning, "Download Fail", QMessageBox.Ok)
            return
        zp = ZipFile("appdata/ffmpeg.zip")
        names_foo = [i for i in zp.namelist() if i.startswith("ffmpeg-master-latest-win64-gpl/")]
        for file in names_foo:
            zp.extract(file)
        zp.close()
        os.rename("ffmpeg-master-latest-win64-gpl", "appdata/FFmpeg")
        os.remove("appdata/ffmpeg.zip")
        self.ffmpeg_progress_dialog.close()
        self.ffmpeg_progress_dialog = None
        self.yes_no_messagebox("Installation Finished", QMessageBox.Information, "Info", QMessageBox.Ok)
        self.ffmpeg = Utils.get_abs_path("appdata/FFmpeg/bin")
        self.update_config("DEFAULT", "ffmpeg_path", self.ffmpeg)
        
    def add_row(self, row_count, data):
        mw.ui.tableWidget.insertRow(row_count)
        for column, string in enumerate(data):
            item = QTableWidgetItem(str(string))
            mw.ui.tableWidget.setItem(row_count, column, item)

    def handle_clicked(self, row, column):
        selection_model = mw.ui.tableWidget.selectionModel()
        selection_model.clearSelection()
        mw.set_enabled(False, False, False)
        index = mw.ui.tableWidget.model().index(row, 0)
        selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        try:
            mw.ui.download_delete_btn.disconnect(self.delete_btn_connection)
            mw.ui.download_open_btn.disconnect(self.play_file_btn_connection)
            mw.ui.download_download_btn.disconnect(self.re_download_file_btn_connection)
        except AttributeError :
            pass
        status = mw.ui.tableWidget.item(row, 4).text()
        if not os.path.isfile(self.downloads[row].filename) and status == "Finished": 
            item = QTableWidgetItem("Deleted")
            mw.ui.tableWidget.setItem(row, 4, item)
            status = "Deleted"
        
        if status == "Finished":
            mw.set_enabled(True, True, True)
        elif status == "Deleted" or status == "Download Failed":
            mw.set_enabled(False, False, True)
        self.delete_btn_connection = mw.ui.download_delete_btn.clicked.connect(lambda ev: self.downloads[row].delete(row))
        self.play_file_btn_connection = mw.ui.download_open_btn.clicked.connect(lambda ev: self.downloads[row].play())
        self.re_download_file_btn_connection = mw.ui.download_download_btn.clicked.connect(lambda ev: self.downloads[row].prepare_for_download(row))

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
            self.resolutions = ['Best Quality', '4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
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
        resolution.insert(0, "Best Quality")
        return resolution

    def prepare_for_download(self, row = None):
        mw.set_enabled(False, False, False)
        self.vid_ext = mw.ui.format_selection.currentText().lower()
        self.vid_res = mw.ui.resolution_selection.currentText() 
        self.vid_res = "Best Quality" if self.vid_res == "" else self.vid_res
        
        if self.playlist: self.download_playlist();return
        
        temp_vid_res = self.vid_res.split("p")[0]
        if ((temp_vid_res != "Best Quality") and (self.vid_ext != "mp3")) and not self.playlist:
            self.download_format = "bv[height<="+str(temp_vid_res)+"]+ba[ext=m4a]/b"
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
            dl.yes_no_messagebox("You cant download the same file at the same time", QMessageBox.Warning, "Warning", QMessageBox.Ok)
            return
        
        self.process = currently_processing
        dl.cur_process.append(currently_processing)
        if row != None:
            self.download(row)
            return
        
        file_name_thread = FileNameThread(self.outtmpl, self.download_format, self.url, self.vid_ext, dl.file)
        file_name_thread.ret_filename.connect(self.check_if_exists)
        file_name_thread.start()
        self.file_name_threads.append(file_name_thread)

    def check_if_exists(self, filename):
        if filename == "Connection Error":
            dl.yes_no_messagebox("ERROR: No internet connection", QMessageBox.Warning, "No internet", QMessageBox.Ok)
            dl.cur_process.remove(self.process)
            return
        if os.path.isfile(filename):
            if not dl.yes_no_messagebox("This file already exists.\nDo you want to overwrite it?", QMessageBox.Warning, "Warning", QMessageBox.Yes | QMessageBox.No):
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
        start, stop = mw.ui.playlist_range_slider.value()
        for i in range(start-1, stop):
            self.playlist_data_objects[i].prepare_for_download()
        
    def download(self, row=None):
        if row == None:
            data = [self.author, self.title, self.vid_ext.upper(), self.vid_res, "Started", ""]
            row_count = mw.ui.tableWidget.rowCount()
            dl.add_row(row_count, data)
        else:
            item  = QTableWidgetItem("Started")
            mw.ui.tableWidget.setItem(row, 4, item)
            row_count = row

        dl_thread = VideoDownloadThread(self.url, self.download_format, self.vid_ext, dl.ffmpeg, self.filename, row_count)
        dl_thread.finished.connect(self.handle_download_finished)
        dl_thread.progress.connect(self.update_progress)
        thread_worker = ThreadWorker(dl_thread)
        mw.threadpool.start(thread_worker)
        mw.ui.top_label.setText("Download Started")
        mw.ui.top_label.setVisible(True)
        timer = QTimer()
        timer.singleShot(5000, lambda: mw.ui.top_label.setVisible(False))
        if row == None: dl.downloads.append(copy.copy(self))
        
    def handle_download_finished(self, success, row):
        if mw.ui.tableWidget.item(row, 0).isSelected():
            mw.set_enabled(True, True, True)
        dl.cur_process.remove(dl.downloads[row].process)
        
        if success:
            item  = QTableWidgetItem("Finished")
            mw.ui.tableWidget.setItem(row, 4, item)
            
        else:
            item  = QTableWidgetItem("Download Failed")
            mw.ui.tableWidget.setItem(row, 4, item)
    def update_progress(self, progress, row, eta):
        item  = QTableWidgetItem(progress)
        mw.ui.tableWidget.setItem(row, 4, item)
        if eta == "Unknown Seconds": return
        item2 = QTableWidgetItem(eta)
        mw.ui.tableWidget.setItem(row, 5, item2)
    def delete(self, row):
        mw.set_enabled(False, False, False)
        if not dl.yes_no_messagebox("Do you really want to delete this file?", QMessageBox.Question, "Question", QMessageBox.Yes | QMessageBox.No):return
        item  = QTableWidgetItem("Deleted")
        mw.ui.tableWidget.setItem(row, 4, item)
        if os.path.isfile(self.filename):
            os.remove(self.filename)
    def play(self):
        mw.set_enabled(False, False, False)
        os.system(f"\"{self.filename}\"")
        
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
            mw.ui.info_start_label.setText("No Internet Connection")
            mw.ui.url_entry.setEnabled(True)
            return

        new_widgs = not bool(self.data)

        if new_widgs:
            dl.new_widget_thread_running = True
            cur_link = mw.ui.url_entry.text()
            self.data = dl.yt_search(cur_link, f"{dl.search+1}:{dl.search+30}", dl.search + 30)

            if self.data == "Connection Error":
                mw.search_labels = mw.search_labels[:dl.search]
                mw.invokeFunc(mw.ui.search_stack_widg, "setCurrentIndex", Qt.QueuedConnection, Q_ARG(int, 0))
                mw.ui.info_start_label.setText("No Internet Connection")
                mw.ui.url_entry.setEnabled(True)
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
                    mw.ui.info_start_label.setText("No Internet Connection")
                    mw.ui.url_entry.setEnabled(True)
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
            self.finished.emit(True if progress == 100.0 else False)
        except requests.exceptions.ConnectionError:
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
        self.row = row
        self.update_eta = 0
        self.is_paused = False
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

            YoutubeDL(ydl_opts).download(self.url)
        except DownloadError as e:
            if "urlopen error" in e.msg or "The read operation timed out" in e.msg:
                self.finished.emit(False, self.row)
            else:
                print(e)

        else:
            self.finished.emit(True, self.row)
            
        
    def _hook(self, d):
        if not self.is_paused:
            self.update_eta += 1
            if not (self.update_eta % 20 == 0):
                return
            if d['status'] == 'downloading':
                try:
                    pr = int(round(round(float(d['downloaded_bytes'])/float(d["total_bytes"]),2)*100, 0))
                except KeyError:
                    pr = int(round(round(float(d['downloaded_bytes'])/float(d["total_bytes_estimate"]),2)*100, 0))
                eta = int(round(float(d['eta']),ndigits=0)) if d["eta"] else "Unknown"
                self.progress.emit(f"{pr}%", self.row, f"{eta} Seconds")
            elif d["status"] == "finished":
                self.progress.emit("", self.row, "")
            
    def _hook_postprocess(self, d):
        if d["status"] == "started":
            self.progress.emit("Postprocessing Started", self.row, "")
        else:
            self.progress.emit("Postprocessing Finished", self.row, "")

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
    def __init__(self):
        super().__init__()
    def run(self):
        global YoutubeDL, DownloadError
        sys.path.insert(0, Utils.get_abs_path("appdata/yt_dlp"))
        from yt_dlp import YoutubeDL
        from yt_dlp.utils import DownloadError
        

if __name__ == "__main__":
    app = QApplication([])
    mw = MainWindow()
    dl = Downloader()
    sys.exit(app.exec())
    
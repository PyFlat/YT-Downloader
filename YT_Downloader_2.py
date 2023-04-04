import io, threading, datetime, re, os, configparser,sys,subprocess

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
#from superqt import QLabeledRangeSlider #Labled Range Slider !!!!! https://pyapp-kit.github.io/superqt/widgets/qlabeledrangeslider/
from urllib.request import urlopen
from PIL import Image
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

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
    return os.path.join(base_path, relative_path)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(1000, 500))
        self.setWindowTitle("Youtube-Downloader-v2.0")
        self.setStyleSheet(open(get_abs_path("appdata/style.qss"), "r").read())
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0,0,0,0)
        self.sideFrame = QFrame()
        
        self.mainFrame = QFrame()
        self.mainFrame.setMinimumSize(930, 500)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        
        self.sideFrame.setLayout(self.verticalLayout)
        
        self.horizontalLayout.addWidget(self.sideFrame)
        self.horizontalLayout.addWidget(self.mainFrame)
        self.horizontalLayout.addStretch(1)
        self.drawSidebar()
        self.drawMain()
        self.bind_keys()
        self.btn_5.setChecked(True)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(300)
        
        self.show()
    def bind_keys(self):
        self.btn_1.clicked.connect(lambda: [self.stackedLayout.setCurrentIndex(1)])
        self.btn_2.clicked.connect(lambda: [self.stackedLayout.setCurrentIndex(2)])
        self.btn_5.clicked.connect(lambda: [self.stackedLayout.setCurrentIndex(0)])
        self.btn_3.clicked.connect(lambda: [self.close()])
    def drawMain(self):
        self.stackedLayout = QStackedLayout()
        self.mainFrame.setLayout(self.stackedLayout)
        self.draw_page_1()
        self.draw_page_2()
        self.draw_page_3()

        self.stackedLayout.addWidget(self.page_3)
        self.stackedLayout.addWidget(self.page_1)
        self.stackedLayout.addWidget(self.page_2)
    def draw_page_1(self):
        self.page_1 = QFrame()
        self.page_1.setObjectName("page_1")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(50,50,50,50)
        self.verticalLayout_2.setSpacing(15)
        
        self.page_1.setLayout(self.verticalLayout_2)

        self.page1_frame = QFrame()
        
        
        self.horizontalLayout_1 = QHBoxLayout()
        self.horizontalLayout_1.setContentsMargins(0,0,0,0)
        self.horizontalLayout_1.setSpacing(10)
        
        self.page1_frame.setLayout(self.horizontalLayout_1)

        self.page1_frame1 = QFrame()
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(0,0,0,0)
        self.verticalLayout_4.setSpacing(20)

        self.page1_frame1.setLayout(self.verticalLayout_4)

        self.image_label = QLabel()
        self.image_label.setMaximumSize(QSize(480, 270))
        self.image_label.setObjectName("image_label")

        self.title = QLabel()
        self.title.setWordWrap(True)
        self.channel = QLabel()
        self.channel.setWordWrap(True)
        self.upload_date = QLabel()

        self.page1_frame2 = QFrame()
        
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(0,0,0,0)
        self.horizontalLayout_2.setSpacing(25)

        self.page1_frame2.setLayout(self.horizontalLayout_2)

        self.btn_6 = QPushButton("Download")
        self.btn_6.setObjectName("download_button")
        self.btn_6.setMinimumWidth(250)

        self.status_label = QLabel()

        self.progressbar = QProgressBar()
        self.progressbar.setMaximumHeight(30)
        self.progressbar.setMinimumWidth(300)
        self.progressbar.setObjectName("progressbar")
        
        self.format = QComboBox()
        self.format.setMinimumWidth(180)
        self.format.setObjectName("format_box")

        self.file_format = QComboBox()
        self.file_format.setMinimumWidth(180)
        self.file_format.setObjectName("file_format_box")

        self.change_location = QPushButton()
        self.change_location.setMinimumWidth(180)
        self.change_location.setText("Change Download Folder")
        self.change_location.setObjectName("change_location_btn")

        self.show_folder = QPushButton()
        self.show_folder.setMinimumWidth(180)
        self.show_folder.setText("Show Folder in Explorer")
        self.show_folder.setObjectName("show_folder_btn")

        self.horizontalLayout_2.addWidget(self.file_format)
        self.horizontalLayout_2.addWidget(self.format)
        self.horizontalLayout_2.addWidget(self.change_location)
        self.horizontalLayout_2.addWidget(self.show_folder)

        self.verticalLayout_4.addWidget(self.title, alignment=Qt.AlignTop)
        self.verticalLayout_4.addWidget(self.channel, alignment=Qt.AlignTop)
        self.verticalLayout_4.addWidget(self.upload_date, alignment=Qt.AlignTop)

        self.horizontalLayout_1.addWidget(self.image_label, alignment=Qt.AlignTop)
        self.horizontalLayout_1.addWidget(self.page1_frame1, alignment=Qt.AlignTop)
        
        self.verticalLayout_2.addWidget(self.page1_frame)
        self.verticalLayout_2.addWidget(self.page1_frame2, alignment=Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.btn_6, alignment=Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.status_label, alignment=Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.progressbar, alignment=Qt.AlignCenter)

    def draw_page_2(self):
        self.page_2 = QFrame()
        self.page_2.setObjectName("page_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(150,0,150,0)
        self.verticalLayout_3.setSpacing(0)
        self.page_2.setLayout(self.verticalLayout_3)
    def draw_page_3(self):
        self.page_3 = QFrame()
        self.page_3.setObjectName("page_3")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(150,0,150,0)
        self.verticalLayout_5.setSpacing(0)
        self.page_3.setLayout(self.verticalLayout_5)

        self.url_entry = QLineEdit()
        self.url_entry.setMinimumSize(QSize(800, 40))
        self.url_entry.setPlaceholderText("Insert URL")
        self.url_entry.setObjectName("url_entry")

        self.verticalLayout_5.addWidget(self.url_entry, alignment=Qt.AlignCenter)  
    def drawSidebar(self):
        self.sidebar = QFrame(self)
        self.sidebar.setMinimumSize(QSize(70, 0))
        self.sidebar.setMaximumSize(QSize(70, 16777215))
        self.sidebar.setObjectName("sidebar")

        self.verticalLayout_1 = QVBoxLayout(self.sidebar)
        self.verticalLayout_1.setObjectName("verticalLayout_3")
        self.verticalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_1.setSpacing(0)

        self.btn_5 = QPushButton(QIcon(get_abs_path("appdata/images/search.png")), "   Search")
        self.btn_5.setObjectName("btn_1")
        self.btn_5.setFixedSize(QSize(70, 50))
        self.btn_5.setIconSize(QSize(30,30))
        self.btn_5.setCheckable(True)
        self.btn_5.setAutoExclusive(True)
        
        self.btn_1 = QPushButton(QIcon(get_abs_path("appdata/images/download.png")), "   Download")
        self.btn_1.setObjectName("btn_1")
        self.btn_1.setFixedSize(QSize(70, 50))
        self.btn_1.setIconSize(QSize(30,30))
        self.btn_1.setCheckable(True)
        self.btn_1.setAutoExclusive(True)
        
        self.btn_2 = QPushButton(QIcon(get_abs_path("appdata/images/settings.png")), "   Settings")
        self.btn_2.setObjectName("btn_2")
        self.btn_2.setFixedSize(QSize(70, 50))
        self.btn_2.setIconSize(QSize(30,30))
        self.btn_2.setCheckable(True)
        self.btn_2.setAutoExclusive(True)
        
        self.btn_3 = QPushButton(QIcon(get_abs_path("appdata/images/quit.png")), "   Exit")
        self.btn_3.setObjectName("btn_3")
        self.btn_3.setFixedSize(QSize(70, 50))
        self.btn_3.setIconSize(QSize(30,30))

        self.btn_4 = QPushButton(QIcon(get_abs_path("appdata/images/menu.png")), "   Hide")
        self.btn_4.setObjectName("btn_4")
        self.btn_4.setFixedSize(QSize(70, 50))
        self.btn_4.clicked.connect(lambda: self.toggle_menu())
        self.btn_4.setIconSize(QSize(30,30))

        
        self.verticalLayout_1.addWidget(self.btn_4, alignment=Qt.AlignCenter|Qt.AlignTop)
        self.verticalLayout_1.addStretch(5)
        self.verticalLayout_1.addWidget(self.btn_5, alignment=Qt.AlignCenter|Qt.AlignTop)
        self.verticalLayout_1.addWidget(self.btn_1, alignment=Qt.AlignCenter|Qt.AlignTop)
        self.verticalLayout_1.addWidget(self.btn_2, alignment=Qt.AlignCenter|Qt.AlignTop)
        self.verticalLayout_1.addStretch(50)
        self.verticalLayout_1.addWidget(self.btn_3, alignment=Qt.AlignCenter|Qt.AlignTop)

        self.verticalLayout.addWidget(self.sidebar)  
    def update_sidebar(self, typ):
        if typ:
            self.btn_1.setFixedWidth(190)
            self.btn_2.setFixedWidth(190)
            self.btn_3.setFixedWidth(190)
            self.btn_4.setFixedWidth(190)
            self.btn_5.setFixedWidth(190)
        else:
            self.btn_1.setFixedWidth(70)
            self.btn_2.setFixedWidth(70)
            self.btn_3.setFixedWidth(70)
            self.btn_4.setFixedWidth(70)
            self.btn_5.setFixedWidth(70)
    def toggle_menu(self):
        width = self.sidebar.width()
        maxExtend = 190
        standard = 70
        if width == standard:
            widthExtended = maxExtend
            val = True
        else:
            widthExtended = standard
            val = False
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.start()
        if val:
            self.update_sidebar(val)
        else:
            self.animation.stateChanged.connect(lambda:self.update_sidebar(val))
    def connect_wid(self, widget ,func):
        widget.connect(lambda: func())
    
class Downloader():
    def __init__(self, window):
        self.win = window
        self.win.connect_wid(self.win.timer.timeout, self.start_load_video)
        self.win.connect_wid(self.win.url_entry.textChanged, self.win.timer.start)
        self.win.connect_wid(self.win.file_format.currentIndexChanged, self.update_file_box)
        self.win.connect_wid(self.win.btn_6.clicked, self.start_download)
        self.win.connect_wid(self.win.change_location.clicked, self.change_location)
        self.win.connect_wid(self.win.show_folder.clicked, self.show_in_explorer)
        self.file_formats = ["Mp4", "Mp3"]
        self.pl_range = None
        self.hide()
        if not os.path.isfile(get_abs_path("appdata/config.ini")):
            threading.Thread(target=self.create_ini).start()
        x = threading.Thread(target=self.load_config)
        x.start()
        x.join()
    def update_file_box(self):
        if self.win.file_format.currentText() == "Mp4":
            self.win.format.setEnabled(True)
        else:
            self.win.format.setEnabled(False)
            self.win.format.setCurrentIndex(0)

    def show(self):
        for i in range(self.win.verticalLayout_2.count()):
            child = self.win.verticalLayout_2.itemAt(i).widget()
            child.setVisible(True)

    def hide(self):
        for i in range(self.win.verticalLayout_2.count()):
            child = self.win.verticalLayout_2.itemAt(i).widget()
            child.hide()
            if hasattr(child, "clear"):
                child.clear()
        self.win.btn_1.setEnabled(False)
    def start_load_video(self):
        threading.Thread(target=self.load_video).start()
    def create_ini(self):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"ffmpeg_path": "C:/FFmpeg/bin",
                             "download_path": "~/Downloads/"}
        with open(get_abs_path("appdata/config.ini"), "w+") as file:
            config.write(file)
    def load_config(self):
        config = configparser.ConfigParser()
        config.read(get_abs_path("appdata/config.ini"))
        self.ffmpeg = config["DEFAULT"]["ffmpeg_path"]
        self.file = config["DEFAULT"]["download_path"]
    def update_config(self, section, key, new_val):
        config = configparser.ConfigParser()
        config.read(get_abs_path("appdata/config.ini"))
        config[section][key] = new_val
        with open(get_abs_path("appdata/config.ini"), "w") as file:
            config.write(file)


    def load_playlist(self, info):
        self.title = info["title"]
        self.author = info["channel"]
        self.playlist_count = info["playlist_count"]
        self.url = self.get_thumbnail_url(info)
        image_byt = urlopen(self.url).read()
        self.MainWindow.button_3.configure(state="normal")
        self.img = Image.open(io.BytesIO(image_byt))
        self.thumbnail_data = self.get_thumbnail_data(self.img)
        self.update_main_frame(True)

    def load_video(self):
        cur_link = self.win.url_entry.text()
        if "&list=" in cur_link and "?v=" in cur_link:
            cur_link = cur_link.split("&list=")[0]
        info = self.get_video_information(cur_link)
        if info != None:
            if "?list=" in cur_link and ("&list=" not in cur_link and "?v=" not in cur_link):
                self.load_playlist(info)
                return
            self.title = info["title"]
            self.author = info["channel"]
            self.upload_date = datetime.datetime.strptime(info["upload_date"], "%Y%m%d").strftime("%d.%m.%Y")
            self.cur_link = cur_link
            self.formats = self.check_formats(info)
            self.url = self.get_thumbnail_url(info)
            self.image_byt = urlopen(self.url).read()
            self.hide()
            self.update_main_frame()
            self.win.btn_1.setEnabled(True)
            self.win.btn_1.click()
        else:
            self.hide()
            self.old_playlist = None


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
        self.show()
        img = QImage()
        img.loadFromData(self.image_byt)
        pixmap = QPixmap.fromImage(img.scaled(480, 360))
        self.win.image_label.setPixmap(pixmap)
        self.win.title.setText(f"Title: {self.title}")
        self.win.channel.setText(f"Uploader: {self.author}")
        self.win.upload_date.setText(f"Upload Date: {self.upload_date}")
        self.win.format.addItems(self.formats)
        self.win.file_format.addItems(self.file_formats)
        self.win.status_label.setVisible(False)
        self.win.progressbar.setVisible(False)


    def change_location(self):
        new_dir = QFileDialog.getExistingDirectory(None, "Select a folder", os.path.expanduser(self.file))
        if new_dir == "":
            return
        self.file = f"{new_dir}/"
        threading.Thread(target = lambda: self.update_config("DEFAULT", "download_path", self.file)).start()

    def show_in_explorer(self):
        f = self.file.replace('/', '\\')
        command = f"explorer.exe {f}"
        subprocess.Popen(command)

    def update_to(self, d):
        if self.win.progressbar.isVisible():
            self.win.progressbar.setVisible(False)
        if d["status"] == "started":
            self.win.status_label.setText("Download Finished, Postprocessing Started")
        elif d["status"] == "finished":
            self.win.status_label.setVisible(False)
            self.win.btn_6.setVisible(True)
            self.win.format.setVisible(True)
            self.win.file_format.setVisible(True)
            self.win.change_location.setVisible(True)
            self.win.show_folder.setVisible(True)


    def update_progress(self, d):
        if d['status'] == 'downloading':
            pr = int(round(round(float(d['downloaded_bytes'])/float(d["total_bytes_estimate"]),2)*100, 0))
            if d["eta"] == None:
                eta = "Unknown"
            else:
                eta = round(float(d['eta']),ndigits=0)
            label_text = f"Time Elapsed: {round(float(d['elapsed']),ndigits=0)}| Estimated Time: {eta}"
            self.win.progressbar.setValue(pr)
            self.win.status_label.setText(label_text)
        elif d["status"] == "finished":
            self.win.status_label.setText("Download Finished")

    def ask_for_overwrite(self):
        qms = QMessageBox()
        qms.setText("This file already exists.\nDo you want to overwrite it?")
        qms.setIcon(QMessageBox.Warning)
        qms.setWindowTitle("Warning")
        qms.resize(250, 100)
        qms.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        qms.setDefaultButton(QMessageBox.No)
        reply = qms.exec()
        if reply == QMessageBox.Yes:
            return True
        else:
            return False
    def start_download(self):
        path = os.path.expandvars(f"{os.path.expanduser(self.file)}{self.title}.{self.win.file_format.currentText().lower()}")
        if os.path.isfile(path):
            if not self.ask_for_overwrite():
                return
        threading.Thread(target=self.download).start()
        self.win.btn_6.setVisible(False)
        self.win.format.setVisible(False)
        self.win.file_format.setVisible(False)
        self.win.change_location.setVisible(False)
        self.win.show_folder.setVisible(False)
        self.win.status_label.setText("")
        self.win.status_label.setVisible(True)
        self.win.progressbar.setValue(0)
        self.win.progressbar.setVisible(True)

    def download(self):
        vid_format = self.win.file_format.currentText().lower()
        vid_quality = self.win.format.currentText().split("p")[0]
        if (vid_quality != "Best Quality") and (vid_format != "mp3"):
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
                "outtmpl": self.file + "%(title)s.%(ext)s",
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
                "outtmpl": self.file + "%(title)s.%(ext)s",
                "merge_output_format": "mp4",
                "quiet": True,
                "noprogress": True,
                'progress_hooks': [self.update_progress],
                "concurrent_fragments": 2,
                "playlist_items": self.pl_range,
                "overwrites": True,
                "postprocessor_hooks": [self.update_to]
                }
        YoutubeDL(ydl_opts).download(self.cur_link)

     
#https://www.youtube.com/watch?v=dQw4w9WgXcQ

if __name__ == "__main__":
    app = QApplication([])
    Downloader(MainWindow())
    app.exec()

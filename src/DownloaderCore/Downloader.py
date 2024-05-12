try:
    from src.DownloaderCore.Threads.VideoDownloadThread import VideoDownloadThread
    from src.DownloaderCore.Threads.YoutubeVideoDownloadThread import YoutubeVideoDownloadThread
    from src.DownloaderCore.Threads.InformationLoadThread import InformationLoadThread
except:
    from Threads.VideoDownloadThread import VideoDownloadThread
    from Threads.YoutubeVideoDownloadThread import YoutubeVideoDownloadThread
    from Threads.InformationLoadThread import InformationLoadThread
Threads = {}
if __name__ == "__main__":
    import sys
    from PySide6.QtCore import QCoreApplication, QTimer, QThread
    class infothread(QThread):
        def __init__(self) -> None:
            super().__init__()
        def run(self):
            while True:
                import sys
                def strpln(i):
                    r = ""
                    rr = 0
                    for c in i:
                        if c != " ":
                            rr = 1
                        if rr:
                            r += c
                    return r
                def spltln(i):
                    r = []
                    a = ""
                    s = 0
                    for c in i:
                        if c == "\"":
                            s ^= 1
                            continue
                        if c == " " and not s:
                            r.append(a)
                            a = ""
                        else:
                            a += c
                    if a:
                        r.append(a)
                    return r
                command = strpln(input("YTDL>"))
                print(command)
                argv = spltln(command)
                argc = len(argv)
                match (argv[0]):
                    case "exit":
                        print("Bye")
                        sys.exit(0)
                    case "download":
                        def progress(a, b):
                            print(a, b)
                        def finish(a):
                            print("EXIT", a)
                        if argc < 6:
                            print("Usage: download <url> <extension> <ffempeg> <format> <output_template>")
                        else:
                        #download https://www.youtube.com/watch?v=HBEsr0MfdmQ mp4 C:/Users/jonas/AppData/Local/Programs/PyFlat Youtube Downloader(2)/appdata/FFmpeg/bin bv[height<=720]+ba[ext=m4a]/b (%(height)sp).%(ext)s
                            thd = YoutubeVideoDownloadThread(argv[1],argv[4],argv[3],argv[5],argv[2],finish, progress)
                            thd.start()
                    case "get-info":
                        if argc < 2:
                            print("Usage: get-info <url>")
                        else:
                            def callback(data, url):
                                print(url, data)
                            def report(data):
                                print(data)
                            thd = InformationLoadThread(argv[1], False, callback)
                            print(thd)
                            thd.start()
                            Threads[argv[1]] = thd
                    case other:
                        print("No matching command found :(")
    def cb(*args):
        print(*args)
    __app__ = QCoreApplication()
    thd = InformationLoadThread("https://www.youtube.com/watch?v=HBEsr0MfdmQ", False, cb)
    thd.start()
    
    sys.exit(__app__.exec())
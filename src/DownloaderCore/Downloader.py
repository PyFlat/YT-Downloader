try:
    from src.DownloaderCore.Threads.VideoDownloadThread import VideoDownloadThread
    from src.DownloaderCore.Threads.YoutubeVideoDownloadThread import YoutubeVideoDownloadThread
except:
    from Threads.VideoDownloadThread import VideoDownloadThread
    from Threads.YoutubeVideoDownloadThread import YoutubeVideoDownloadThread

if __name__ == "__main__":
    from PySide6.QtCore import QCoreApplication, QTimer
    import sys
    def await_input():
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
            case other:
                print("No matching command found :(")
        QTimer.singleShot(0, await_input)
    __app__ = QCoreApplication()
    await_input()
    sys.exit(__app__.exec())
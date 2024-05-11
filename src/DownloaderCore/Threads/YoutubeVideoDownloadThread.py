try:
    from src.DownloaderCore.Threads.VideoDownloadThread import VideoDownloadThread
except ModuleNotFoundError:
    from Threads.VideoDownloadThread import VideoDownloadThread
class YoutubeVideoDownloadThread(VideoDownloadThread):
    class EXTENSIONS():
        MP3 = "mp3"
        MP4 = "mp4"
        SUPPORTED = [MP3,MP4]
    def __init__(self, url: str, format: str, ffmpeg_path: str, output_template: str, extension: str = EXTENSIONS.MP4,  finished_callback: object | None = None, progress_callback: object | None = None) -> None:
        if not extension in YoutubeVideoDownloadThread.EXTENSIONS.SUPPORTED:
            raise ValueError(f"Provided extension {extension} does not match with the supported extensions {str(YoutubeVideoDownloadThread.EXTENSIONS.SUPPORTED)}!")
        match (extension):
            case YoutubeVideoDownloadThread.EXTENSIONS.MP3:
                options = {
                    "format": "bestaudio/best",
                    "ffmpeg_location": ffmpeg_path,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'
                    }],
                    "outtmpl": output_template[:-4],
                    "quiet": True,
                    "noprogress": True,
                    'progress_hooks': [super()._progress_hook],
                    "overwrites": True,
                    "postprocessor_hooks": [super()._finish_hook],
                    "socket_timeout": 15,
                }
            case YoutubeVideoDownloadThread.EXTENSIONS.MP4:
                options = {
                    "format": format,
                    "ffmpeg_location": ffmpeg_path,
                    "outtmpl": output_template,
                    "merge_output_format": "mp4",
                    "quiet": True,
                    "noprogress": True,
                    'progress_hooks': [super()._progress_hook],
                    "concurrent_fragments": 2,
                    "overwrites": True,
                    "postprocessor_hooks": [super()._finish_hook],
                    "socket_timeout": 15,
                }
            case other:
                raise ValueError("You messed up terribly. You should not get this error. Good Luck!")
        super().__init__(url, options, finished_callback, progress_callback)
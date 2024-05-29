import copy
from typing import Any, Callable, Dict, Union

from src.DownloaderCore.formats import YOUTUBE_VIDEO
from src.DownloaderCore.Threads.VideoDownloadThread import VideoDownloadThread


class YoutubeVideoDownloadThread(VideoDownloadThread):
    def __init__(
        self,
        yt_dlp: Any,
        url: str,
        finished_callback: Union[Callable, None] = None,
        progress_callback: Union[Callable, None] = None,
        **options: Dict[str, Any]
    ) -> None:
        """
        Initialize the YoutubeVideoDownloadThread.

        :param yt_dlp: The youtube-dl or yt-dlp instance.
        :param url: The URL of the video to download.
        :param finished_callback: Optional callback function to call when download is finished.
        :param progress_callback: Optional callback function to call to report download progress.
        :param options: Additional options for video download configuration.
        :raises ValueError: If an invalid or missing ID is provided.
        """
        new_options = self._get_new_options(options)

        new_options["progress_hooks"] = [self._progress_hook]
        new_options["postprocessor_hooks"] = [self._finish_hook]

        self._update_options_with_user_input(new_options, options)

        super().__init__(yt_dlp, url, new_options, finished_callback, progress_callback)

    def _get_new_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve the yt_dlp options based on the provided ID.

        :param options: The user-provided options.
        :return: A dictionary of yt_dlp options.
        :raises ValueError: If an invalid or missing ID is provided.
        """
        new_options = {}
        for option in YOUTUBE_VIDEO["video_formats"] + YOUTUBE_VIDEO["audio_formats"]:
            if "ID" in options and options["ID"] == option["ID"]:
                new_options = copy.deepcopy(option["yt_dlp_options"])
                break

        if not new_options:
            raise ValueError("Invalid or missing ID")

        return new_options

    def _update_options_with_user_input(
        self, new_options: Dict[str, Any], options: Dict[str, Any]
    ) -> None:
        """
        Update the new options with user-provided input.

        :param new_options: The initial yt_dlp options.
        :param options: The user-provided options.
        """
        for key in options:
            if key in new_options:
                if new_options[key] is not None and "{" in new_options[key]:
                    new_options[key] = new_options[key].format(options[key])
                else:
                    new_options[key] = options[key]

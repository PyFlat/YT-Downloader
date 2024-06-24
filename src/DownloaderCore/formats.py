BASE_OPTIONS = {
    "socket_timeout": 15,
    "quiet": True,
    "noprogress": True,
    "overwrites": None,
    "ffmpeg_location": None,
    "outtmpl": None,
    "updatetime": False,
    "progress_hooks": [],
    "postprocessor_hooks": [],
}

BASE_YOUTUBE_OPTIONS_VIDEO = {
    **BASE_OPTIONS,
    "concurrent_fragments": 2,
    "outtmpl": "{}/%(title)s (%(height)sp).%(ext)s",
}

BASE_YOUTUBE_OPTIONS_AUDIO = {**BASE_OPTIONS, "outtmpl": "{}/%(title)s.%(ext)s"}

X_VIDEO = {
    "webpage_url_domain": "x.com",
    "video_formats": [
        {
            "extension": "MP4",
            "ID": "video/mp4/best",
            "best_format": True,
            "yt_dlp_options": {
                **BASE_YOUTUBE_OPTIONS_VIDEO,
                "merge_output_format": "mp4",
                "format": "bv*+ba[ext=m4a]/b",
            },
        },
    ],
}

TIKTOK_VIDEO = {
    "webpage_url_domain": "tiktok.com",
    "video_formats": [
        {
            "extension": "MP4",
            "ID": "video/mp4/best",
            "best_format": True,
            "yt_dlp_options": {
                **BASE_YOUTUBE_OPTIONS_VIDEO,
                "merge_output_format": "mp4",
                "format": "bv*+ba[ext=m4a]/b",
            },
        },
    ],
}

YOUTUBE_VIDEO = {
    "webpage_url_domain": "youtube.com",
    "resolutions": [
        "4320p",
        "2160p",
        "1440p",
        "1080p",
        "720p",
        "480p",
        "360p",
        "240p",
        "144p",
    ],
    "video_formats": [
        {
            "extension": "MP4",
            "ID": "video/mp4/custom_res",
            "best_format": False,
            "yt_dlp_options": {
                **BASE_YOUTUBE_OPTIONS_VIDEO,
                "merge_output_format": "mp4",
                "format": "bv[height<={}]+ba[ext=m4a]/b",
            },
        },
        {
            "extension": "MP4",
            "ID": "video/mp4/best",
            "best_format": True,
            "yt_dlp_options": {
                **BASE_YOUTUBE_OPTIONS_VIDEO,
                "merge_output_format": "mp4",
                "format": "bv*+ba[ext=m4a]/b",
            },
        },
        {
            "extension": "MKV",
            "ID": "video/mkv/best",
            "best_format": True,
            "yt_dlp_options": {
                **BASE_YOUTUBE_OPTIONS_VIDEO,
                "merge_output_format": "mkv",
                "format": "bv*+ba[ext=m4a]/b",
            },
        },
        {
            "extension": "AVI",
            "ID": "video/avi/best",
            "best_format": True,
            "yt_dlp_options": {
                **BASE_YOUTUBE_OPTIONS_VIDEO,
                "merge_output_format": "avi",
                "format": "bv*+ba[ext=m4a]/b",
            },
        },
    ],
    "audio_formats": [
        {
            "extension": "MP3",
            "ID": "audio/mp3/best",
            "best_format": True,
            "yt_dlp_options": {
                **BASE_YOUTUBE_OPTIONS_AUDIO,
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            },
        },
        {
            "extension": "M4A",
            "ID": "audio/m4a/best",
            "best_format": True,
            "yt_dlp_options": {
                **BASE_YOUTUBE_OPTIONS_AUDIO,
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "m4a",
                        "preferredquality": "192",
                    }
                ],
            },
        },
    ],
}

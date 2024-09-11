def create_video_format(
    extension: str, merge_format: str, format_string: str, best_format=True
) -> dict:
    return {
        "extension": extension,
        "ID": f"video/{extension.lower()}/{ 'best' if best_format else 'custom_res'}",
        "best_format": best_format,
        "yt_dlp_options": {
            **BASE_YOUTUBE_OPTIONS_VIDEO,
            "merge_output_format": merge_format,
            "format": format_string,
        },
    }


def create_audio_format(extension: str, codec: str, quality=192):
    return {
        "extension": extension,
        "ID": f"audio/{extension.lower()}/best",
        "best_format": True,
        "yt_dlp_options": {
            **BASE_YOUTUBE_OPTIONS_AUDIO,
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": codec,
                    "preferredquality": str(quality),
                }
            ],
        },
    }


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

RESOLUTIONS = [
    "4320p",
    "2160p",
    "1440p",
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p",
    "144p",
]

# X Video configuration
X_VIDEO = {
    "video_formats": [
        create_video_format("MP4", "mp4", "bv*+ba[ext=m4a]/b"),
    ],
}

# TikTok Video configuration
TIKTOK_VIDEO = {
    "video_formats": [
        create_video_format("MP4", "mp4", "bv*+ba[ext=m4a]/b"),
    ],
}

# Twitch Video configuration
TWITCH_VIDEO = {
    "video_formats": [
        create_video_format("MP4", "mp4", "bv*+ba[ext=m4a]/b"),
    ],
}

# Twitch Video configuration
ZDF_VIDEO = {
    "video_formats": [
        create_video_format("MP4", "mp4", "bv*+ba[ext=m4a]/b"),
    ],
}

# YouTube Video configuration
YOUTUBE_VIDEO = {
    "resolutions": RESOLUTIONS,
    "video_formats": [
        create_video_format(
            "MP4", "mp4", "bv[height<={}]+ba[ext=m4a]/b", best_format=False
        ),
        create_video_format("MP4", "mp4", "bv*+ba[ext=m4a]/b"),
        create_video_format("MKV", "mkv", "bv*+ba[ext=m4a]/b"),
        create_video_format("AVI", "avi", "bv*+ba[ext=m4a]/b"),
    ],
    "audio_formats": [
        create_audio_format("MP3", "mp3"),
        create_audio_format("M4A", "m4a"),
    ],
}

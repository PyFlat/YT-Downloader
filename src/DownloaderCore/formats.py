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

[
    {
        "id": "0",
        "url": "https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/04b966316b4147c192674791705b6028_1640704739?lk3s=81f88b70&nonce=50009&refresh_token=f7cb2f97e95a00e83faeaa25a31d5699&x-expires=1719349200&x-signature=miX36KuI1OrFZmiv5iHW5qkI3hQ%3D&shp=81f88b70&shcp=-",
    },
    {
        "id": "1",
        "url": "https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/98a991d5264c4aec8d910290f5dfb10e_1640704740?lk3s=81f88b70&nonce=16520&refresh_token=ff1181d1770bb5f969f58ff08ecb1ab7&x-expires=1719349200&x-signature=ajaGxJPabwvQVpsg1g%2Fdl1vIRd8%3D&shp=81f88b70&shcp=-",
    },
    {
        "id": "2",
        "url": "https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/e314b86a7e6e46d7b3d1e0f7aec3ebb9?lk3s=81f88b70&nonce=72119&refresh_token=e1d61015b5ea400d96e6112dd3e65bc1&x-expires=1719349200&x-signature=S5z83GeSnVUJIyry0Kr0xDAJLhE%3D&shp=81f88b70&shcp=-",
    },
]

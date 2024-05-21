YOUTUBE_VIDEO = {
    "webpage_url_domain": "youtube.com",
    "video_formats": [
        {
            "extension": "MP4",
            "yt_dlp_options": {
                "socket_timeout": 15,
                "quiet": True,
                "noprogress": True,
                "concurrent_fragments": 2,
                "merge_output_format": "mp4",
                "overwrites": None,                     # True; False
                "format": None,                         # bv[height<= RESOLUTION ]+ba[ext=m4a]/b; bv*+ba[ext=m4a]/b
                "ffmpeg_location": None,                # FFmpeg Path != None
                "outtmpl": None,                        # {OUTPUTPATH}/%(title)s (%(height)sp).%(ext)s
                "progress_hooks": [],                   # progress_hook
                "postprocessor_hooks": [],              # finish_hook
            },
        }
    ],
    "audio_formats": [
        {
            "extension": "MP3",
            "yt_dlp_options": {
                "socket_timeout": 15,
                "quiet": True,
                "noprogress": True,
                "overwrites": None,                     # True; False
                "format": "bestaudio/best",
                "ffmpeg_location": None,                # FFmpeg Path != None
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": None,                        # {OUTPUTPATH}/%(title)s.%(ext)s
                "progress_hooks": [],                   # progress_hook
                "postprocessor_hooks": [],              # finish_hook
            },
        }
    ],
}

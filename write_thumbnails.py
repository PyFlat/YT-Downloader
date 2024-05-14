import os
from yt_dlp import YoutubeDL

def download_thumbnails(video_url, output_folder="thumbnails"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts = {
        'skip_download': True,
        'write_all_thumbnails': True,
        'outtmpl': os.path.join(output_folder, '%(id)s.%(ext)s')
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

download_thumbnails("https://www.youtube.com/watch?v=JSuWJoDWoJI")

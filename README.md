# YT-Downloader
A YouTube Downloader, using tkinter, yt-dlp, customtkinter

## FFmpeg is required for full funcionality:
- If FFmpeg is under this path "C:/FFmpeg/bin" everything is ok
- Otherwise you have to create a "ffmpeg.txt" file in the same folder the "YT Downloader.exe" is
- In this file you put your path to the "ffmpeg/bin" folder
- Use "/" instead of "\\" 
- If you copy the path out of windows you have to replace them

## How to use:
- Download the "YT Downloader.exe"
- Execute it
- If Windows defender pops up, you have to trust us
- Insert a Video or Playlist URL in the Top entry
- Select the Format (Supported: MP3, MP4)
- If you selected mp4 and the url is a video not a playlist you can select the resolution of the video
- If you inserted a playlist you can choose which range will be downloaded
- e.g. you open the selection window and insert 5 in the left and 7 in the right entry:
- The downloader will now download the videos 5,6,7 of the playlist
- If you have selected your download location (Default: Downloads) you can click on "Start Download"

## Changelog:
- Bug Fixing
- Changed Functionality using yt-dlp to get video and playlist information isntead of apafy and pytube
- Updated Modules
- Implemented partial playlist download function
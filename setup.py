
from __future__ import annotations


from cx_Freeze import Executable, setup

try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    get_qt_plugins_paths = None

include_files = ["appdata", "languages"]

if get_qt_plugins_paths:
    include_files += get_qt_plugins_paths("PySide6", "platform")

base = "Win32GUI"

build_exe_options = {
    "optimize": 2,
    "includes": [
        "optparse",
        "html.parser",
        "uuid",
        "fileinput",
    ],
    "excludes": [
        "tkinter",
        "yt_dlp"],
    "include_files": include_files,
    "zip_include_packages": ["PySide6"],
}

executables = [Executable("main.py", base=base, icon="appdata/images/app-icon.ico")]

setup(
    name="youtube_downloader",
    version="1.3.2",
    description="Youtube Downloader",
    options={"build_exe": build_exe_options},
    executables=executables,
)

from PySide6.QtCore import Qt
from qfluentwidgets import InfoBadge

from src.DownloaderCore.Downloader import Downloader
from src.DownloaderCore.DownloadManager import download_manager_instance
from src.GUI.CustomWidgets.DownloadWidgets.BaseDownloadWidget import BaseDownloadWidget
from src.GUI.CustomWidgets.DownloadWidgets.PlaylistDownloadWidget import (
    PlaylistDownloadWidget,
)
from src.GUI.CustomWidgets.DownloadWidgets.VideoDownloadWidget import (
    VideoDownloadWidget,
)
from src.GUI.Interfaces.DownloadInterface import DownloadInterface


class DownloadWidgetManager:
    def __init__(self):
        self.info_badge = None
        self.download_interface = None
        self.downloader = None
        self.widgets: list[BaseDownloadWidget] = []

    def setInterface(
        self,
        info_badge: InfoBadge,
        download_interface: DownloadInterface,
        downloader: Downloader,
    ):
        self.info_badge = info_badge
        self.download_interface = download_interface
        self.downloader = downloader

    def addVideoDownloadWidget(
        self,
        widget_information: dict = {},
        **options,
    ):
        if self.download_interface == None:
            return

        is_playlist = widget_information.get("selected-ids") != []
        cur_downloads = 0
        max_downloads = len(widget_information.get("selected-ids"))

        job_str = download_manager_instance.formatTaskString(
            widget_information.get("url"), widget_information.get("format-id")
        )

        if not download_manager_instance.isTask(job_str):
            download_manager_instance.addTask(job_str)
        else:
            return

        self.info_badge.setText(str(download_manager_instance.getTaskCount()))
        if is_playlist:
            download_widget = PlaylistDownloadWidget(
                self.download_interface, widget_information
            )
        else:
            download_widget = VideoDownloadWidget(
                self.download_interface, widget_information
            )
        self.widgets.append(download_widget)
        self.download_interface.verticalLayout.addWidget(
            download_widget, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter
        )

        def start():
            print(f"Download started")

        def progress(result: dict):
            if result.get("postprocessing"):
                download_widget.updatePostProcessStatus(result)
            else:
                download_widget.updateStatus(result)

        def finish(success, url):
            nonlocal cur_downloads, max_downloads
            download_widget.finishStatus(success, url)
            cur_downloads += 1
            if not is_playlist or cur_downloads == max_downloads:
                download_manager_instance.removeTask(job_str)
                self.info_badge.setText(str(download_manager_instance.getTaskCount()))

        if is_playlist:
            self.downloader.download_playlist(
                url=widget_information.get("url"),
                start_callback=start,
                progress_callback=progress,
                finish_callback=finish,
                playlist_items=widget_information.get("selected-ids"),
                **options,
            )
        else:
            self.downloader.downloadVideo(
                url=widget_information.get("url"),
                start_callback=start,
                progress_callback=progress,
                finish_callback=finish,
                **options,
            )

    def updateDownloadWidgets(self):
        for widget in self.widgets:
            widget.update_pixmap()


download_widget_manager = DownloadWidgetManager()

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from src.DownloaderCore.Downloader import Downloader
from src.DownloaderCore.DownloadManager import download_manager_instance
from src.GUI.CustomWidgets.VideoDownloadWidget import VideoDownloadWidget
from src.GUI.Interfaces.DownloadInterface import DownloadInterface


class DownloadWidgetManager:
    def __init__(self):
        self.download_interface = None
        self.downloader = None
        self.widgets = []

    def setInterface(
        self, download_interface: DownloadInterface, downloader: Downloader
    ):
        self.download_interface = download_interface
        self.downloader = downloader

    def addVideoDownloadWidget(
        self,
        thumbnail_url,
        title,
        channel,
        format_id,
        url,
        selected_ids: list[int] = None,
        **options,
    ):
        if self.download_interface == None:
            return

        job_str = download_manager_instance.formatTaskString(url, format_id)

        # if not download_manager_instance.isTask(job_str):
        #     download_manager_instance.addTask(job_str)
        # else:
        #     return

        download_widget = VideoDownloadWidget(
            self.download_interface, thumbnail_url, title, channel, format_id
        )
        self.widgets.append(download_widget)
        self.download_interface.verticalLayout.addWidget(
            download_widget, 0, Qt.AlignTop | Qt.AlignCenter
        )

        def start():
            print(f"Download started")

        def progress(result: dict):
            if result.get("postprocessing"):
                download_widget.updatePostProcessStatus(result)
            else:
                download_widget.updateStatus(result)

        def finish(success):
            download_widget.finishStatus(success)
            download_manager_instance.removeTask(job_str)

        if selected_ids != []:
            self.downloader.download_playlist(
                url, start, progress, finish, selected_ids, **options
            )
        else:
            self.downloader.downloadVideo(url, start, progress, finish, **options)


download_widget_manager = DownloadWidgetManager()

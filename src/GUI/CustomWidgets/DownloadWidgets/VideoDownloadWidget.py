from src.GUI.CustomWidgets.DownloadWidgets.BaseDownloadWidget import BaseDownloadWidget
from src.GUI.Interfaces.DownloadInterface import DownloadInterface


class VideoDownloadWidget(BaseDownloadWidget):
    def __init__(self, parent: DownloadInterface = None, widget_information: dict = {}):
        super().__init__(parent, widget_information)
        self.last_eta = 0
        self.last_speed = ""

    def updateStatus(self, status_dict: dict):

        downloaded_bytes = status_dict.get("downloaded_bytes", 0)
        total_bytes = status_dict.get("total_bytes") or status_dict.get(
            "total_bytes_estimate"
        )
        if total_bytes:
            progress = round(100 * downloaded_bytes / total_bytes)
        else:
            progress = 0

        eta = status_dict.get("_eta_str", self.last_eta)
        if eta != "Unknown":
            self.last_eta = eta
        else:
            eta = self.last_eta

        speed = status_dict.get("_speed_str", self.last_speed).lstrip()
        if "Unknown" not in speed:
            self.last_speed = speed
        else:
            speed = self.last_speed

        total_size = status_dict.get("_total_bytes_str", "N/A").lstrip()
        if total_size == "N/A":
            total_size = status_dict.get("_total_bytes_estimate_str", "???").lstrip()
            total_size = "~" + total_size
        text_to_set = f"{progress}% of {total_size} at ({speed}) - {eta} left"

        super().updateStatus(progress, text_to_set, "Status: Downloading...")

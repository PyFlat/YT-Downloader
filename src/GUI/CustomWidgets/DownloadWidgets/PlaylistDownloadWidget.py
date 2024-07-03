from PySide6.QtGui import QColor

from src.GUI.CustomWidgets.DownloadWidgets.BaseDownloadWidget import BaseDownloadWidget
from src.GUI.CustomWidgets.PLSmallDownloadWidget import PLSmallDownloadWidget
from src.GUI.Interfaces.DownloadInterface import DownloadInterface


class PlaylistDownloadWidget(BaseDownloadWidget):
    def __init__(self, parent: DownloadInterface = None, widget_information: dict = {}):
        super().__init__(parent, widget_information, True)
        self.widget_information = widget_information

        self.downloadWidgets = {}

        self.finishedWidgets = {}

        self.__total_videos = len(self.widget_information.get("selected-ids"))

        self.__failed = 0

        self.__addVideosToDownloadList()

        progress_text = f"0/{self.__total_videos} Videos downloaded"

        super().updateStatus(0, progress_text)

    def __addVideosToDownloadList(self):
        entries: list = self.widget_information.get("playlist-entries")
        for id in self.widget_information.get("selected-ids"):
            entry: dict = entries[id - 1]
            widget = super().addDownloadLabel(entry.get("title"), entry.get("uploader"))
            self.downloadWidgets[entry.get("id")] = widget

    def updateStatus(self, status_dict: dict[dict, str]):
        # with open("data.json", "a+") as file:
        #     file.write(json.dumps(status_dict))
        display_id = status_dict.get("info_dict").get("display_id")
        if display_id in self.downloadWidgets:
            widget: PLSmallDownloadWidget = self.downloadWidgets.get(display_id)
            percent = status_dict.get("_percent_str").replace("%", "").lstrip()
            widget.set_progress(float(percent))

    def finishStatus(self, success, id):
        if id not in self.downloadWidgets:
            raise KeyError("You should not get this error!")
        widget: PLSmallDownloadWidget = self.downloadWidgets.pop(id)
        if not success:
            widget.set_progress(0)
            self.__failed += 1
            widget.add_shadow_effect(QColor(255, 0, 0, 180))
        else:
            widget.add_shadow_effect(QColor(0, 200, 60, 150))
        self.finishedWidgets[id] = widget
        finishedVids = len(self.finishedWidgets)

        if finishedVids != self.__total_videos:
            completed = (finishedVids / self.__total_videos) * 100
            progress_text = f"{finishedVids}/{self.__total_videos} Videos downloaded"
            status_text = "Status: Downloading..."
        else:
            completed = 100
            progress_text = f"Download of {self.__total_videos} videos finished ({self.__failed} failed)"
            status_text = "Status: Download finished"

        super().updateStatus(completed, progress_text, status_text)

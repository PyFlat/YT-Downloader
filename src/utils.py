def transformVideoDuration(duration_secs: int = 0) -> str:
    minutes, seconds = divmod(duration_secs, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        duration = (
            f"{hours:02.0f} hours, {minutes:02.0f} minutes, {seconds:02.0f} seconds"
        )
    elif minutes > 0:
        duration = f"{minutes:02.0f} minutes, {seconds:02.0f} seconds"
    else:
        duration = f"{seconds:02.0f} seconds"

    return duration


def getPlaylistSum(entries: list) -> int:
    return sum(
        [entry["duration"] if entry["duration"] is not None else 0 for entry in entries]
    )


from qfluentwidgets import FluentWindow

from src.GUI.Interfaces.SettingInterface import SettingInterface


def checkForFFmpegBinaries() -> bool:
    import os

    from src.Config.Config import cfg

    return os.path.isfile(f"{cfg.get(cfg.ffmpeg_path)}/ffmpeg.exe") and os.path.isfile(
        f"{cfg.get(cfg.ffmpeg_path)}/ffprobe.exe"
    )


def checkForFFmpegDialog(
    parent: FluentWindow, setting_interface: SettingInterface
) -> bool:
    ffmpeg_existing = checkForFFmpegBinaries()
    if not ffmpeg_existing:
        from PySide6.QtGui import Qt
        from qfluentwidgets import MessageBox, PrimaryPushButton, PushButton

        def on_btn_clicked(btn_type: str):
            msgb.close()
            match btn_type:
                case "start_download":
                    parent.switchTo(setting_interface)
                    setting_interface.downloadFFmpegCard.button.click()
                case "set_ffmpeg_path":
                    parent.switchTo(setting_interface)
                    setting_interface.ffmpegPathCard.button.click()
                case _:
                    pass

        title = "FFmpeg or FFprobe Missing"
        content = (
            "FFmpeg and/or FFprobe were not found on your system. These components are required for the downloader to function correctly. "
            "Please download and install them, or manually set the path to the installation binaries."
        )

        msgb = MessageBox(title, content, parent)
        msgb.yesButton.setVisible(False)
        msgb.cancelButton.setVisible(False)

        start_download_btn = PrimaryPushButton("Download FFmpeg", msgb.buttonGroup)
        set_ffmpeg_path_btn = PrimaryPushButton("Set FFmpeg Path", msgb.buttonGroup)
        cancel_btn = PushButton("Cancel", msgb.buttonGroup)

        start_download_btn.clicked.connect(lambda: on_btn_clicked("start_download"))
        set_ffmpeg_path_btn.clicked.connect(lambda: on_btn_clicked("set_ffmpeg_path"))
        cancel_btn.clicked.connect(lambda: on_btn_clicked("cancel"))

        msgb.buttonLayout.addWidget(
            start_download_btn, 1, Qt.AlignmentFlag.AlignVCenter
        )
        msgb.buttonLayout.addWidget(
            set_ffmpeg_path_btn, 1, Qt.AlignmentFlag.AlignVCenter
        )
        msgb.buttonLayout.addWidget(cancel_btn, 1, Qt.AlignmentFlag.AlignVCenter)

        msgb.exec()

class DownloadManager:
    def __init__(self) -> None:
        self.jobs: list[str] = []

    def addTask(self, job: str, throw_error: bool = True) -> bool:
        if job in self.jobs:
            if throw_error:
                raise ValueError(
                    f"Cannot add job for {job}.\n This job does already exist. Active Jobs:\n{'[' + ','.join(self.jobs)+']'}"
                )
            return False
        self.jobs.append(job)
        return True

    def removeTask(self, job: str, throw_error: bool = True) -> bool:
        if not job in self.jobs:
            if throw_error:
                raise ValueError(
                    f"Cannot remove job for {job}.\n This job does not exist. Active Jobs:\n{'[' + ','.join(self.jobs)+']'}"
                )
            return False
        self.jobs.remove(job)
        return True

    def formatTaskString(
        self,
        video_url: str,
        format_info: str,
        use_playlist_seperation: bool = False,
        playlist_url: str = "",
    ) -> str:
        if use_playlist_seperation:
            if playlist_url == "":
                raise ValueError(
                    f"Cannot format playlist-seperated task without valid playlist."
                )
            return (
                f"[URL: {video_url} | FORMAT: {format_info} | PLAYLIST: {playlist_url}]"
            )
        return f"[URL: {video_url} | FORMAT: {format_info}]"

    def isTask(self, job: str) -> bool:
        return job in self.jobs


download_manager_instance = DownloadManager()

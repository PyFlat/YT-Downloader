def transformVideoDuration(duration_secs: int = 0) -> str:
    minutes, seconds = divmod(duration_secs, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        duration = f"{hours:02} hours, {minutes:02} minutes, {seconds:02} seconds"
    elif minutes > 0:
        duration = f"{minutes:02} minutes, {seconds:02} seconds"
    else:
        duration = f"{seconds:02} seconds"

    return duration


def getPlaylistSum(entries: list) -> int:
    return sum(
        [entry["duration"] if entry["duration"] is not None else 0 for entry in entries]
    )

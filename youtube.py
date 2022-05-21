"""All things youtube"""


def upload_video(filepath, video_name, video_description, tags=None):
    """Uploads a given file to youtube"""
    # TODO fill this
    raise NotImplementedError


def get_date_and_number_from_filepath(filepath):
    chunks = filepath.split("_")
    date = chunks[-2]
    idx = chunks[-1]
    return date, idx


def db_to_youtube(video: dict):
    """Uploads a given video object (look at db.py for more information about
    the video object) to Youtube - and returns a new video object with the
    youtube information in it"""
    if video.get("youtube_id"):
        return video

    if not ("date" in video and "idx" in video):
        date, idx = get_date_and_number_from_filepath(video.converted_filepath)
        video.date = date
        video.idx = idx

    video.youtube_id = upload_video(
        video["converted_filepath"],
        f"River Session on {video.date} - #{video.idx}",
        f"A video from our trip to the river on {video.date}",
        tags=None,
    )
    return video

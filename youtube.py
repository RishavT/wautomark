"""All things youtube"""

def upload_video(filepath, video_name, video_description, tags=None):
    """Uploads a given file to youtube"""
    # TODO fill this
    raise NotImplementedError

def get_name_from_filepath(filepath):
    chunks = filepath.split("_")
    date = chunks[-2]
    number = chunks[-1]
    return f"River Session on {date} - #{number}"

def db_to_youtube(video: dict):
    """Uploads a given video object (look at db.py for more information about
    the video object) to Youtube - and returns a new video object with the
    youtube information in it"""
    if video.get("youtube_id"):
        return video

    video["youtube_id"] = upload_video(
        video["converted_filepath"],
        get_name_from_filepath(video["converted_filepath"]),
        "",
        tags=None)
    return video



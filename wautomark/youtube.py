"""All things youtube"""
import os
import sys
from io import StringIO
from youtube_upload import main as youtube_main


class YoutubeAuthenticationError(Exception):
    pass


def upload_video(
    filepath,
    video_name,
    video_description,
    visibility="unlisted",
    tags=None,
    fix_auth=False,
):
    """Uploads a given file to youtube"""
    # First patch youtube_main to save the output in a string
    original_run_main = youtube_main.run_main
    yt_out = StringIO(" ")

    def new_run_main(*args, **kwargs):
        kwargs["output"] = yt_out
        return original_run_main(*args, **kwargs)

    youtube_main.run_main = new_run_main

    # Now we patch the auth mechanism to fail if not found (instead of try to
    # get interactively)
    if not fix_auth:

        def raise_auth_error(*args, **kwargs):
            raise YoutubeAuthenticationError(
                "Auth failed. Please log in via SSH and run `python youtube.py auth`"
            )

        youtube_main.auth._get_credentials_interactively = raise_auth_error
    # End of patch

    # now upload the video
    youtube_main.main(
        [
            f"--title={video_name}",
            f"--privacy={visibility}",
            "--client-secrets=youtube_secrets.json",
            "--credentials-file=youtube_creds.json",
            filepath,
        ]
    )
    video_id = yt_out.getvalue().strip()
    print(f"video ID: {video_id}")
    return video_id


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


def test_upload(args):
    filepath = args[0]
    name = os.path.basename(filepath)
    description = name
    upload_video(filepath, name, description)


def fix_auth(args):
    filepath = "youtube-auth-dummy.mp4"
    name = os.path.basename(filepath)
    description = name
    upload_video(filepath, name, description, fix_auth=True)


if __name__ == "__main__":
    if sys.argv[1] == "upload":
        test_upload(sys.argv[2:])
    elif sys.argv[1] == "fix_auth":
        fix_auth(sys.argv[2:])

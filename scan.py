"""Scans for new hard drives and adds watermarks videos"""

import logging
import sys
import os
import shutil
from datetime import date
from video import VideoManager
from drive import upload_to_folder, get_folder_link_from_id

OUTPUT_DIRECTORY = os.path.join(os.getenv("HOME"), "video_output")
INPUT_DIRECTORY = os.path.join(os.getenv("HOME"), "video_input")
PROCESSED_DIRECTORY = os.path.join(os.getenv("HOME"), "processed_raw")
INITIAL = set()

logger = logging.getLogger("wautomark")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def get_uid():
    """Returns a unique prefix for all the files"""
    return f"t4a_videos_{str(date.today())}"


def get_drives():
    out = os.popen("df").read()
    out = out.split("\n")[1:]
    drives = set()
    for line in out:
        if "\t" in line:
            words = line.split("\t")
        else:
            words = line.split(" ")
        drivename = words[0].strip()
        mountpoint = words[-1].strip()
        drives.add((drivename, mountpoint))

    return drives


def process_ghosts():
    # TODO implement this
    pass


def cleanup():
    logger.info("Cleaning up")
    paths = os.popen(f"find {INPUT_DIRECTORY}").read().split("\n")
    files = [p for p in paths if p.endswith("mp4")]
    if not files:
        shutil.rmtree(INPUT_DIRECTORY)
    else:
        logger.error("There are gost videos in the input directory")


def setup():
    logging.info("setting up")
    INITIAL.update(get_drives())
    for directory in [
        OUTPUT_DIRECTORY,
        INPUT_DIRECTORY,
        PROCESSED_DIRECTORY,
    ]:
        os.system(f"mkdir -p {directory}")


def fail(*args):
    with open(os.path.join(os.getenv("HOME"), "failed.txt"), "w") as thefile:
        thefile.write("FAILED: {','.join(args)}")


def get_mp4s(folder):
    out = os.popen(f"find {folder}").read().split("\n")
    out = [x.strip() for x in out]
    mp4s = [x for x in out if x.lower().endswith("mp4")]
    return mp4s


def should_add(folder):
    """Check if this drive needs to be added"""
    try:
        with open(os.path.join(folder, "wautomark_add"), encoding="utf-8") as file:
            if file.read().lower().strip() == "yes":
                return True
    except FileNotFoundError:
        pass

    # Check if this is a go pro folder
    has_gopro_videos = bool(
        os.popen(f"find {folder} | grep -i 'gopro.*mp4'").read().strip()
    )
    return has_gopro_videos


def add_drive(drivename, mountpoint, upload_to_drive=True, force=False):
    # Check if this drive needs to be added
    if not (force or should_add(mountpoint)):
        logger.info(f"Skipping drive {drivename}: {mountpoint}")
        return

    uid = get_uid()
    logger.info("Adding drive %s:%s, uid: %s", drivename, mountpoint, uid)

    mp4s = get_mp4s(mountpoint)
    if not mp4s:
        logger.info("Nothing to add. exiting")
        return

    logger.info("Creating input directory for %s", uid)
    unique_input_dir = os.path.join(INPUT_DIRECTORY, uid)
    try:
        os.mkdir(unique_input_dir)
    except FileExistsError:
        pass
    except Exception as e:
        logger.exception(e)
        fail(drivename, mountpoint, uid)
        return

    for source in mp4s:
        if source.endswith("processed.mp4"):
            logging.error("Duplicate file %s", source)
            continue
        filename = os.path.split(source)[1]
        dest = os.path.join(unique_input_dir, filename)
        shutil.copy(source, dest)

        logger.info("Copied %s from drive to %s", filename, unique_input_dir)
        logger.info("Converting")

        vm = VideoManager(
            watermark_path="watermark.png",
            watermark_text=open("watermark.txt").read(),
            audio_path="audio.mp3",
            output_dir=OUTPUT_DIRECTORY,
            uid=uid,
        )
        converted_path = vm.add(source, dest, preview=False)

        if upload_to_drive:
            logger.info(f"Uploading %s to drive", converted_path)
            file_id, folder_id = upload_to_folder(converted_path)
            logger.info(
                "Uploaded %s to %s",
                os.path.basename(converted_path),
                get_folder_link_from_id(folder_id),
            )

        logger.info("Removing original file")
        assert os.path.isfile(source)
        os.remove(source)
        shutil.move(
            dest, os.path.join(PROCESSED_DIRECTORY, f"{filename}.{uid}.processed.mp4")
        )


def scan():
    """Scans and returns new drives"""
    setup()
    new_drives = get_drives() - INITIAL
    for drive in new_drives:
        add_drive(*drive)
    cleanup()
    process_ghosts()


def test(folder_name):
    """Tests adding a folder"""
    drivename = "testdrive"
    add_drive(drivename, folder_name)


if __name__ == "__main__":
    test(sys.argv[1])

import os
import sys
import json
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    ImageClip,
)
from moviepy.audio.fx.audio_loop import audio_loop
from loggers import logger, tg_logger, CustomProgressLogger
from db import Videos

"""Code to process videos"""


class VideoManager:

    serialize_fields = [
        "original_filepath",
        "copied_filepath",
        "converted_filepath",
        "original_hash",
        "converted_hash",
    ]

    class VideoAlreadyConverted(ValueError):
        def __init__(self, *args, video=None, **kwargs):
            self.video = video
            super().__init__(*args, **kwargs)

    def __init__(
        self,
        fps=30,
        watermark_path="",
        watermark_text="",
        audio_path="",
        output_dir="output",
        final_height=1080,
        big_watermark_scale=0.30,
        get_new_idx=None,
        get_videos=None,
        update_videos=None,
        uid=None,
    ):
        self.fps = fps
        self.watermark_path = watermark_path
        self.watermark_text = watermark_text
        self.audio_path = audio_path
        self.output_dir = output_dir
        self.final_height = final_height
        self.big_watermark_scale = big_watermark_scale
        self.uid = uid
        self.original_filepath = None
        self.copied_filepath = None
        self.converted_filepath = None
        self.original_hash = None
        self.converted_hash = None
        self.get_new_idx = get_new_idx
        self.get_videos = get_videos
        self.update_videos = update_videos

        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    @classmethod
    def append_to_filepath(cls, filepath, *args):
        """Appends a string to the file name before the extension. You can pass
        everything that you want to append as subsequent args after the
        filepath

        Example:
            cls.append_to_filepath("hello/world.txt", "a", "b")
            will return hello/worldab.txt
        """
        no_ext, ext = os.path.splitext(filepath)
        for to_append in args:
            no_ext += to_append
        return no_ext + ext

    @classmethod
    def hashit(cls, path):
        return os.popen(f"md5sum {path}").read().split()[0]

    def to_dict(self):
        the_dict = {}
        for field in self.serialize_fields:
            the_dict[field] = getattr(self, field)
        return the_dict

    def save_drive_file_id(self, file_id):
        video = self.get_videos().get(self.original_filepath)
        video["drive_id"] = file_id
        self.update_videos(self.original_filepath, video)

    def add(self, original_filepath, filepath, preview=False):
        """Does the following:
        1. Resize the video to match self.final_height
        2. Add a watermark to the video
        3. Replace audio with some random music
        4. Save to self.output_dir
        """

        self.original_filepath = original_filepath
        self.copied_filepath = filepath
        self.original_hash = self.hashit(original_filepath)
        if not preview:
            for key, video in self.get_videos().items():
                if self.original_hash == video["original_hash"]:
                    original_basename = os.path.basename(video["original_filepath"])
                    raise self.VideoAlreadyConverted(
                        f"{original_basename} has already been converted", video=video
                    )
        self.converted_filepath = os.path.join(
            self.output_dir,
            f"{self.uid}_{self.get_new_idx()}.mp4",
        )

        # Create moviepie obj without audio
        clip = VideoFileClip(filepath, audio=False)

        # Resize the video to self.final_height
        clip = clip.resize((self.final_height * clip.w / clip.h), self.final_height)

        # Add a center watermark
        duration = clip.duration

        center_watermark = ImageClip(self.watermark_path)
        center_watermark = center_watermark.resize(
            (
                clip.w * self.big_watermark_scale,
                clip.w
                * self.big_watermark_scale
                * center_watermark.h
                / center_watermark.w,
            )
        )
        center_watermark = center_watermark.set_pos("center")

        # Add a bottom watermark
        bottom_watermark = TextClip(
            self.watermark_text, color="white", fontsize=24, font="Open-Sans-Regular"
        )
        bottom_watermark = bottom_watermark.set_pos(("center", "center"))
        bottom_watermark = bottom_watermark.on_color(
            size=(clip.w, bottom_watermark.h),
            color=(0, 0, 0),
            pos=("center", "center"),
            col_opacity=0.3,
        )
        bottom_watermark = bottom_watermark.set_pos(("center", "bottom"))
        clip = CompositeVideoClip([clip, center_watermark, bottom_watermark])
        clip.duration = duration

        # Add audio
        audio = AudioFileClip(self.audio_path)
        if duration > audio.duration:
            audio = audio_loop(audio, duration=duration)
        else:
            audio.duration = duration
        clip = clip.set_audio(audio)
        clip.duration = duration

        # Preview or Save the video
        if preview:
            clip.preview()
            return
        clip.write_videofile(
            self.converted_filepath,
            fps=self.fps,
            threads=3,
            codec="libx264",
            logger=CustomProgressLogger(
                additional_loggers_prefix=f"{os.path.basename(self.original_filepath)}: "
            ),
        )
        self.converted_hash = self.hashit(self.converted_filepath)
        self.update_videos(self.original_filepath, self.to_dict())
        return self.converted_filepath

    def add_folder(self, folderpath, *args, extension=None, **kwargs):
        """Adds all files inside a folder. You can filter by extension."""
        for filepath in os.listdir(folderpath):
            if extension and not filepath.lower().endswith(extension):
                continue
            filepath = os.path.join(folderpath, filepath)
            try:
                self.add(filepath, filepath, *args, **kwargs)
            except self.VideoAlreadyConverted as exc:
                logger.exception(exc)
                logger.info(exc.video)


if __name__ == "__main__":
    VideoDB = Videos("test.txt")
    folderpath = "input"
    extension = "mp4"
    watermark_path = "watermark.png"
    watermark_text = "team4adventure"
    audio_path = "audio.mp3"
    preview = len(sys.argv) > 1 and sys.argv[1] == "preview"
    vm = VideoManager(
        watermark_path=watermark_path,
        watermark_text=watermark_text,
        audio_path=audio_path,
        uid="helloworld",
        get_new_idx=VideoDB.get_new_idx,
        get_videos=VideoDB.get_videos,
        update_videos=VideoDB.update_videos,
    )
    vm.add_folder(folderpath, extension=extension, preview=preview)

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
from loggers import logger, tg_logger

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
        fps=24,
        watermark_path="",
        watermark_text="",
        audio_path="",
        output_dir="output",
        final_width=1280,
        big_watermark_scale=0.30,
        uid=None,
    ):
        self.fps = fps
        self.watermark_path = watermark_path
        self.watermark_text = watermark_text
        self.audio_path = audio_path
        self.output_dir = output_dir
        self.final_width = final_width
        self.big_watermark_scale = big_watermark_scale
        self.uid = uid
        self.original_filepath = None
        self.copied_filepath = None
        self.converted_filepath = None
        self.original_hash = None
        self.converted_hash = None

        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    @property
    def videos(self):
        try:
            with open("results.txt") as thefile:
                return json.load(thefile)
        except Exception as e:
            return {}

    @videos.setter
    def videos(self, value):
        with open("results.txt", "w") as thefile:
            return json.dump(value, thefile)

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

    def add(self, original_filepath, filepath, preview=False):
        """Does the following:
        1. Resize the video to match self.final_width
        2. Add a watermark to the video
        3. Replace audio with some random music
        4. Save to self.output_dir
        """

        self.original_filepath = original_filepath
        self.copied_filepath = filepath
        self.original_hash = self.hashit(original_filepath)
        for video in self.videos.values():
            if self.original_hash == video["original_hash"]:
                original_basename = os.path.basename(video["original_filepath"])
                raise self.VideoAlreadyConverted(
                    f"{original_basename} has already been converted", video=video
                )
        self.converted_filepath = os.path.join(
            self.output_dir,
            f"{self.uid}_{len(self.videos.keys()) + 1}.mp4",
        )

        # Create moviepie obj without audio
        clip = VideoFileClip(filepath, audio=False)

        # Resize the video to self.final_width
        clip = clip.resize((self.final_width, self.final_width * clip.h / clip.w))

        # Add a center watermark
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
        duration = clip.duration
        clip = CompositeVideoClip([clip, center_watermark])
        clip.duration = duration

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
        clip = CompositeVideoClip([clip, bottom_watermark])
        clip.duration = duration

        # Add audio
        audio = AudioFileClip(self.audio_path)
        if duration > audio.duration:
            audio = audio_loop(audio, duration=duration)
        clip = clip.set_audio(audio)
        clip.duration = duration

        # Preview or Save the video
        if preview:
            clip.preview()
            return
        clip.write_videofile(self.converted_filepath, fps=self.fps, codec="libx264")
        self.converted_hash = self.hashit(self.converted_filepath)
        videos = self.videos
        videos[self.original_filepath] = self.to_dict()
        self.videos = videos
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
    )
    vm.add_folder(folderpath, extension=extension, preview=preview)

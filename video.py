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

"""Code to process videos"""


class VideoManager:
    def __init__(
        self,
        watermark_path="",
        watermark_text="",
        audio_path="",
        output_dir="output",
        final_width=1280,
        big_watermark_scale=0.30,
    ):
        self.watermark_path = watermark_path
        self.watermark_text = watermark_text
        self.audio_path = audio_path
        self.videos = []
        self.output_dir = output_dir
        self.final_width = final_width
        self.big_watermark_scale = big_watermark_scale
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    def add(self, filepath, preview=False):
        """Does the following:
        1. Resize the video to match self.final_width
        2. Add a watermark to the video
        3. Replace audio with some random music
        4. Save to self.output_dir
        """

        output_path = os.path.join(self.output_dir, f"{len(self.videos) + 1}.mp4")

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
        # audio = audio_loop(audio, duration=clip.duration)
        clip = clip.set_audio(audio)

        # Preview or Save the video
        if preview:
            clip.preview()
            return
        clip.write_videofile(output_path, fps=24, codec="libx264")
        self.videos.append((filepath, output_path))

        with open("results.txt", "w") as thefile:
            json.dump(self.videos, thefile)

    def add_folder(self, folderpath, *args, extension=None, **kwargs):
        """Adds all files inside a folder. You can filter by extension."""
        for filepath in os.listdir(folderpath):
            if extension and not filepath.lower().endswith(extension):
                continue
            self.add(os.path.join(folderpath, filepath), *args, **kwargs)


if __name__ == "__main__":
    folderpath = "input"
    extension = "mp4"
    watermark_path = "watermark.png"
    watermark_text = "team4adventure"
    audio_path = "audio.mp3"
    preview = sys.argv[1] == "preview"
    vm = VideoManager(
        watermark_path=watermark_path,
        watermark_text=watermark_text,
        audio_path=audio_path,
    )
    vm.add_folder(folderpath, extension=extension, preview=preview)

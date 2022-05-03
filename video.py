import os
import json
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    ImageClip,
)

"""Code to process videos"""


class VideoManager:
    def __init__(self, watermark_path="", output_dir="output", final_width=1280):
        self.watermark_path = watermark_path
        self.videos = []
        self.output_dir = output_dir
        self.final_width = final_width
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    def add(self, filepath):
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

        # Add a watermark
        watermark = ImageClip(self.watermark_path)
        watermark = watermark.resize((clip.w, clip.w * watermark.h / watermark.w))
        watermark = watermark.set_pos("center")
        duration = clip.duration
        clip = CompositeVideoClip([clip, watermark])
        clip.duration = duration
        # clip.add_mask(watermark)

        # Replace audio
        # TODO do this

        # Save the video
        clip.write_videofile(output_path, fps=24, codec="libx264")
        self.videos.append((filepath, output_path))

        with open("results.txt", "w") as thefile:
            json.dump(self.videos, thefile)

    def add_folder(self, folderpath, extension=None):
        """Adds all files inside a folder. You can filter by extension."""
        for filepath in os.listdir(folderpath):
            if extension and not filepath.lower().endswith(extension):
                continue
            self.add(os.path.join(folderpath, filepath))


if __name__ == "__main__":
    folderpath = "input"
    extension = "mp4"
    watermark_path = "watermark.png"
    vm = VideoManager(watermark_path=watermark_path)
    vm.add_folder(folderpath, extension=extension)

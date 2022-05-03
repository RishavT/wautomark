Automatically watermark videos

## Set up
Requirements: pipenv, ffmpeg, imagemagick

```
pipenv shell  # Initiates the pipenv shell
pipenv sync  # Installs dependencies
pipenv sync --dev # Installs dev dependencies
```

For testing, edit the data towards the end of `video.py` (in the `if __name__
== "__main__" block`) and run either of the following:
1. `python video.py preview` - Will show a live preview of the new file
2. `python video.py` - Will convert the file and save in the `output` directory

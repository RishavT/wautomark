Automatically watermark videos

## Set up
Requirements: pipenv, ffmpeg, imagemagick, a telegram bot added to a group, a
google service account to upload to google drive

```
pipenv shell  # Initiates the pipenv shell
pipenv sync  # Installs dependencies
pipenv sync --dev # Installs dev dependencies
```

## Running locally without docker

1. Create the JSON files - `sa.json`, `drive.json` and `telegram.json`. For
   example json files, contact me.
2. Make sure no external USB drives are attached (that you want to use with
   this tool), and run `SET_INITIAL_DRIVES=yes python scan.py setup`
3. Connect your gopro memory card via usb
4. Run `python scan.py scan`

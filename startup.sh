# Startup script for docker
# If initial drives doesn't exist, run initial setup
ls $HOME/initial_drives || SET_INITIAL_DRIVES=yes pipenv run python scan.py setup
pipenv run python scan.py scan

# Sleep for sometime before quitting
echo "Done. Sleeping for 10 seconds then exiting"
sleep 10s

# Startup script

# Make sure we're in this directory
cd $(dirname ${BASH_SOURCE[0]})

# If initial drives doesn't exist, run initial setup
ls $HOME/initial_drives || SET_INITIAL_DRIVES=yes pipenv run python scan.py setup
pipenv run python scan.py scan

# Sleep for sometime before quitting
echo "Done. Exiting"

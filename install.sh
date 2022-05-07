#!/bin/bash
mkdir -p /prj
ls ./sa.json || (echo "sa.json needs to exist" && exit -1)
ls ./telegram.json || (echo "telegram.json needs to exist" && exit -1)
ls ./drive.json || (echo "drive.json needs to exist" && exit -1)
cp ./* /prj
cd /prj

# Update
apt update -y

# Install dev utils
apt install tmux vim -y

# Install python3 and pip
apt install python3 python3-pip -y

# Install pyenv
apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git -y
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init --path)"\nfi' >> ~/.bashrc

source ~/.bashrc

# Set up pip env
pip install pipenv
pipenv sync

# Enable the service
cp ./wautomark.service /etc/systemd/system/wautomark.service
systemctl enable wautomark

# Start the service
systemctl start wautomark

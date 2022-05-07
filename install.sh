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

# Set up pip env
pip install pip
pipenv sync

# Enable the service
cp ./wautomark.service /etc/systemd/system/wautomark.service
systemctl enable wautomark

# Start the service
systemctl start wautomark

#!/bin/bash
# Install system dependencies
apt-get update
apt-get install -y python3-dev portaudio19-dev python3-pip python3-setuptools ffmpeg

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
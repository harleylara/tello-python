#!/bin/bash

echo "Installing Gstreamer"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
fi

if [ "$OS" == "Ubuntu" ] || [ "$OS" == "Debian" ]; then
    sudo apt-get install -y libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev \
        libgstreamer-plugins-bad1.0-dev \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-libav \
        gstreamer1.0-doc \
        gstreamer1.0-tools \
        gstreamer1.0-x \
        gstreamer1.0-alsa \
        gstreamer1.0-gl \
        gstreamer1.0-gtk3 \
        gstreamer1.0-qt5 \
        gstreamer1.0-pulseaudio
elif ["$OS" == "Fedora"]; then
    sudo dnf install -y gstreamer1-devel \
        gstreamer1-plugins-base-tools \
        gstreamer1-doc \
        gstreamer1-plugins-base-devel \
        gstreamer1-plugins-good \
        gstreamer1-plugins-good-extras \
        gstreamer1-plugins-ugly \
        gstreamer1-plugins-bad-free \
        gstreamer1-plugins-bad-free-devel \
        gstreamer1-plugins-bad-free-extras
else
    echo "Unsupported OS"
fi

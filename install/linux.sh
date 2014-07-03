#!/bin/bash
set -e
sudo aptitude install git python-pip -y

sudo pip install gitpython==0.3.2.RC1 pyyaml==3.11

# apply bugfix to gitpython

sudo sed -i "523s/Total'):$/Total'\) or line.startswith('\ ='\):/" /usr/local/lib/python2.7/dist-packages/git/remote.py

sudo ln -s /opt/devman/devman /usr/local/bin/devman

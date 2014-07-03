#!/bin/bash
set -e
aptitude install git python-pip -y
pip install gitpython pyyaml

# GitPython
pip install gitpython==0.3.2.RC1 pyyaml==3.11

sudo ln -s /opt/devman/devman /usr/local/bin/devman

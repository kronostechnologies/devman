#!/bin/bash
set -e
DOT="$(dirname $(readlink -f ${BASH_SOURCE[0]}))"

if [ ! -h /usr/local/bin/devman ]
then
  ln -s $DOT/devman /usr/local/bin/devman
fi

pip install gitpython --upgrade
pip install pyyaml --upgrade

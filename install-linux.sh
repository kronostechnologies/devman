#!/bin/bash
set -e
DOT="$(dirname $(readlink -f ${BASH_SOURCE[0]}))"

if [ ! -d ~/bin ]
then
  mkdir ~/bin
fi

if [ ! -h ~/bin/devman ]
then
  ln -s $DOT/devman ~/bin/devman
fi

pip install gitpython --upgrade
pip install pyyaml --upgrade

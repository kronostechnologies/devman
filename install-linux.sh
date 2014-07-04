#!/bin/bash
set -e
DOT="$(dirname $(readlink -f ${BASH_SOURCE[0]}))"

sudo aptitude install git -y

if [ ! -d ~/bin ]
then
  mkdir ~/bin
fi

if [ ! -h ~/bin/devman ]
then
  ln -s $DOT/devman ~/bin/devman
fi

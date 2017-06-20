#!/bin/bash
set -e
DOT="$(dirname $(readlink -f ${BASH_SOURCE[0]}))"

if ! command -v devman >/dev/null 2>&1; then
  if [ "`id -u`" -eq 0 ]; then
    ln -nsf $DOT/devman /usr/local/bin/
  else
    mkdir -p ~/bin
    ln -nsf $DOT/devman ~/bin/
  fi
fi

sudo pip install gitpython --upgrade
sudo pip install pyyaml --upgrade

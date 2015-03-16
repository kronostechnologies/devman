#!/bin/bash
set -e

# Homebrew
if [ -x "$(command -v brew)" ]; then
  echo "Homebew is installed"
else
  echo "Installing Homebew..."
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

# Git, python, PHP & coreutils
for pkg in coreutils git php56 composer python; do
  if brew list -1 | grep -q "^${pkg}\$"; then
    echo "Package '$pkg' is installed, upgrading to latest..."
    brew upgrade $pkg 2> /dev/null || true
  else
    echo "Installing '$pkg'..."
    brew install $pkg
  fi
done

# Python gitdb
PIP_LIST=$(pip list)
if echo $PIP_LIST | grep -q "gitdb"; then
  echo "gitdb is installed, upgrading to latest..."
  pip install --upgrade gitdb
else
  echo "Installing python gitdb"
  pip install gitdb
fi

pip install gitpython --upgrade
pip install pyyaml --upgrade

# Use GNU readlink from coreutils
DOT="$(dirname $(greadlink -f ${BASH_SOURCE[0]}))"

if [ ! -d ~/bin ]; then
  mkdir ~/bin
fi

if [ ! -h ~/bin/devman ]; then
  ln -s $DOT/devman ~/bin/devman
fi

if [ -f ~/.zshrc ]; then
  TARGET_PROFILE=~/.zshrc
else
  TARGET_PROFILE=~/.profile
fi

# Add ~/bin to path
SET_PATH="export PATH=\"\$PATH:\$HOME/bin\""
if cat $TARGET_PROFILE | grep -q "^$SET_PATH\$"; then
  echo "PATH already set"
else
  echo "Setting PATH"
  echo $SET_PATH >> $TARGET_PROFILE
fi

# Setup PYTHONPATH
SET_PYTHONPATH="export PYTHONPATH=\$(brew --prefix)/lib/python2.7/site-packages:\$PYTHONPATH"
if cat $TARGET_PROFILE | grep -q "^$SET_PYTHONPATH\$"; then
  echo "PYTHONPATH already set"
else
  echo "Setting PYTHONPATH"
  echo $SET_PYTHONPATH >> $TARGET_PROFILE
fi

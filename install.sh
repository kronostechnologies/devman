#!/bin/bash

DOTPATH="$(dirname "$(if [[ "$(uname)" == 'Darwin' ]]; then (readlink "$0" || echo "$0"); else readlink -f "$0"; fi)")"
cd "${DOTPATH}"

if ! command -v pipenv; then
  python3 -m pip install pipenv
fi

PIPENV_IGNORE_VIRTUALENVS=1 pipenv install

#!/bin/bash
set -e

# xtract pyyaml 3.11 yaml lib
if [ ! -d yaml ];
then
  wget -q http://pyyaml.org/download/pyyaml/PyYAML-3.11.tar.gz -O - | tar xfvpz - PyYAML-3.11/lib/yaml --transform 's/PyYAML-3.11\/lib\/yaml/yaml/' 
fi

if [ ! -d git ];
then
  wget -q  https://github.com/gitpython-developers/GitPython/archive/0.3.tar.gz -O - | tar xfpvz - GitPython-0.3/git --transform 's/GitPython-0.3\/git/git/'
fi


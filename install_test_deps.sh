#!/bin/sh

python --version 2>&1 | grep -q 'Python 3'

if [ $? -eq 0 ]
then
    # Python 3
    exec pip install -r requirements/test.hash
else
    # Python 2 or PyPy
    exec pip install -r requirements/test.hash -r requirements/py27.hash
fi

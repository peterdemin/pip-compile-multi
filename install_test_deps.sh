#!/bin/sh

python --version 2>&1 | grep -q 'Python 3'

if [ $? -eq 0 ]
then
    # Python 3
    exec pip install -r requirements/test.txt
else
    # Python 2 or PyPy
    exec pip install -r requirements/test.txt -r requirements/py27.txt
fi

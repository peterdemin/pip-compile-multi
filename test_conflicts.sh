#!/bin/sh

set -x

if pip-compile-multi -d conflicting-in-merge;
then
   echo ERROR: conflict was not found in conflicting-in-merge
   exit 1
else
   echo SUCCESS: conflict detected in conflicting-in-merge
fi

if pip-compile-multi -d conflicting-in-ref;
then
   echo ERROR: conflict was not found in conflicting-in-ref
   exit 1
else
   echo SUCCESS: conflict detected in conflicting-in-ref
fi

exit 0

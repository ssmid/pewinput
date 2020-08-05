#!/bin/bash

mkdir pewinput
cp src/pewinput.py pewinput/__init__.py
cc -Wall -Werror -pedantic src/pewinput.c -o pewinput/libpewinput.so -fPIC -shared

#!/bin/sh
# Remove Python bytecode and cache directories to keep the repo clean
set -e
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
find . -name '*.pyo' -delete

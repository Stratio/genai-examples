#!/bin/bash -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

while IFS= read -r module; do
    cd "$BASEDIR"/"$module"
    echo "Cleaning module $module ..."
    rm -rf dist
    rm -rf dist_download
done < $MODULES_FILE_NAME

find . -type f -name 'tmp*' -delete
find . -type d -name '.pytest_cache' -exec rm -rf {} +
find . -type d -name '__pycache__' -exec rm -rf {} +

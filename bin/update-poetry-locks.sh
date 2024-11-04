#!/bin/bash -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

while IFS= read -r module; do
    cd "$BASEDIR"/"$module"
    echo "Updating poetry.lock in module $module ..."
    poetry lock --no-update
    echo "Installing packages for module $module ..."
    poetry install
done < $MODULES_FILE_NAME

#!/bin/bash -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

while IFS= read -r module; do
    cd "$BASEDIR"/"$module"
    echo "Checking Poetry version in module $module ..."
    poetry_version=$(poetry --version 2>&1)
    echo $poetry_version
    if [[ "$poetry_version" != *"(version 2."* ]]; then
        echo "Poetry version >= 2.0 is required!"
        exit 1
    fi
    echo "Cleaning stratio-staging cache in module $module ..."
    poetry cache clear stratio-staging --all --no-interaction
    echo "Updating poetry.lock in module $module ..."
    poetry lock
    echo "Installing packages for module $module ..."
    poetry install
done < $MODULES_FILE_NAME

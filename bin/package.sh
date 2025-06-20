#!/bin/bash -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

while IFS= read -r module; do
    cd "$BASEDIR"/"$module"
    export POETRY_VIRTUALENVS_IN_PROJECT=true
    export POETRY_CACHE_DIR="$BASEDIR/.cache/poetry"

    echo "Building FAT package for module $module ..."
    # tomlkit could be already installed if the UTs were run before
    poetry run pip install --disable-pip-version-check tomlkit
    export PYTHONUNBUFFERED=1
    export GENAI_BUILDER_GLOBAL_CACHE_PATH="$BASEDIR/.cache/genai-builder"
    poetry run build-fat-package
done < $MODULES_FILE_NAME

#!/bin/bash -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

# the "change-version" phase is not called for snapshots
if [ ! -e VERSION_PY ]; then
    ./bin/change-version.sh "$1"
fi

while IFS= read -r module; do
    cd "$BASEDIR"/"$module"
    export POETRY_VIRTUALENVS_IN_PROJECT=true
    export POETRY_CACHE_DIR="$BASEDIR/.cache/poetry"

    echo "Installing dependencies for module $module ..."
    poetry install --only main
done < $MODULES_FILE_NAME

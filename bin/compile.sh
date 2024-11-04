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
    echo "Installing dependencies for module $module ..."
    poetry install --only main
    echo "Generating requirements.txt for module $module ..."
    # poetry export > requirements.txt  # Discarded: https://github.com/python-poetry/poetry-plugin-export/issues/183
    # Note: "poetry install" also includes the developed package using:
    #       -e git+https://github.com/xxx/genai-chains.git@8e67...#egg=genai_chain_docs&subdirectory=genai-chain-docs
    # TODO - Exclude also genai-core ¿?
    poetry run pip freeze | grep -vwE "genai-chains" > requirements.txt
done < $MODULES_FILE_NAME

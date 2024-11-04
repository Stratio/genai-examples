#!/bin/bash -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

if [ -z "$1" ]; then
    VERSION=$(<"$BASEDIR/VERSION")
else
    VERSION=$1
fi

# https://packaging.python.org/en/latest/specifications/version-specifiers/
VERSION_PY=$VERSION
# PR: VERSION = 0.1.0-PR39-SNAPSHOT => VERSION_PY = 0.1.0.dev39
if [[ ${VERSION_PY} == *-PR* ]]; then
    version_digits=$(echo "$VERSION_PY" | cut -d'-' -f1)
    build_number=$(echo "$VERSION_PY" | cut -d'-' -f2 | sed 's/PR/dev/')
    VERSION_PY="$version_digits.$build_number"
fi
# SNAPSHOT: VERSION = 0.1.0-SNAPSHOT => VERSION_PY = 0.1.0a0
if [[ ${VERSION_PY} == *-SNAPSHOT* ]]; then
    version_digits=$(echo "$VERSION_PY" | cut -d'-' -f1)
    VERSION_PY="${version_digits}a0"
fi
# MILESTONE: VERSION = 0.1.0-M5 => VERSION_PY = 0.1.0b5
if [[ ${VERSION_PY} == *-M* ]]; then
    version_digits=$(echo "$VERSION_PY" | cut -d'-' -f1)
    build_number=$(echo "$VERSION_PY" | cut -d'-' -f2 | sed 's/M/b/')
    VERSION_PY="$version_digits$build_number"
fi
# RELESE: VERSION = 0.1.0-BUILD => VERSION_PY = 0.1.0
if [[ ${VERSION_PY} == *-BUILD* ]]; then
    version_digits=$(echo "$VERSION_PY" | cut -d'-' -f1)
    VERSION_PY="${version_digits}"
fi
# PRE-RELESE: VERSION = 0.1.0-662f39e => VERSION_PY = 0.1.0rc0+662f39e
if [[ ${VERSION_PY} == *-* ]]; then
    version_digits=$(echo $VERSION_PY | cut -d'-' -f1)
    hash=$(echo $VERSION_PY | cut -d'-' -f2)
    VERSION_PY="${version_digits}rc0+${hash}"
fi

echo "Replacing package version to: $VERSION_PY"
echo "$VERSION" > VERSION
echo "$VERSION_PY" > VERSION_PY

while IFS= read -r module; do
    cd "$BASEDIR"/"$module"
    echo "Changing version in module $module ..."
    sed -i "s/^version *= *\"[^\"]*\"/version = \"$VERSION_PY\"/" pyproject.toml
done < $MODULES_FILE_NAME

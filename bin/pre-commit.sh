#!/bin/bash
set -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

# Get a list of files staged for commit
STAGED_FILES=$(git diff --cached --name-only)
echo $STAGED_FILES

# For each module, lint the files
while IFS= read -r module; do
    cd "$BASEDIR"/"$module"
    echo "Running pre-commit for module $module ..."

    change_found=false
    for FILE in $STAGED_FILES; do
        if [[ "$FILE" == "$module"* ]]; then
            change_found=true
            break
        fi
    done
    if $change_found; then
        poetry run black -q ./
        poetry run isort ./
    fi

done < $MODULES_FILE_NAME

# Add modified files
cd "$BASEDIR"
for FILE in $STAGED_FILES; do
    # If the file was modified, stage it again
    if [[ $(git status --porcelain "$FILE") =~ ^[AM] ]]; then
        echo "adding $FILE"
        git add -u "$FILE"
    fi
done
#!/bin/bash -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

while IFS= read -r module; do
    cd "$BASEDIR"/"$module"

    echo "Installing test dependencies for module $module ..."
    poetry install

    echo "Checking code format for module $module ..."
    poetry run black --check ./

    echo "Running lint for module $module ..."
    poetry run pylint './**/*.py' --msg-template="$module/{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > pylint-report.txt || true

    # "sonar.python.mypy.reportPaths" is not supported in Stratio SonarQube's
    # echo "Checking code types for module $module ..."
    # poetry run mypy ./ > mypy-report.txt || true
    # sed -i 's/^/'"$module"'\//' mypy-report.txt 

    echo "Running unit tests for module $module ..."
    poetry run pytest "--cov=." --cov-report "xml:pytest-coverage.xml" tests/unit
done < $MODULES_FILE_NAME

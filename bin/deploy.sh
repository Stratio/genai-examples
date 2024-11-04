#!/bin/bash -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
MODULES_FILE_NAME="release-modules"
VERSION_PY=$(cat VERSION_PY)
USERNAME="stratio"
NEXUS_PYPI_URL="http://qa.int.stratio.com/repository"
NEXUS_PYPI_BROWSE_URL="http://qa.int.stratio.com/#browse/browse"
# For milestones, pre-releases and releases
NEXUS_PYPI_RELEASES=python-releases
# For snapshots
NEXUS_PYPI_SNAPSHOTS=python-snapshots
# For PRs
NEXUS_PYPI_STAGING=python-staging

if [ ! -f "$MODULES_FILE_NAME" ]; then
    echo "Error: $MODULES_FILE_NAME file not found"
    exit 1
fi

echo "JOB_NAME = ${JOB_NAME}"

NEXUS_PYPI_REPOSITORY=$NEXUS_PYPI_SNAPSHOTS
# RELEASE / PRE_RELEASE / MILESTONE: JOB_NAME=Release/GenAI/genai-core
if [[ ${JOB_NAME} == Release* ]]; then
    NEXUS_PYPI_REPOSITORY=$NEXUS_PYPI_RELEASES
fi
# PR: JOB_NAME=GenAI/genai-core/PR-39
if [[ ${JOB_NAME} == *PR-* ]]; then
    NEXUS_PYPI_REPOSITORY=$NEXUS_PYPI_STAGING
fi

while IFS= read -r module; do
    cd "$BASEDIR"/"$module"
    poetry config repositories.nexus "${NEXUS_PYPI_URL}/${NEXUS_PYPI_REPOSITORY}/"
    poetry config http-basic.nexus "${USERNAME}" "${NEXUSPASS}"

    echo "Publishing package for module $module in ${NEXUS_PYPI_URL}/${NEXUS_PYPI_REPOSITORY}/"
    poetry publish -r nexus
    echo "Package available in ${NEXUS_PYPI_BROWSE_URL}:${NEXUS_PYPI_REPOSITORY}:${module}%2F${VERSION_PY}"
done < $MODULES_FILE_NAME

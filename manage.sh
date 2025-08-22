#!/usr/bin/env bash

set -e

source .venv/bin/activate

# shellcheck disable=SC2046
export $(grep -v '^#' fbomatic.env | xargs -0)

python ./src/manage.py "$@"

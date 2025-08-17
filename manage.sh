#!/usr/bin/env bash

set -e

source .venv/bin/activate

# shellcheck disable=SC2046
export $(xargs < fbomatic.env)

python ./src/manage.py "$@"

#!/usr/bin/env bash

set -e

uv sync --locked --extra mysql

./manage.sh compilemessages
./manage.sh collectstatic --no-input

./manage.sh migrate
./manage.sh createinitialrevisions

touch tmp/restart.txt

#!/usr/bin/env bash

set -e

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv sync --locked --extra mysql --managed-python

./manage.sh compilemessages
./manage.sh collectstatic --no-input

./manage.sh migrate
./manage.sh createinitialrevisions

touch tmp/restart.txt

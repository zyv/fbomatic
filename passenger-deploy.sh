#!/usr/bin/env bash

set -e

GIT_SOURCES="../git/fbomatic"
ENV_FILE="fbomatic.env"

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv sync --locked --extra mysql --managed-python

./manage.sh compilemessages
./manage.sh collectstatic --no-input

./manage.sh migrate
./manage.sh createinitialrevisions

if [ -d "$GIT_SOURCES" ] ; then

  pushd "$GIT_SOURCES"
    GIT_HASH="$(git rev-parse --short HEAD)"
  popd

  sed -E "s/^#?PROJECT_VERSION=/PROJECT_VERSION=$GIT_HASH/" "$ENV_FILE" > "$ENV_FILE.new"
  mv "$ENV_FILE.new" "$ENV_FILE"

fi

mkdir -p tmp
touch tmp/restart.txt

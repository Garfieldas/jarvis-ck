#!/bin/bash
set -e

PYTHON_BIN="${PYTHON_BIN:-./venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
	PYTHON_BIN=python3
fi

"$PYTHON_BIN" manage.py collectstatic --noinput --clear --no-post-process
"$PYTHON_BIN" manage.py makemessages -l 'lt' --ignore site-packages
"$PYTHON_BIN" manage.py migrate
"$PYTHON_BIN" manage.py runserver 0.0.0.0:8000

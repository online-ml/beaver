#!/bin/sh

set -e
. /venv/bin/activate
exec uvicorn wsgi:dam.http_server --host 0.0.0.0 --port 3000

#!/bin/bash
# Start API and frontend for development
set -e

# Locate project root (one directory above this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"
cd "$ROOT_DIR"

python -m uvicorn web.api.main:app --reload &
API_PID=$!

sleep 1
python -m uvicorn web.frontend.main:app --reload --port 8001 &
FRONT_PID=$!

echo "API running at http://localhost:8000"
echo "Frontend running at http://localhost:8001"

trap "kill $API_PID $FRONT_PID" INT TERM
wait $API_PID $FRONT_PID

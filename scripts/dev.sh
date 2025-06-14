#!/bin/bash
# Start API and frontend for development
set -e

python -m uvicorn web.api.main:app --reload &
API_PID=$!

sleep 1
python -m uvicorn web.frontend.main:app --reload --port 8001 &
FRONT_PID=$!

echo "API running at http://localhost:8000"
echo "Frontend running at http://localhost:8001"

trap "kill $API_PID $FRONT_PID" INT TERM
wait $API_PID $FRONT_PID

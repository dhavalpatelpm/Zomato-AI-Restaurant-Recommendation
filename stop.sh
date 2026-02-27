#!/bin/bash
# Stop the project: kills backend (port 8000) and frontend (port 5173)

echo "Stopping AI Restaurant Recommender..."

kill_port() {
  PORT=$1
  PID=$(lsof -ti :$PORT 2>/dev/null)
  if [ -n "$PID" ]; then
    kill -9 $PID 2>/dev/null || kill $PID 2>/dev/null || true
    echo "  Stopped process on port $PORT (PID $PID)"
  fi
}

kill_port 8000
kill_port 5173

echo "Done."

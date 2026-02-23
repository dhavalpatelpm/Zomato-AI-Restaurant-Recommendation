#!/bin/bash
# Unified start script: starts backend first, waits for it to be ready, then starts frontend.
# Run from project root: ./start.sh

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== Starting AI Restaurant Recommender ==="

# Start backend in background
echo "[1/3] Starting backend API..."
(
  cd ai-restaurant-recommender
  if [ -d .venv ]; then
    source .venv/bin/activate
  fi
  PYTHONPATH=. python -m uvicorn src.phase3_api_service.app:app --host 0.0.0.0 --port 8000
) &
BACKEND_PID=$!

# Wait for backend to be ready (health check)
echo "[2/3] Waiting for backend to be ready..."
MAX_WAIT=60
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
  if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "Backend is ready!"
    break
  fi
  sleep 2
  ELAPSED=$((ELAPSED + 2))
  echo "  ... waiting (${ELAPSED}s)"
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
  echo "Error: Backend failed to start within ${MAX_WAIT}s"
  kill $BACKEND_PID 2>/dev/null || true
  exit 1
fi

# Start frontend
echo "[3/3] Starting frontend (http://localhost:5173)..."
echo ""
echo "=== Both services running. Press Ctrl+C to stop. ==="
trap "kill $BACKEND_PID 2>/dev/null || true; kill $FRONTEND_PID 2>/dev/null || true; exit" INT TERM
(
  cd frontend
  npm run dev
) &
FRONTEND_PID=$!

wait

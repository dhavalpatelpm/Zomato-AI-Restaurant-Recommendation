#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f .env ]; then
  echo "Creating .env from .env.example (set GROQ_API_KEY for production)"
  cp .env.example .env
fi

echo "Building containers..."
docker compose build

echo "Starting services..."
docker compose up -d

echo "Waiting for backend health..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend is healthy"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "Backend health check failed"
    docker compose logs backend
    docker compose down
    exit 1
  fi
  sleep 2
done

echo "Testing backend health endpoint..."
curl -sf http://localhost:8000/health || { echo "Backend health check failed"; docker compose down; exit 1; }

echo "Testing frontend..."
curl -sf -o /dev/null http://localhost:3000 || { echo "Frontend check failed"; docker compose down; exit 1; }

echo "All infrastructure checks passed"
docker compose down

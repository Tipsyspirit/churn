#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Kill any stale uvicorn processes
if command -v taskkill >/dev/null 2>&1; then
    taskkill //F //IM python.exe >/dev/null 2>&1 || true
    sleep 1
elif command -v pkill >/dev/null 2>&1; then
    pkill -f uvicorn || true
    sleep 1
fi

# Activate venv
if [ -d ".venv" ]; then
    source .venv/Scripts/activate
elif [ -d "backend/.venv" ]; then
    source backend/.venv/Scripts/activate
else
    echo "No venv found. Create one first:" >&2
    echo "  py -3.11 -m venv .venv" >&2
    exit 1
fi

cd backend

# Clear bytecode cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Start uvicorn
echo "Starting backend..."
python -m uvicorn main:app --port 8000
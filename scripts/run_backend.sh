#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../backend"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  py -3.11 -m venv .venv
fi

source .venv/Scripts/activate
python -m uvicorn main:app --reload --port 8000
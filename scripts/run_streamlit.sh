#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
    echo "Creating shared venv..."
    py -3.11 -m venv .venv
fi
source .venv/Scripts/activate

cd streamlit_app
python -m streamlit run app.py
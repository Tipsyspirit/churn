#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../streamlit_app"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  py -3.11 -m venv .venv
fi

source .venv/Scripts/activate
python -m streamlit run app.py
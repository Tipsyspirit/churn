#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/ml/models/customer_churn_model.joblib"
DST="$ROOT/backend/artifacts/customer_churn_model.joblib"
mkdir -p "$(dirname "$DST")"
cp "$SRC" "$DST"
echo "Copied $(ls -lh "$DST" | awk '{print $5}') → $DST"
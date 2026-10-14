#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../ml/src"
python train.py \
  --data "../data/raw/E Commerce Dataset.xlsx" \
  --out "../models/customer_churn_model.joblib"
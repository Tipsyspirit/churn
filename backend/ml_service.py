import joblib
import pandas as pd
from config import MODEL_PATH

ARTIFACT = joblib.load(MODEL_PATH)
MODEL = ARTIFACT["model"]
THRESHOLD = ARTIFACT["threshold"]
NUMERIC = ARTIFACT["numeric_features"]
CATEGORICAL = ARTIFACT["categorical_features"]

print(f"[ml_service] model loaded — threshold={THRESHOLD}")

def _risk(p: float) -> str:
    if p < 0.40: return "low"
    if p <= 0.70: return "med"
    return "high"

def _frame(rows):
    df = pd.DataFrame(rows)
    return df[NUMERIC + CATEGORICAL]

def predict_one(features: dict) -> dict:
    prob = float(MODEL.predict_proba(_frame([features]))[:, 1][0])
    return {
        "churn_probability": prob,
        "predicted_churn": int(prob >= THRESHOLD),
        "risk": _risk(prob),
        "threshold": THRESHOLD,
    }

def predict_bulk(rows):
    probs = MODEL.predict_proba(_frame(rows))[:, 1]
    out = []
    for i, p in enumerate(probs):
        p = float(p)
        out.append({
            "index": i,
            "churn_probability": p,
            "predicted_churn": int(p >= THRESHOLD),
            "risk": _risk(p),
            "threshold": THRESHOLD,
        })
    return out
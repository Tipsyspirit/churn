import math
import pandas as pd
import streamlit as st
from pathlib import Path
from utils import session, api, styles, charts
from components.upload_report import show as show_report

st.set_page_config(page_title="Upload · ChurnSight", layout="wide")
styles.inject()
session.init()
session.require_login()


# =========================================================
# Constants — MUST come before run_pipeline()
# =========================================================
REQUIRED_NUMERIC = [
    "Tenure", "CityTier", "WarehouseToHome", "HourSpendOnApp",
    "NumberOfDeviceRegistered", "SatisfactionScore", "NumberOfAddress",
    "Complain", "OrderAmountHikeFromlastYear", "CouponUsed",
    "OrderCount", "DaySinceLastOrder", "CashbackAmount",
]

REQUIRED_CATEGORICAL = [
    "PreferredLoginDevice", "PreferredPaymentMode", "Gender",
    "PreferedOrderCat", "MaritalStatus",
]

REQUIRED = REQUIRED_NUMERIC + REQUIRED_CATEGORICAL


# =========================================================
# Helpers
# =========================================================
def safe_float(v, default=0.0) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    if math.isnan(f) or math.isinf(f):
        return default
    return f


def safe_str(v, default="Unknown") -> str:
    if v is None:
        return default
    try:
        if isinstance(v, float) and math.isnan(v):
            return default
    except Exception:
        pass
    s = str(v).strip()
    if s == "" or s.lower() in ("nan", "none", "null"):
        return default
    return s


# =========================================================
# Main pipeline
# =========================================================
def run_pipeline(df: pd.DataFrame, name: str):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        st.error(f"Expected: {REQUIRED}")
        return

    df = df.copy()
    if "customer_id" not in df.columns:
        df["customer_id"] = [f"C-{i+1}" for i in range(len(df))]

    # --- Sanitize numeric columns ---
    for k in REQUIRED_NUMERIC:
        df[k] = pd.to_numeric(df[k], errors="coerce")
        df[k] = df[k].replace([float("inf"), float("-inf")], pd.NA)
        median = df[k].median()
        df[k] = df[k].fillna(median if pd.notna(median) else 0.0)

    # --- Sanitize categorical columns ---
    for k in REQUIRED_CATEGORICAL:
        df[k] = df[k].fillna("Unknown").astype(str)
        df[k] = df[k].replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})

    # --- Build JSON-safe payload ---
    customers = []
    for _, row in df.iterrows():
        features = {k: safe_float(row[k]) for k in REQUIRED_NUMERIC}
        features.update({k: safe_str(row[k]) for k in REQUIRED_CATEGORICAL})
        customers.append({"id": str(row["customer_id"]), "features": features})

    with st.spinner("Scoring customers..."):
        try:
            results = api.predict_bulk(customers)
        except Exception as e:
            st.error(f"Prediction failed: {e}")
            return

    preds = pd.DataFrame([{
        "customer_id": r["id"],
        "churn_probability": r["churn_probability"],
        "predicted_churn": r["predicted_churn"],
        "risk": r["risk"],
    } for r in results])

    merged = df.merge(preds, on="customer_id", how="left")
    st.session_state["customers"] = merged
    st.session_state["predictions"] = preds
    st.session_state["upload_report"] = {
        "file": name, "total": len(df), "valid": len(results),
        "failed": len(df) - len(results), "errors": [],
    }
    st.success(f"Scored {len(df)} customers from {name}")


# =========================================================
# Page header
# =========================================================
st.title("Upload customer data")
st.caption("CSV must contain the 18 features the model was trained on.")


# =========================================================
# Upload controls
# =========================================================
uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
use_sample = st.button("Use sample data")


if uploaded:
    try:
        df = pd.read_csv(uploaded)
        run_pipeline(df, uploaded.name)
    except Exception as e:
        st.error(f"Could not read the file: {e}")


if use_sample:
    sample_path = Path(__file__).resolve().parents[2] / "ml" / "data" / "raw" / "sample_customers.csv"
    if sample_path.exists():
        try:
            df = pd.read_csv(sample_path)
            run_pipeline(df, "sample_customers.csv")
        except Exception as e:
            st.error(f"Could not read the sample: {e}")
    else:
        st.error(f"Sample file not found at {sample_path}")


# =========================================================
# Show results if predictions exist
# =========================================================
if st.session_state.get("predictions") is not None:
    df = st.session_state["customers"]
    preds = st.session_state["predictions"]
    st.divider()
    st.subheader("Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Customers", len(df))
    c2.metric("Predicted churn",
              f"{(preds['predicted_churn'].mean()*100):.1f}%")
    c3.metric("High risk", int((preds["risk"] == "high").sum()))
    c4.metric("Avg probability",
              f"{(preds['churn_probability'].mean()*100):.1f}%")

    st.plotly_chart(charts.risk_donut(preds), use_container_width=True)
    st.plotly_chart(charts.churn_by_tenure(df), use_container_width=True)
    st.plotly_chart(charts.probability_histogram(preds), use_container_width=True)

    if st.button("Go to Customers →"):
        st.switch_page("pages/3_Customers.py")
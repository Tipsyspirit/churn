import io
import pandas as pd
import streamlit as st
from utils import session, api, styles
from components.kpi_cards import kpi
from utils import charts

st.set_page_config(page_title="Upload · ChurnSight", layout="wide")
styles.inject()
session.init()
session.require_login()

st.title("Upload customer data")
st.caption("CSV must contain the 18 features your model was trained on.")

REQUIRED = [
    "Tenure","CityTier","WarehouseToHome","PreferredLoginDevice",
    "PreferredPaymentMode","Gender","HourSpendOnApp","NumberOfDeviceRegistered",
    "PreferedOrderCat","SatisfactionScore","MaritalStatus","NumberOfAddress",
    "Complain","OrderAmountHikeFromlastYear","CouponUsed","OrderCount",
    "DaySinceLastOrder","CashbackAmount",
]

uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
use_sample = st.button("Use sample data")

def run_pipeline(df: pd.DataFrame, name: str):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        return
    df = df.copy()
    df["customer_id"] = df.get("customer_id", pd.Series([f"C-{i+1}" for i in range(len(df))]))

    customers = []
    for _, row in df.iterrows():
        customers.append({
            "id": str(row["customer_id"]),
            "features": {k: (int(row[k]) if k in ["CityTier","NumberOfDeviceRegistered","SatisfactionScore","NumberOfAddress","Complain"] else float(row[k]))
                         if k not in ["PreferredLoginDevice","PreferredPaymentMode","Gender","PreferedOrderCat","MaritalStatus"]
                         else str(row[k]) for k in REQUIRED}
        })

    with st.spinner("Scoring customers..."):
        results = api.predict_bulk(customers)

    preds = pd.DataFrame([{
        "customer_id": r["id"],
        "churn_probability": r["churn_probability"],
        "predicted_churn": r["predicted_churn"],
        "risk": r["risk"],
    } for r in results])

    merged = df.merge(preds, left_on="customer_id", right_on="customer_id", how="left")
    st.session_state["customers"] = merged
    st.session_state["predictions"] = preds
    st.session_state["upload_report"] = {"file": name, "rows": len(df)}
    st.success(f"Scored {len(df)} customers from {name}")

if uploaded:
    df = pd.read_csv(uploaded)
    run_pipeline(df, uploaded.name)

if use_sample:
    from pathlib import Path
    sample_path = Path(__file__).resolve().parents[2] / "ml" / "data" / "raw" / "sample_customers.csv"
    if sample_path.exists():
        df = pd.read_csv(sample_path)
        run_pipeline(df, "sample_customers.csv")
    else:
        st.error("Sample file not found. Place sample_customers.csv in ml/data/raw/.")

if st.session_state.get("predictions") is not None:
    df = st.session_state["customers"]
    preds = st.session_state["predictions"]
    st.divider()
    st.subheader("Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Customers", len(df))
    with c2: kpi("Predicted churn", f"{(preds['predicted_churn'].mean()*100):.1f}%")
    with c3: kpi("High risk", int((preds["risk"]=="high").sum()))
    with c4: kpi("Avg probability", f"{(preds['churn_probability'].mean()*100):.1f}%")

    st.plotly_chart(charts.risk_donut(preds), use_container_width=True)
    st.plotly_chart(charts.churn_by_tenure(df), use_container_width=True)
    st.plotly_chart(charts.probability_histogram(preds), use_container_width=True)

    if st.button("Go to Customers →"):
        st.switch_page("pages/3_Customers.py")
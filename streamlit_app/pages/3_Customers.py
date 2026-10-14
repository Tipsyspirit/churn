import streamlit as st
import pandas as pd
from utils import session, styles

st.set_page_config(page_title="Customers · ChurnSight", layout="wide")
styles.inject()
session.init()
session.require_login()

st.title("Customers")

if st.session_state.get("customers") is None:
    st.info("Upload a dataset first.")
    if st.button("Go to Upload"): st.switch_page("pages/2_Upload.py")
    st.stop()

df = st.session_state["customers"].copy()

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    q = st.text_input("Search by customer ID", "")
with c2:
    risk = st.selectbox("Risk", ["all", "high", "med", "low"])
with c3:
    sort_col = st.selectbox("Sort by", ["churn_probability", "Tenure", "DaySinceLastOrder"])

if q:
    df = df[df["customer_id"].astype(str).str.contains(q, case=False)]
if risk != "all":
    df = df[df["risk"] == risk]
df = df.sort_values(sort_col, ascending=(sort_col != "churn_probability"))

st.caption(f"{len(df)} customers")

st.dataframe(
    df[["customer_id","Tenure","DaySinceLastOrder","Complain","churn_probability","risk"]],
    use_container_width=True, height=500,
)

st.download_button(
    "Download predictions CSV",
    df.to_csv(index=False).encode(),
    file_name="churn_predictions.csv",
    mime="text/csv",
)
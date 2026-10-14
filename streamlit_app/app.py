import streamlit as st
from utils import session, styles, api

st.set_page_config(page_title="ChurnSight", page_icon="📉", layout="wide")
styles.inject()
session.init()

st.title("ChurnSight")
st.caption("Customer Churn Prediction Dashboard")

# Backend health check
h = api.health()
if h.get("status") != "ok":
    st.error(f"Backend unreachable at {api.API_BASE}. Start it with `uvicorn main:app --reload`.")
    st.stop()
else:
    st.success(f"Backend online · Model threshold {h.get('model_threshold', 'n/a')}")

if not session.is_logged_in():
    st.info("Sign in to continue.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/1_Login.py")
    st.stop()

user = st.session_state["user"]
st.write(f"Signed in as **{user['name']}** ({user['role']})")

# Navigation shortcuts
c1, c2, c3, c4 = st.columns(4)
with c1: 
    if st.button("Upload data"): st.switch_page("pages/2_Upload.py")
with c2:
    if st.button("Customers"): st.switch_page("pages/3_Customers.py")
with c3:
    if st.button("Predict"): st.switch_page("pages/4_Predict.py")
with c4:
    if st.button("Log out", type="secondary"): session.logout(); st.rerun()
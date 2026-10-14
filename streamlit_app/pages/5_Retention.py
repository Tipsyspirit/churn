import streamlit as st
from datetime import date, timedelta
from utils import session, styles
from components.kpi_cards import risk_badge

st.set_page_config(page_title="Retention · ChurnSight", layout="wide")
styles.inject()
session.init()
session.require_login()

st.title("Retention tasks")

if st.session_state.get("predictions") is None:
    st.info("Upload a dataset first.")
    st.stop()

if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

preds = st.session_state["predictions"]
high = preds[preds["risk"] == "high"]

st.subheader(f"{len(high)} high-risk customers need attention")

if st.button("Create tasks for all high-risk customers", type="primary"):
    for _, row in high.iterrows():
        if not any(t["customer_id"] == row["customer_id"] for t in st.session_state["tasks"]):
            st.session_state["tasks"].append({
                "customer_id": row["customer_id"],
                "probability": row["churn_probability"],
                "assignee": "",
                "due": date.today() + timedelta(days=3),
                "status": "To contact",
            })
    st.success(f"{len(high)} tasks created")

tasks = st.session_state["tasks"]
if tasks:
    for i, t in enumerate(tasks):
        with st.expander(f"{t['customer_id']} · {t['probability']*100:.0f}% · {t['status']}"):
            c1, c2, c3 = st.columns(3)
            with c1: tasks[i]["assignee"] = st.text_input("Assignee", t["assignee"], key=f"a{i}")
            with c2: tasks[i]["due"] = st.date_input("Due", t["due"], key=f"d{i}")
            with c3: tasks[i]["status"] = st.selectbox("Status", ["To contact","Contacted","Retained","Churned"],
                                                      index=["To contact","Contacted","Retained","Churned"].index(t["status"]), key=f"s{i}")
else:
    st.info("No tasks yet.")
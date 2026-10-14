import streamlit as st
from utils import session, styles, api
from components.kpi_cards import greeting

st.set_page_config(
    page_title="ChurnSight",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)
styles.inject()
session.init()

# ===== Sidebar branding =====
with st.sidebar:
    st.markdown(
        '<div style="padding: 8px 16px 20px; font-family: Sora, sans-serif; '
        'font-size: 22px; font-weight: 700; color: #F5EE50;">'
        '📉 ChurnSight</div>',
        unsafe_allow_html=True,
    )

# ===== Backend health =====
h = api.health()
if h.get("status") != "ok":
    st.error(
        f"Backend unreachable at {api.API_BASE}. "
        "Start it with `uvicorn main:app --reload`."
    )
    st.stop()

# ===== Not logged in =====
if not session.is_logged_in():
    st.title("Welcome to ChurnSight")
    st.caption("Sign in to continue.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/1_Login.py")
    st.stop()

# ===== Logged in: home dashboard =====
user = st.session_state["user"]

greeting(
    user["name"].split()[0],
    f"Model threshold {h.get('model_threshold', 'n/a')} · signed in as {user['role']}",
)

st.markdown(
    '<div style="background:#1D1D1D; color:#F2F2F2; border-radius:22px; '
    'padding:14px 20px; display:flex; align-items:center; gap:12px; '
    'font-size:14px; margin-bottom:20px;">'
    '<span style="width:8px; height:8px; border-radius:50%; background:#7be0a4; '
    'display:inline-block;"></span>'
    'Backend online'
    '</div>',
    unsafe_allow_html=True,
)

# Quick-nav cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Upload data", use_container_width=True):
        st.switch_page("pages/2_Upload.py")
with col2:
    if st.button("View customers", use_container_width=True):
        st.switch_page("pages/3_Customers.py")
with col3:
    if st.button("Predict one", use_container_width=True):
        st.switch_page("pages/4_Predict.py")
with col4:
    if st.button("Sign out", type="secondary", use_container_width=True):
        session.logout()
        st.rerun()

# Show KPIs if a dataset is already loaded
if st.session_state.get("predictions") is not None:
    from components.kpi_cards import kpi, section
    import plotly.express as px
    from utils import charts

    preds = st.session_state["predictions"]
    df = st.session_state["customers"]

    section("Overview", "Summary of the current dataset")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Customers", f"{len(df):,}",
            f"From {st.session_state.get('upload_report', {}).get('file', 'upload')}")
    with c2:
        kpi("Predicted churn", f"{(preds['predicted_churn'].mean()*100):.1f}%",
            "Customers with 50%+ probability", variant="dark")
    with c3:
        kpi("High risk", int((preds["risk"] == "high").sum()),
            "Need attention this week")
    with c4:
        kpi("Avg risk", f"{(preds['churn_probability'].mean()*100):.1f}%",
            "Across all customers", variant="yellow")

    st.markdown("")
    st.plotly_chart(charts.risk_donut(preds), use_container_width=True)
    st.plotly_chart(charts.churn_by_tenure(df), use_container_width=True)
    st.plotly_chart(charts.probability_histogram(preds), use_container_width=True)
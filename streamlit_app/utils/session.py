import streamlit as st

def init():
    defaults = {
        "token": None,
        "user": None,
        "customers": None,      # DataFrame of uploaded customers
        "predictions": None,    # DataFrame with churn probabilities
        "upload_report": None,  # dict with valid/failed rows
        "history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def is_logged_in() -> bool:
    return st.session_state.get("token") is not None

def require_login():
    if not is_logged_in():
        st.warning("Please sign in first.")
        st.switch_page("pages/1_Login.py")
        st.stop()

def has_role(*roles) -> bool:
    u = st.session_state.get("user") or {}
    return u.get("role") in roles

def logout():
    for k in ["token", "user", "customers", "predictions", "upload_report", "history"]:
        st.session_state[k] = None
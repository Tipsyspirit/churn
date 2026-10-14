import streamlit as st

DEFAULTS = {
    "token": None,
    "user": None,
    "customers": None,
    "predictions": None,
    "upload_report": None,
    "tasks": [],
}

def init():
    for k, v in DEFAULTS.items():
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
    for k in DEFAULTS.keys():
        st.session_state[k] = DEFAULTS[k]
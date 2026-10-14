import streamlit as st

def set_session(token: str, user: dict):
    st.session_state["token"] = token
    st.session_state["user"] = user

def current_user():
    return st.session_state.get("user")

def role():
    u = current_user() or {}
    return u.get("role", "viewer")

def can_write():
    return role() in ("analyst", "admin")

def is_admin():
    return role() == "admin"
import streamlit as st
from utils import session, api, styles

st.set_page_config(page_title="Login · ChurnSight", layout="centered")
styles.inject()
session.init()

st.title("Sign in")

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary")
    if submitted:
        try:
            data = api.login(email, password)
            st.session_state["token"] = data["access_token"]
            st.session_state["user"] = data["user"]
            st.success("Signed in")
            st.switch_page("app.py")
        except Exception as e:
            st.error(str(e))

with tab2:
    with st.form("register_form"):
        name = st.text_input("Name")
        email_r = st.text_input("Email", key="reg_email")
        password_r = st.text_input("Password (min 6 chars)", type="password", key="reg_pwd")
        role = st.selectbox("Role (demo)", ["analyst", "admin", "viewer"])
        submitted_r = st.form_submit_button("Create account", type="primary")
    if submitted_r:
        try:
            data = api.register(name, email_r, password_r, role)
            st.session_state["token"] = data["access_token"]
            st.session_state["user"] = data["user"]
            st.success("Account created")
            st.switch_page("app.py")
        except Exception as e:
            st.error(str(e))

if session.is_logged_in():
    if st.button("← Back to dashboard"):
        st.switch_page("app.py")
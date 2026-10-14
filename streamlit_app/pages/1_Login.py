import streamlit as st
from utils import session, api, styles

st.set_page_config(page_title="Login · ChurnSight", layout="centered")
styles.inject()
session.init()

# Center column
_, mid, _ = st.columns([1, 1.5, 1])
with mid:
    st.markdown("""
    <div style="text-align:center; margin-bottom:24px;">
        <div style="font-family:Sora,sans-serif; font-size:28px; font-weight:700;">
            📉 ChurnSight
        </div>
        <div style="color:#636363; margin-top:6px;">Sign in to continue</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", type="primary",
                                              use_container_width=True)
        if submitted:
            try:
                data = api.login(email, password)
                st.session_state["token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                st.switch_page("app.py")
            except Exception as e:
                st.error(str(e))

    with tab2:
        with st.form("register_form"):
            name = st.text_input("Name")
            email_r = st.text_input("Email", key="reg_email")
            password_r = st.text_input("Password (min 6 chars)",
                                       type="password", key="reg_pwd")
            role = st.selectbox("Role (demo)", ["analyst", "admin", "viewer"])
            submitted_r = st.form_submit_button("Create account",
                                                type="primary",
                                                use_container_width=True)
        if submitted_r:
            try:
                data = api.register(name, email_r, password_r, role)
                st.session_state["token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                st.switch_page("app.py")
            except Exception as e:
                st.error(str(e))

    if session.is_logged_in():
        if st.button("← Back to dashboard", use_container_width=True):
            st.switch_page("app.py")
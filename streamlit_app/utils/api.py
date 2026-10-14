import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

def _headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def _handle(resp):
    if resp.status_code == 401:
        st.session_state["token"] = None
        st.session_state["user"] = None
        st.error("Session expired. Please sign in again.")
        st.switch_page("pages/1_Login.py")
        st.stop()
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(f"{resp.status_code}: {detail}")
    return resp.json()

def register(name, email, password, role="analyst"):
    return _handle(requests.post(
        f"{API_BASE}/api/auth/register",
        json={"name": name, "email": email, "password": password, "role": role},
    ))

def login(email, password):
    return _handle(requests.post(
        f"{API_BASE}/api/auth/login",
        json={"email": email, "password": password},
    ))

def me():
    return _handle(requests.get(f"{API_BASE}/api/auth/me", headers=_headers()))

def predict_bulk(customers: list[dict]):
    return _handle(requests.post(
        f"{API_BASE}/api/predict/bulk",
        json={"customers": customers},
        headers=_headers(),
    ))

def predict_one(customer_id, features: dict):
    return _handle(requests.post(
        f"{API_BASE}/api/predict",
        json={"id": customer_id, "features": features},
        headers=_headers(),
    ))

def history():
    return _handle(requests.get(f"{API_BASE}/api/history", headers=_headers()))

def health():
    try:
        return requests.get(f"{API_BASE}/api/health", timeout=3).json()
    except Exception:
        return {"status": "unreachable"}
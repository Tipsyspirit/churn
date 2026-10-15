import os
import requests
import streamlit as st


def _resolve_api_base() -> str:
    """
    Priority:
      1. Streamlit secrets (cloud deployment)
      2. Environment variable (local .env)
      3. Default localhost
    """
    val = ""
    try:
        val = st.secrets.get("API_BASE", "")
    except Exception:
        val = ""
    if not val:
        val = os.getenv("API_BASE", "http://localhost:8000")
    val = str(val).strip().rstrip("/")
    # Remove accidental "/api" suffix if someone added it
    if val.endswith("/api"):
        val = val[:-4]
    return val


API_BASE = _resolve_api_base()


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
    url = f"{API_BASE}/api/auth/register"
    try:
        r = requests.post(
            url,
            json={"name": name, "email": email, "password": password, "role": role},
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Cannot reach backend at {API_BASE}: {e}")
    return _handle(r)


def login(email, password):
    url = f"{API_BASE}/api/auth/login"
    try:
        r = requests.post(
            url,
            json={"email": email, "password": password},
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Cannot reach backend at {API_BASE}: {e}")
    return _handle(r)


def me():
    url = f"{API_BASE}/api/auth/me"
    try:
        r = requests.get(url, headers=_headers(), timeout=30)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Cannot reach backend at {API_BASE}: {e}")
    return _handle(r)


def predict_one(customer_id, features):
    url = f"{API_BASE}/api/predict"
    try:
        r = requests.post(
            url,
            json={"id": customer_id, "features": features},
            headers=_headers(),
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Cannot reach backend at {API_BASE}: {e}")
    return _handle(r)


def predict_bulk(customers):
    url = f"{API_BASE}/api/predict/bulk"
    try:
        r = requests.post(
            url,
            json={"customers": customers},
            headers=_headers(),
            timeout=60,
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Cannot reach backend at {API_BASE}: {e}")
    return _handle(r)


def history():
    url = f"{API_BASE}/api/history"
    try:
        r = requests.get(url, headers=_headers(), timeout=30)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Cannot reach backend at {API_BASE}: {e}")
    return _handle(r)


def health():
    try:
        return requests.get(f"{API_BASE}/api/health", timeout=5).json()
    except Exception:
        return {"status": "unreachable"}
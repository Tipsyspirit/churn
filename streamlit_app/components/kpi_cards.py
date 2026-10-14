import streamlit as st

def kpi(label, value, sub=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def risk_badge(risk: str):
    return f'<span class="risk-pill risk-{risk}">{risk.upper()}</span>'
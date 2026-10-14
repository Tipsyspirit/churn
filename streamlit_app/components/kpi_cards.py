import streamlit as st


def kpi(label: str, value, sub: str = "", variant: str = "light"):
    """
    variant: light | dark | yellow
    """
    st.markdown(f"""
    <div class="kpi-card {variant if variant != 'light' else ''}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def risk_badge(risk: str) -> str:
    labels = {"low": "Low", "med": "Medium", "high": "High"}
    return f'<span class="risk-pill risk-{risk}">{labels.get(risk, risk)}</span>'


def greeting(name: str, subtitle: str = ""):
    st.markdown(f'<div class="greeting">Hi, {name}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="greeting-sub">{subtitle}</div>', unsafe_allow_html=True)


def section(title: str, subtitle: str = ""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)
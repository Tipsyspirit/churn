import streamlit as st

def inject():
    st.markdown("""
    <style>
    .kpi-card {
        background: #FFFFFF; border-radius: 18px; padding: 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    .kpi-value { font-size: 34px; font-weight: 700; color: #202020; }
    .kpi-label { font-size: 13px; color: #636363; }
    .risk-pill { padding: 3px 12px; border-radius: 99px; font-size: 12px; font-weight: 600; }
    .risk-low  { background:#D9F3E4; color:#1E7A48; }
    .risk-med  { background:#FFE9C2; color:#8F5200; }
    .risk-high { background:#FFD9D4; color:#B02A20; }
    </style>
    """, unsafe_allow_html=True)
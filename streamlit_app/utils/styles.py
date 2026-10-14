import streamlit as st

# ChurnSight design tokens (from theme.css)
CSS = """
<style>
/* ===== Fonts ===== */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Sora:wght@500;600;700&display=swap');

:root {
    --bg: #7D7D7D;
    --card: #FFFFFF;
    --dark: #1D1D1D;
    --dark2: #2D2D2D;
    --line: #E3E3E0;
    --line-dark: #3A3A3A;
    --track: #E9E9E6;
    --hover: #F3F3F0;
    --fg: #202020;
    --muted: #636363;
    --on-dark: #F2F2F2;
    --muted-dark: #ABABAB;
    --y: #F5EE50;
    --y2: #E3DB2E;
    --y-ink: #202020;
    --low: #1E7A48;
    --low-bg: #D9F3E4;
    --med: #8F5200;
    --med-bg: #FFE9C2;
    --high: #B02A20;
    --high-bg: #FFD9D4;
}

/* ===== Global ===== */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
}

h1, h2, h3, h4 {
    font-family: 'Sora', 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: -0.02em !important;
    color: var(--fg) !important;
}

/* Page background — apply to the main scroll area */
.stApp {
    background: var(--bg) !important;
}

.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* Hide Streamlit's default header / hamburger / deploy button */
header[data-testid="stHeader"] {
    display: none !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
    background: var(--dark) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: var(--on-dark) !important;
}
[data-testid="stSidebar"] a {
    color: var(--on-dark) !important;
    padding: 10px 16px !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    margin: 2px 8px !important;
    display: block !important;
    transition: background 0.2s !important;
}
[data-testid="stSidebar"] a:hover {
    background: var(--dark2) !important;
}
[data-testid="stSidebar"] a[aria-current="page"] {
    background: var(--card) !important;
    color: var(--fg) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--on-dark) !important;
}

/* ===== Buttons ===== */
.stButton > button {
    background: var(--y) !important;
    color: var(--y-ink) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 18px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    min-height: 42px !important;
    transition: transform 0.15s, background 0.2s !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: var(--y2) !important;
    transform: translateY(-2px) !important;
    color: var(--y-ink) !important;
}
.stButton > button:focus {
    box-shadow: 0 0 0 3px rgba(245, 238, 80, 0.5) !important;
}

/* Secondary buttons (like "Log out") */
.stButton > button[kind="secondary"] {
    background: var(--track) !important;
    color: var(--fg) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--hover) !important;
}

/* ===== Inputs ===== */
.stTextInput input,
.stNumberInput input,
.stSelectbox > div > div,
.stDateInput input,
.stTextArea textarea {
    border-radius: 10px !important;
    border: 1px solid var(--line) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    min-height: 42px !important;
    background: var(--card) !important;
    color: var(--fg) !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stSelectbox > div > div:focus-within {
    border-color: var(--fg) !important;
    box-shadow: 0 0 0 2px rgba(32, 32, 32, 0.1) !important;
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 99px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: var(--muted) !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--card) !important;
    color: var(--fg) !important;
}

/* ===== Forms ===== */
[data-testid="stForm"] {
    background: var(--card) !important;
    border-radius: 22px !important;
    padding: 24px !important;
    border: 1px solid var(--line) !important;
    box-shadow: 0 0 0 1px transparent !important;
}

/* ===== Metrics (fallback) ===== */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border-radius: 22px !important;
    padding: 18px 22px !important;
    box-shadow: 0 0 0 1px var(--line) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Sora', sans-serif !important;
    color: var(--fg) !important;
    font-weight: 600 !important;
    letter-spacing: -0.03em !important;
}

/* ===== Dataframes ===== */
[data-testid="stDataFrame"] {
    border-radius: 18px !important;
    overflow: hidden !important;
    border: 1px solid var(--line) !important;
}
[data-testid="stDataFrame"] * {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
}

/* ===== Expander ===== */
.streamlit-expanderHeader, details summary {
    background: var(--card) !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
}

/* ===== File uploader ===== */
[data-testid="stFileUploader"] section {
    background: var(--card) !important;
    border-radius: 18px !important;
    border: 2px dashed var(--line) !important;
    padding: 24px !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--y) !important;
}

/* ===== Alerts ===== */
[data-testid="stAlert"] {
    border-radius: 14px !important;
    font-size: 14px !important;
}

/* ===== Custom classes we inject via markdown ===== */

/* KPI card */
.kpi-card {
    background: var(--card);
    border-radius: 22px;
    padding: 20px 22px;
    box-shadow: 0 0 0 1px var(--line);
    min-height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1),
                box-shadow 0.25s;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 30px -14px rgba(0, 0, 0, 0.35);
}
.kpi-label {
    font-size: 13px;
    color: var(--muted);
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.kpi-label .ic {
    width: 30px;
    height: 30px;
    border-radius: 9px;
    display: grid;
    place-items: center;
    font-size: 14px;
    font-weight: 700;
}
.kpi-value {
    font-family: 'Sora', sans-serif;
    font-size: 34px;
    font-weight: 600;
    color: var(--fg);
    letter-spacing: -0.03em;
    margin-top: 14px;
}
.kpi-sub {
    font-size: 12px;
    color: var(--muted);
    margin-top: 4px;
}

/* Dark KPI card */
.kpi-card.dark {
    background: var(--dark);
}
.kpi-card.dark .kpi-label,
.kpi-card.dark .kpi-sub { color: var(--muted-dark); }
.kpi-card.dark .kpi-value { color: var(--y); }

/* Yellow KPI card */
.kpi-card.yellow {
    background: var(--y);
}
.kpi-card.yellow .kpi-label,
.kpi-card.yellow .kpi-sub { color: #55521A; }
.kpi-card.yellow .kpi-value { color: var(--y-ink); }

/* Risk pills */
.risk-pill {
    padding: 3px 12px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
}
.risk-pill::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
}
.risk-low  { background: var(--low-bg); color: var(--low); }
.risk-med  { background: var(--med-bg); color: var(--med); }
.risk-high { background: var(--high-bg); color: var(--high); }

/* Prediction result panel */
.result-panel {
    background: var(--card);
    border-radius: 22px;
    padding: 26px 24px;
    box-shadow: 0 0 0 1px var(--line);
}
.result-id {
    font-family: 'Sora', sans-serif;
    font-size: 26px;
    font-weight: 600;
    color: var(--fg);
    margin: 6px 0 12px;
}
.result-top {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 8px;
}
.outcome {
    font-size: 13px;
    font-weight: 700;
}
.outcome.bad { color: var(--high); }
.outcome.ok  { color: var(--low); }
.result-prob {
    font-family: 'Sora', sans-serif;
    font-size: 68px;
    line-height: 1;
    font-weight: 600;
    color: var(--fg);
    letter-spacing: -0.04em;
    margin: 6px 0 4px;
}

/* Risk band strip */
.risk-band {
    display: flex;
    height: 10px;
    border-radius: 5px;
    overflow: hidden;
    margin: 14px 0 20px;
    position: relative;
}
.risk-band i {
    display: block;
    height: 100%;
}
.risk-band .low  { background: var(--low); }
.risk-band .med  { background: #F0A63A; }
.risk-band .high { background: var(--high); }

/* Section title */
.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 20px;
    font-weight: 600;
    color: var(--fg);
    margin: 12px 0 6px;
}
.section-sub {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 12px;
}

/* Tag chip (like "customers at risk" tags) */
.chip-tag {
    display: inline-block;
    background: var(--y);
    color: var(--y-ink);
    padding: 2px 10px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    margin: 0 4px;
}

/* Sidebar navigation label */
[data-testid="stSidebarNav"] {
    padding-top: 20px !important;
}

/* Hide the collapse button of the sidebar for a cleaner look */
[data-testid="stSidebarCollapseButton"] {
    color: var(--on-dark) !important;
}

/* Make the "st.write" greeting text look right */
.greeting {
    font-family: 'Sora', sans-serif;
    font-size: 42px;
    font-weight: 600;
    color: #FFFFFF;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}
.greeting-sub {
    color: #FFFFFF;
    font-weight: 500;
    font-size: 15px;
    margin-bottom: 24px;
}
</style>
"""

def inject():
    st.markdown(CSS, unsafe_allow_html=True)
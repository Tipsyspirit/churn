import streamlit as st

CSS = """
<style>
/* ===== Force dark text on titles, headers, subtitles ===== */

/* Streamlit's native title/header/subheader */
h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"] h1,
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3,
[data-testid="stHeading"] h4,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3,
[data-testid="stHeadingWithActionElements"] h4,
[data-testid="stHeadingContainer"] *,
[data-testid="stHeader"] * {
    color: #14141A !important;
}

/* Streamlit's native title/subheader/caption */
.stTitle,
.stHeader,
.stSubheader,
.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    color: #6B6B75 !important;
}

/* Force the main title dark */
.stTitle {
    color: #14141A !important;
    font-weight: 700 !important;
}

/* Any paragraph in the main area */
.main p,
[data-testid="stMarkdownContainer"] p {
    color: #14141A !important;
}

/* Sidebar should stay light — re-assert */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] * {
    color: #F4F4F2 !important;
}
/* =========================================================
   Fonts
   ========================================================= */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Sora:wght@500;600;700&display=swap');

/* =========================================================
   Design tokens
   ========================================================= */
:root {
    /* Surfaces */
    --bg: #F5F5F3;              /* page — active warm off-white */
    --bg-2: #EFEFEC;            /* subtle alternate surface */
    --card: #FFFFFF;
    --card-hover: #FCFCFB;

    /* Dark surfaces */
    --dark: #17171A;            /* sidebar, dark cards */
    --dark-2: #232326;
    --dark-3: #2E2E33;

    /* Borders */
    --line: #E7E7E3;
    --line-strong: #D8D8D3;
    --line-dark: #323236;
    --track: #ECECE8;

    /* Text */
    --fg: #14141A;
    --fg-2: #3A3A42;
    --muted: #6B6B75;
    --muted-2: #90909A;
    --on-dark: #F4F4F2;
    --on-dark-muted: #96969E;

    /* Brand — yellow accent */
    --y: #F5EE50;
    --y-2: #E4DD2C;
    --y-ink: #14141A;

    /* Risk */
    --low: #1B7F4C;
    --low-bg: #E0F5E9;
    --med: #9B5A00;
    --med-bg: #FFF0CF;
    --high: #B02A20;
    --high-bg: #FFE4DE;

    /* Shadows */
    --shadow-xs: 0 1px 2px rgba(20, 20, 26, 0.04);
    --shadow-sm: 0 1px 3px rgba(20, 20, 26, 0.06), 0 1px 2px rgba(20, 20, 26, 0.04);
    --shadow-md: 0 4px 16px -2px rgba(20, 20, 26, 0.08), 0 2px 6px -2px rgba(20, 20, 26, 0.05);
    --shadow-lg: 0 12px 32px -8px rgba(20, 20, 26, 0.14), 0 4px 12px -4px rgba(20, 20, 26, 0.08);

    /* Radii */
    --r-sm: 8px;
    --r-md: 12px;
    --r-lg: 16px;
    --r-xl: 22px;
}

/* =========================================================
   Global
   ========================================================= */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4 {
    font-family: 'Sora', 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: -0.025em !important;
    color: var(--fg) !important;
    font-weight: 600 !important;
}

.stApp {
    background: var(--bg) !important;
    color: var(--fg) !important;
}

.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1240px !important;
}

/* Hide Streamlit chrome */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
/* =========================================================
   SIDEBAR — LIGHT
   ========================================================= */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E7E7E3 !important;
    box-shadow: 1px 0 0 rgba(20, 20, 26, 0.04) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 12px !important;
}

/* Nav links */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    color: #3A3A42 !important;
    padding: 10px 16px !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    margin: 2px 12px !important;
    display: block !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    text-decoration: none !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: #F2F2EF !important;
    color: #14141A !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
    background: #F5EE50 !important;
    color: #14141A !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 2px rgba(20, 20, 26, 0.04) !important;
}

/* Logo/branding */
[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {
    content: "ChurnSight";
    display: block;
    font-family: 'Sora', sans-serif;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #14141A !important;
    padding: 20px 24px 24px;
}

/* All sidebar text is dark now */
[data-testid="stSidebar"] * {
    color: #3A3A42 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #14141A !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #3A3A42 !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {
    color: #3A3A42 !important;
}

/* Collapse chevron */
[data-testid="stSidebarCollapseButton"] {
    color: #3A3A42 !important;
}

/* =========================================================
   Buttons
   ========================================================= */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background: var(--y) !important;
    color: var(--y-ink) !important;
    border: none !important;
    border-radius: var(--r-md) !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    min-height: 42px !important;
    transition: transform 0.12s ease, background 0.15s ease, box-shadow 0.15s ease !important;
    box-shadow: var(--shadow-xs) !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background: var(--y-2) !important;
    transform: translateY(-1px) !important;
    color: var(--y-ink) !important;
    box-shadow: 0 6px 16px -4px rgba(245, 238, 80, 0.6) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Secondary buttons */
.stButton > button[kind="secondary"],
.stDownloadButton > button[kind="secondary"] {
    background: var(--card) !important;
    color: var(--fg) !important;
    border: 1px solid var(--line) !important;
    box-shadow: var(--shadow-xs) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--bg-2) !important;
    border-color: var(--line-strong) !important;
    transform: translateY(-1px) !important;
}

/* =========================================================
   Inputs
   ========================================================= */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input {
    border-radius: var(--r-md) !important;
    border: 1px solid var(--line) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    min-height: 42px !important;
    background: var(--card) !important;
    color: var(--fg) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
.stDateInput input:focus {
    border-color: var(--fg) !important;
    box-shadow: 0 0 0 3px rgba(20, 20, 26, 0.08) !important;
}

[data-baseweb="select"] > div {
    border-radius: var(--r-md) !important;
    border-color: var(--line) !important;
    min-height: 42px !important;
    background: var(--card) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: var(--fg) !important;
    box-shadow: 0 0 0 3px rgba(20, 20, 26, 0.08) !important;
}

.stSlider [data-baseweb="slider"] > div > div {
    background: var(--y) !important;
}

label, .stMarkdown label {
    font-weight: 500 !important;
    font-size: 13px !important;
    color: var(--fg-2) !important;
}

/* =========================================================
   Tabs
   ========================================================= */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: transparent !important;
    border-bottom: 1px solid var(--line) !important;
    padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--r-md) var(--r-md) 0 0 !important;
    padding: 10px 18px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    color: var(--muted) !important;
    border: none !important;
    transition: color 0.15s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--fg) !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: var(--fg) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--y) !important;
    margin-bottom: -1px !important;
}

/* =========================================================
   Forms
   ========================================================= */
[data-testid="stForm"] {
    background: var(--card) !important;
    border-radius: var(--r-xl) !important;
    padding: 26px !important;
    border: 1px solid var(--line) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* =========================================================
   Metrics
   ========================================================= */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border-radius: var(--r-lg) !important;
    padding: 20px 22px !important;
    border: 1px solid var(--line) !important;
    box-shadow: var(--shadow-xs) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Sora', sans-serif !important;
    color: var(--fg) !important;
    font-weight: 600 !important;
    letter-spacing: -0.03em !important;
}

/* =========================================================
   Dataframes
   ========================================================= */
[data-testid="stDataFrame"] {
    border-radius: var(--r-lg) !important;
    overflow: hidden !important;
    border: 1px solid var(--line) !important;
    box-shadow: var(--shadow-xs) !important;
}
[data-testid="stDataFrame"] * {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
}

/* =========================================================
   Expander
   ========================================================= */
details, .streamlit-expanderHeader {
    background: var(--card) !important;
    border-radius: var(--r-md) !important;
    border: 1px solid var(--line) !important;
    box-shadow: var(--shadow-xs) !important;
}
details summary {
    font-weight: 600 !important;
    padding: 12px 16px !important;
}

/* =========================================================
   File uploader
   ========================================================= */
[data-testid="stFileUploader"] section {
    background: var(--card) !important;
    border-radius: var(--r-xl) !important;
    border: 2px dashed var(--line-strong) !important;
    padding: 28px !important;
    transition: border-color 0.2s ease, background 0.2s ease !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--y) !important;
    background: #FEFEFA !important;
}

/* =========================================================
   Alerts
   ========================================================= */
[data-testid="stAlert"] {
    border-radius: var(--r-md) !important;
    font-size: 14px !important;
    padding: 14px 18px !important;
    border: 1px solid transparent !important;
}
[data-testid="stAlert"][data-baseweb="notification"][kind="info"] {
    background: #EEF1FA !important;
    border-color: #DDE4F5 !important;
}
[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {
    background: var(--low-bg) !important;
    border-color: #C6EAD5 !important;
}
[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {
    background: var(--med-bg) !important;
    border-color: #F0DFB8 !important;
}
[data-testid="stAlert"][data-baseapi="notification"][kind="negative"] {
    background: var(--high-bg) !important;
    border-color: #F5C8C0 !important;
}

/* =========================================================
   Custom classes
   ========================================================= */

/* ---- KPI card ---- */
.kpi-card {
    background: var(--card);
    border-radius: var(--r-xl);
    padding: 20px 22px;
    border: 1px solid var(--line);
    box-shadow: var(--shadow-xs);
    min-height: 132px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.22s cubic-bezier(0.2, 0.8, 0.2, 1),
                box-shadow 0.22s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
}
.kpi-label {
    font-size: 13px;
    color: var(--muted);
    font-weight: 500;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}
.kpi-label .ic {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    font-size: 15px;
    flex: none;
}
.kpi-value {
    font-family: 'Sora', sans-serif;
    font-size: 36px;
    font-weight: 600;
    color: var(--fg);
    letter-spacing: -0.035em;
    line-height: 1;
    margin-top: 16px;
    font-variant-numeric: tabular-nums;
}
.kpi-sub {
    font-size: 12px;
    color: var(--muted);
    margin-top: 8px;
    font-weight: 500;
}
.kpi-card.dark {
    background: var(--dark);
    border-color: transparent;
}
.kpi-card.dark .kpi-label,
.kpi-card.dark .kpi-sub { color: var(--on-dark-muted); }
.kpi-card.dark .kpi-value { color: var(--y); }

.kpi-card.yellow {
    background: var(--y);
    border-color: transparent;
}
.kpi-card.yellow .kpi-label { color: #55521A; }
.kpi-card.yellow .kpi-sub { color: #6E6A1E; }
.kpi-card.yellow .kpi-value { color: var(--y-ink); }

/* ---- Risk pills ---- */
.risk-pill {
    padding: 3px 12px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    letter-spacing: 0.01em;
    line-height: 1.6;
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

/* ---- Prediction result panel ---- */
.result-panel {
    background: var(--card);
    border-radius: var(--r-xl);
    padding: 28px 26px;
    border: 1px solid var(--line);
    box-shadow: var(--shadow-md);
    animation: fadeUp 0.35s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.result-eyebrow {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 600;
}
.result-id {
    font-family: 'Sora', sans-serif;
    font-size: 26px;
    font-weight: 600;
    color: var(--fg);
    margin: 8px 0 14px;
    letter-spacing: -0.02em;
}
.result-top {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 8px;
}
.outcome { font-size: 13px; font-weight: 700; }
.outcome.bad { color: var(--high); }
.outcome.ok  { color: var(--low); }
.result-prob {
    font-family: 'Sora', sans-serif;
    font-size: 72px;
    line-height: 1;
    font-weight: 600;
    color: var(--fg);
    letter-spacing: -0.045em;
    margin: 8px 0 4px;
    font-variant-numeric: tabular-nums;
}

/* ---- Risk band ---- */
.risk-band {
    display: flex;
    height: 10px;
    border-radius: 5px;
    overflow: visible;
    margin: 18px 0 8px;
    position: relative;
}
.risk-band i {
    display: block;
    height: 100%;
}
.risk-band .low  { background: var(--low); border-radius: 5px 0 0 5px; }
.risk-band .med  { background: #F0A63A; }
.risk-band .high { background: var(--high); border-radius: 0 5px 5px 0; }
.risk-band .mk {
    position: absolute;
    top: -6px;
    width: 4px;
    height: 22px;
    border-radius: 2px;
    background: var(--fg);
    transform: translateX(-50%);
    outline: 3px solid var(--card);
    transition: left 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.band-labels {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: var(--muted);
    font-weight: 500;
}

/* ---- Section ---- */
.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: var(--fg);
    margin: 24px 0 4px;
    letter-spacing: -0.015em;
}
.section-sub {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 14px;
}

/* ---- Page header ---- */
.page-head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
    padding: 12px 0 22px;
    animation: fadeIn 0.35s ease-out;
}
.page-head h1 {
    font-family: 'Sora', sans-serif;
    font-size: clamp(28px, 3.4vw, 42px);
    line-height: 1.05;
    font-weight: 700;
    color: var(--fg);
    margin: 0;
    letter-spacing: -0.03em;
}
.page-head p {
    margin: 8px 0 0;
    color: var(--muted);
    font-size: 15px;
    font-weight: 500;
    max-width: 60ch;
}

/* ---- Info strip ---- */
.strip {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 18px;
    border-radius: var(--r-md);
    font-size: 13px;
    font-weight: 500;
    background: var(--card);
    border: 1px solid var(--line);
    box-shadow: var(--shadow-xs);
    margin-bottom: 18px;
}
.strip .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--low);
    flex: none;
}
.strip.dark {
    background: var(--dark);
    color: var(--on-dark);
    border-color: transparent;
}
.strip.dark .dot { background: #7BE0A4; }

/* ---- Empty state ---- */
.empty {
    text-align: center;
    padding: 44px 24px;
    display: grid;
    gap: 12px;
    justify-items: center;
}
.empty h3 { font-size: 20px; margin: 0; }
.empty p { color: var(--muted); max-width: 46ch; margin: 0; }
.empty .ic {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--track);
    display: grid;
    place-items: center;
    font-size: 22px;
    color: var(--muted);
}

/* ---- Greeting ---- */
.greeting {
    font-family: 'Sora', sans-serif;
    font-size: 42px;
    font-weight: 600;
    color: var(--fg);
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}
.greeting-sub {
    color: var(--muted);
    font-weight: 500;
    font-size: 15px;
    margin-bottom: 24px;
}

/* ---- Mono ---- */
.mono {
    font-family: ui-monospace, "SF Mono", Menlo, monospace !important;
    font-variant-numeric: tabular-nums;
}

/* =========================================================
   Animations
   ========================================================= */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
}
/* =========================================================
   Chart cards
   ========================================================= */

/* Every st.plotly_chart gets a card wrapper via CSS */
[data-testid="stPlotlyChart"] {
    background: var(--card);
    border-radius: var(--r-xl);
    border: 1px solid var(--line);
    box-shadow: var(--shadow-sm);
    padding: 22px 22px 8px;
    margin-bottom: 16px;
    transition: box-shadow 0.2s ease;
}
[data-testid="stPlotlyChart"]:hover {
    box-shadow: var(--shadow-md);
}

/* Remove extra inner padding Plotly adds */
[data-testid="stPlotlyChart"] .js-plotly-plot {
    border-radius: 0 !important;
}

/* Two-up chart rows need equal heights — force them */
[data-testid="stHorizontalBlock"] [data-testid="stPlotlyChart"] {
    min-height: 340px;
}

/* Chart section header (styled via markdown above the chart) */
.chart-card-header {
    margin: 24px 0 10px;
    padding: 0 4px;
}
.chart-card-title {
    font-family: 'Sora', sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: var(--fg);
    letter-spacing: -0.015em;
}
.chart-card-sub {
    font-size: 12px;
    color: var(--muted);
    margin-top: 4px;
    font-weight: 500;
}

/* =========================================================
   Column alignment fixes
   ========================================================= */

/* Make every column stretch to equal height */
[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}

/* Ensure vertical blocks (columns) fill their height */
[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
}

/* Nested markdown inside columns should not collapse */
[data-testid="column"] > div {
    flex: 1 0 auto !important;
    display: flex !important;
    flex-direction: column !important;
}

/* =========================================================
   KPI row alignment
   ========================================================= */

/* Consistent spacing for KPI rows */
[data-testid="stHorizontalBlock"] .kpi-card {
    height: 100%;
}

/* Prevent Streamlit's default column gaps from being uneven */
[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    padding: 0 6px;
}
[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {
    padding-left: 0;
}
[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
    padding-right: 0;
}

/* =========================================================
   Dataframe + table alignment
   ========================================================= */

[data-testid="stDataFrame"] {
    margin-bottom: 16px;
}

/* =========================================================
   Section spacing consistency
   ========================================================= */
.section-title + .section-sub {
    margin-top: -2px;
}
/* =========================================================
   Fix white-on-white text issues
   ========================================================= */

/* Main app text — force dark text on light background */
.stApp,
.stApp p,
.stApp span,
.stApp div,
.stApp label,
.stApp .stMarkdown,
.stApp .stMarkdown p,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stText"] {
    color: var(--fg) !important;
}

/* Caption text (small grey text under titles) */
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] *,
.stApp .stCaption,
.stApp small {
    color: var(--muted) !important;
}

/* File uploader — fix all inner text */
[data-testid="stFileUploader"] {
    color: var(--fg) !important;
}
[data-testid="stFileUploader"] *,
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] div {
    color: var(--fg) !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--muted) !important;
}

/* The "Browse files" button inside the uploader keeps its dark bg + white text */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] button span,
[data-testid="stFileUploader"] button div {
    color: #FFFFFF !important;
    background: var(--dark) !important;
}

/* Expander header text */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    color: var(--fg) !important;
}

/* Sidebar labels should stay light on dark bg */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--on-dark) !important;
}

/* Widget labels (above inputs) */
.stApp [data-testid="stWidgetLabel"],
.stApp [data-testid="stWidgetLabel"] *,
.stApp [data-testid="stWidgetLabel"] p {
    color: var(--fg) !important;
}

/* Selectbox, multiselect — placeholder text */
[data-baseweb="select"] [data-testid="stMarkdownContainer"],
[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: var(--fg) !important;
}
[data-baseweb="select"] [aria-hidden="true"] {
    color: var(--muted) !important;
}

/* Tables / dataframes headers */
[data-testid="stDataFrame"] *,
[data-testid="stTable"] * {
    color: var(--fg) !important;
}

/* Tooltip and hover text */
[data-testid="stTooltipIcon"],
[data-testid="stTooltipContent"] {
    color: var(--fg) !important;
}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)
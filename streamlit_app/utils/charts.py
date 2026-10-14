import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

RISK_COLORS = {"low": "#1E7A48", "med": "#8F5200", "high": "#B02A20"}

def risk_donut(df: pd.DataFrame):
    counts = df["risk"].value_counts().reset_index()
    counts.columns = ["risk", "count"]
    fig = px.pie(counts, names="risk", values="count", hole=0.6,
                 color="risk", color_discrete_map=RISK_COLORS,
                 title="Risk distribution")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=50, b=10))
    return fig

def churn_by_tenure(df: pd.DataFrame):
    df = df.copy()
    df["tenure_bucket"] = pd.cut(df["Tenure"], bins=[0,6,12,24,48,999],
                                  labels=["0-6","7-12","13-24","25-48","49+"])
    grouped = df.groupby("tenure_bucket", observed=True).agg(
        customers=("churn_probability","count"),
        high_risk=("risk", lambda s: (s=="high").sum()),
    ).reset_index()
    fig = go.Figure()
    fig.add_bar(x=grouped["tenure_bucket"], y=grouped["customers"], name="All customers", marker_color="#E9E9E4")
    fig.add_bar(x=grouped["tenure_bucket"], y=grouped["high_risk"], name="High risk", marker_color="#F5EE50")
    fig.update_layout(barmode="group", height=340, title="Customers and high-risk by tenure")
    return fig

def probability_histogram(df: pd.DataFrame):
    fig = px.histogram(df, x="churn_probability", nbins=30,
                       color="risk", color_discrete_map=RISK_COLORS,
                       title="Churn probability distribution")
    fig.update_layout(height=320)
    return fig
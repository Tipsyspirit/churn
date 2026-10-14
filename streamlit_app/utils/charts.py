import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Design palette
Y = "#F5EE50"
Y2 = "#E3DB2E"
DARK = "#1D1D1D"
CARD = "#FFFFFF"
MUTED = "#636363"
LINE = "#E3E3E0"
TRACK = "#E9E9E6"
LOW = "#1E7A48"
MED = "#8F5200"
HIGH = "#B02A20"

RISK_COLORS = {"low": LOW, "med": MED, "high": HIGH}
RISK_LABELS = {"low": "Low", "med": "Medium", "high": "High"}

# Common layout for all charts
def _theme(fig, height=340, title=None):
    fig.update_layout(
        height=height,
        title=dict(
            text=title,
            font=dict(family="Sora, sans-serif", size=16, color=DARK),
            x=0, xanchor="left",
        ) if title else None,
        font=dict(family="Plus Jakarta Sans, sans-serif", size=13, color=DARK),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        margin=dict(l=20, r=20, t=50 if title else 20, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            font=dict(size=12),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=LINE,
        tickfont=dict(color=MUTED, size=12),
    )
    fig.update_yaxes(
        gridcolor=LINE,
        gridwidth=1,
        zeroline=False,
        tickfont=dict(color=MUTED, size=12),
    )
    return fig


def risk_donut(df: pd.DataFrame):
    counts = df["risk"].value_counts().reset_index()
    counts.columns = ["risk", "count"]
    counts["label"] = counts["risk"].map(RISK_LABELS)
    fig = px.pie(
        counts, names="label", values="count", hole=0.62,
        color="risk", color_discrete_map=RISK_COLORS,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        marker=dict(line=dict(color=CARD, width=3)),
        textfont=dict(family="Plus Jakarta Sans, sans-serif", size=12),
    )
    _theme(fig, height=320, title="Risk distribution")
    return fig


def churn_by_tenure(df: pd.DataFrame):
    df = df.copy()
    df["bucket"] = pd.cut(
        df["Tenure"], bins=[-1, 6, 12, 24, 48, 999],
        labels=["0-6", "7-12", "13-24", "25-48", "49+"],
    )
    grouped = (
        df.groupby("bucket", observed=True)
        .agg(customers=("churn_probability", "count"),
             high_risk=("risk", lambda s: (s == "high").sum()))
        .reset_index()
    )
    fig = go.Figure()
    fig.add_bar(
        x=grouped["bucket"], y=grouped["customers"],
        name="All customers",
        marker_color="#E9E9E4",
        marker_line_width=0,
    )
    fig.add_bar(
        x=grouped["bucket"], y=grouped["high_risk"],
        name="High risk",
        marker_color=Y,
        marker_line_width=0,
    )
    fig.update_layout(barmode="group", bargap=0.35, bargroupgap=0.1)
    _theme(fig, height=340, title="Customers and high-risk by tenure")
    return fig


def probability_histogram(df: pd.DataFrame):
    fig = px.histogram(
        df, x="churn_probability", nbins=30,
        color="risk", color_discrete_map=RISK_COLORS,
        labels={"churn_probability": "Churn probability"},
    )
    fig.update_traces(marker_line_width=0)
    _theme(fig, height=320, title="Churn probability distribution")
    return fig
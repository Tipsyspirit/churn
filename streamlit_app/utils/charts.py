import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ---------------------------------------------------------
# Design tokens
# ---------------------------------------------------------
Y = "#F5EE50"
Y2 = "#E3DB2E"
DARK = "#14141A"
CARD = "#FFFFFF"
MUTED = "#6B6B75"
MUTED_2 = "#90909A"
LINE = "#E7E7E3"
TRACK = "#ECECE8"
FG = "#14141A"

LOW = "#1B7F4C"
MED = "#9B5A00"
HIGH = "#B02A20"

RISK_COLORS = {"low": LOW, "med": MED, "high": HIGH}
RISK_LABELS = {"low": "Low", "med": "Medium", "high": "High"}

FONT_FAMILY = "Plus Jakarta Sans, system-ui, sans-serif"
HEADING_FONT = "Sora, Plus Jakarta Sans, sans-serif"


# ---------------------------------------------------------
# Shared theme
# ---------------------------------------------------------
def _apply_theme(fig, height: int = 340):
    """Apply the ChurnSight visual language to any Plotly figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=36, r=20, t=20, b=40),
        font=dict(family=FONT_FAMILY, size=12, color=FG),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hoverlabel=dict(
            bgcolor=DARK,
            bordercolor=DARK,
            font=dict(family=FONT_FAMILY, size=12, color="#F4F4F2"),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=LINE,
        tickfont=dict(color=MUTED, size=11),
        zeroline=False,
        title=None,
    )
    fig.update_yaxes(
        gridcolor=LINE,
        gridwidth=1,
        tickfont=dict(color=MUTED, size=11),
        zeroline=False,
        title=None,
    )
    return fig


# ---------------------------------------------------------
# Risk donut
# ---------------------------------------------------------
def risk_donut(df: pd.DataFrame, height: int = 320):
    counts = df["risk"].value_counts().reset_index()
    counts.columns = ["risk", "count"]
    counts["label"] = counts["risk"].map(RISK_LABELS)
    # Preserve order low → med → high
    order = ["Low", "Medium", "High"]
    counts["label"] = pd.Categorical(counts["label"], categories=order, ordered=True)
    counts = counts.sort_values("label")

    fig = go.Figure(
        data=[
            go.Pie(
                labels=counts["label"],
                values=counts["count"],
                hole=0.62,
                marker=dict(
                    colors=[RISK_COLORS["low"], RISK_COLORS["med"], RISK_COLORS["high"]],
                    line=dict(color=CARD, width=3),
                ),
                textinfo="percent",
                textposition="outside",
                textfont=dict(family=FONT_FAMILY, size=12, color=FG),
                hovertemplate="<b>%{label}</b><br>%{value} customers<br>%{percent}<extra></extra>",
                sort=False,
                direction="clockwise",
            )
        ]
    )
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family=FONT_FAMILY, size=12, color=FG),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(family=FONT_FAMILY, size=12, color=MUTED),
            itemsizing="constant",
        ),
        hoverlabel=dict(
            bgcolor=DARK,
            bordercolor=DARK,
            font=dict(family=FONT_FAMILY, size=12, color="#F4F4F2"),
        ),
    )
    return fig


# ---------------------------------------------------------
# Customers by tenure (grouped bars)
# ---------------------------------------------------------
def churn_by_tenure(df: pd.DataFrame, height: int = 340):
    df = df.copy()
    df["bucket"] = pd.cut(
        df["Tenure"],
        bins=[-1, 6, 12, 24, 48, 999],
        labels=["0–6", "7–12", "13–24", "25–48", "49+"],
    )
    grouped = (
        df.groupby("bucket", observed=True)
        .agg(
            customers=("churn_probability", "count"),
            high_risk=("risk", lambda s: (s == "high").sum()),
        )
        .reset_index()
    )

    fig = go.Figure()
    fig.add_bar(
        x=grouped["bucket"],
        y=grouped["customers"],
        name="All customers",
        marker=dict(color=TRACK, line=dict(width=0)),
        hovertemplate="<b>%{x} months</b><br>All customers: %{y}<extra></extra>",
    )
    fig.add_bar(
        x=grouped["bucket"],
        y=grouped["high_risk"],
        name="High risk",
        marker=dict(color=Y, line=dict(width=0)),
        hovertemplate="<b>%{x} months</b><br>High risk: %{y}<extra></extra>",
    )
    fig.update_layout(barmode="group", bargap=0.35, bargroupgap=0.12)
    _apply_theme(fig, height=height)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(family=FONT_FAMILY, size=12, color=MUTED),
        ),
    )
    return fig


# ---------------------------------------------------------
# Churn probability histogram
# ---------------------------------------------------------
def probability_histogram(df: pd.DataFrame, height: int = 340):
    df = df.copy()
    # Color each bar by the dominant risk band of the bin
    fig = go.Figure()

    # Draw three separate traces stacked, one per risk band
    for risk, label, color in [
        ("low", "Low", LOW),
        ("med", "Medium", MED),
        ("high", "High", HIGH),
    ]:
        subset = df[df["risk"] == risk]["churn_probability"]
        if len(subset) == 0:
            continue
        fig.add_trace(
            go.Histogram(
                x=subset,
                name=label,
                nbinsx=30,
                marker=dict(color=color, line=dict(width=0)),
                opacity=0.9,
                hovertemplate="<b>%{x:.2f}</b><br>" + label + ": %{y}<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="stack",
        bargap=0.04,
    )
    _apply_theme(fig, height=height)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(family=FONT_FAMILY, size=12, color=MUTED),
        ),
    )
    fig.update_xaxes(title=None, tickformat=".0%")
    return fig


# ---------------------------------------------------------
# Tenure × average risk line (optional chart)
# ---------------------------------------------------------
def risk_by_recency(df: pd.DataFrame, height: int = 320):
    df = df.copy()
    df["bucket"] = pd.cut(
        df["DaySinceLastOrder"],
        bins=[-1, 15, 30, 45, 60, 90, 999],
        labels=["0–15", "16–30", "31–45", "46–60", "61–90", "90+"],
    )
    grouped = (
        df.groupby("bucket", observed=True)
        .agg(avg_risk=("churn_probability", "mean"), n=("churn_probability", "count"))
        .reset_index()
    )

    fig = go.Figure()
    fig.add_scatter(
        x=grouped["bucket"],
        y=grouped["avg_risk"],
        mode="lines+markers",
        line=dict(color=FG, width=2.5, shape="spline", smoothing=0.5),
        marker=dict(color=Y, size=10, line=dict(color=FG, width=2)),
        hovertemplate="<b>%{x} days</b><br>Avg risk: %{y:.1%}<extra></extra>",
        name="Average risk",
    )

    _apply_theme(fig, height=height)
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    return fig


# ---------------------------------------------------------
# Feature importance (horizontal bars)
# ---------------------------------------------------------
def feature_importance(names, values, height: int = 360):
    # Sort ascending so the largest appears at the top
    pairs = sorted(zip(names, values), key=lambda p: p[1])
    names_sorted = [p[0] for p in pairs]
    values_sorted = [p[1] for p in pairs]

    fig = go.Figure(
        go.Bar(
            x=values_sorted,
            y=names_sorted,
            orientation="h",
            marker=dict(color=Y, line=dict(width=0)),
            hovertemplate="<b>%{y}</b><br>Importance: %{x:.3f}<extra></extra>",
        )
    )

    _apply_theme(fig, height=height)
    fig.update_xaxes(showgrid=True, gridcolor=LINE)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=11, color=FG))
    return fig
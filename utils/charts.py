"""
charts.py — Plotly chart-building functions for the dashboard.

Each function returns a plotly Figure object. The caller renders it
with st.plotly_chart(fig, use_container_width=True).

A single consistent colour palette is used across all charts.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ------------------------------------------------------------------
# Shared colour palette (Plotly's "Bold" qualitative palette)
# ------------------------------------------------------------------
COLOR_PALETTE = px.colors.qualitative.Bold
TEMPLATE = "plotly_white"


# ------------------------------------------------------------------
# Chart 1 — Campaign-wise Spend vs Revenue (grouped bar)
# ------------------------------------------------------------------

def campaign_spend_vs_revenue(df_agg: pd.DataFrame) -> go.Figure:
    """
    Grouped bar chart comparing Spend and Revenue per campaign.

    Parameters
    ----------
    df_agg : pd.DataFrame
        Must have columns: campaign name, spend, revenue.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_agg["campaign name"],
        y=df_agg["spend"],
        name="Spend",
        marker_color=COLOR_PALETTE[0],
    ))
    fig.add_trace(go.Bar(
        x=df_agg["campaign name"],
        y=df_agg["revenue"],
        name="Revenue",
        marker_color=COLOR_PALETTE[1],
    ))

    fig.update_layout(
        title="Campaign-wise Spend vs Revenue",
        barmode="group",
        xaxis_title="Campaign",
        yaxis_title="Amount (₹)",
        template=TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
    )
    return fig


# ------------------------------------------------------------------
# Chart 2 — Daily Spend & Revenue trend (line chart)
# ------------------------------------------------------------------

def daily_trend(df: pd.DataFrame) -> go.Figure:
    """
    Line chart showing daily Spend and Revenue over time.

    Parameters
    ----------
    df : pd.DataFrame
        Row-level data with columns: date, spend, revenue.
    """
    daily = df.groupby("date", as_index=False).agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    ).sort_values("date")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["spend"],
        mode="lines+markers", name="Daily Spend",
        line=dict(color=COLOR_PALETTE[2], width=2),
        marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["revenue"],
        mode="lines+markers", name="Daily Revenue",
        line=dict(color=COLOR_PALETTE[3], width=2),
        marker=dict(size=5),
    ))

    fig.update_layout(
        title="Daily Spend & Revenue Trend",
        xaxis_title="Date",
        yaxis_title="Amount (₹)",
        template=TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
        hovermode="x unified",
    )
    return fig


# ------------------------------------------------------------------
# Chart 3 — Platform-wise breakdown (stacked bar)
# ------------------------------------------------------------------

def platform_breakdown(df_platform: pd.DataFrame) -> go.Figure:
    """
    Grouped bar chart showing Spend, Revenue, and ROI split by platform.

    Parameters
    ----------
    df_platform : pd.DataFrame
        Aggregated by platform with columns: platform, spend, revenue, roi (%).
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_platform["platform"],
        y=df_platform["spend"],
        name="Spend",
        marker_color=COLOR_PALETTE[4],
    ))
    fig.add_trace(go.Bar(
        x=df_platform["platform"],
        y=df_platform["revenue"],
        name="Revenue",
        marker_color=COLOR_PALETTE[5],
    ))

    fig.update_layout(
        title="Platform-wise Spend & Revenue",
        barmode="group",
        xaxis_title="Platform",
        yaxis_title="Amount (₹)",
        template=TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
    )
    return fig


# ------------------------------------------------------------------
# Chart 4 — Top & Bottom campaigns by ROI (horizontal bar)
# ------------------------------------------------------------------

def top_bottom_roi(df_agg: pd.DataFrame, n: int = 5) -> go.Figure:
    """
    Horizontal bar chart showing Top N and Bottom N campaigns by ROI.

    Parameters
    ----------
    df_agg : pd.DataFrame
        Aggregated by campaign with column: roi (%).
    n : int
        Number of campaigns to show from each end.
    """
    sorted_df = df_agg.sort_values("roi (%)", ascending=False)

    top = sorted_df.head(n).copy()
    bottom = sorted_df.tail(n).copy()

    # Combine, keeping order: bottom first (so top appears at the top of bar chart)
    combined = pd.concat([bottom, top]).drop_duplicates(subset=["campaign name"])

    fig = go.Figure()

    # Colour bars: green for positive ROI, red for negative
    colors = [
        COLOR_PALETTE[1] if v >= 0 else COLOR_PALETTE[6]
        for v in combined["roi (%)"]
    ]

    fig.add_trace(go.Bar(
        y=combined["campaign name"],
        x=combined["roi (%)"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in combined["roi (%)"]],
        textposition="outside",
    ))

    fig.update_layout(
        title=f"Top {n} & Bottom {n} Campaigns by ROI",
        xaxis_title="ROI (%)",
        yaxis_title="",
        template=TEMPLATE,
        margin=dict(t=60, l=180, b=40),
        showlegend=False,
    )
    return fig

"""
charts.py — Plotly chart-building functions for the dashboard.

Each function returns a plotly Figure object. The caller renders it
with st.plotly_chart(fig, use_container_width=True).

Premium dark theme with neon accents and modern chart styles.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# Shared colour palette — Neon accents on dark backgrounds
# ------------------------------------------------------------------
NEON_CYAN = "#00d4ff"
NEON_MAGENTA = "#ff006e"
NEON_LIME = "#39ff14"
NEON_AMBER = "#ffbe0b"
NEON_PURPLE = "#b537f2"
NEON_CORAL = "#ff6b6b"
NEON_TEAL = "#20e3b2"
NEON_PINK = "#ff71ce"

COLOR_PALETTE = [
    NEON_CYAN, NEON_MAGENTA, NEON_LIME, NEON_AMBER,
    NEON_PURPLE, NEON_CORAL, NEON_TEAL, NEON_PINK,
]

# Transparent dark background for charts
CHART_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.06)"
AXIS_COLOR = "rgba(255,255,255,0.4)"
FONT_COLOR = "rgba(255,255,255,0.85)"
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"


def _base_layout(**overrides) -> dict:
    """Return a common layout dict for all charts."""
    base = dict(
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR, size=12),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=AXIS_COLOR, size=11),
            title_font=dict(color=AXIS_COLOR, size=12),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=AXIS_COLOR, size=11),
            title_font=dict(color=AXIS_COLOR, size=12),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=FONT_COLOR, size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=60, b=40, l=60, r=20),
        hoverlabel=dict(
            bgcolor="rgba(15,20,40,0.92)",
            bordercolor="rgba(0,212,255,0.3)",
            font=dict(color="#ffffff", family=FONT_FAMILY, size=13),
        ),
    )
    base.update(overrides)
    return base


# ------------------------------------------------------------------
# Chart 1 — Campaign-wise Spend vs Revenue (gradient bars)
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
        marker=dict(
            color=NEON_CYAN,
            opacity=0.85,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x}</b><br>Spend: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df_agg["campaign name"],
        y=df_agg["revenue"],
        name="Revenue",
        marker=dict(
            color=NEON_MAGENTA,
            opacity=0.85,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(
            title=dict(
                text="💰 Campaign Spend vs Revenue",
                font=dict(size=16, color=FONT_COLOR),
                x=0,
                xanchor="left",
            ),
            barmode="group",
            bargap=0.25,
            bargroupgap=0.1,
        )
    )
    return fig


# ------------------------------------------------------------------
# Chart 2 — Daily Spend & Revenue trend (area chart with gradient)
# ------------------------------------------------------------------

def daily_trend(df: pd.DataFrame) -> go.Figure:
    """
    Area chart showing daily Spend and Revenue over time with
    gradient fills and smooth spline curves.

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

    # Revenue area (behind)
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["revenue"],
        mode="lines",
        name="Daily Revenue",
        line=dict(color=NEON_LIME, width=2.5, shape="spline", smoothing=1.0),
        fill="tozeroy",
        fillcolor="rgba(57,255,20,0.08)",
        hovertemplate="<b>%{x|%d %b}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    ))

    # Spend area (front)
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["spend"],
        mode="lines",
        name="Daily Spend",
        line=dict(color=NEON_CYAN, width=2.5, shape="spline", smoothing=1.0),
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.08)",
        hovertemplate="<b>%{x|%d %b}</b><br>Spend: ₹%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(
            title=dict(
                text="📈 Daily Spend & Revenue Trend",
                font=dict(size=16, color=FONT_COLOR),
                x=0,
                xanchor="left",
            ),
            hovermode="x unified",
        )
    )
    return fig


# ------------------------------------------------------------------
# Chart 3 — Platform breakdown (donut chart)
# ------------------------------------------------------------------

def platform_breakdown(df_platform: pd.DataFrame) -> go.Figure:
    """
    Donut chart showing revenue split by platform with center stats.

    Parameters
    ----------
    df_platform : pd.DataFrame
        Aggregated by platform with columns: platform, spend, revenue, roi (%).
    """
    total_rev = df_platform["revenue"].sum()

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=df_platform["platform"],
        values=df_platform["revenue"],
        hole=0.55,
        marker=dict(
            colors=COLOR_PALETTE[:len(df_platform)],
            line=dict(color="rgba(10,14,39,1)", width=3),
        ),
        textinfo="label+percent",
        textfont=dict(color=FONT_COLOR, size=12, family=FONT_FAMILY),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Revenue: ₹%{value:,.0f}<br>"
            "Share: %{percent}<extra></extra>"
        ),
        pull=[0.03] * len(df_platform),
    ))

    fig.update_layout(
        **_base_layout(
            title=dict(
                text="🎯 Platform Revenue Share",
                font=dict(size=16, color=FONT_COLOR),
                x=0,
                xanchor="left",
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color=FONT_COLOR, size=11),
                bgcolor="rgba(0,0,0,0)",
            ),
            annotations=[
                dict(
                    text=f"₹{total_rev:,.0f}",
                    x=0.5, y=0.55,
                    font=dict(size=18, color=NEON_CYAN, family=FONT_FAMILY),
                    showarrow=False,
                ),
                dict(
                    text="Total Revenue",
                    x=0.5, y=0.45,
                    font=dict(size=11, color=AXIS_COLOR, family=FONT_FAMILY),
                    showarrow=False,
                ),
            ],
        )
    )
    return fig


# ------------------------------------------------------------------
# Chart 4 — Top & Bottom campaigns by ROI (lollipop chart)
# ------------------------------------------------------------------

def top_bottom_roi(df_agg: pd.DataFrame, n: int = 5) -> go.Figure:
    """
    Lollipop chart showing Top N and Bottom N campaigns by ROI.

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

    # Combine, keeping order: bottom first (so top appears at the top of chart)
    combined = pd.concat([bottom, top]).drop_duplicates(subset=["campaign name"])

    # Colour: green for positive, red for negative
    colors = [NEON_LIME if v >= 0 else NEON_CORAL for v in combined["roi (%)"]]

    fig = go.Figure()

    # Lollipop stems (lines from 0 to value)
    for i, (_, row) in enumerate(combined.iterrows()):
        fig.add_trace(go.Scatter(
            x=[0, row["roi (%)"]],
            y=[row["campaign name"], row["campaign name"]],
            mode="lines",
            line=dict(
                color=colors[i],
                width=2,
            ),
            showlegend=False,
            hoverinfo="skip",
        ))

    # Lollipop circles
    fig.add_trace(go.Scatter(
        y=combined["campaign name"],
        x=combined["roi (%)"],
        mode="markers+text",
        marker=dict(
            size=14,
            color=colors,
            line=dict(width=2, color="rgba(10,14,39,1)"),
            opacity=0.9,
        ),
        text=[f"{v:.1f}%" for v in combined["roi (%)"]],
        textposition="middle right",
        textfont=dict(color=FONT_COLOR, size=11, family=FONT_FAMILY),
        hovertemplate="<b>%{y}</b><br>ROI: %{x:.1f}%<extra></extra>",
        showlegend=False,
        cliponaxis=False,
    ))

    fig.update_layout(
        **_base_layout(
            title=dict(
                text=f"🏆 Top {n} & Bottom {n} Campaigns by ROI",
                font=dict(size=16, color=FONT_COLOR),
                x=0,
                xanchor="left",
            ),
            xaxis_title="ROI (%)",
            yaxis_title="",
            showlegend=False,
            margin=dict(t=60, l=180, b=40, r=80),
        )
    )

    # Add a zero line
    fig.add_vline(
        x=0,
        line_dash="dot",
        line_color="rgba(255,255,255,0.2)",
        line_width=1,
    )

    return fig

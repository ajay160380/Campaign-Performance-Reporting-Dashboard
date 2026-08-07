"""
metrics.py — Marketing performance metric calculations.

All functions operate on pandas DataFrames / Series and handle
divide-by-zero gracefully (returning 0.0 instead of inf/NaN).
"""

import pandas as pd


# ------------------------------------------------------------------
# Row-level metric columns (added to the DataFrame)
# ------------------------------------------------------------------

def add_metric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute CTR, CPC, CPM, Conversion Rate, and ROI for every row
    and append them as new columns.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain: impressions, clicks, spend, revenue, conversions.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with five new columns added.
    """
    df = df.copy()

    df["ctr (%)"] = safe_divide(df["clicks"], df["impressions"]) * 100
    df["cpc"] = safe_divide(df["spend"], df["clicks"])
    df["cpm"] = safe_divide(df["spend"], df["impressions"]) * 1000
    df["conversion rate (%)"] = safe_divide(df["conversions"], df["clicks"]) * 100
    df["roi (%)"] = safe_divide(df["revenue"] - df["spend"], df["spend"]) * 100

    return df


# ------------------------------------------------------------------
# Aggregated KPI summary (for top cards)
# ------------------------------------------------------------------

def compute_summary_kpis(df: pd.DataFrame) -> dict:
    """
    Return a dictionary of aggregated KPIs using correct weighted
    calculations (not simple averages of per-row ratios).

    Keys: total_spend, total_revenue, total_clicks, total_impressions,
          total_conversions, overall_ctr, overall_cpc, overall_cpm,
          overall_conv_rate, overall_roi.
    """
    total_spend = df["spend"].sum()
    total_revenue = df["revenue"].sum()
    total_clicks = df["clicks"].sum()
    total_impressions = df["impressions"].sum()
    total_conversions = df["conversions"].sum()

    return {
        "total_spend": total_spend,
        "total_revenue": total_revenue,
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "total_conversions": total_conversions,
        "overall_ctr": _safe_div(total_clicks, total_impressions) * 100,
        "overall_cpc": _safe_div(total_spend, total_clicks),
        "overall_cpm": _safe_div(total_spend, total_impressions) * 1000,
        "overall_conv_rate": _safe_div(total_conversions, total_clicks) * 100,
        "overall_roi": _safe_div(total_revenue - total_spend, total_spend) * 100,
    }


# ------------------------------------------------------------------
# Campaign-level aggregation (for charts / tables)
# ------------------------------------------------------------------

def aggregate_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Group by `group_col`, sum raw metrics, then recompute derived
    metrics from the sums (correct weighted calculation).
    """
    agg = df.groupby(group_col, as_index=False).agg(
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
        conversions=("conversions", "sum"),
    )
    # Re-derive ratio metrics from aggregated totals
    agg["ctr (%)"] = safe_divide(agg["clicks"], agg["impressions"]) * 100
    agg["cpc"] = safe_divide(agg["spend"], agg["clicks"])
    agg["cpm"] = safe_divide(agg["spend"], agg["impressions"]) * 1000
    agg["conversion rate (%)"] = safe_divide(agg["conversions"], agg["clicks"]) * 100
    agg["roi (%)"] = safe_divide(agg["revenue"] - agg["spend"], agg["spend"]) * 100
    return agg


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Element-wise division; returns 0.0 where denominator is 0."""
    result = numerator / denominator.where(denominator != 0, other=float("nan"))
    return result.fillna(0.0)


def _safe_div(a: float, b: float) -> float:
    """Scalar division returning 0.0 on divide-by-zero."""
    return a / b if b != 0 else 0.0

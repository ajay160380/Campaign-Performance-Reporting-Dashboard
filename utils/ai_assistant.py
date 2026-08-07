"""
ai_assistant.py — AI-powered insights using Groq's free LLM API.

Builds a compact data summary from Pandas aggregations (never sends
raw data) and uses Llama 3.1 via Groq to answer natural-language
questions about campaign performance.
"""

import os
import pandas as pd

# ------------------------------------------------------------------
# Data summary builder (pure Pandas — no LLM involved)
# ------------------------------------------------------------------

def build_data_summary(
    df: pd.DataFrame,
    kpis: dict,
    campaign_agg: pd.DataFrame,
    platform_agg: pd.DataFrame,
) -> str:
    """
    Build a compact plain-text summary of the filtered campaign data.

    This summary is sent as context to the LLM so it can answer
    questions with real numbers — without ever seeing the raw dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered DataFrame with metric columns.
    kpis : dict
        Output of metrics.compute_summary_kpis().
    campaign_agg : pd.DataFrame
        Campaign-level aggregation.
    platform_agg : pd.DataFrame
        Platform-level aggregation.

    Returns
    -------
    str
        Human-readable data summary for the LLM context window.
    """
    lines = []

    # --- Date range ---
    if "date" in df.columns and not df.empty:
        min_date = df["date"].min().strftime("%d %b %Y")
        max_date = df["date"].max().strftime("%d %b %Y")
        lines.append(f"DATE RANGE: {min_date} to {max_date}")
        lines.append(f"Total data points (rows): {len(df)}")
    lines.append("")

    # --- Overall KPIs ---
    lines.append("OVERALL PERFORMANCE:")
    lines.append(f"  Total Spend: Rs. {kpis['total_spend']:,.2f}")
    lines.append(f"  Total Revenue: Rs. {kpis['total_revenue']:,.2f}")
    lines.append(f"  Total Clicks: {kpis['total_clicks']:,.0f}")
    lines.append(f"  Total Impressions: {kpis['total_impressions']:,.0f}")
    lines.append(f"  Total Conversions: {kpis['total_conversions']:,.0f}")
    lines.append(f"  Overall CTR: {kpis['overall_ctr']:.2f}%")
    lines.append(f"  Overall CPC: Rs. {kpis['overall_cpc']:.2f}")
    lines.append(f"  Overall CPM: Rs. {kpis['overall_cpm']:.2f}")
    lines.append(f"  Overall Conversion Rate: {kpis['overall_conv_rate']:.2f}%")
    lines.append(f"  Overall ROI: {kpis['overall_roi']:.2f}%")
    lines.append("")

    # --- Platform-wise breakdown ---
    lines.append("PLATFORM-WISE BREAKDOWN:")
    for _, row in platform_agg.iterrows():
        lines.append(
            f"  {row['platform']}: "
            f"Spend=Rs. {row['spend']:,.0f}, "
            f"Revenue=Rs. {row['revenue']:,.0f}, "
            f"Clicks={row['clicks']:,.0f}, "
            f"CTR={row['ctr (%)']:.2f}%, "
            f"ROI={row['roi (%)']:.1f}%"
        )
    lines.append("")

    # --- Top 5 campaigns by ROI ---
    sorted_by_roi = campaign_agg.sort_values("roi (%)", ascending=False)
    top5 = sorted_by_roi.head(5)
    lines.append("TOP 5 CAMPAIGNS BY ROI:")
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        lines.append(
            f"  {i}. {row['campaign name']}: "
            f"ROI={row['roi (%)']:.1f}%, "
            f"Spend=Rs. {row['spend']:,.0f}, "
            f"Revenue=Rs. {row['revenue']:,.0f}"
        )
    lines.append("")

    # --- Bottom 5 campaigns by ROI ---
    bottom5 = sorted_by_roi.tail(5).sort_values("roi (%)", ascending=True)
    lines.append("BOTTOM 5 CAMPAIGNS BY ROI:")
    for i, (_, row) in enumerate(bottom5.iterrows(), 1):
        lines.append(
            f"  {i}. {row['campaign name']}: "
            f"ROI={row['roi (%)']:.1f}%, "
            f"Spend=Rs. {row['spend']:,.0f}, "
            f"Revenue=Rs. {row['revenue']:,.0f}"
        )
    lines.append("")

    # --- Best and worst single day by revenue ---
    if "date" in df.columns:
        daily = df.groupby("date", as_index=False).agg(
            revenue=("revenue", "sum"),
            spend=("spend", "sum"),
        )
        if not daily.empty:
            best_day = daily.loc[daily["revenue"].idxmax()]
            worst_day = daily.loc[daily["revenue"].idxmin()]
            lines.append("DAILY HIGHLIGHTS:")
            lines.append(
                f"  Best day by revenue: {best_day['date'].strftime('%d %b %Y')} "
                f"(Revenue=Rs. {best_day['revenue']:,.0f}, Spend=Rs. {best_day['spend']:,.0f})"
            )
            lines.append(
                f"  Worst day by revenue: {worst_day['date'].strftime('%d %b %Y')} "
                f"(Revenue=Rs. {worst_day['revenue']:,.0f}, Spend=Rs. {worst_day['spend']:,.0f})"
            )

    return "\n".join(lines)


# ------------------------------------------------------------------
# Groq LLM integration
# ------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a marketing data analyst assistant. Answer the user's question "
    "using ONLY the campaign performance data summary provided below. "
    "Be concise, use specific numbers from the data, and never invent "
    "numbers that aren't in the summary. If the question can't be answered "
    "from the data provided, say so clearly.\n\n"
    "When mentioning currency amounts, use the Rs. symbol as shown in the data."
)

# Models in order of preference (free-tier friendly)
MODELS = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]


def is_api_key_set() -> bool:
    """Check whether the GROQ_API_KEY environment variable is configured."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    return len(key) > 0


def get_ai_response(user_question: str, data_summary: str) -> str:
    """
    Send a question + data summary to Groq and return the LLM's answer.

    Parameters
    ----------
    user_question : str
        The user's natural-language question.
    data_summary : str
        Compact data summary built by build_data_summary().

    Returns
    -------
    str
        The model's response text, or a graceful error message.
    """
    try:
        from groq import Groq

        client = Groq()  # reads GROQ_API_KEY from env automatically

        user_content = (
            f"Here is the campaign performance data summary:\n\n"
            f"{data_summary}\n\n"
            f"Question: {user_question}"
        )

        # Try each model in preference order
        last_error = None
        for model in MODELS:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    max_tokens=400,
                    temperature=0.3,  # low temp for factual, grounded answers
                )
                return response.choices[0].message.content
            except Exception as model_err:
                last_error = model_err
                continue  # try next model

        # All models failed
        return (
            f"⚠️ Could not get a response from any available model. "
            f"Error: {last_error}"
        )

    except ImportError:
        return (
            "⚠️ The `groq` package is not installed. "
            "Run `pip install groq` to enable AI insights."
        )
    except Exception as e:
        return f"⚠️ AI Assistant error: {e}"

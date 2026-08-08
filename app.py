"""
app.py — Campaign Performance & Reporting Dashboard

Main Streamlit application. Orchestrates data loading, validation,
metric computation, visualisation, and report export.

Premium dark-themed UI with glassmorphism, neon accents, and animations.

Run with:  streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd

from utils.data_loader import (
    load_file,
    validate_columns,
    run_quality_checks,
    clean_data,
)
from utils.metrics import add_metric_columns, compute_summary_kpis, aggregate_by
from utils.charts import (
    campaign_spend_vs_revenue,
    daily_trend,
    platform_breakdown,
    top_bottom_roi,
)
from utils.report_generator import generate_excel_report, generate_pdf_report
from utils.ai_assistant import build_data_summary, get_ai_response, is_api_key_set


# ------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Campaign Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Minimal decorative CSS — theme handled by .streamlit/config.toml
# IMPORTANT: No font-family overrides (breaks Material Icons)
# ------------------------------------------------------------------
st.html("""
<style>
    /* Thin scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
    ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.25); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.45); }

    /* KPI cards — glassmorphic glow + hover lift */
    [data-testid="stMetric"] {
        border: 1px solid rgba(0,212,255,0.12) !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25), 0 0 40px rgba(0,212,255,0.04) !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(0,212,255,0.3) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35), 0 0 60px rgba(0,212,255,0.08) !important;
    }
    [data-testid="stMetricLabel"] {
        color: rgba(0,212,255,0.85) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        font-size: 0.78rem !important;
    }

    /* Gradient dividers */
    [data-testid="stDivider"], hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent 0%, rgba(0,212,255,0.2) 20%, rgba(181,55,242,0.2) 50%, rgba(0,212,255,0.2) 80%, transparent 100%) !important;
    }

    /* Fix for multiselect tag overflow and ballooning */
    .stMultiSelect [data-baseweb="select"] > div {
        padding-bottom: 5px !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        margin-top: 5px !important;
        margin-bottom: 0px !important;
        border-radius: 6px !important;
        padding: 0px 2px !important;
    }
    .stMultiSelect [data-baseweb="tag"] span {
        font-size: 0.8rem !important;
        color: #ffffff !important;
    }

    /* Chat Messages Styling */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-radius: 12px;
        padding: 1rem !important;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    /* User Message Bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, rgba(0,212,255,0.05) 0%, rgba(0,212,255,0.01) 100%) !important;
        border-right: 3px solid #00d4ff !important;
        border-left: none !important;
    }
    /* Assistant Message Bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, rgba(181,55,242,0.05) 0%, rgba(181,55,242,0.01) 100%) !important;
        border-left: 3px solid #b537f2 !important;
        border-right: none !important;
    }
    /* Avatar tweaks */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] {
        background-color: transparent !important;
        border-radius: 50% !important;
    }

    /* Premium KPI Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 12px;
        padding: 1.25rem 1rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3), inset 0 0 0 1px rgba(255,255,255,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 3px;
        background: linear-gradient(90deg, #00d4ff, #b537f2);
        opacity: 0.8;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,212,255,0.15), inset 0 0 0 1px rgba(255,255,255,0.1);
        border: 1px solid rgba(0,212,255,0.3);
    }

    [data-testid="stMetricLabel"] > div {
        color: #8b9bb4 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0,212,255,0.2);
    }
    
    /* Small layout fix to remove default margin inside metric */
    [data-testid="stMetric"] > div {
        margin: 0 !important;
    }

    /* Chart containers — subtle glass border */
    [data-testid="stPlotlyChart"] {
        border: 1px solid rgba(0,212,255,0.08) !important;
        border-radius: 14px !important;
        padding: 8px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stPlotlyChart"]:hover {
        border-color: rgba(0,212,255,0.18) !important;
        box-shadow: 0 4px 24px rgba(0,212,255,0.06) !important;
    }

    /* Download buttons — gradient accent */
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(0,212,255,0.12) 0%, rgba(181,55,242,0.12) 100%) !important;
        border: 1px solid rgba(0,212,255,0.2) !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, rgba(0,212,255,0.22) 0%, rgba(181,55,242,0.22) 100%) !important;
        border-color: rgba(0,212,255,0.45) !important;
        box-shadow: 0 4px 20px rgba(0,212,255,0.12) !important;
        transform: translateY(-1px) !important;
    }

    /* Fade-in animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .main .block-container { animation: fadeInUp 0.5s ease-out; }
</style>
""")


# ------------------------------------------------------------------
# Section A — Header & file upload
# ------------------------------------------------------------------
st.title("📊 Campaign Performance & Reporting Dashboard")
st.caption(
    "Upload your campaign data (CSV or XLSX) to analyze performance metrics, "
    "visualize trends, and export professional reports."
)

uploaded_file = st.file_uploader(
    "Upload campaign data",
    type=["csv", "xlsx"],
    help="Expected columns: Campaign Name, Date, Impressions, Clicks, Spend, Revenue, Conversions, Platform",
)

# ------------------------------------------------------------------
# Load data: uploaded file or fall back to bundled sample
# ------------------------------------------------------------------
SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "sample_campaign_data.csv")

if uploaded_file is not None:
    raw_df = load_file(uploaded_file)
    data_source = f"📁 Uploaded: {uploaded_file.name}"
else:
    raw_df = pd.read_csv(SAMPLE_PATH)
    raw_df.columns = raw_df.columns.str.strip().str.lower()
    data_source = "📦 Using bundled sample dataset"

if raw_df is None:
    st.stop()

st.caption(data_source)

# ------------------------------------------------------------------
# Data validation & quality report
# ------------------------------------------------------------------
missing_cols = validate_columns(raw_df)

if missing_cols:
    st.error(
        f"❌ **Missing required columns:** {', '.join(c.title() for c in missing_cols)}. "
        "Please upload a file with all required columns."
    )
    st.stop()

# Run quality checks and show expandable report
quality = run_quality_checks(raw_df)

with st.expander("🔍 Data quality report", expanded=False):
    issues_found = False

    # Missing values
    if quality["missing_values"]:
        issues_found = True
        st.warning(
            f"⚠️ **Missing values detected** in: "
            + ", ".join(f"{col.title()} ({cnt} rows)" for col, cnt in quality["missing_values"].items())
        )

    # Duplicates
    n_dups = len(quality["duplicate_idx"])
    if n_dups > 0:
        issues_found = True
        st.warning(f"⚠️ **{n_dups} duplicate row(s)** found (same Campaign + Date + Platform).")

    # Clicks > Impressions
    n_imp = len(quality["clicks_gt_imp"])
    if n_imp > 0:
        issues_found = True
        st.error(f"🚫 **{n_imp} impossible row(s):** Clicks > Impressions.")

    # Negative values
    n_neg = len(quality["negative_vals"])
    if n_neg > 0:
        issues_found = True
        st.error(f"🚫 **{n_neg} row(s)** with negative values in numeric columns.")

    # Unparseable dates
    n_bad = len(quality["bad_dates"])
    if n_bad > 0:
        issues_found = True
        st.warning(f"⚠️ **{n_bad} row(s)** with unparseable dates (will be excluded).")

    if not issues_found:
        st.success("✅ All data looks clean — no issues detected!")

    # Summary line
    valid_est = quality["total_rows"] - n_dups - n_imp - n_neg - n_bad
    st.markdown(
        f"**Summary:** ✅ ~{valid_est} valid rows  |  "
        f"⚠️ {n_dups + len(quality['missing_values'])} rows with issues  |  "
        f"🗑️ {n_dups} duplicates will be removed"
    )

# ------------------------------------------------------------------
# Clean the data
# ------------------------------------------------------------------
with st.spinner("Cleaning and processing data…"):
    df = clean_data(raw_df, drop_duplicates=True, fill_missing_zero=True)
    df = add_metric_columns(df)

# ------------------------------------------------------------------
# Section B — Sidebar filters
# ------------------------------------------------------------------
st.sidebar.header("🎛️ Filters")

# Date range
if "date" in df.columns:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
else:
    date_range = None

# Campaign multi-select
all_campaigns = sorted(df["campaign name"].unique())
selected_campaigns = st.sidebar.multiselect(
    "Campaigns",
    options=all_campaigns,
    default=all_campaigns,
)

# Platform multi-select
all_platforms = sorted(df["platform"].unique())
selected_platforms = st.sidebar.multiselect(
    "Platforms",
    options=all_platforms,
    default=all_platforms,
)

# Apply filters
filtered = df.copy()

if date_range and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]

if selected_campaigns:
    filtered = filtered[filtered["campaign name"].isin(selected_campaigns)]

if selected_platforms:
    filtered = filtered[filtered["platform"].isin(selected_platforms)]

if filtered.empty:
    st.warning("No data matches the current filters. Adjust the sidebar filters.")
    st.stop()

# ------------------------------------------------------------------
# Section C — Top KPI cards
# ------------------------------------------------------------------
st.divider()
st.subheader("📈 Key performance indicators")
st.caption("Real-time metrics across all filtered campaigns")

kpis = compute_summary_kpis(filtered)

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total Spend", f"₹{kpis['total_spend']:,.0f}")
col2.metric("Total Revenue", f"₹{kpis['total_revenue']:,.0f}")
col3.metric("Total Clicks", f"{kpis['total_clicks']:,.0f}")
col4.metric("Overall CTR", f"{kpis['overall_ctr']:.2f}%")
col5.metric("Overall CPC", f"₹{kpis['overall_cpc']:.2f}")
col6.metric("Overall ROI", f"{kpis['overall_roi']:.1f}%")

# ------------------------------------------------------------------
# Section D — Charts
# ------------------------------------------------------------------
st.divider()
st.subheader("📊 Visual analytics")
st.caption("Interactive charts powered by Plotly — hover for details")

# Aggregate data for charts
campaign_agg = aggregate_by(filtered, "campaign name")
platform_agg = aggregate_by(filtered, "platform")

# Row 1: two charts side by side
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig1 = campaign_spend_vs_revenue(campaign_agg)
    st.plotly_chart(fig1, width="stretch")

with chart_col2:
    fig2 = daily_trend(filtered)
    st.plotly_chart(fig2, width="stretch")

# Row 2: two charts side by side
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    fig3 = platform_breakdown(platform_agg)
    st.plotly_chart(fig3, width="stretch")

with chart_col4:
    fig4 = top_bottom_roi(campaign_agg)
    st.plotly_chart(fig4, width="stretch")

# ------------------------------------------------------------------
# Section E — Data table
# ------------------------------------------------------------------
st.divider()
st.subheader("📋 Filtered dataset")
st.caption("Browse and inspect the underlying campaign data")

# Prepare display columns with nicely formatted headers
display_df = filtered.copy()
if "date" in display_df.columns:
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
display_df.columns = [c.title() for c in display_df.columns]

st.dataframe(
    display_df,
    width="stretch",
    height=400,
)
st.caption(f"Showing {len(filtered):,} rows after filtering.")

# ------------------------------------------------------------------
# Section F — Report downloads
# ------------------------------------------------------------------
st.divider()
st.subheader("📥 Export reports")
st.caption("Download formatted reports for stakeholders")

dl_col1, dl_col2 = st.columns(2)

with dl_col1:
    with st.spinner("Generating Excel report…"):
        excel_buf = generate_excel_report(filtered, kpis, platform_agg)
    st.download_button(
        label="⬇️ Download Excel Report",
        data=excel_buf,
        file_name="campaign_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with dl_col2:
    with st.spinner("Generating PDF report…"):
        # Determine date range for PDF header
        pdf_dates = None
        if "date" in filtered.columns:
            pdf_dates = (filtered["date"].min(), filtered["date"].max())
        pdf_buf = generate_pdf_report(kpis, campaign_agg, date_range=pdf_dates)
    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_buf,
        file_name="campaign_report.pdf",
        mime="application/pdf",
    )

# ------------------------------------------------------------------
# Section G — AI Insights Assistant
# ------------------------------------------------------------------
st.divider()
st.subheader("🤖 AI insights assistant")
# Build data summary (needed for AI responses)
data_summary = build_data_summary(filtered, kpis, campaign_agg, platform_agg)

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Suggested question buttons ---
suggested_qs = [
    "Which campaign performed best?",
    "Which platform should I invest more in?",
    "Summarize this period's performance",
    "What's dragging down ROI?",
]

sq_cols = st.columns(len(suggested_qs))
for i, q in enumerate(suggested_qs):
    if sq_cols[i].button(q, key=f"sq_{i}", width="stretch"):
        st.session_state.pending_question = q

# --- Display chat history ---
for msg in st.session_state.chat_history:
    avatar_emoji = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar_emoji):
        st.markdown(msg["content"])

# --- Chat input (always visible) ---
user_input = st.chat_input("Ask a question about your campaign data...")

# Check if a suggested question was clicked
if "pending_question" in st.session_state:
    user_input = st.session_state.pending_question
    del st.session_state.pending_question

if user_input:
    # Add user message to history and display it
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Get AI response
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Analyzing your campaign data..."):
            response = get_ai_response(user_input, data_summary)
        st.markdown(response)

    # Add assistant response to history
    st.session_state.chat_history.append(
        {"role": "assistant", "content": response}
    )

    # Keep only the last 10 messages to avoid unbounded growth
    if len(st.session_state.chat_history) > 20:  # 10 pairs = 20 messages
        st.session_state.chat_history = st.session_state.chat_history[-20:]

    # Rerun to clear the input and show updated history cleanly
    st.rerun()

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.divider()
st.caption("Campaign Performance & Reporting Dashboard · Built with Streamlit & Plotly")

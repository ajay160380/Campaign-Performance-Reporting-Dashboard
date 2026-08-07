"""
app.py — Campaign Performance & Reporting Dashboard

Main Streamlit application. Orchestrates data loading, validation,
metric computation, visualisation, and report export.

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
)

# ------------------------------------------------------------------
# Custom CSS for a cleaner look
# ------------------------------------------------------------------
st.markdown("""
<style>
    /* KPI card styling — glassmorphism, works on both light & dark themes */
    [data-testid="stMetric"] {
        background: rgba(30, 58, 95, 0.85) !important;
        padding: 18px 22px !important;
        border-radius: 12px;
        border: 1px solid rgba(100, 180, 255, 0.2);
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        backdrop-filter: blur(8px);
    }
    [data-testid="stMetricLabel"] {
        color: #93c5fd !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    /* Section dividers */
    hr {
        border-color: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Section A — Header & file upload
# ------------------------------------------------------------------
st.title("📊 Campaign Performance & Reporting Dashboard")
st.markdown(
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

with st.expander("🔍 Data Quality Report", expanded=False):
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
st.subheader("📈 Key Performance Indicators")

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
st.subheader("📊 Visual Analytics")

# Aggregate data for charts
campaign_agg = aggregate_by(filtered, "campaign name")
platform_agg = aggregate_by(filtered, "platform")

# Row 1: two charts side by side
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig1 = campaign_spend_vs_revenue(campaign_agg)
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    fig2 = daily_trend(filtered)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: two charts side by side
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    fig3 = platform_breakdown(platform_agg)
    st.plotly_chart(fig3, use_container_width=True)

with chart_col4:
    fig4 = top_bottom_roi(campaign_agg)
    st.plotly_chart(fig4, use_container_width=True)

# ------------------------------------------------------------------
# Section E — Data table
# ------------------------------------------------------------------
st.divider()
st.subheader("📋 Filtered Dataset")

# Prepare display columns with nicely formatted headers
display_df = filtered.copy()
if "date" in display_df.columns:
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
display_df.columns = [c.title() for c in display_df.columns]

st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
)
st.caption(f"Showing {len(filtered):,} rows after filtering.")

# ------------------------------------------------------------------
# Section F — Report downloads
# ------------------------------------------------------------------
st.divider()
st.subheader("📥 Export Reports")

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
st.subheader("🤖 Ask AI About This Data")

if not is_api_key_set():
    st.info(
        "💡 **AI Assistant needs a free Groq API key.**\n\n"
        "1. Get one at [console.groq.com](https://console.groq.com)\n"
        "2. Set it before running: `export GROQ_API_KEY=your_key_here`\n"
        "3. Restart the app — the chat will appear here."
    )
else:
    # Build compact data summary from current filtered data
    data_summary = build_data_summary(filtered, kpis, campaign_agg, platform_agg)

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # --- Suggested question buttons ---
    st.caption("Try a suggested question:")
    suggested_qs = [
        "Which campaign performed best?",
        "Which platform should I invest more in?",
        "Summarize this period's performance",
        "What's dragging down ROI?",
    ]

    sq_cols = st.columns(len(suggested_qs))
    for i, q in enumerate(suggested_qs):
        if sq_cols[i].button(q, key=f"sq_{i}", use_container_width=True):
            st.session_state.pending_question = q

    # --- Display chat history ---
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Chat input ---
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
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        with st.chat_message("assistant"):
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

    st.caption("Powered by Llama 3.1 (Groq, free tier)")

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.divider()
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem;'>"
    "Campaign Performance & Reporting Dashboard · Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True,
)

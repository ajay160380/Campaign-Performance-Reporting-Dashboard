# 📊 Campaign Performance & Reporting Dashboard + AI Insights

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://campaign-performance-iq.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75.svg)](https://plotly.com/)
[![Groq LLM](https://img.shields.io/badge/Groq-Llama%203.1%20LLM-orange.svg)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🚀 **Live Interactive Demo:** [https://campaign-performance-iq.streamlit.app](https://campaign-performance-iq.streamlit.app)

An end-to-end, production-grade **Digital Marketing Campaign Performance & Reporting Dashboard** equipped with automated data validation, marketing analytics engine, interactive Plotly visualizations, formatted Excel/PDF reporting, and a grounded **AI Insights Assistant** powered by **Llama 3.1 via Groq**.

Built specifically to demonstrate **Marketing Analytics**, **Data Engineering Quality Control (QA)**, and **Generative AI Integration** for modern digital advertising evaluation.

---

## 🎯 Executive Summary & Key Highlights

| Feature | Capabilities & Engineering Value |
|---|---|
| 📥 **Flexible Data Ingestion** | Ingests `.csv` and `.xlsx` ad performance reports seamlessly. |
| 🛡️ **Automated Data Quality Audit** | Identifies nulls, duplicates, invalid rows (Clicks > Impressions), and negative values before processing. |
| 🧮 **Weighted Marketing Metrics** | Accurate mathematical weighted aggregations for CTR, CPC, CPM, Conv Rate, and ROI (handles divide-by-zero safely). |
| 📈 **Dynamic Plotly Analytics** | Grouped bars, time-series line trends, platform splits, and ranked ROI comparison charts. |
| 🤖 **Grounded AI Assistant** | Instant natural-language Q&A using Groq's Llama 3.1 based on aggregated data context (0% hallucination design). |
| 📄 **Automated Export Engine** | Formatted multi-sheet Excel workbooks (`openpyxl`) and 1-page executive PDF summaries (`fpdf2`). |

---

## 🏗️ System Architecture & Data Pipeline

```
┌──────────────────────────┐
│   User File (CSV/XLSX)   │ (or bundled sample data)
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   1. Ingestion & Pre-proc│  utils/data_loader.py
│  Case-insensitive match │  Clean col names, parse dates
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  2. Data Quality Audit   │  run_quality_checks()
│  Checks: Dupes, Nulls,   │  Flag invalid rows & display
│  Negative, Clicks > Imp  │  "Data Quality Report"
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ 3. Data Cleaning & Engine│  clean_data() & utils/metrics.py
│ Compute CTR, CPC, CPM,   │  Row-level & Weighted Aggregations
│ Conv. Rate, ROI %        │  Safe division (no Inf/NaN)
└────────────┬─────────────┘
             │
  ┌──────────┼───────────────────────┬────────────────────────┐
  │          │                       │                        │
  ▼          ▼                       ▼                        ▼
┌────────┐ ┌───────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  KPI   │ │ Interactive Charts│  │   Export Engine     │  │  AI Insights Engine │
│ Cards  │ │  4 Plotly Visuals │  │  Excel (2-Sheet)    │  │  Llama 3.1 (Groq)   │
│ (6x)   │ │  (Live Filtered)  │  │  PDF Executive Rpt  │  │  Grounded System    │
└────────┘ └───────────────────┘  └─────────────────────┘  └─────────────────────┘
```

---

## 📊 Core Marketing Metrics & Mathematical Definitions

All ratio metrics rely on **weighted mathematical sums**, preventing common aggregation errors like "averaging percentages."

$$CTR (\%) = \left( \frac{\sum \text{Clicks}}{\sum \text{Impressions}} \right) \times 100$$

$$CPC = \frac{\sum \text{Spend}}{\sum \text{Clicks}}$$

$$CPM = \left( \frac{\sum \text{Spend}}{\sum \text{Impressions}} \right) \times 1000$$

$$\text{Conversion Rate} (\%) = \left( \frac{\sum \text{Conversions}}{\sum \text{Clicks}} \right) \times 100$$

$$ROI (\%) = \left( \frac{\sum \text{Revenue} - \sum \text{Spend}}{\sum \text{Spend}} \right) \times 100$$

> 🛡️ **Divide-by-Zero Safety:** All calculations execute via `utils.metrics.safe_divide()`, ensuring clean `0.0` output rather than runtime `Inf` or `NaN` crashes.

---

## 🛡️ Data Quality & QA Pipeline

To demonstrate enterprise-grade **Quality Assurance (QA)**, the system performs a multi-point audit upon file upload:

```
[ Uploaded File ] ──► Data Quality Audit Module
                         ├── 🔍 Missing required schema columns
                         ├── ⚠️ Null/Missing numeric cells
                         ├── 🔄 Duplicate campaign records (Campaign + Date + Platform)
                         ├── 🚫 Impossible metrics (Clicks > Impressions)
                         ├── 🚫 Negative spend/revenue values
                         └── 📅 Unparseable date strings
```

*Results are displayed transparently in an interactive **Data Quality Report** expander panel before cleaned data feeds the analytical engine.*

---

## 🤖 Grounded AI Insights Assistant

The integrated **AI Analyst** allows users to ask natural-language questions about their campaign performance:

- *"Which campaign gave the highest return on ad spend?"*
- *"Why is ROI negative on Twitter?"*
- *"Summarize this month's top performing channels."*

```
┌─────────────────────────────────┐
│ Filtered Dataset Aggregations   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Compact Plain-Text Context      │ (1.8 KB lightweight summary)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Groq Llama 3.1 Instant LLM      │ ◄── User Question + System Prompt
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Fact-Grounded Markdown Answer   │ (0% Hallucination - Strict Context Limit)
└─────────────────────────────────┘
```

### Key AI Features:
- **Zero Hallucination System Prompt:** The LLM is restricted to answering *strictly* using the provided Pandas summary.
- **Privacy & Speed:** Raw user rows are never sent to external APIs; only aggregated statistics are transmitted.
- **Model Fallback Routing:** Automatic failover between `llama-3.1-8b-instant` and `llama-3.3-70b-versatile`.
- **Graceful Fallback:** If `GROQ_API_KEY` is not provided, the core dashboard remains 100% operational with setup instructions.

---

## 💻 Visual Interface Walkthrough

```
+-----------------------------------------------------------------------------------+
|  📊 Campaign Performance & Reporting Dashboard                                     |
|  Upload Campaign File [.csv, .xlsx]  [📦 Sample Data Loaded]                       |
+-----------------------------------------------------------------------------------+
| 🔍 Data Quality Report (Expandable Audit)                                          |
| ✅ ~104 Valid Rows  |  ⚠️ 9 Rows Flagged  |  🗑️ 6 Duplicates Removed                 |
+-----------------------------------------------------------------------------------+
|  📈 KEY PERFORMANCE INDICATORS                                                    |
|  +------------------+ +------------------+ +------------------+ +------------------+ |
|  |   Total Spend    | |  Total Revenue   | |   Total Clicks   | |   Overall ROI    | |
|  |   ₹903,124       | |  ₹1,889,652      | |   320,846        | |   109.2%         | |
|  +------------------+ +------------------+ +------------------+ +------------------+ |
+-----------------------------------------------------------------------------------+
|  📊 VISUAL ANALYTICS (Plotly Interactive)                                         |
|  [Bar: Spend vs Revenue]                      [Line: Daily Spend/Revenue Trend]   |
|  [Grouped Bar: Platform Performance]          [H-Bar: Top & Bottom 5 ROI]         |
+-----------------------------------------------------------------------------------+
|  📋 FILTERED DATASET (Sortable & Searchable Table)                                |
+-----------------------------------------------------------------------------------+
|  📥 EXPORT REPORTS                                                                |
|  [ ⬇️ Download Excel Report (.xlsx) ]         [ ⬇️ Download PDF Report (.pdf) ]     |
+-----------------------------------------------------------------------------------+
|  🤖 ASK AI ABOUT THIS DATA (Groq Llama 3.1)                                       |
|  [ Suggested: "Which campaign performed best?" | "What is dragging down ROI?" ]     |
|  💬 User: Which platform should I invest more in?                                 |
|  🤖 AI: Meta delivered the highest revenue (₹749,601) with a 172.6% ROI...         |
+-----------------------------------------------------------------------------------+
```

---

## 📄 Automated Report Exports

### 📊 Excel Report (`openpyxl`)
- **Sheet 1 ("Summary"):** Executive KPI summary cards + Platform performance matrix. Styled with dark headers, auto-fit column widths, and currency formatting.
- **Sheet 2 ("Campaign Data"):** Complete cleaned dataset with computed row-level CTR, CPC, CPM, Conv Rate, and ROI metrics.

### 📑 PDF Executive Summary (`fpdf2`)
- Single-page formatted executive brief containing period dates, high-level metrics, and side-by-side Top 5 vs Bottom 5 Campaign ROI performance tables.
- Generated purely in-memory (`io.BytesIO`) without temporary disk files.

---

## 🛠️ Tech Stack & Dependencies

| Layer | Component | Description |
|---|---|---|
| **Frontend UI** | Streamlit | Reactive single-page web framework |
| **Data Engine** | Pandas & NumPy | High-performance tabular transformation |
| **Visualization** | Plotly Express & Graph Objects | Dynamic JavaScript-powered interactive charts |
| **LLM Inference** | Groq SDK | Ultra-fast open-source LLM inference (`llama-3.1-8b-instant`) |
| **Excel Export** | OpenPyXL | Spreadsheet styling, multi-sheet generation |
| **PDF Export** | FPDF2 | Portable document format report generation |

---

## 🚀 Quickstart & Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/ajay160380/Campaign-Performance-Reporting-Dashboard.git
cd Campaign-Performance-Reporting-Dashboard

# 2. Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Set Groq API Key (Optional, for AI Assistant)
export GROQ_API_KEY="your_groq_api_key_here"

# 5. Launch local application
streamlit run app.py
```

The application will launch at `http://localhost:8501`.

---

## 📁 Repository Structure

```
Campaign-Performance-Reporting-Dashboard/
├── app.py                         # Main Streamlit orchestration entrypoint
├── utils/
│   ├── __init__.py
│   ├── data_loader.py             # Data ingestion, schema validation & cleaning
│   ├── metrics.py                 # Mathematical formula engine & weighted aggregations
│   ├── charts.py                  # Plotly visualization builders
│   ├── report_generator.py        # In-memory Excel & PDF generator
│   └── ai_assistant.py            # Groq Llama 3.1 LLM integration & prompt engineering
├── sample_data/
│   └── sample_campaign_data.csv   # Realistic demo dataset (~110 rows with QA test cases)
├── .gitignore                     # Git tracking exclusions
├── requirements.txt               # Locked dependencies
└── README.md                      # Project documentation
```

---

## 🤝 Interview & Presentation Context

When presenting this project in a **Marketing Analyst / Data Analyst** interview:
1. **Business Problem:** Marketers waste hours manually calculating campaign metrics across fragmented ad platforms (Meta, Google, LinkedIn) and stitching Excel files.
2. **Solution:** Automated ingest-to-insight dashboard with zero backend overhead.
3. **Engineering Rigor:** Built-in QA pipeline catches dirty data before reporting; weighted averages ensure mathematical truth; in-memory stream generation enables instant downloads.
4. **AI Innovation:** Added a grounded LLM assistant that translates raw metrics into executive-ready narrative insights instantly.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p center="align">
  Crafted with ❤️ by <a href="https://github.com/ajay160380">Ajay Vishwakarma</a>
</p>

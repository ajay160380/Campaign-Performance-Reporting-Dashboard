<div align="center">
  
# 🚀 Campaign Performance & Reporting Dashboard

**An End-to-End Digital Marketing Analytics Engine with Automated QA & AI Insights**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://campaign-performance-iq.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458.svg?style=for-the-badge&logo=pandas)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive_Charts-3F4F75.svg?style=for-the-badge&logo=plotly)](https://plotly.com/)
[![Groq LLM](https://img.shields.io/badge/Groq-Llama_3.1-F55036.svg?style=for-the-badge)](https://groq.com/)

[**Live Interactive Demo**](https://campaign-performance-iq.streamlit.app) 🌟

</div>

---

## ✨ Why this Dashboard?

This is not just another data visualizer. This is a **production-grade marketing analytics engine**. It comes equipped with:
*   🛡️ **Automated Data Quality Audit** 
*   🧠 **Smart Auto Column Mapping** (perfect for Kaggle datasets!)
*   📈 **Mathematical Weighted Aggregations**
*   🤖 **Grounded AI Insights Assistant** (0% Hallucination)
*   📑 **Excel & PDF Export Engines**

---

## 🗺️ System Architecture & Pipeline

```mermaid
graph TD
    classDef user fill:#6c5ce7,stroke:#fff,stroke-width:2px,color:#fff;
    classDef process fill:#0984e3,stroke:#fff,stroke-width:2px,color:#fff;
    classDef engine fill:#00b894,stroke:#fff,stroke-width:2px,color:#fff;
    classDef output fill:#fdcb6e,stroke:#fff,stroke-width:2px,color:#2d3436;

    A[User CSV/XLSX Upload]:::user --> B(Smart Column Mapping & Parser):::process
    B --> C{Data Quality Audit}:::engine
    C -->|Drops Nulls/Dupes| D[Data Cleaning Engine]:::process
    C -->|Flags Bad Rows| E[QA Report UI]:::output
    D --> F[Metrics Calculation]:::engine
    F --> G[KPI Cards]:::output
    F --> H[Plotly Charts]:::output
    F --> I[PDF/Excel Exports]:::output
    F --> J((Llama 3.1 AI Engine)):::engine
    J --> K[Natural Language Insights]:::output
```

---

## 🎨 Visual Interface Walkthrough

```mermaid
mindmap
  root((Dashboard Interface))
    Upload Zone
      Drag & Drop CSV/XLSX
      Smart Kaggle Detection
    Data Quality Report
      Duplicate Check
      Missing Values
      Negative Values
    Key Performance Indicators
      Total Spend
      Total Revenue
      ROI %
      CTR & CPC
    Visual Analytics
      Spend vs Revenue Bar
      Daily Trend Line
      Platform Share Donut
      Top & Bottom ROI
    AI Assistant
      Chat Interface
      Llama 3.1 Inference
```

---

## 🧠 Smart Auto Column Mapping (NEW!)

Tired of manually renaming columns when you download data from Kaggle or Meta Ads? The dashboard now includes a **Fuzzy Match Engine** that automatically detects and renames over **50+ column variations**.

| Dataset Format | Dashboard Automatically Detects As |
| :--- | :--- |
| `Acquisition_Cost`, `Amount_Spent`, `Budget` | ➡️ **Spend** |
| `Channels_Used`, `ad_network` | ➡️ **Platform** |
| `Total_Revenue`, `Conversion_Value` | ➡️ **Revenue** |
| `Leads`, `Installs`, `Registrations` | ➡️ **Conversions** |
| `Campaign_Type`, `ad_group` | ➡️ **Campaign Name** |

---

## 🧮 Core Marketing Metrics

All ratio metrics rely on **weighted mathematical sums**, preventing common aggregation errors like "averaging percentages."

$$CTR (\%) = \left( \frac{\sum \text{Clicks}}{\sum \text{Impressions}} \right) \times 100$$
$$CPC = \frac{\sum \text{Spend}}{\sum \text{Clicks}}$$
$$CPM = \left( \frac{\sum \text{Spend}}{\sum \text{Impressions}} \right) \times 1000$$
$$ROI (\%) = \left( \frac{\sum \text{Revenue} - \sum \text{Spend}}{\sum \text{Spend}} \right) \times 100$$

> 🛡️ **Divide-by-Zero Safety:** All calculations execute via `utils.metrics.safe_divide()`, ensuring clean `0.0` output rather than runtime crashes.

---

## 🤖 Grounded AI Insights Assistant

The integrated **AI Analyst** allows users to ask natural-language questions about their campaign performance:

- *"Which campaign gave the highest return on ad spend?"*
- *"Why is ROI negative on Twitter?"*
- *"Summarize this month's top performing channels."*

**Zero Hallucination System:** Raw user rows are never sent to external APIs; only aggregated statistics (1.8KB compact context) are transmitted to Groq's `llama-3.1-8b-instant`.

---

## 💻 Tech Stack & Dependencies

<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-f55036?style=for-the-badge" />
</p>

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
> The application will launch at `http://localhost:8501`.

---

<div align="center">
  <p>Crafted with ❤️ by <a href="https://github.com/ajay160380">Ajay Vishwakarma</a></p>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License: MIT"/>
</div>

# Campaign Performance & Reporting Dashboard

A Streamlit-based interactive dashboard for analyzing digital ad campaign performance. Upload your campaign data (CSV/XLSX), explore key marketing metrics, visualize trends, and export professional reports — all from a single browser tab.

---

## ✨ Features

- **Drag-and-drop upload** — supports CSV and XLSX files
- **Automatic data validation** — flags missing values, duplicates, impossible rows, and bad dates
- **5 marketing metrics** computed automatically: CTR, CPC, CPM, Conversion Rate, ROI
- **6 KPI cards** — at-a-glance summary of overall performance
- **4 interactive Plotly charts:**
  - Campaign-wise Spend vs Revenue (grouped bar)
  - Daily Spend & Revenue trend (line chart)
  - Platform-wise breakdown (grouped bar)
  - Top & Bottom campaigns by ROI (horizontal bar)
- **Live sidebar filters** — filter by date range, campaign, and platform
- **Sortable data table** — view the full filtered dataset with computed metrics
- **Excel export** — multi-sheet workbook with styled Summary + Campaign Data sheets
- **PDF export** — one-page report with KPI summary and top/bottom campaign tables
- **Bundled sample data** — dashboard loads a demo dataset by default so it's never empty
- **AI Insights Assistant** — ask natural-language questions about your data, powered by Llama 3.1 via Groq (free tier)

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Streamlit | Web UI framework |
| Pandas | Data processing & metric calculations |
| Plotly | Interactive charts |
| openpyxl | Excel read/write with formatting |
| fpdf2 | PDF report generation |
| Groq SDK | Free LLM inference (Llama 3.1) |

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/your-username/campaign-dashboard.git
cd campaign-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set up AI Insights — get a free key at console.groq.com
export GROQ_API_KEY=your_groq_api_key_here

# 4. Launch the dashboard
streamlit run app.py
```

The app opens at `http://localhost:8501`. Upload your own CSV/XLSX or explore the bundled sample data.

---

## 📁 Project Structure

```
campaign-dashboard/
├── app.py                         # Main Streamlit app (entry point)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py             # Upload handling, schema validation, cleaning
│   ├── metrics.py                 # CTR, CPC, CPM, Conv. Rate, ROI calculations
│   ├── charts.py                  # All Plotly chart-building functions
│   ├── report_generator.py        # Excel + PDF export logic
│   └── ai_assistant.py            # Groq LLM integration + data summariser
├── sample_data/
│   └── sample_campaign_data.csv   # Realistic synthetic dataset (~110 rows)
├── requirements.txt
└── README.md
```

---

## 📊 Expected Input Format

Your uploaded file should contain these columns (case-insensitive):

| Column | Type | Required |
|---|---|---|
| Campaign Name | string | ✅ |
| Date | date | ✅ |
| Impressions | int | ✅ |
| Clicks | int | ✅ |
| Spend | float | ✅ |
| Revenue | float | ✅ |
| Conversions | int | ✅ |
| Platform | string | ✅ |

---

## 🤖 AI Insights Assistant (Optional)

The dashboard includes a chat-based AI assistant that answers natural-language questions about your campaign data (e.g., "Which campaign had the best ROI?", "Why is CTR low on Meta?").

**How it works:**
- Uses **Llama 3.1** (open-source LLM) via [Groq](https://groq.com)'s free inference API
- A compact data summary is built from Pandas aggregations and sent as context — the raw dataset is never sent to the API
- Answers reference actual numbers from your data, not hallucinated figures

**Setup:**
1. Get a free API key at [console.groq.com](https://console.groq.com)
2. Set the environment variable before running the app:
   ```bash
   export GROQ_API_KEY=your_key_here
   ```
3. The AI chat section appears at the bottom of the dashboard

> If `GROQ_API_KEY` is not set, the rest of the dashboard works fully — the AI section simply shows a setup message.

---

## ☁️ Deployment

This app can be deployed for free on **Streamlit Community Cloud**:

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and select `app.py` as the entry point
4. Click **Deploy** — that's it!

---

## 📸 Screenshots

*Coming soon — replace this section with actual screenshots after running the app.*

---

## 📄 License

MIT

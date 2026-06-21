# SEO Ranking Changes Analyzer

> **Analyze SEO ranking shifts fast — powered by Google Search Console or Sistrix data, no API costs, 100% private.**

[![MIT License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b.svg)](https://streamlit.io)

---

## What it does

The **SEO Ranking Changes Analyzer** is a bilingual (🇩🇪/🇬🇧) Streamlit dashboard that turns raw CSV exports into actionable insights about keyword ranking changes. It supports two data sources — Google Search Console and Sistrix — switchable in the sidebar at any time.

Everything is processed **locally in RAM only**. No data is ever stored, sent to an external API, or persisted to disk. Upload your file, analyze, done.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Dual analysis mode** | Switch between **Google Search Console** (real clicks & impressions) and **Sistrix** (search volume + CTR model) in one click |
| **Executive Summary** | Auto-generated narrative summary of wins, losses & quick wins — ready to paste into your client report |
| **Topic Clustering** | NLP-based keyword clustering by head terms — no API, no cost, milliseconds |
| **Search Intent Detection** | Classifies keywords as `KNOW`, `DO (Transactional)`, `regional:CITY`, `regional:COUNTRY` for DE & EN data |
| **Low Hanging Fruits** | Surfaces position 11–15 keywords with high existing impressions/SV that need just a small push to reach page 1 |
| **Monetary Loss (Sistrix)** | Estimates the AdWords-equivalent value of traffic lost based on CPC data |
| **Directory Analysis (Sistrix)** | Groups losses by URL path to identify underperforming site sections |
| **Ranking Drop Categories** | Hard segments: Out of Top 3, Out of Top 10, Page 2 drops, Complete losses (fell out of Top 100) |
| **Bilingual UI** | Full German & English interface — switch at any time without reloading |
| **100% Private** | No database, no third-party APIs — all data lives in transient server RAM only |

---

## 📊 Analysis Tabs

### Google Search Console Mode
1. **Topic Clusters** — Keyword loss grouped by head terms, click-loss based
2. **Ranking Drops** — Top 3 / Top 10 / Page 2 / Complete losses with click impact
3. **Click Losses** — All losers sorted by absolute click loss
4. **Low Hanging Fruits** — Position 11–15 keywords sorted by real impressions
5. **Winners** — Keywords with click gains
6. **All Data** — Full export with filters for cluster, change type, intent, keyword search

### Sistrix Mode
1. **Directory Analysis** — URL-path grouped traffic & value losses
2. **Topic Clusters** — Keyword loss grouped by head terms, SV-based
3. **Ranking Drops** — Top 3 / Top 10 / Page 2 / Complete losses with SV impact
4. **Low Hanging Fruits** — Position 11–15 keywords sorted by search volume
5. **Winners** — New Top-10 keywords
6. **All Data** — Full export with filters for cluster, change type, directory, intent, keyword search

---

## 📁 Supported Input Formats

### Google Search Console
Export a **date comparison** from GSC → Performance → Queries → Compare dates → Export as CSV.
The file must have exactly **9 columns**: Keyword, Clicks (new/old), Impressions (new/old), CTR (new/old), Position (new/old).

### Sistrix
Export a **keyword comparison** from Sistrix → Keywords → Compare → Export as CSV.
Required columns: `Keyword`, `Position#1`, `Position#2`, `Search Volume`, `URL`.
Optional columns used when present: `CPC`, `Competition`.

---

## 🚀 Quick Start

### Option 1 — Streamlit Community Cloud (recommended)
The app is hosted publicly at: **[your-app-url.streamlit.app](https://your-app-url.streamlit.app)**  
No installation needed. Just open the link and upload your CSV.

### Option 2 — Run locally with `uv` (fastest)

[`uv`](https://docs.astral.sh/uv/) handles the virtual environment and dependencies automatically:

```bash
# Clone the repository
git clone https://github.com/wingerter/seo-ranking-changes-analyzer.git
cd seo-ranking-changes-analyzer

# Run the app (installs dependencies on first run)
uv run --python 3.12 --with-requirements requirements.txt streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Option 3 — Run locally with pip

```bash
# Clone the repository
git clone https://github.com/wingerter/seo-ranking-changes-analyzer.git
cd seo-ranking-changes-analyzer

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Start the app
streamlit run app.py
```

---

## 🛠️ Tech Stack

| Package | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | UI framework & server |
| [Pandas](https://pandas.pydata.org) | Data processing |
| [Plotly](https://plotly.com/python/) | Interactive charts |

No external APIs are called at runtime.

---

## 🔒 Privacy

- Uploaded CSV files are processed **exclusively in transient RAM**.
- Data is **never stored** on disk or in a database.
- Data is **never sent** to any third-party service.
- All data is erased the moment your session ends (tab close / page reload).
- Hosting on Streamlit Community Cloud (Snowflake) processes connection logs and IP addresses. See the [Snowflake Privacy Policy](https://www.snowflake.com/legal/privacy-policy/) for details.

---

## 📄 License

MIT License © 2026 Benjamin "SEOux Indianer" Wingerter  
[seouxindianer.de](https://seouxindianer.de)

Co-developed with [Antigravity](https://antigravity.dev) 🤖 — AI Coding Assistant by Google DeepMind

See [LICENSE](LICENSE) for the full license text.

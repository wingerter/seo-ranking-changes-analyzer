# SEO Ranking Changes Analyzer

> **Stop wasting hours in Excel. Instantly analyze ranking drops, group keywords by topic, and identify high-value search intent shifts from Google Search Console or Sistrix exports — 100% private and free.**

[![MIT License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b.svg)](https://streamlit.io)

---

## Why use this Analyzer?

Analyzing weekly or monthly ranking shifts across thousands of keywords is tedious. Standard tools give you flat lists, and spreadsheets require manual filtering, VLOOKUPs, and pivot tables.

This tool does the heavy lifting for you:
*   **Save hours of reporting time:** It auto-generates a ready-to-paste executive summary (in German or English) highlighting key wins, critical losses, and quick wins for your client reports.
*   **Zero API costs & no limits:** Analyze massive exports in milliseconds without paying for external credits or API tokens.
*   **100% Data Privacy:** Your client data is safe. All processing happens locally in transient server RAM. Files are never stored on disk, saved to a database, or sent to third-party APIs.

---

## ✨ Features for SEOs

| Feature | What it does for you |
|---|---|
| **Dual Data Source Support** | Switch seamlessly between **Google Search Console** (real clicks & impressions) and **Sistrix** (search volume & CPC) depending on what data you want to analyze. |
| **Ready-to-Paste Summaries** | Instantly writes a narrative executive summary of SEO performance (wins, page-1 drops, and low-hanging fruits) ready to paste directly into emails or slide decks. |
| **Automatic Topic Clustering** | Automatically groups thousands of keywords into logical thematic clusters (by main search term) so you can see which product categories or topics lost the most visibility. |
| **Search Intent Detection** | Classifies search terms as `KNOW` (informational), `DO` (transactional), `regional:CITY`, or `regional:COUNTRY` (supports DE, EN, ES, FR, IT, NL, CS, RU, PT, HR, LA, FI, SV, and Klingon!) to analyze if you lost transactional or informational traffic. |
| **Low-Hanging Fruits Finder** | Instantly surfaces keywords ranking on page 2 (positions 11–15) with high impressions or search volume. These are your fastest opportunities for quick traffic gains. |
| **AdWords Traffic Value (Sistrix)** | Translates organic traffic losses into concrete monetary value (using CPC data), showing you exactly how much it would cost to buy back that lost traffic with Google Ads. |
| **Directory Performance (Sistrix)** | Groups ranking drops by URL directory (e.g. `/blog/` vs. `/shop/`) to identify which sections of your site took the biggest hits. |
| **Categorized Ranking Drops** | Segments drops into clear action groups: Fell out of Top 3, Fell out of Top 10, Fell to Page 2, and Complete Losses (fell out of the Top 100). |
| **Bilingual Interface** | Switch between a full German and English interface instantly at the click of a button in the sidebar. |

---

## 📁 How to export your CSV files

### Google Search Console Mode
1. Go to **Google Search Console** -> **Performance** -> **Search Results**.
2. Set your filters, click on the date filter, select **Compare**, and choose your comparison periods (e.g., *Compare last 28 days to previous period*).
3. Go to the **Queries** tab and click **Export** -> **Download CSV**.
4. Upload the exported CSV to the analyzer.

### Sistrix Mode
1. In **Sistrix**, go to **Keywords** -> **Compare**.
2. Select the two dates you want to compare (e.g., current week vs. previous week or month).
3. Click the **Export** button at the top right of the comparison table to download the CSV.
4. Upload the exported CSV to the analyzer.

---

## 🚀 Quick Start

### Web App (No installation needed)
The analyzer is hosted and ready to use online:
👉 **[your-app-url.streamlit.app](https://your-app-url.streamlit.app)** *(Note: Replace with your actual deployed URL)*

---

### Local Installation (For in-house SEO teams)

If you prefer to run the analyzer locally on your computer:

#### Option A: Running with `uv` (Recommended - fastest)
[`uv`](https://docs.astral.sh/uv/) is a modern Python package manager that runs the tool without manual virtual environment setup:

```bash
# Clone the repository
git clone https://github.com/wingerter/seo-ranking-changes-analyzer.git
cd seo-ranking-changes-analyzer

# Run the app (automatically installs Python and dependencies)
uv run --python 3.12 --with-requirements requirements.txt streamlit run app.py
```

#### Option B: Running with standard `pip`
```bash
# Clone the repository
git clone https://github.com/wingerter/seo-ranking-changes-analyzer.git
cd seo-ranking-changes-analyzer

# Setup a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies and start
pip install -r requirements.txt
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔒 Privacy & Security

*   Uploaded CSV files are processed **only in transient RAM**.
*   No data is **ever stored** on disk or in a database.
*   No data is **ever transmitted** to external APIs or third parties.
*   Everything is erased the moment you close the browser tab or reload the page.

---

## 📄 License

MIT License © 2026 Benjamin "SEOux Indianer" Wingerter  
[seouxindianer.de](https://seouxindianer.de)

Co-developed with [Antigravity](https://antigravity.dev) 🤖 — AI Coding Assistant by Google DeepMind

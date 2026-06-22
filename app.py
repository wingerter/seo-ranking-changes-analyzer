import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from urllib.parse import urlparse
import math
import io
import re
import base64
import time
import subprocess
from collections import Counter
import streamlit.components.v1 as components

st.set_page_config(
    page_title="SEO Ranking Changes Analyzer",
    page_icon="assets/logo-head-clear.png",
    layout="wide"
)

# --- Load Brand Styles ---
try:
    with open("brand_style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Could not load brand_style.css: {e}")

# =============================================================================
# SIDEBAR — Logo, Language, Mode
# =============================================================================
# --- Compact sidebar header CSS ---
st.markdown("""
<style>
/* Shrink sidebar top padding */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem !important;
}
/* Remove all margin/padding from sidebar image block */
section[data-testid="stSidebar"] [data-testid="stImage"] {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stImage"] img {
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
}
/* Compress radio widget in sidebar */
section[data-testid="stSidebar"] .stRadio {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}
section[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
    display: none !important;
}
section[data-testid="stSidebar"] .stRadio > div {
    gap: 0.5rem !important;
    margin-top: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:first-child > div {
    gap: 0 !important;
}
/* Compact horizontal rule in sidebar */
section[data-testid="stSidebar"] hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar: compact language toggle only (logo moves to bottom)
lang_choice = st.sidebar.radio("Language / Sprache", options=["DE", "EN"], index=0, horizontal=True)
lang = "DE" if "DE" in lang_choice else "EN"

st.sidebar.markdown("---")


mode_options_de = ["Google Search Console (Queries.csv)", "Sistrix (Keyword-Vergleichs-Export)"]
mode_options_en = ["Google Search Console (Queries.csv)", "Sistrix (Keyword Comparison Export)"]
mode_options = mode_options_de if lang == "DE" else mode_options_en

mode_label = "Datenquelle / Analysemodus" if lang == "DE" else "Data Source / Analysis Mode"
mode = st.sidebar.selectbox(mode_label, options=mode_options, index=0)
mode_key = "gsc" if "Google" in mode else "sistrix"

# =============================================================================
# TRANSLATIONS
# =============================================================================
translations = {
    "EN": {
        # Common
        "title_gsc": "GSC Ranking Changes Analyzer",
        "title_sistrix": "Sistrix Ranking Changes Analyzer",
        "subtitle_gsc": "Upload your Google Search Console comparison export (Queries.csv) and analyze real click losses and quick wins.",
        "subtitle_sistrix": "Upload your Sistrix comparison export and analyze keyword losses, traffic impact, and quick wins.",
        "sidebar_data": "1. Data & Settings",
        "upload_label_gsc": "GSC Queries.csv Upload",
        "upload_label_sistrix": "Sistrix CSV Upload",
        "dates_header": "Date Range for Charts",
        "date_old": "Date for Position#1 (Old)",
        "date_new": "Date for Position#2 (New)",
        "cluster_settings": "Clustering Settings",
        "brand_input": "Brand Keywords (comma-separated)",
        "brand_help": "Keywords containing these terms will be grouped into a 'Brand' cluster.",
        "cluster_count": "Number of Topic Clusters",
        "data_lang": "Data Language (for Search Intent)",
        "data_lang_options": ["Deutsch", "English", "Español", "Français", "Italiano", "Other"],
        "data_lang_help": "Select the language of your keyword data to correctly determine search intent (KNOW, DO, regional). For ES/FR/IT/Other, intent analysis is skipped.",
        "btn_analyze": "Analyze",
        "err_format_gsc": "Could not recognize the GSC format. Please upload a standard Queries.csv from a GSC date comparison (exactly 9 columns expected).",
        "err_format_sistrix": "Could not recognize the Sistrix format. Please check the file (columns 'Keyword' and 'Position#1' must exist exactly like this).",
        "err_read": "Error reading CSV: ",
        "err_req": "The following required columns are missing: ",
        "succ_load": "File successfully loaded and analyzed!",
        "info_upload_gsc": "Please upload a GSC Queries.csv file, select a mode, and click 'Analyze'.",
        "info_upload_sistrix": "Please upload a Sistrix CSV file, select a mode, and click 'Analyze'.",
        "intent_not_analyzed_msg": "Search intent analysis was skipped because the data language is set to 'Other' or a non-supported language.",
        "intent_not_analyzed": "Not Analyzed",
        # KPIs — GSC
        "kpi_header_gsc": "Overview: Real GSC Clicks",
        "kpi_lost_total": "📉 Lost Clicks (Total)",
        "kpi_gained_total": "📈 Gained Clicks (Total)",
        "kpi_net_change": "🖱️ Net Click Change",
        "kpi_top3_drops": "🚨 Top 3 Drops",
        "kpi_top10_drops": "⚠️ Top 10 Drops",
        "kpi_lhf": "🎯 Low Hanging Fruits",
        "kpi_lhf_link": "See tab below",
        "kpi_lhf_help_gsc": "Actual impressions generated in the current timeframe by keywords ranking on positions 11-15. High impressions here mean great potential if pushed to page 1.",
        "kpi_cluster_title": "Topic Cluster Performance",
        "kpi_best_cluster": "Best Cluster",
        "kpi_worst_cluster": "Worst Cluster",
        "kpi_top3_title": "Top 3 Drops (Worst 5)",
        "clicks": "Clicks",
        # KPIs — Sistrix
        "kpi_header_sistrix": "Overview: Business Impact",
        "kpi_lost_total_sv": "📉 Lost Search Volume (Total)",
        "kpi_gained_total_sv": "📈 Gained Search Volume (Total)",
        "kpi_net_change_sv": "📊 Net Search Volume Change",
        "kpi_avg_pos_change": "🗺️ Avg. Position Change",
        "kpi_value_total": "💶 Monetary Loss (AdWords Equivalent)",
        "kpi_total_loss": "❌ Complete Losses",
        "kpi_total_loss_help": "Keywords that fell out of the Top 100 completely.",
        "kpi_lhf_help_sistrix": "Actual search volume of keywords ranking on positions 11-15. High search volume here means great potential if pushed to page 1.",
        "dir_chart_title_sv": "Which directories lost the most search volume?",
        "dir_chart_label_t_sv": "Lost Search Volume",
        "cl_chart_title_sv": "Which topic clusters lost the most search volume?",
        "cl_chart_label_t_sv": "Lost Search Volume",
        # Intent
        "kpi_intent_title": "Search Intent Distribution",
        # Tabs
        "tab_summary": "Summary",
        "tab_dir": "Directory Analysis",
        "tab_cluster": "Topic Clusters",
        "tab_drops": "Ranking Drops",
        "tab_losses": "Click Losses (Detail)",
        "tab_lhf": "Low Hanging Fruits",
        "tab_winners": "Winners",
        "tab_all": "All Data",
        # Directory tab (Sistrix)
        "dir_sub": "Lost Traffic & Value by Directory",
        "dir_empty": "No data available.",
        "dir_chart_title": "Which directories cost us the most traffic?",
        "dir_chart_label_d": "Directory",
        "dir_chart_label_t": "Lost Traffic (Estimated)",
        # Cluster tab
        "cl_sub": "Traffic Loss by Topic Clusters",
        "cl_desc": "Automatic grouping of losing keywords by their most frequent head terms.",
        "cl_chart_title": "Which topic clusters lost the most traffic?",
        "cl_chart_label_c": "Topic Cluster",
        "cl_chart_label_t": "Lost Traffic (Estimated)",
        "cl_chart_label_v": "Lost Clicks",
        "cl_detail": "#### Detail Data per Cluster",
        "cl_select": "Select one or multiple clusters for detail insights:",
        "cl_sum_sv": "Total affected search volume in selected clusters:",
        "cl_sum_clicks": "Total lost clicks in selected clusters:",
        "cl_empty": "No drops available for clustering.",
        "cl_other": "Other",
        # Ranking Drops tab
        "rd_sub": "Ranking Drops Overview",
        "rd_filter": "Filter by keyword (optional):",
        "rd_t3_title": "#### 1. Top 3 Drops (Ranking losses starting in Top 3)",
        "rd_t3_empty": "No Top 3 Drops found.",
        "rd_t3_desc": "These are your most critical keyword losses. Positions 1-3 generate the majority of click-through rates and organic traffic. Losing these rankings results in an immediate and noticeable traffic drop. Affected: **{count}** keywords, representing **{vol}** search volume, an estimated traffic loss of **{traffic}** clicks, and an AdWords value equivalent loss of **{val}**.",
        "rd_t10_title": "#### 2. Top 10 Drops (Ranking losses starting in Top 10)",
        "rd_t10_empty": "No Top 10 Drops found.",
        "rd_t10_desc": "Keywords that lost visibility on the first search engine results page (positions 4-10). While still on Page 1, any drop here significantly reduces click share. Affected: **{count}** keywords, representing **{vol}** search volume, an estimated traffic loss of **{traffic}** clicks, and an AdWords value equivalent loss of **{val}**.",
        "rd_p2_title": "#### 3. Page 2 Drops (Ranking losses starting on Page 2)",
        "rd_p2_empty": "No Page 2 Drops found.",
        "rd_p2_desc": "Keywords that were ranking on Page 2 (positions 11-20) and lost ground. These keywords were close to entering the high-traffic Page 1 threshold, but have now drifted further away. Affected: **{count}** keywords, representing **{vol}** search volume, an estimated traffic loss of **{traffic}** clicks, and an AdWords value equivalent loss of **{val}**.",
        "rd_100_title": "#### 4. Complete Losses (Fell out of Top 100)",
        "rd_100_empty": "No keywords fell out of Top 100.",
        "rd_100_desc": "Keywords that fell out of the Top 100 rankings entirely, meaning a complete loss of organic search visibility for these terms. Affected: **{count}** keywords, representing **{vol}** search volume, an estimated traffic loss of **{traffic}** clicks, and an AdWords value equivalent loss of **{val}**.",
        "rd_sum_vol": "Affected Search Volume:",
        "rd_sum_traf": "(Estimated Traffic Loss:",
        "rd_sum_clicks": "Total lost clicks:",
        "rd_t3_desc_gsc": "These are your most critical keyword losses. Positions 1-3 generate the majority of click-through rates and organic traffic. Losing these rankings results in an immediate and noticeable traffic drop. Affected: **{count}** keywords, representing a loss of **{clicks}** clicks and **{impressions}** impressions.",
        "rd_t10_desc_gsc": "Keywords that lost visibility on the first search engine results page (positions 4-10). While still on Page 1, any drop here significantly reduces click share. Affected: **{count}** keywords, representing a loss of **{clicks}** clicks and **{impressions}** impressions.",
        "rd_p2_desc_gsc": "Keywords that were ranking on Page 2 (positions 11-20) and lost ground. These keywords were close to entering the high-traffic Page 1 threshold, but have now drifted further away. Affected: **{count}** keywords, representing a loss of **{clicks}** clicks and **{impressions}** impressions.",
        "rd_100_desc_gsc": "Keywords that fell out of the Top 100 rankings entirely, meaning a complete loss of organic search visibility for these terms. Affected: **{count}** keywords, representing a loss of **{clicks}** clicks and **{impressions}** impressions.",
        # Click Losses tab (GSC only)
        "cd_sub": "Biggest absolute click losses (All)",
        # LHF tab
        "lhf_sub": "Low Hanging Fruits (Position 11 - 15)",
        "lhf_desc_gsc": "These keywords currently rank on the top half of page 2 (Position 11-15) and already generate the real impressions shown above. With tiny on-page optimizations, you can push these over the threshold to page 1 and turn those impressions into massive traffic.",
        "lhf_desc_sistrix": "These keywords currently rank on the top half of page 2 (Position 11-15) and already generate the real search volume shown above. With tiny on-page optimizations, you can push these over the threshold to page 1 and turn those impressions into massive traffic.",
        "lhf_empty": "No keywords found in range 11-15.",
        # Winners tab
        "win_sub_gsc": "Winners (Click Gains)",
        "win_sub_sistrix": "Winners (New in Top 10)",
        "win_empty": "No winners found.",
        "win_chart_title": "Winner Keywords by Search Volume",
        "win_chart_label_pos": "New Position",
        "win_chart_label_gain": "Gained Clicks",
        # All Data tab
        "ad_sub": "All Data (Complete Export)",
        "ad_filter_cluster": "Filter by Cluster",
        "ad_filter_change": "Filter by Change Type",
        "ad_filter_dir": "Filter by Directory",
        "ad_filter_kw": "Search Keyword",
        "ad_filter_intent": "Filter by Search Intent",
        "lhf_pot_help": "Calculated optimization potential (0-10) based on ranking position and volume/impressions",
        "lhf_diff_label": "Difficulty",
        "lhf_diff_help": "Estimated ranking difficulty based on search volume or impressions",
        "dir_chart_title_tree": "Lost Search Volume Distribution by Directory (Treemap)",
        # Footer / Legal
        "footer": "MIT License &copy; 2026 Benjamin &quot;SEOux Indianer&quot; Wingerter | Created in Munich &amp; Bangkok with ❤️ | <a href='https://seouxindianer.de' target='_blank' style='color: #2ea3f2; text-decoration: underline;'>seouxindianer.de</a> | Co-developed with Antigravity 🤖",
        "legal_header": "Legal & Privacy Policy",
        "imprint_body": """### Imprint

**Information pursuant to § 5 DDG:**
Benjamin Wingerter
SEOux Indianer
Email: mytools@mindblowmedia.com
Website: seouxindianer.de

**Disclaimer:**
The contents of this app were created with the utmost care. However, we cannot guarantee the correctness, completeness, or topicality of the content.""",
        "privacy_body": """### Privacy Policy

**1. General Information**
This privacy policy informs you about the nature, scope, and purpose of the processing of personal data within this web application.

**2. Data Controller**
Benjamin Wingerter
Email: mytools@mindblowmedia.com

**3. Hosting (Streamlit Cloud)**
This app is hosted on Streamlit Community Cloud, a service provided by Snowflake Inc. (106 East Babcock Street, Suite 3A, Bozeman, MT 59715, USA). To serve the app securely, Snowflake processes connection logs and IP addresses of visitors. This processing is based on our legitimate interest in a secure and efficient operation of the application (Art. 6 (1) (f) GDPR). For more details, please refer to the Snowflake Privacy Policy.

**4. Processing of Uploaded Files (CSV)**
When you upload an export file:
- The file is processed **exclusively in the transient memory (RAM)** of the server to generate dashboards.
- The uploaded data is **never stored permanently on any storage drive or database**.
- As soon as you terminate your session (e.g., by closing the browser tab, reloading the page, or replacing the file), all processed data is completely erased.
- The legal basis for this processing is Art. 6 (1) (f) GDPR (our legitimate interest in providing you with this analysis tool).

**5. Your Rights**
You have the right to access, rectify, erase, or restrict the processing of your personal data, as well as the right to data portability and objection.""",
    },
    "DE": {
        # Common
        "title_gsc": "GSC Ranking Changes Analyzer",
        "title_sistrix": "Sistrix Ranking Changes Analyzer",
        "subtitle_gsc": "Lade deinen Google Search Console Vergleichsexport (Queries.csv) hoch und analysiere reale Klick-Verluste und Quick-Wins.",
        "subtitle_sistrix": "Lade deinen Sistrix-Vergleichsexport hoch und analysiere Keyword-Verluste, Traffic-Impact und Quick Wins.",
        "sidebar_data": "1. Daten & Einstellungen",
        "upload_label_gsc": "GSC Queries.csv Upload",
        "upload_label_sistrix": "Sistrix CSV Upload",
        "dates_header": "Datumsangaben für die Diagramme",
        "date_old": "Datum für Position#1 (Alt)",
        "date_new": "Datum für Position#2 (Neu)",
        "cluster_settings": "Clustering Einstellungen",
        "brand_input": "Brand-Keywords (kommagetrennt)",
        "brand_help": "Keywords, die diese Begriffe enthalten, werden in einem eigenen 'Brand' Cluster gesammelt.",
        "cluster_count": "Anzahl der Themen-Cluster",
        "data_lang": "Daten-Sprache (für Suchintent)",
        "data_lang_options": ["Deutsch", "English", "Español", "Français", "Italiano", "Andere"],
        "data_lang_help": "Wähle die Sprache deiner Keyword-Daten, um den Suchintent korrekt zu bestimmen. Für ES/FR/IT/Andere wird die Analyse übersprungen.",
        "btn_analyze": "Analysieren",
        "err_format_gsc": "Das GSC-Format konnte nicht erkannt werden. Bitte lade eine standardmäßige Queries.csv aus einem GSC-Zeitraumvergleich hoch (genau 9 Spalten erwartet).",
        "err_format_sistrix": "Konnte das Sistrix-Format nicht erkennen. Bitte prüfe die Datei (Spaltennamen 'Keyword' und 'Position#1' müssen exakt so existieren).",
        "err_read": "Fehler beim Lesen der CSV: ",
        "err_req": "Die folgenden benötigten Spalten fehlen: ",
        "succ_load": "Datei erfolgreich geladen und analysiert!",
        "info_upload_gsc": "Bitte lade eine GSC Queries.csv Datei hoch, wähle den Modus und klicke auf 'Analysieren'.",
        "info_upload_sistrix": "Bitte lade eine Sistrix CSV-Datei hoch, wähle den Modus und klicke auf 'Analysieren'.",
        "intent_not_analyzed_msg": "Die Suchintent-Analyse wurde übersprungen, da die Daten-Sprache nicht unterstützt wird.",
        "intent_not_analyzed": "Nicht analysiert",
        # KPIs — GSC
        "kpi_header_gsc": "Überblick: Echte GSC-Klicks",
        "kpi_lost_total": "📉 Verlorene Klicks (Gesamt)",
        "kpi_gained_total": "📈 Gewonnene Klicks (Gesamt)",
        "kpi_net_change": "🖱️ Netto Klick-Veränderung",
        "kpi_top3_drops": "🚨 Top 3 Abstürze",
        "kpi_top10_drops": "⚠️ Top 10 Abstürze",
        "kpi_lhf": "🎯 Low Hanging Fruits",
        "kpi_lhf_link": "Siehe Reiter unten",
        "kpi_lhf_help_gsc": "Echte Impressionen, die diese Keywords im aktuellen Zeitraum auf den Positionen 11-15 gesammelt haben. Viele Impressionen hier bedeuten hohes Potenzial für Seite 1.",
        "kpi_cluster_title": "Themen-Cluster Performance",
        "kpi_best_cluster": "Bestes Cluster",
        "kpi_worst_cluster": "Schlechtestes Cluster",
        "kpi_top3_title": "Top 3 Abstürze (Die 5 schlimmsten)",
        "clicks": "Klicks",
        # KPIs — Sistrix
        "kpi_header_sistrix": "Überblick: Business Impact",
        "kpi_lost_total_sv": "📉 Verlorenes Suchvolumen (Gesamt)",
        "kpi_gained_total_sv": "📈 Gewonnenes Suchvolumen (Gesamt)",
        "kpi_net_change_sv": "📊 Netto Suchvolumen-Veränderung",
        "kpi_avg_pos_change": "🗺️ Ø Positions-Veränderung",
        "kpi_value_total": "💶 Monetärer Verlust (AdWords-Äquivalent)",
        "kpi_total_loss": "❌ Komplette Verluste",
        "kpi_total_loss_help": "Keywords, die komplett aus den Top 100 gefallen sind.",
        "kpi_lhf_help_sistrix": "Das komplette Suchvolumen, das diese Keywords im aktuellen Zeitraum auf den Positionen 11-15 sammeln.",
        "dir_chart_title_sv": "Welche Verzeichnisse haben am meisten Suchvolumen verloren?",
        "dir_chart_label_t_sv": "Verlorenes Suchvolumen",
        "cl_chart_title_sv": "Welche Themen-Cluster haben am meisten Suchvolumen verloren?",
        "cl_chart_label_t_sv": "Verlorenes Suchvolumen",
        # Intent
        "kpi_intent_title": "Suchintents-Verteilung",
        # Tabs
        "tab_summary": "Zusammenfassung",
        "tab_dir": "Verzeichnis-Analyse",
        "tab_cluster": "Themen-Cluster",
        "tab_drops": "Ranking Drops",
        "tab_losses": "Klick-Verluste (Detail)",
        "tab_lhf": "Low Hanging Fruits",
        "tab_winners": "Gewinner",
        "tab_all": "Alle Daten",
        # Directory tab (Sistrix)
        "dir_sub": "Verlorener Traffic & Wert nach Verzeichnis",
        "dir_empty": "Keine Daten vorhanden.",
        "dir_chart_title": "Welche Verzeichnisse kosten uns am meisten Traffic?",
        "dir_chart_label_d": "Verzeichnis",
        "dir_chart_label_t": "Verlorene Klicks (Schätzung)",
        # Cluster tab
        "cl_sub": "Traffic-Verlust nach Themen-Clustern",
        "cl_desc": "Automatische Bündelung der Verlierer-Keywords nach den häufigsten Begriffen (Head-Terms).",
        "cl_chart_title": "Welche Themen-Cluster haben am meisten Traffic verloren?",
        "cl_chart_label_c": "Themen-Cluster",
        "cl_chart_label_t": "Verlorener Traffic (Schätzung)",
        "cl_chart_label_v": "Verlorene Klicks",
        "cl_detail": "#### Detail-Daten pro Cluster",
        "cl_select": "Wähle ein oder mehrere Cluster für Detail-Insights:",
        "cl_sum_sv": "Gesamtes betroffenes Suchvolumen in den gewählten Clustern:",
        "cl_sum_clicks": "Gesamte verlorene Klicks in den gewählten Clustern:",
        "cl_empty": "Keine Abstürze zum Clustern vorhanden.",
        "cl_other": "Sonstiges",
        # Ranking Drops tab
        "rd_sub": "Alle Abstürze in der Übersicht",
        "rd_filter": "Nach Keyword filtern (optional):",
        "rd_t3_title": "#### 1. Top 3 Abstürze (Ranking-Verluste aus den Top 3)",
        "rd_t3_empty": "Keine Top 3 Drops gefunden.",
        "rd_t3_desc": "Dies sind Ihre kritischsten Keyword-Verluste. Die Positionen 1–3 generieren den Großteil der Klicks und des organischen Traffics. Ein Verlust hier führt zu einem spürbaren Einbruch. Betroffen: **{count}** Keywords mit einem Suchvolumen von **{vol}**, einem geschätzten Traffic-Verlust von **{traffic}** Klicks und einem AdWords-Wertverlust von **{val}**.",
        "rd_t10_title": "#### 2. Top 10 Abstürze (Ranking-Verluste aus den Top 10)",
        "rd_t10_empty": "Keine Top 10 Drops gefunden.",
        "rd_t10_desc": "Keywords, die Sichtbarkeit auf der ersten Suchergebnisseite (Positionen 4–10) verloren haben. Obwohl sie noch sichtbar sind, sinkt die Klickrate mit jeder tieferen Position drastisch. Betroffen: **{count}** Keywords mit einem Suchvolumen von **{vol}**, einem geschätzten Traffic-Verlust von **{traffic}** Klicks und einem AdWords-Wertverlust von **{val}**.",
        "rd_p2_title": "#### 3. Seite 2 Abstürze (Ranking-Verluste von Seite 2)",
        "rd_p2_empty": "Keine Seite 2 Drops gefunden.",
        "rd_p2_desc": "Keywords, die auf Seite 2 (Positionen 11–20) gerankt haben und an Boden verloren haben. Diese Keywords waren kurz vor der einkommensstarken ersten Seite, sind nun aber weiter nach hinten gerutscht. Betroffen: **{count}** Keywords mit einem Suchvolumen von **{vol}**, einem geschätzten Traffic-Verlust von **{traffic}** Klicks und einem AdWords-Wertverlust von **{val}**.",
        "rd_100_title": "#### 4. Komplette Verluste (Aus Top 100 gefallen)",
        "rd_100_empty": "Keine Keywords aus den Top 100 gefallen.",
        "rd_100_desc": "Keywords, die vollständig aus den Top 100 Rankings herausgefallen sind, was einen kompletten Verlust der organischen Sichtbarkeit für diese Begriffe bedeutet. Betroffen: **{count}** Keywords mit einem Suchvolumen von **{vol}**, einem geschätzten Traffic-Verlust von **{traffic}** Klicks und einem AdWords-Wertverlust von **{val}**.",
        "rd_sum_vol": "Angezeigtes Suchvolumen:",
        "rd_sum_traf": "(Geschätzter Traffic-Verlust:",
        "rd_sum_clicks": "Verlorene Klicks gesamt:",
        "rd_t3_desc_gsc": "Dies sind Ihre kritischsten Keyword-Verluste. Die Positionen 1–3 generieren den Großteil der Klicks und des organischen Traffics. Ein Verlust hier führt zu einem spürbaren Einbruch. Betroffen: **{count}** Keywords mit einem Verlust von **{clicks}** Klicks und **{impressions}** Impressionen.",
        "rd_t10_desc_gsc": "Keywords, die Sichtbarkeit auf der ersten Suchergebnisseite (Positionen 4–10) verloren haben. Obwohl sie noch sichtbar sind, sinkt die Klickrate mit jeder tieferen Position drastisch. Betroffen: **{count}** Keywords mit einem Verlust von **{clicks}** Klicks und **{impressions}** Impressionen.",
        "rd_p2_desc_gsc": "Keywords, die auf Seite 2 (Positionen 11–20) gerankt haben und an Boden verloren haben. Diese Keywords waren kurz vor der einkommensstarken ersten Seite, sind nun aber weiter nach hinten gerutscht. Betroffen: **{count}** Keywords mit einem Verlust von **{clicks}** Klicks und **{impressions}** Impressionen.",
        "rd_100_desc_gsc": "Keywords, die vollständig aus den Top 100 Rankings herausgefallen sind, was einen kompletten Verlust der organischen Sichtbarkeit für diese Begriffe bedeutet. Betroffen: **{count}** Keywords mit einem Verlust von **{clicks}** Klicks und **{impressions}** Impressionen.",
        # Click Losses tab (GSC only)
        "cd_sub": "Größte absolute Klick-Verluste (Alle)",
        # LHF tab
        "lhf_sub": "Low Hanging Fruits (Position 11 - 15)",
        "lhf_desc_gsc": "Diese sogenannten **Schwellen-Keywords** ranken aktuell auf der oberen Hälfte von Seite 2 (Position 11-15) und generieren dort bereits die gezeigten, echten Impressionen. Mit geringen On-Page-Optimierungen können Sie diese Keywords über die Schwelle auf Seite 1 schieben.",
        "lhf_desc_sistrix": "Diese sogenannten **Schwellen-Keywords** ranken aktuell auf der oberen Hälfte von Seite 2 (Position 11-15) und generieren dort bereits das angezeigte Suchvolumen. Mit winzigen inhaltlichen Optimierungen kannst du diese Keywords über die Schwelle auf Seite 1 schieben.",
        "lhf_empty": "Keine Keywords im Bereich 11-15 gefunden.",
        # Winners tab
        "win_sub_gsc": "Gewinner (Klick-Zuwachs)",
        "win_sub_sistrix": "Gewinner (Neu in den Top 10)",
        "win_empty": "Keine Gewinner gefunden.",
        "win_chart_title": "Gewinner-Keywords nach Suchvolumen",
        "win_chart_label_pos": "Neue Position",
        "win_chart_label_gain": "Gewonnene Klicks",
        # All Data tab
        "ad_sub": "Alle Daten (Gesamter Export)",
        "ad_filter_cluster": "Nach Cluster filtern",
        "ad_filter_change": "Nach Change-Typ filtern",
        "ad_filter_dir": "Nach Verzeichnis filtern",
        "ad_filter_kw": "Keyword suchen",
        "ad_filter_intent": "Nach Suchintent filtern",
        "lhf_pot_help": "Berechnetes Optimierungspotenzial (0-10) basierend auf Ranking-Position und Suchvolumen/Impressionen",
        "lhf_diff_label": "Schwierigkeit",
        "lhf_diff_help": "Geschätzte Ranking-Schwierigkeit basierend auf Suchvolumen oder Impressionen",
        "dir_chart_title_tree": "Verteilung des verlorenen Suchvolumens nach Verzeichnis (Treemap)",
        # Footer / Legal
        "footer": "MIT License &copy; 2026 Benjamin &quot;SEOux Indianer&quot; Wingerter | Erstellt in München &amp; Bangkok mit ❤️ | <a href='https://seouxindianer.de' target='_blank' style='color: #2ea3f2; text-decoration: underline;'>seouxindianer.de</a> | Mitentwickelt von Antigravity 🤖",
        "legal_header": "Rechtliches / Impressum",
        "imprint_body": """### Impressum

**Angaben gemäß § 5 DDG:**
Benjamin Wingerter
SEOux Indianer
E-Mail: mytools@mindblowmedia.com
Website: seouxindianer.de

**Haftungsausschluss (Disclaimer):**
Die Inhalte dieser App wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen.""",
        "privacy_body": """### Datenschutzerklärung

**1. Allgemeine Hinweise**
Diese Datenschutzerklärung klärt Sie über die Art, den Umfang und Zweck der Verarbeitung von personenbezogenen Daten innerhalb dieser Webanwendung (App) auf.

**2. Verantwortlicher**
Benjamin Wingerter
E-Mail: mytools@mindblowmedia.com

**3. Hosting (Streamlit Cloud)**
Diese App wird auf der Streamlit Community Cloud gehostet, einem Dienst von Snowflake Inc. (106 East Babcock Street, Suite 3A, Bozeman, MT 59715, USA). Zur Bereitstellung und zum sicheren Betrieb der App verarbeitet Snowflake Verbindungsdaten und IP-Adressen der Besucher.

**4. Verarbeitung von hochgeladenen Dateien (CSV)**
Wenn Sie eine Exportdatei hochladen:
- Die Datei wird **ausschließlich im Arbeitsspeicher (RAM)** des Servers verarbeitet.
- Die hochgeladenen Daten werden **zu keinem Zeitpunkt dauerhaft auf Datenträgern oder in einer Datenbank gespeichert**.
- Sobald Sie Ihre Sitzung beenden, werden alle Daten vollständig gelöscht.
- Die Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO.

**5. Ihre Rechte**
Sie haben das Recht auf Auskunft, Berichtigung, Löschung und Einschränkung der Verarbeitung Ihrer personenbezogenen Daten sowie das Recht auf Datenübertragbarkeit und Widerspruch.""",
    }
}

t = translations[lang]

# =============================================================================
# HELPER: Number Formatting
# =============================================================================
def format_num(val, decimal_places=0):
    if pd.isnull(val):
        return ""
    formatted_str = f"{val:,.{decimal_places}f}"
    if lang == "DE":
        placeholder = "|||"
        temp = formatted_str.replace(",", placeholder)
        temp = temp.replace(".", ",")
        formatted_str = temp.replace(placeholder, ".")
    return formatted_str

# =============================================================================
# HELPER: Plotly Styling
# =============================================================================
def style_plotly_fig(fig):
    title_text = ""
    if fig.layout.title is not None:
        if isinstance(fig.layout.title, str):
            title_text = fig.layout.title
        elif hasattr(fig.layout.title, 'text') and fig.layout.title.text is not None:
            title_text = fig.layout.title.text
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font_family="Raleway",
        font_color="#232323",
        margin=dict(l=60, r=40, t=45, b=45),
        title=dict(text=title_text, font=dict(family="Raleway", color="#232323", size=15)),
        xaxis=dict(
            title=dict(text=""),
            gridcolor="#dfdfdf", zerolinecolor="#dfdfdf", linecolor="#dfdfdf",
            tickfont=dict(family="Open Sans", color="#535353")
        ),
        yaxis=dict(
            title=dict(text=""),
            gridcolor="#dfdfdf", zerolinecolor="#dfdfdf", linecolor="#dfdfdf",
            tickfont=dict(family="Open Sans", color="#535353")
        )
    )
    return fig

# =============================================================================
# HELPER: CTR Estimation (Sistrix)
# =============================================================================
def estimate_ctr(pos):
    ctr_map = {1: 0.30, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05,
               6: 0.04, 7: 0.03, 8: 0.02, 9: 0.015, 10: 0.01}
    return ctr_map.get(int(pos) if not pd.isnull(pos) else 0, 0.0)

# =============================================================================
# HELPER: Search Intent Classifier
# =============================================================================
def get_intent(kw, lang_choice):
    kw_lower = str(kw).lower()
    intents = []
    # Supported languages only: Deutsch (index 0) and English (index 1)
    supported_options = t["data_lang_options"]

    if lang_choice == supported_options[0]:  # Deutsch
        if re.search(r'((.*\s|^)w(er|em|en|essen|ie|ann|o|elche|as|obei|omit|oran|orin|ohin|obei|eshalb|arum|ieso|orauf|orum|ovor|ogegen|odurch|oher|eswegen|oraus)\s.*)|((.*\s|^)anleitung|anweisung|beschreibung|bestimmung|bin ich|definition|erklärung|forum|frage|gesetz|guide|(.*\s|^)hilfe|how to|muss|kann(\s.*|$)|(.*\s|^)darf|methode|quora|rechtlich|regeln|tipps|tutorial|brauche|vor was|walkthrough|diy|yahoo clever|gute frage)(\s.*|$)', kw_lower):
            intents.append("KNOW")
        if re.search(r'.*aktionen.*|.*am billigsten.*|.*anfordern.*|.*angebot.*|.*anmeldung.*|.*auf lager.*|.*bestellbar.*|.*bestellen.*|.*billig.*|.*coupon.*|.*discount.*|.*download.*|.*free.*|.*garantie.*|.*gebraucht.*|.*gewinnen.*|.*gewinnspiel.*|.*gratis.*|.*günstig.*|.*günstige.*|.*günstiges.*|.*günstigste.*|.*gutschein.*|.*gutscheincode.*|.*im angebot.*|.*in stock.*|.*kaufen.*|.*käuflich.*|.*kontakt.*|.*kostenlos.*|.*leihen.*|.*mieten.*|.*mit kreditkarte.*|.*mit paypal.*|.*ohne schufa.*|.*online kaufen.*|.*onlineshop.*|.*pdf.*|.*preis.*|.*preisausschreiben.*|.*preisvergleich.*|.*preiswert.*|.*rabatt.*|.*shop.*|.*special.*|.*template.*|.*überbestände.*|.*umsonst.*|.*verkauf.*|.*vorlage.*|.*vorrätig.*|.*werbung.*|.*wo kauf.*|.*zu verkaufen.*', kw_lower):
            intents.append("DO (Transactional)")
        if re.search(r'.*berlin.*|.*münchen.*|.*hamburg.*|.*köln.*|.*frankfurt.*|.*stuttgart.*|.*düsseldorf.*|.*dortmund.*|.*essen.*|.*leipzig.*|.*bremen.*|.*dresden.*|.*hannover.*|.*nürnberg.*|.*duisburg.*|.*bochum.*|.*wuppertal.*|.*bielefeld.*|.*bonn.*|.*münster.*|.*karlsruhe.*|.*mannheim.*|.*augsburg.*|.*wiesbaden.*|.*gelsenkirchen.*|.*mönchengladbach.*|.*braunschweig.*|.*chemnitz.*|.*kiel.*|.*aachen.*|.*halle.*|.*magdeburg.*|.*freiburg.*|.*krefeld.*|.*lübeck.*|.*oberhausen.*|.*erfurt.*|.*mainz.*|.*rostock.*|.*kassel.*|.*saarbrücken.*|.*hagen.*|.*hamm.*|.*mülheim.*|.*osnabrück.*|.*ludwigshafen.*|.*leverkusen.*|.*oldenburg.*|.*solingen.*|.*heidelberg.*|.*potsdam.*|.*darmstadt.*|.*regensburg.*|.*ingolstadt.*|.*würzburg.*|.*wolfsburg.*|.*ulm.*|.*göttingen.*|.*bremerhaven.*|.*recklinghausen.*|.*koblenz.*|.*moers.*|.*bergisch gladbach.*|.*reutlingen.*|.*erlangen.*|.*siegen.*', kw_lower):
            intents.append("regional:CITY")
        if re.search(r'.*belgien.*|.*bulgarien.*|.*dänemark.*|.*deutschland.*|.*estland.*|.*finnland.*|.*frankreich.*|.*griechenland.*|.*irland.*|.*italien.*|.*kroatien.*|.*lettland.*|.*litauen.*|.*luxemburg.*|.*malta.*|.*niederlande.*|.*österreich.*|.*polen.*|.*portugal.*|.*rumänien.*', kw_lower):
            intents.append("regional:COUNTRY")

    elif lang_choice == supported_options[1]:  # English
        if re.search(r'\b(who|what|where|when|why|how|which|whose|whom|guide|tutorial|tips|definition|explain|explanation|how\s+to|faq|forum|info|information|meaning|instruction|manual|example|examples|case\s+study|learn|training|course|help|support|diy|walkthrough)\b', kw_lower):
            intents.append("KNOW")
        if re.search(r'\b(buy|order|cheap|coupon|discount|download|free|shop|price|pricing|sale|purchase|store|promo|deal|deals|rent|hire|cheapest|voucher|booking|book)\b', kw_lower):
            intents.append("DO (Transactional)")
        if re.search(r'\b(near\s+me|local|nearby|map|directions|address|hours|opening\s+hours|london|new\s+york|nyc|los\s+angeles|chicago|houston|phoenix|philadelphia|dallas|san\s+diego|austin|san\s+francisco|seattle|denver|boston|miami|atlanta|las\s+vegas|toronto|vancouver|sydney|melbourne|brisbane|perth|auckland)\b', kw_lower):
            intents.append("regional:CITY")
        if re.search(r'\b(us|usa|united\s+states|uk|united\s+kingdom|england|great\s+britain|canada|australia|nz|new\s+zealand|ireland|scotland|wales|south\s+africa)\b', kw_lower):
            intents.append("regional:COUNTRY")
    else:
        # ES, FR, IT, Other — analysis skipped
        return "not analyzed"

    return ", ".join(intents) if intents else "undefined"

# =============================================================================
# HELPER: Low Hanging Fruits (LHF) Calculations
# =============================================================================
def calculate_lhf_gsc(row):
    pos = row['Position_New']
    imp = row['Impressions_New']
    if lang == "DE":
        diff = "🔴 Schwer" if imp > 10000 else ("🟡 Mittel" if imp > 2000 else "🟢 Leicht")
    else:
        diff = "🔴 High" if imp > 10000 else ("🟡 Medium" if imp > 2000 else "🟢 Low")
    
    factor = 16 - pos
    log_part = math.log10(imp + 10)
    score = min((factor * log_part) / 2.0, 10.0)
    return pd.Series([score, diff])

def calculate_lhf_sistrix(row):
    pos = row['Position#2']
    sv = row['Search Volume']
    if lang == "DE":
        diff = "🔴 Schwer" if sv > 5000 else ("🟡 Mittel" if sv > 1000 else "🟢 Leicht")
    else:
        diff = "🔴 High" if sv > 5000 else ("🟡 Medium" if sv > 1000 else "🟢 Low")
    
    factor = 16 - pos
    log_part = math.log10(sv + 10)
    score = min((factor * log_part) / 2.0, 10.0)
    return pd.Series([score, diff])

# =============================================================================
# HELPER: Styled Dataframe Renderer
# =============================================================================
def display_styled_dataframe(df_to_show, sort_col, ascending=False):
    pct_sign = " %" if lang == "DE" else "%"
    loss_cols = [c for c in ['Traffic Loss', 'Lost Value €', 'Clicks Loss'] if c in df_to_show.columns]
    gain_cols = [c for c in ['Traffic Gain', 'Clicks Gain'] if c in df_to_show.columns]

    styler = df_to_show.sort_values(sort_col, ascending=ascending).style
    format_dict = {}

    if loss_cols:
        styler = styler.map(lambda x: 'color: #993333; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=loss_cols)
        for c in loss_cols:
            if c == 'Lost Value €':
                if lang == "EN":
                    format_dict[c] = lambda x: f"▼ -€{format_num(x, 2)}" if pd.notnull(x) and x > 0 else ("€0.00" if pd.notnull(x) else "")
                else:
                    format_dict[c] = lambda x: f"▼ -{format_num(x, 2)} €" if pd.notnull(x) and x > 0 else ("0,00 €" if pd.notnull(x) else "")
            else:
                format_dict[c] = lambda x: f"▼ -{format_num(x)}" if pd.notnull(x) and x > 0 else ("0" if pd.notnull(x) else "")

    if gain_cols:
        styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=gain_cols)
        for c in gain_cols:
            format_dict[c] = lambda x: f"▲ +{format_num(x)}" if pd.notnull(x) and x > 0 else ("0" if pd.notnull(x) else "")

    for c in ['Search Volume', 'Traffic#1', 'Traffic#2', 'Impressions_New', 'Impressions_Old', 'Clicks_New', 'Clicks_Old']:
        if c in df_to_show.columns:
            format_dict[c] = lambda x: format_num(x) if pd.notnull(x) else ""

    for c in ['Position#1', 'Position#2']:
        if c in df_to_show.columns:
            format_dict[c] = lambda x: "-" if pd.notnull(x) and x == 101 else (format_num(x, 2) if pd.notnull(x) else "")

    for c in ['Position_Old', 'Position_New']:
        if c in df_to_show.columns:
            format_dict[c] = lambda x: "-" if pd.notnull(x) and x == 101 else (format_num(x, 2) if pd.notnull(x) else "")

    if 'Position Change' in df_to_show.columns:
        styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else ('color: #993333; font-weight: bold;' if pd.notnull(x) and x < 0 else ''), subset=['Position Change'])
        format_dict['Position Change'] = lambda x: f"▲ +{format_num(abs(x), 2)}" if pd.notnull(x) and x > 0 else (f"▼ -{format_num(abs(x), 2)}" if pd.notnull(x) and x < 0 else format_num(0.0, 2))

    for c in ['Traffic Change', 'Clicks Change']:
        if c in df_to_show.columns:
            styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else ('color: #993333; font-weight: bold;' if pd.notnull(x) and x < 0 else ''), subset=[c])
            format_dict[c] = lambda x: f"▲ +{format_num(x)}" if pd.notnull(x) and x > 0 else (f"▼ -{format_num(abs(x))}" if pd.notnull(x) and x < 0 else "0")

    styler = styler.format(format_dict)
    st.dataframe(styler, use_container_width=True)

# =============================================================================
# APP TITLE
# =============================================================================
st.title(t[f"title_{mode_key}"])
st.markdown(t[f"subtitle_{mode_key}"])

# =============================================================================
# LOADING OVERLAY
# =============================================================================
loading_placeholder = st.empty()

if st.session_state.get("show_custom_loader"):
    logo_base64 = ""
    try:
        with open("assets/logo-head-clear.png", "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception:
        pass

    custom_loader_html = f"""<div class="custom-loader-overlay">
    <div class="loader-logo-container">
        <img class="loader-logo" src="data:image/png;base64,{logo_base64}" />
        <svg class="loader-svg" viewBox="0 0 100 100">
            <circle class="loader-bg-circle" cx="50" cy="50" r="45" />
            <circle class="loader-fill-circle" cx="50" cy="50" r="45" />
        </svg>
    </div>
</div>
<style>
.custom-loader-overlay {{
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    background-color: rgba(35, 35, 35, 0.15);
    backdrop-filter: blur(2px);
    z-index: 999999;
    display: flex; justify-content: center; align-items: center;
    pointer-events: all;
}}
.loader-logo-container {{
    position: relative; width: 140px; height: 140px;
    display: flex; justify-content: center; align-items: center;
    background: #ffffff; border-radius: 50%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}}
.loader-logo {{ width: 80px; height: 80px; object-fit: contain; z-index: 1; }}
.loader-svg {{ position: absolute; top: 0; left: 0; width: 140px; height: 140px; z-index: 2; }}
.loader-bg-circle {{ fill: none; stroke: rgba(153, 51, 51, 0.05); stroke-width: 6; }}
.loader-fill-circle {{
    fill: none; stroke: rgba(153, 51, 51, 0.7); stroke-width: 6;
    stroke-linecap: round; stroke-dasharray: 283; stroke-dashoffset: 283;
    animation: fill-progress 1.5s ease-in-out infinite alternate, rotate-spinner 2s linear infinite;
    transform-origin: center;
}}
@keyframes fill-progress {{ 0% {{ stroke-dashoffset: 283; }} 100% {{ stroke-dashoffset: 28; }} }}
@keyframes rotate-spinner {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
</style>"""
    loading_placeholder.markdown(custom_loader_html, unsafe_allow_html=True)
    time.sleep(1.2)

# =============================================================================
# SIDEBAR — Settings
# =============================================================================
st.sidebar.header(t["sidebar_data"])

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False
if 'show_success_alert' not in st.session_state:
    st.session_state['show_success_alert'] = False

def trigger_analysis():
    st.session_state['analyzed'] = True
    st.session_state['show_custom_loader'] = True
    st.session_state['show_success_alert'] = True

def on_file_upload():
    st.session_state['analyzed'] = False
    st.session_state['show_success_alert'] = False

upload_label = t[f"upload_label_{mode_key}"]
uploaded_file = st.sidebar.file_uploader(upload_label, type=["csv"], on_change=on_file_upload)

# Date inputs — Sistrix mode only
if mode_key == "sistrix":
    st.sidebar.subheader(t["dates_header"])
    date_old = st.sidebar.date_input(t["date_old"], value=pd.to_datetime('today') - pd.DateOffset(months=1))
    date_new = st.sidebar.date_input(t["date_new"], value=pd.to_datetime('today'))

st.sidebar.subheader(t["cluster_settings"])
brand_input = st.sidebar.text_input(t["brand_input"], value="", help=t["brand_help"])
num_clusters = st.sidebar.slider(t["cluster_count"], min_value=5, max_value=50, value=20, step=5)
data_lang_choice = st.sidebar.selectbox(t["data_lang"], options=t["data_lang_options"], index=0, help=t["data_lang_help"])

if uploaded_file is not None:
    st.sidebar.button(t["btn_analyze"], type="primary", on_click=trigger_analysis)

# Sidebar — Logo (full width) + Legal
st.sidebar.markdown("---")
st.sidebar.image("assets/logo-horizontal.png", use_container_width=True)
with st.sidebar.expander(t["legal_header"]):
    st.markdown(t["imprint_body"])
    st.markdown("---")
    st.markdown(t["privacy_body"])

# =============================================================================
# MAIN ANALYSIS BLOCK
# =============================================================================
pct_sign = " %" if lang == "DE" else "%"

if uploaded_file is not None and st.session_state['analyzed']:

    # =========================================================================
    # PARSING — branched by mode
    # =========================================================================
    try:
        content = uploaded_file.getvalue()
        df = None

        if mode_key == "gsc":
            # GSC: detect 9-column CSV
            for enc in ['utf-8', 'utf-16', 'latin1', 'utf-8-sig']:
                for sep in [',', ';', '\t']:
                    try:
                        temp_df = pd.read_csv(io.BytesIO(content), encoding=enc, sep=sep)
                        if len(temp_df.columns) == 9:
                            df = temp_df
                            break
                    except Exception:
                        continue
                if df is not None:
                    break
            if df is None:
                raise Exception(t["err_format_gsc"])
            df.columns = [
                "Keyword",
                "Clicks_New", "Clicks_Old",
                "Impressions_New", "Impressions_Old",
                "CTR_New", "CTR_Old",
                "Position_New", "Position_Old"
            ]

        elif mode_key == "sistrix":
            # Sistrix: detect Keyword + Position#1 columns
            for enc in ['utf-8', 'utf-16', 'latin1', 'utf-8-sig']:
                for sep in ['\t', ';', ',']:
                    for skip in [0, 1, 2, 3, 4, 5]:
                        try:
                            temp_df = pd.read_csv(io.BytesIO(content), encoding=enc, sep=sep, skiprows=skip, on_bad_lines='skip')
                            temp_df.columns = [str(c).strip().strip('"').strip("'") for c in temp_df.columns]
                            if 'Keyword' in temp_df.columns and 'Position#1' in temp_df.columns:
                                df = temp_df
                                break
                        except Exception:
                            continue
                    if df is not None:
                        break
                if df is not None:
                    break
            if df is None:
                raise Exception(t["err_format_sistrix"])

            req_cols = ["Keyword", "Position#1", "Position#2", "Search Volume", "URL"]
            missing_cols = [col for col in req_cols if col not in df.columns]
            if missing_cols:
                st.error(f"{t['err_req']} {missing_cols}")
                st.stop()

    except Exception as e:
        st.error(f"{t['err_read']}{e}")
        st.stop()

    if st.session_state.get('show_success_alert', False):
        success_msg = t["succ_load"]
        st.markdown(
            f"""
            <div class="custom-success-alert">
                <svg class="success-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>{success_msg}</span>
            </div>
            <style>
            .custom-success-alert {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem;
                margin-bottom: 1.5rem;
                border: 1px solid rgba(144, 194, 116, 0.3);
                border-radius: 8px;
                color: #3b5e2b;
                background-color: rgba(144, 194, 116, 0.1);
                font-family: inherit;
                font-size: 0.95rem;
                overflow: hidden;
                max-height: 150px;
                animation: fadeOutAlert 0.5s ease-out 3s forwards;
            }}
            .success-icon {{
                color: #90c274;
                flex-shrink: 0;
            }}
            @keyframes fadeOutAlert {{
                0% {{
                    opacity: 1;
                    max-height: 150px;
                    padding: 1rem;
                    margin-bottom: 1.5rem;
                    border-width: 1px;
                }}
                100% {{
                    opacity: 0;
                    max-height: 0;
                    padding-top: 0;
                    padding-bottom: 0;
                    margin-bottom: 0;
                    border-width: 0;
                    visibility: hidden;
                }}
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        st.session_state['show_success_alert'] = False

    # =========================================================================
    # DATA CLEANING — mode-specific
    # =========================================================================
    if mode_key == "gsc":
        df = df.dropna(subset=['Keyword'])
        df = df[df['Keyword'].astype(str).str.strip() != ""]
        for col in df.columns[1:]:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = df[col].str.extract(r'([0-9.]+)')[0]
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Position_New'] = df['Position_New'].replace(0, 101)
        df['Position_Old'] = df['Position_Old'].replace(0, 101)

        # Derived columns
        df['Clicks Loss'] = df['Clicks_Old'] - df['Clicks_New']
        df['Clicks Gain'] = df['Clicks_New'] - df['Clicks_Old']
        df['Clicks Change'] = df['Clicks_New'] - df['Clicks_Old']
        df['Impressions Loss'] = df['Impressions_Old'] - df['Impressions_New']
        df['Position Change'] = df['Position_Old'] - df['Position_New']

        def get_change_type_gsc(row):
            po, pn = row['Position_Old'], row['Position_New']
            if po == 101 and pn != 101: return "New"
            elif po <= 3 and pn > 3: return "OoTop3"
            elif po <= 10 and pn > 10: return "OoTop10"
            elif 10 < po <= 20 and pn > 20: return "OoSERP2"
            elif po <= 100 and pn > 100: return "OoTop100"
            elif po > 10 and pn <= 10: return "IntoTop10"
            elif abs(po - pn) < 1.0: return "None"
            else: return "Changed"
        df['Change'] = df.apply(get_change_type_gsc, axis=1)

    elif mode_key == "sistrix":
        if df['Search Volume'].dtype == 'object':
            df['Search Volume'] = df['Search Volume'].astype(str).str.replace('.', '', regex=False).str.replace(',', '', regex=False)
        df['Search Volume'] = pd.to_numeric(df['Search Volume'], errors='coerce').fillna(0)

        if 'CPC' in df.columns:
            if df['CPC'].dtype == 'object':
                df['CPC'] = df['CPC'].astype(str).str.replace(',', '.', regex=False)
            df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce').fillna(0.0)
        else:
            df['CPC'] = 0.0

        if 'Competition' in df.columns:
            if df['Competition'].dtype == 'object':
                df['Competition'] = df['Competition'].astype(str).str.replace(',', '.', regex=False)
            df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce').fillna(0.0)
        else:
            df['Competition'] = 0.0

        for col in ['Position#1', 'Position#2']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(101)
            df[col] = df[col].replace(0, 101)

        def get_first_directory(url):
            try:
                path = urlparse(str(url)).path
                parts = path.strip('/').split('/')
                if len(parts) > 0 and parts[0] != '':
                    return f"/{parts[0]}/"
                return "/"
            except Exception:
                return "/"
        df['Directory'] = df['URL'].apply(get_first_directory)

        # Traffic & value columns
        df['Traffic#1'] = df['Search Volume'] * df['Position#1'].apply(estimate_ctr)
        df['Traffic#2'] = df['Search Volume'] * df['Position#2'].apply(estimate_ctr)
        df['Traffic Loss'] = df['Traffic#1'] - df['Traffic#2']
        df['Traffic Gain'] = df['Traffic#2'] - df['Traffic#1']
        df['Lost Value €'] = df['Traffic Loss'].clip(lower=0) * df['CPC']
        df['Position Change'] = df['Position#1'] - df['Position#2']
        df['Traffic Change'] = df['Traffic#2'] - df['Traffic#1']

        # SV-mode metric columns (fixed)
        df['Metric Loss'] = 0.0
        df.loc[df['Position Change'] < 0, 'Metric Loss'] = df['Search Volume']
        df['Metric Gain'] = 0.0
        df.loc[df['Position Change'] > 0, 'Metric Gain'] = df['Search Volume']
        df['Metric Change'] = df['Metric Gain'] - df['Metric Loss']

        def get_change_type_sistrix(row):
            po, pn = row['Position#1'], row['Position#2']
            if po == 101 and pn != 101: return "New"
            elif po <= 3 and pn > 3: return "OoTop3"
            elif po <= 10 and pn > 10: return "OoTop10"
            elif 10 < po <= 20 and pn > 20: return "OoSERP2"
            elif po <= 100 and pn > 100: return "OoTop100"
            elif po > 10 and pn <= 10: return "IntoTop10"
            elif abs(po - pn) < 1.0: return "None"
            else: return "Changed"
        df['Change'] = df.apply(get_change_type_sistrix, axis=1)

    # =========================================================================
    # SHARED: Clustering
    # =========================================================================
    stopwords_de = set([
        "und", "oder", "kaufen", "test", "erfahrung", "erfahrungen", "günstig", "online", "shop",
        "mit", "für", "von", "in", "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer",
        "eines", "auf", "im", "am", "zu", "ist", "sind", "wie", "was", "wo", "wer", "warum", "als", "an",
        "bei", "aus", "nach", "um", "bis", "über", "unter", "vor", "zwischen", "aber", "nur", "auch",
        "dass", "dann", "wenn", "so", "sich", "nicht", "noch", "mehr", "durch", "zum", "zur"
    ])
    stopwords_en = set([
        "and", "or", "buy", "test", "experience", "cheap", "online", "shop", "with", "for", "of", "in",
        "the", "a", "an", "on", "at", "to", "is", "are", "how", "what", "where", "who", "why", "as",
        "from", "after", "about", "under", "before", "between", "but", "only", "also", "that", "then",
        "if", "so", "not", "more", "by"
    ])
    stopwords = stopwords_en if lang == "EN" else stopwords_de
    brand_terms = [b.strip().lower() for b in brand_input.split(',')] if brand_input.strip() else []

    if mode_key == "gsc":
        temp_losers = df[df['Clicks Loss'] > 0]
        non_brand_kws = temp_losers[~temp_losers['Keyword'].apply(
            lambda kw: any(b and b in str(kw).lower() for b in brand_terms)
        )]['Keyword'].dropna().tolist()
    else:
        temp_losers = df[df['Traffic Loss'] > 0]
        non_brand_kws = temp_losers[temp_losers['Keyword'].apply(
            lambda kw: not any(b and b in str(kw).lower() for b in brand_terms)
        )]['Keyword'].dropna().tolist()

    word_counts = Counter()
    for kw in non_brand_kws:
        words = re.findall(r'\b\w+\b', str(kw).lower())
        for w in words:
            if w not in stopwords and len(w) > 2 and not w.isnumeric():
                word_counts[w] += 1

    top_head_terms = [word for word, count in word_counts.most_common(num_clusters)]

    def get_cluster(kw):
        kw_lower = str(kw).lower()
        for b in brand_terms:
            if b and b in kw_lower:
                return "Brand"
        for term in top_head_terms:
            if re.search(rf'\b{re.escape(term)}\b', kw_lower):
                return term.capitalize()
        return "undefined"

    df['Cluster'] = df['Keyword'].apply(get_cluster)

    # =========================================================================
    # SHARED: Search Intent
    # =========================================================================
    intent_skipped = data_lang_choice not in [t["data_lang_options"][0], t["data_lang_options"][1]]
    if intent_skipped:
        df['Search Intent'] = "not analyzed"
    else:
        df['Search Intent'] = df['Keyword'].apply(lambda kw: get_intent(kw, data_lang_choice))


    # =========================================================================
    # SHARED: Segment Definitions
    # =========================================================================
    if mode_key == "gsc":
        losers = df[df['Clicks Loss'] > 0].copy()
        winners = df[df['Clicks Gain'] > 0].copy()
        top3_drops = df[(df['Position_Old'] <= 3) & (df['Position_New'] > 3) & (df['Clicks Loss'] > 0)]
        top10_drops = df[(df['Position_Old'] <= 10) & (df['Position_New'] > 10) & (df['Clicks Loss'] > 0)]
        page2_drops = df[(df['Position_Old'] > 10) & (df['Position_Old'] <= 20) & (df['Position_New'] > 20) & (df['Clicks Loss'] > 0)]
        total_loss = df[(df['Position_Old'] <= 100) & (df['Position_New'] > 100) & (df['Clicks Loss'] > 0)]
        low_hanging = df[(df['Position_New'] >= 11) & (df['Position_New'] <= 15)]
    else:
        losers = df[df['Position Change'] < 0].copy()
        winners = df[df['Position Change'] > 0].copy()
        top3_drops = df[(df['Position#1'] <= 3) & (df['Position Change'] < 0)]
        top10_drops = df[(df['Position#1'] <= 10) & (df['Position Change'] < 0)]
        page2_drops = df[(df['Position#1'] > 10) & (df['Position#1'] <= 20) & (df['Position Change'] < 0)]
        total_loss = df[(df['Position#1'] <= 100) & (df['Position#2'] > 100)]
        low_hanging = df[(df['Position#2'] >= 11) & (df['Position#2'] <= 15)]

    # =========================================================================

    # TAB DEEP-LINK LOGIC (shared)
    # =========================================================================
    def on_tab_change():
        active_tab = st.session_state.get("main_tabs")
        if active_tab == t["tab_lhf"]:
            st.query_params["tab"] = "lhf"
        elif active_tab == t["tab_drops"]:
            st.query_params["tab"] = "drops"
        else:
            if "tab" in st.query_params:
                del st.query_params["tab"]

    if "tab" in st.query_params and "main_tabs" not in st.session_state:
        param_val = st.query_params["tab"]
        if param_val == "lhf":
            st.session_state["main_tabs"] = t["tab_lhf"]
            st.session_state["scroll_target"] = "low-hanging-fruits"
        elif param_val == "top3":
            st.session_state["main_tabs"] = t["tab_drops"]
            st.session_state["scroll_target"] = "top3-drops"
        elif param_val == "top10":
            st.session_state["main_tabs"] = t["tab_drops"]
            st.session_state["scroll_target"] = "top10-drops"
        elif param_val == "drops":
            st.session_state["main_tabs"] = t["tab_drops"]

    if mode_key == "gsc":
        tab_sum, tab2, tab5, tab4, tab3, tab1, tab6 = st.tabs([
            t["tab_summary"], t["tab_drops"], t["tab_winners"], t["tab_lhf"],
            t["tab_losses"], t["tab_cluster"], t["tab_all"]
        ], key="main_tabs", on_change=on_tab_change)

        with tab_sum:
            st.header(t["kpi_header_gsc"])

            total_clicks_lost = int(losers['Clicks Loss'].sum())
            total_clicks_gained = int(winners['Clicks Gain'].sum())
            net_clicks = total_clicks_gained - total_clicks_lost
            lhf_impressions = int(low_hanging['Impressions_New'].sum())

            total_clicks_old = df['Clicks_Old'].sum()
            pct_change = (net_clicks / total_clicks_old * 100) if total_clicks_old > 0 else 0.0
            if net_clicks > 0:
                pct_change_formatted = f"+{format_num(pct_change, decimal_places=1)}{pct_sign}"
            elif net_clicks < 0:
                pct_change_formatted = f"{format_num(pct_change, decimal_places=1)}{pct_sign}"
            else:
                pct_change_formatted = f"{format_num(0.0, decimal_places=1)}{pct_sign}"

            loss_val_str = f"-{format_num(total_clicks_lost)}"
            gain_val_str = f"+{format_num(total_clicks_gained)}"
            net_val_str = f"+{format_num(net_clicks)}" if net_clicks > 0 else format_num(net_clicks)
            pct_val_str = pct_change_formatted

            # Percentage differences for GSC lost and gained total clicks
            loss_pct = (total_clicks_lost / total_clicks_old * 100) if total_clicks_old > 0 else 0.0
            loss_pct_str = f"-{format_num(loss_pct, 1)}{pct_sign}"
            gain_pct = (total_clicks_gained / total_clicks_old * 100) if total_clicks_old > 0 else 0.0
            gain_pct_str = f"+{format_num(gain_pct, 1)}{pct_sign}"

            top3_count = len(top3_drops)
            top3_loss_val = int(top3_drops['Clicks Loss'].sum())
            top3_pct = (top3_loss_val / total_clicks_old * 100) if total_clicks_old > 0 else 0.0
            clicks_unit = "Klicks" if lang == "DE" else "clicks"
            top3_loss_str = f"-{format_num(top3_loss_val)} {clicks_unit} (-{format_num(top3_pct, 1)}{pct_sign})"

            top10_count = len(top10_drops)
            top10_loss_val = int(top10_drops['Clicks Loss'].sum())
            top10_pct = (top10_loss_val / total_clicks_old * 100) if total_clicks_old > 0 else 0.0
            top10_loss_str = f"-{format_num(top10_loss_val)} {clicks_unit} (-{format_num(top10_pct, 1)}{pct_sign})"

            lhf_count = len(low_hanging)
            lhf_imp = format_num(lhf_impressions)
            total_imp_new = df['Impressions_New'].sum()
            lhf_pct = (lhf_impressions / total_imp_new * 100) if total_imp_new > 0 else 0.0
            lhf_delta_str = f"+{lhf_imp} Imp. (+{format_num(lhf_pct, 1)}{pct_sign})"

            # For backward compatibility in story_text
            top3_loss = f"-{format_num(top3_loss_val)}"
            top10_loss = f"-{format_num(top10_loss_val)}"

            if lang == "DE":
                story_text = f"""<p style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1rem;'>
    Im analysierten Zeitraum verzeichnete die Website eine
    <strong style='color: #232323;'>Netto-Klick-Veränderung von <span style='color: {"#90c274" if net_clicks > 0 else "#993333"}; font-weight: bold;'>{net_val_str}</span> ({pct_val_str})</strong>.
    Dieser Wert setzt sich aus einem <strong>Gewinn von <span style='color: #90c274; font-weight: bold;'>{gain_val_str}</span> Klicks</strong>
    und einem <strong>Verlust von <span style='color: #993333; font-weight: bold;'>{loss_val_str}</span> Klicks</strong> zusammen.
    </p>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Haupttreiber des Klick-Verlusts:</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li style='margin-bottom: 0.5rem;'><strong>Abstürze aus den Top 3:</strong> <span style='font-weight: bold;'>{format_num(top3_count)} Keywords</span> sind aus den Top-Positionen (1-3) herausgerutscht. Verlust: <span style='color: #993333; font-weight: bold;'>{top3_loss} Klicks</span>.</li>
    <li style='margin-bottom: 0.5rem;'><strong>Abstürze aus den Top 10:</strong> <span style='font-weight: bold;'>{format_num(top10_count)} Keywords</span> haben die erste Suchergebnisseite verlassen. Verlust: <span style='color: #993333; font-weight: bold;'>{top10_loss} Klicks</span>.</li>
    </ul>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Quick-Wins / Handlungsempfehlungen:</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li>Es wurden <strong style='color: #90c274;'>{format_num(lhf_count)} Schwellen-Keywords (Low Hanging Fruits)</strong> auf den Positionen 11-15 identifiziert. Diese erzielen aktuell bereits <span style='font-weight: bold;'>{lhf_imp} Impressionen</span> auf Seite 2. Durch gezielte On-Page-Optimierung können diese schnell auf Seite 1 geschoben werden.</li>
    </ul>"""
                story_title = "Executive Summary & Marketing-Story"
            else:
                story_text = f"""<p style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1rem;'>
    During the analyzed timeframe, the website recorded a
    <strong style='color: #232323;'>Net Click Change of <span style='color: {"#90c274" if net_clicks > 0 else "#993333"}; font-weight: bold;'>{net_val_str}</span> ({pct_val_str})</strong>.
    This value is composed of a <strong>gain of <span style='color: #90c274; font-weight: bold;'>{gain_val_str}</span> clicks</strong>
    and a <strong>loss of <span style='color: #993333; font-weight: bold;'>{loss_val_str}</span> clicks</strong>.
    </p>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Main Drivers of Click Loss:</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li style='margin-bottom: 0.5rem;'><strong>Drops from Top 3:</strong> <span style='font-weight: bold;'>{format_num(top3_count)} keywords</span> slipped out of the top positions (1-3). This caused a loss of <span style='color: #993333; font-weight: bold;'>{top3_loss} clicks</span>.</li>
    <li style='margin-bottom: 0.5rem;'><strong>Drops from Top 10:</strong> <span style='font-weight: bold;'>{format_num(top10_count)} keywords</span> fell off page 1, resulting in a loss of <span style='color: #993333; font-weight: bold;'>{top10_loss} clicks</span>.</li>
    </ul>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Quick-Wins / Actionable Recommendations:</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li>We identified <strong style='color: #90c274;'>{format_num(lhf_count)} Threshold Keywords (Low Hanging Fruits)</strong> ranking on positions 11-15. These already generate <span style='font-weight: bold;'>{lhf_imp} impressions</span> on page 2. Targeted on-page optimization can push these onto page 1 quickly.</li>
    </ul>"""
                story_title = "Executive Summary & Marketing Story"

            kpi_col1, kpi_col2 = st.columns([5, 3])
            with kpi_col1:
                with st.container(border=True, key="gsc_exec_summary_container"):
                    st.markdown(f"""<h3 style='margin-top: 0; margin-bottom: 1rem; font-family: "Raleway", sans-serif; font-weight: 800; color: #232323;'>{story_title}</h3>{story_text}""", unsafe_allow_html=True)
                    def select_lhf_tab_gsc():
                        st.session_state["main_tabs"] = t["tab_lhf"]
                        st.query_params["tab"] = "lhf"
                        st.session_state["scroll_target"] = "low-hanging-fruits"
                        st.session_state["show_custom_loader"] = True
                    def select_top3_tab_gsc():
                        st.session_state["main_tabs"] = t["tab_drops"]
                        st.query_params["tab"] = "top3"
                        st.session_state["scroll_target"] = "top3-drops"
                        st.session_state["show_custom_loader"] = True
                    def select_top10_tab_gsc():
                        st.session_state["main_tabs"] = t["tab_drops"]
                        st.query_params["tab"] = "top10"
                        st.session_state["scroll_target"] = "top10-drops"
                        st.session_state["show_custom_loader"] = True
                    b_col1, b_col2, b_col3 = st.columns(3)
                    with b_col1:
                        st.button("🔍 Top 3 Drops", key="goto_top3_btn", on_click=select_top3_tab_gsc, type="secondary", use_container_width=True)
                    with b_col2:
                        st.button("🔍 Top 10 Drops", key="goto_top10_btn", on_click=select_top10_tab_gsc, type="secondary", use_container_width=True)
                    with b_col3:
                        st.button("🎯 Low Hanging Fruits", key="goto_lhf_btn", on_click=select_lhf_tab_gsc, type="secondary", use_container_width=True)

            with kpi_col2:
                st.metric(t["kpi_net_change"], net_val_str, delta=pct_val_str)
                sub_c1, sub_c2 = st.columns(2)
                with sub_c1:
                    st.metric(t["kpi_lost_total"], loss_val_str, delta=loss_pct_str, delta_color="normal")
                with sub_c2:
                    st.metric(t["kpi_gained_total"], gain_val_str, delta=gain_pct_str, delta_color="normal")
                sub_c3, sub_c4 = st.columns(2)
                with sub_c3:
                    st.metric(t["kpi_top3_drops"], format_num(top3_count), delta=top3_loss_str, delta_color="normal")
                with sub_c4:
                    st.metric(t["kpi_top10_drops"], format_num(top10_count), delta=top10_loss_str, delta_color="normal")
                st.metric(t["kpi_lhf"], format_num(lhf_count), delta=lhf_delta_str, delta_color="off", help=t["kpi_lhf_help_gsc"])

            st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)

            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                st.markdown("#### " + t["kpi_cluster_title"])
                cluster_net = df.groupby('Cluster')['Clicks Change'].sum().reset_index()
                cluster_net = cluster_net[cluster_net['Cluster'] != "undefined"]
                if not cluster_net.empty:
                    best_cluster = cluster_net.loc[cluster_net['Clicks Change'].idxmax()]
                    worst_cluster = cluster_net.loc[cluster_net['Clicks Change'].idxmin()]
                    best_val = best_cluster['Clicks Change']
                    best_delta = f"+{format_num(best_val)} {t['clicks']}" if best_val > 0 else f"{format_num(best_val)} {t['clicks']}"
                    worst_val = worst_cluster['Clicks Change']
                    worst_delta = f"+{format_num(worst_val)} {t['clicks']}" if worst_val > 0 else f"{format_num(worst_val)} {t['clicks']}"
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(t["kpi_best_cluster"], best_cluster['Cluster'], best_delta)
                    with c2:
                        st.metric(t["kpi_worst_cluster"], worst_cluster['Cluster'], worst_delta)
                    top_bottom = pd.concat([cluster_net.nlargest(3, 'Clicks Change'), cluster_net.nsmallest(3, 'Clicks Change')]).drop_duplicates().sort_values('Clicks Change')
                    fig_net = px.bar(top_bottom, x='Clicks Change', y='Cluster', orientation='h',
                                     color='Clicks Change', color_continuous_scale=[[0.0, '#993333'], [0.5, '#dfdfdf'], [1.0, '#90c274']], height=200)
                    style_plotly_fig(fig_net)
                    fig_net.update_layout(margin=dict(l=10, r=10, t=25, b=10))
                    st.plotly_chart(fig_net, use_container_width=True)

            with viz_col2:
                st.markdown("#### " + t["kpi_top3_title"])
                if not top3_drops.empty:
                    worst_top3 = top3_drops.nlargest(5, 'Clicks Loss').sort_values('Clicks Loss', ascending=True)
                    fig_t3 = px.bar(worst_top3, x='Clicks Loss', y='Keyword', orientation='h',
                                    color_discrete_sequence=['#2ea3f2'], height=270)
                    style_plotly_fig(fig_t3)
                    fig_t3.update_layout(margin=dict(l=10, r=10, t=25, b=10))
                    st.plotly_chart(fig_t3, use_container_width=True)
                else:
                    st.info(t["rd_t3_empty"])

            if not intent_skipped:
                viz_col3, viz_col4 = st.columns(2)
                with viz_col3:
                    st.markdown("#### " + t["kpi_intent_title"])
                    intent_df = df.assign(Intent=df['Search Intent'].str.split(', ')).explode('Intent')
                    intent_counts = intent_df['Intent'].value_counts().reset_index()
                    intent_counts.columns = ['Search Intent', 'Count']
                    color_map = {"DO (Transactional)": "#1f86cf", "KNOW": "#2ea3f2",
                                 "regional:CITY": "#0f5a90", "regional:COUNTRY": "#535353", "undefined": "#dfdfdf"}
                    fig_pie = px.pie(intent_counts, values='Count', names='Search Intent',
                                     color='Search Intent', color_discrete_map=color_map, hole=0.4, height=280)
                    style_plotly_fig(fig_pie)
                    fig_pie.update_layout(margin=dict(l=10, r=10, t=25, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True)
                with viz_col4:
                    st.markdown("#### Details")
                    intent_pct = intent_df['Intent'].value_counts(normalize=True).reset_index()
                    intent_pct.columns = ['Search Intent', 'Percentage']
                    intent_pct['Percentage'] = intent_pct['Percentage'] * 100
                    intent_summary = pd.merge(intent_counts, intent_pct, on='Search Intent')
                    col_intent = 'Search Intent' if lang == 'EN' else 'Suchintent'
                    col_count = 'Keywords (Count)' if lang == 'EN' else 'Keywords (Anzahl)'
                    col_share = 'Share (%)' if lang == 'EN' else 'Anteil (%)'
                    intent_summary.columns = [col_intent, col_count, col_share]
                    formatted_intent_summary = intent_summary.copy()
                    formatted_intent_summary[col_count] = formatted_intent_summary[col_count].apply(lambda x: format_num(x))
                    formatted_intent_summary[col_share] = formatted_intent_summary[col_share].apply(lambda x: f"{format_num(x, 1)}{pct_sign}")
                    st.write("")
                    st.dataframe(formatted_intent_summary, use_container_width=True, hide_index=True)
            else:
                st.info(t["intent_not_analyzed_msg"])


        with tab1:
            st.subheader(t["cl_sub"])
            st.markdown(t["cl_desc"])
            if not losers.empty:
                cluster_vol = losers.groupby('Cluster').agg(
                    Clicks_Lost=('Clicks Loss', 'sum'),
                    Keyword_Count=('Keyword', 'count')
                ).reset_index()
                cluster_vol = cluster_vol[cluster_vol['Clicks_Lost'] > 0].sort_values('Clicks_Lost', ascending=False)
                fig_cluster = px.bar(cluster_vol, x='Cluster', y='Clicks_Lost',
                                     title=t["cl_chart_title"],
                                     labels={'Cluster': t["cl_chart_label_c"], 'Clicks_Lost': t["cl_chart_label_v"]},
                                     color='Clicks_Lost', color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#2ea3f2']])
                style_plotly_fig(fig_cluster)
                st.plotly_chart(fig_cluster, use_container_width=True)
                st.markdown(t["cl_detail"])
                opts = [c for c in cluster_vol['Cluster'].tolist() if c != "undefined"] + (["undefined"] if "undefined" in cluster_vol['Cluster'].tolist() else [])
                selected_clusters = st.multiselect(t["cl_select"], options=opts)
                if selected_clusters:
                    cluster_df = losers[losers['Cluster'].isin(selected_clusters)]
                    st.write(f"{t['cl_sum_clicks']} **{format_num(int(cluster_df['Clicks Loss'].sum()))}**")
                    display_styled_dataframe(cluster_df[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
            else:
                st.info(t["cl_empty"])

        with tab2:
            st.subheader(t["rd_sub"])
            kw_filter = st.text_input(t["rd_filter"]).strip().lower()
            f_top3 = top3_drops[top3_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top3_drops
            f_top10 = top10_drops[top10_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top10_drops
            f_page2 = page2_drops[page2_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else page2_drops
            f_total = total_loss[total_loss['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else total_loss

            st.markdown("<div id='top3-drops'></div>", unsafe_allow_html=True)
            st.markdown(t["rd_t3_title"])
            if not f_top3.empty:
                t_clicks = format_num(int(f_top3['Clicks Loss'].sum()))
                t_impressions = format_num(int(f_top3['Impressions Loss'].sum()))
                t_count = format_num(len(f_top3))
                desc_text = t["rd_t3_desc_gsc"].format(count=t_count, clicks=t_clicks, impressions=t_impressions)
                st.markdown(desc_text)
                st.write(f"{t['rd_sum_clicks']} **{format_num(int(f_top3['Clicks Loss'].sum()))}**")
                display_styled_dataframe(f_top3[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
            else:
                st.info(t["rd_t3_empty"])

            st.markdown("<div id='top10-drops'></div>", unsafe_allow_html=True)
            st.markdown(t["rd_t10_title"])
            if not f_top10.empty:
                t_clicks = format_num(int(f_top10['Clicks Loss'].sum()))
                t_impressions = format_num(int(f_top10['Impressions Loss'].sum()))
                t_count = format_num(len(f_top10))
                desc_text = t["rd_t10_desc_gsc"].format(count=t_count, clicks=t_clicks, impressions=t_impressions)
                st.markdown(desc_text)
                st.write(f"{t['rd_sum_clicks']} **{format_num(int(f_top10['Clicks Loss'].sum()))}**")
                display_styled_dataframe(f_top10[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
            else:
                st.info(t["rd_t10_empty"])

            st.markdown(t["rd_p2_title"])
            if not f_page2.empty:
                t_clicks = format_num(int(f_page2['Clicks Loss'].sum()))
                t_impressions = format_num(int(f_page2['Impressions Loss'].sum()))
                t_count = format_num(len(f_page2))
                desc_text = t["rd_p2_desc_gsc"].format(count=t_count, clicks=t_clicks, impressions=t_impressions)
                st.markdown(desc_text)
                st.write(f"{t['rd_sum_clicks']} **{format_num(int(f_page2['Clicks Loss'].sum()))}**")
                display_styled_dataframe(f_page2[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
            else:
                st.info(t["rd_p2_empty"])

            st.markdown(t["rd_100_title"])
            if not f_total.empty:
                t_clicks = format_num(int(f_total['Clicks Loss'].sum()))
                t_impressions = format_num(int(f_total['Impressions Loss'].sum()))
                t_count = format_num(len(f_total))
                desc_text = t["rd_100_desc_gsc"].format(count=t_count, clicks=t_clicks, impressions=t_impressions)
                st.markdown(desc_text)
                st.write(f"{t['rd_sum_clicks']} **{format_num(int(f_total['Clicks Loss'].sum()))}**")
                display_styled_dataframe(f_total[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
            else:
                st.info(t["rd_100_empty"])

        with tab3:
            st.subheader(t["cd_sub"])
            display_styled_dataframe(losers[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')

        with tab4:
            st.subheader(t["lhf_sub"], anchor="low-hanging-fruits")
            st.markdown(t["lhf_desc_gsc"])
            if not low_hanging.empty:
                lhf_df = low_hanging.copy()
                lhf_df[['Potential Score', 'Difficulty']] = lhf_df.apply(calculate_lhf_gsc, axis=1)
                cols_to_show = ['Keyword', 'Difficulty', 'Potential Score', 'Position Change', 'Position_Old', 'Position_New', 'Impressions_New', 'Clicks_New']
                styler = lhf_df[cols_to_show].sort_values('Impressions_New', ascending=False).style
                format_dict = {}
                format_dict['Potential Score'] = lambda x: f"{x:.1f}"
                for c in ['Impressions_New', 'Clicks_New']:
                    format_dict[c] = lambda x: format_num(x) if pd.notnull(x) else ""
                for c in ['Position_Old', 'Position_New']:
                    format_dict[c] = lambda x: "-" if pd.notnull(x) and x == 101 else (format_num(x, 2) if pd.notnull(x) else "")
                styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else ('color: #993333; font-weight: bold;' if pd.notnull(x) and x < 0 else ''), subset=['Position Change'])
                format_dict['Position Change'] = lambda x: f"▲ +{format_num(abs(x), 2)}" if pd.notnull(x) and x > 0 else (f"▼ -{format_num(abs(x), 2)}" if pd.notnull(x) and x < 0 else format_num(0.0, 2))
                styler = styler.format(format_dict)
                st.dataframe(
                    styler,
                    column_config={
                        "Potential Score": st.column_config.ProgressColumn(
                            "Potential Score",
                            help=t.get("lhf_pot_help", "Calculated potential (0-10)"),
                            format="%.1f",
                            min_value=0.0,
                            max_value=10.0,
                        ),
                        "Difficulty": st.column_config.TextColumn(
                            t.get("lhf_diff_label", "Difficulty"),
                            help=t.get("lhf_diff_help", "Estimated difficulty")
                        )
                    },
                    use_container_width=True
                )
            else:
                st.info(t["lhf_empty"])

        with tab5:
            st.subheader(t["win_sub_gsc"])
            if not winners.empty:
                display_winners = winners[(winners['Position Change'] > 0) & (~((winners['Position_New'] > 11) & (winners['Position Change'] < 9)))]
                if not display_winners.empty:
                    fig_win = px.scatter(display_winners, x="Clicks Gain", y="Position_New",
                                         size="Clicks_New", color="Position Change",
                                         hover_name="Keyword", title=t["win_chart_title"],
                                         labels={'Position_New': t["win_chart_label_pos"], 'Clicks Gain': t["win_chart_label_gain"]},
                                         color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#90c274']])
                    fig_win.update_yaxes(autorange="reversed")
                    style_plotly_fig(fig_win)
                    st.plotly_chart(fig_win, use_container_width=True)
                    display_styled_dataframe(display_winners[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Gain', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Gain')
                else:
                    st.info(t["win_empty"])
            else:
                st.info(t["win_empty"])

        with tab6:
            st.subheader(t["ad_sub"])
            all_cols = ['Cluster', 'Search Intent', 'Keyword', 'Change', 'Position Change', 'Clicks Change',
                        'Position_Old', 'Position_New', 'Impressions_Old', 'Impressions_New', 'Clicks_Old', 'Clicks_New']
            all_cols = [c for c in all_cols if c in df.columns]
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                all_clusters = sorted(df['Cluster'].dropna().unique().tolist())
                sel_cluster = st.multiselect(t["ad_filter_cluster"], options=all_clusters)
            with col_f2:
                all_intents = set()
                for i in df['Search Intent'].dropna():
                    for piece in i.split(', '):
                        all_intents.add(piece)
                sel_intent = st.multiselect(t["ad_filter_intent"], options=sorted(list(all_intents)))
            with col_f3:
                all_changes = sorted(df['Change'].dropna().unique().tolist())
                sel_change = st.multiselect(t["ad_filter_change"], options=all_changes)
            with col_f4:
                search_kw = st.text_input(t["ad_filter_kw"], key="ad_kw")
            f_df = df[all_cols].copy()
            if sel_cluster:
                f_df = f_df[f_df['Cluster'].isin(sel_cluster)]
            if sel_intent:
                f_df = f_df[f_df['Search Intent'].apply(lambda x: any(c in x for c in sel_intent))]
            if sel_change:
                f_df = f_df[f_df['Change'].isin(sel_change)]
            if search_kw:
                f_df = f_df[f_df['Keyword'].astype(str).str.lower().str.contains(search_kw.lower(), na=False)]
            display_styled_dataframe(f_df, sort_col='Clicks Change', ascending=False)

    elif mode_key == "sistrix":
        tab_sum, tab2, tab4, tab3, tab_d, tab1, tab5 = st.tabs([
            t["tab_summary"], t["tab_drops"], t["tab_winners"], t["tab_lhf"],
            t["tab_dir"], t["tab_cluster"], t["tab_all"]
        ], key="main_tabs", on_change=on_tab_change)

        with tab_sum:
            st.header(t["kpi_header_sistrix"])

            gained_keywords_count = int((df['Position Change'] > 0).sum())
            lost_keywords_count = int((df['Position Change'] < 0).sum())
            avg_gain_pos = df[df['Position Change'] > 0]['Position Change'].mean()
            if pd.isnull(avg_gain_pos): avg_gain_pos = 0.0
            avg_loss_pos = abs(df[df['Position Change'] < 0]['Position Change'].mean())
            if pd.isnull(avg_loss_pos): avg_loss_pos = 0.0
            avg_pos_change = df['Position Change'].mean()
            if pd.isnull(avg_pos_change): avg_pos_change = 0.0

            gained_keywords_sv = df[df['Position Change'] > 0]['Search Volume'].sum()
            lost_keywords_sv = df[df['Position Change'] < 0]['Search Volume'].sum()
            total_sv = df['Search Volume'].sum()
            total_sv_old = total_sv
            total_metric_old = total_sv_old

            total_sv_loss = losers['Search Volume'].sum()
            total_sv_gained = winners['Search Volume'].sum()
            net_sv = total_sv_gained - total_sv_loss
            pct_sv_change = (net_sv / total_sv_old * 100) if total_sv_old > 0 else 0.0

            net_sv_sign = "+" if net_sv > 0 else ""
            net_sv_val_str = f"{net_sv_sign}{format_num(int(net_sv))} SV"
            pct_sv_val_str = f"{net_sv_sign}{format_num(pct_sv_change, 1)}{pct_sign}"
            loss_sv_pct_str = f"-{format_num(total_sv_loss / total_sv_old * 100 if total_sv_old > 0 else 0.0, 1)}{pct_sign}"
            gain_sv_pct_str = f"+{format_num(total_sv_gained / total_sv_old * 100 if total_sv_old > 0 else 0.0, 1)}{pct_sign}"
            loss_sv_val_str = f"-{format_num(int(total_sv_loss))} SV"
            gain_sv_val_str = f"+{format_num(int(total_sv_gained))} SV"

            total_clicks_old = df['Traffic#1'].sum()
            total_clicks_loss = df['Traffic Loss'].clip(lower=0).sum()
            total_clicks_gain = df['Traffic Gain'].clip(lower=0).sum()
            net_clicks = total_clicks_gain - total_clicks_loss
            pct_clicks_change = (net_clicks / total_clicks_old * 100) if total_clicks_old > 0 else 0.0
            clicks_unit = "Klicks" if lang == "DE" else "clicks"
            net_clicks_sign = "+" if net_clicks > 0 else ""
            net_clicks_val_str = f"{net_clicks_sign}{format_num(int(net_clicks))} {clicks_unit}"
            pct_clicks_val_str = f"{net_clicks_sign}{format_num(pct_clicks_change, 1)}{pct_sign}"

            total_value_old = (df['Traffic#1'] * df['CPC']).sum()
            total_value_loss = df['Lost Value €'].sum()
            pct_value_change = (total_value_loss / total_value_old * 100) if total_value_old > 0 else 0.0
            value_val_str = f"-{format_num(total_value_loss, 2)} €" if lang == "DE" else f"-€{format_num(total_value_loss, 2)}"
            value_pct_str = f"-{format_num(pct_value_change, 1)}{pct_sign}"

            top3_count = len(top3_drops)
            top3_loss_val = top3_drops['Search Volume'].sum()
            top3_pct = (top3_loss_val / total_sv_old * 100) if total_sv_old > 0 else 0.0
            top3_loss_str = f"-{format_num(int(top3_loss_val))} SV (-{format_num(top3_pct, 1)}{pct_sign})"
            top3_loss_only = f"{format_num(int(top3_loss_val))} SV"

            top10_count = len(top10_drops)
            top10_loss_val = top10_drops['Search Volume'].sum()
            top10_pct = (top10_loss_val / total_sv_old * 100) if total_sv_old > 0 else 0.0
            top10_loss_str = f"-{format_num(int(top10_loss_val))} SV (-{format_num(top10_pct, 1)}{pct_sign})"
            top10_loss_only = f"{format_num(int(top10_loss_val))} SV"

            total_loss_count = len(total_loss)
            total_loss_loss_val = total_loss['Search Volume'].sum()
            total_loss_pct = (total_loss_loss_val / total_sv_old * 100) if total_sv_old > 0 else 0.0
            total_loss_loss_str = f"-{format_num(int(total_loss_loss_val))} SV (-{format_num(total_loss_pct, 1)}{pct_sign})"
            total_loss_loss_only = f"{format_num(int(total_loss_loss_val))} SV"

            lhf_count = len(low_hanging)
            lhf_search_vol = int(low_hanging['Search Volume'].sum())
            lhf_sv = format_num(lhf_search_vol)
            lhf_pct = (lhf_search_vol / total_sv_old * 100) if total_sv_old > 0 else 0.0
            lhf_delta_str = f"+{lhf_sv} SV (+{format_num(lhf_pct, 1)}{pct_sign})"

            avg_pos_change_sign = "+" if avg_pos_change > 0 else ""
            avg_pos_change_val_str = f"{avg_pos_change_sign}{format_num(avg_pos_change, 2)}"
            avg_pos_change_delta_str = f"+{gained_keywords_count} / -{lost_keywords_count} KWs"

            date_range_str_old = date_old.strftime('%d.%m.%Y')
            date_range_str_new = date_new.strftime('%d.%m.%Y')

            if lang == "DE":
                story_text = f"""<p style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1rem;'>
    Im Vergleich vom <strong>{date_range_str_old}</strong> zum <strong>{date_range_str_new}</strong> verzeichnete Ihre Website folgende Ranking-Entwicklungen:
    </p>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Ranking-Veränderungen (Positions-Daten):</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li style='margin-bottom: 0.5rem;'><strong>Positions-Gewinne:</strong> <span style='font-weight: bold;'>{format_num(gained_keywords_count)} Keywords</span> verbessert (Ø <span style='color: #90c274; font-weight: bold;'>+{format_num(avg_gain_pos, 1)} Positionen</span>, Gesamt-SV: <span style='font-weight: bold;'>{format_num(gained_keywords_sv)} SV</span>).</li>
    <li style='margin-bottom: 0.5rem;'><strong>Positions-Verluste:</strong> <span style='font-weight: bold;'>{format_num(lost_keywords_count)} Keywords</span> verschlechtert (Ø <span style='color: #993333; font-weight: bold;'>-{format_num(avg_loss_pos, 1)} Positionen</span>, Gesamt-SV: <span style='font-weight: bold;'>{format_num(lost_keywords_sv)} SV</span>).</li>
    <li style='margin-bottom: 0.5rem;'><strong>Gesamt-Tendenz:</strong> Ø Positions-Veränderung: <span style='font-weight: bold; color: {"#90c274" if avg_pos_change > 0 else "#993333"};'>{avg_pos_change_sign}{format_num(avg_pos_change, 2)} Positionen</span> (Gesamt-SV: <span style='font-weight: bold;'>{format_num(total_sv)} SV</span>).</li>
    </ul>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Haupttreiber der Ranking-Abstürze:</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li style='margin-bottom: 0.5rem;'><strong>Abstürze aus den Top 3:</strong> <span style='font-weight: bold;'>{format_num(top3_count)} Keywords</span> verloren Top-Positionen (Verlust: <span style='color: #993333; font-weight: bold;'>{top3_loss_only}</span>).</li>
    <li style='margin-bottom: 0.5rem;'><strong>Abstürze aus den Top 10:</strong> Weitere <span style='font-weight: bold;'>{format_num(top10_count)} Keywords</span> fielen von Seite 1 (Verlust: <span style='color: #993333; font-weight: bold;'>{top10_loss_only}</span>).</li>
    <li style='margin-bottom: 0.5rem;'><strong>Vollständige Ranking-Verluste:</strong> <span style='font-weight: bold;'>{format_num(total_loss_count)} Keywords</span> komplett aus den Top 100 herausgefallen (Verlust: <span style='color: #993333; font-weight: bold;'>{total_loss_loss_only}</span>).</li>
    </ul>"""
                story_title = "Executive Summary & Marketing-Story"
            else:
                story_text = f"""<p style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1rem;'>
    Comparing <strong>{date_range_str_old}</strong> to <strong>{date_range_str_new}</strong>, your website recorded the following ranking developments:
    </p>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Ranking Changes (Position Data):</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li style='margin-bottom: 0.5rem;'><strong>Position Gains:</strong> <span style='font-weight: bold;'>{format_num(gained_keywords_count)} keywords</span> improved (avg. <span style='color: #90c274; font-weight: bold;'>+{format_num(avg_gain_pos, 1)} positions</span>, total SV: <span style='font-weight: bold;'>{format_num(gained_keywords_sv)} SV</span>).</li>
    <li style='margin-bottom: 0.5rem;'><strong>Position Losses:</strong> <span style='font-weight: bold;'>{format_num(lost_keywords_count)} keywords</span> deteriorated (avg. <span style='color: #993333; font-weight: bold;'>-{format_num(avg_loss_pos, 1)} positions</span>, total SV: <span style='font-weight: bold;'>{format_num(lost_keywords_sv)} SV</span>).</li>
    <li style='margin-bottom: 0.5rem;'><strong>Overall Trend:</strong> Avg. position change: <span style='font-weight: bold; color: {"#90c274" if avg_pos_change > 0 else "#993333"};'>{avg_pos_change_sign}{format_num(avg_pos_change, 2)} positions</span> (total SV: <span style='font-weight: bold;'>{format_num(total_sv)} SV</span>).</li>
    </ul>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Main Drivers of Ranking Drops:</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li style='margin-bottom: 0.5rem;'><strong>Drops from Top 3:</strong> <span style='font-weight: bold;'>{format_num(top3_count)} keywords</span> lost top positions (loss of <span style='color: #993333; font-weight: bold;'>{top3_loss_only}</span>).</li>
    <li style='margin-bottom: 0.5rem;'><strong>Drops from Top 10:</strong> <span style='font-weight: bold;'>{format_num(top10_count)} keywords</span> fell off page 1 (loss of <span style='color: #993333; font-weight: bold;'>{top10_loss_only}</span>).</li>
    <li style='margin-bottom: 0.5rem;'><strong>Complete Losses:</strong> <span style='font-weight: bold;'>{format_num(total_loss_count)} keywords</span> dropped out of the Top 100 (loss of <span style='color: #993333; font-weight: bold;'>{total_loss_loss_only}</span>).</li>
    </ul>
    <h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Quick-Wins / Actionable Recommendations:</h4>
    <ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
    <li>Focus on <strong style='color: #90c274;'>{format_num(lhf_count)} Threshold Keywords (Low Hanging Fruits)</strong> on positions 11-15 ({lhf_sv} SV on page 2).</li>
    </ul>"""
                story_title = "Executive Summary & Marketing Story"

            kpi_col1, kpi_col2 = st.columns([5, 3])
            with kpi_col1:
                with st.container(border=True, key="exec_summary_container"):
                    st.markdown(f"""<h3 style='margin-top: 0; margin-bottom: 1rem; font-family: "Raleway", sans-serif; font-weight: 800; color: #232323;'>{story_title}</h3>{story_text}""", unsafe_allow_html=True)
                    def select_lhf_tab_sis():
                        st.session_state["main_tabs"] = t["tab_lhf"]
                        st.query_params["tab"] = "lhf"
                        st.session_state["scroll_target"] = "low-hanging-fruits"
                        st.session_state["show_custom_loader"] = True
                    def select_top3_tab_sis():
                        st.session_state["main_tabs"] = t["tab_drops"]
                        st.query_params["tab"] = "top3"
                        st.session_state["scroll_target"] = "top3-drops"
                        st.session_state["show_custom_loader"] = True
                    def select_top10_tab_sis():
                        st.session_state["main_tabs"] = t["tab_drops"]
                        st.query_params["tab"] = "top10"
                        st.session_state["scroll_target"] = "top10-drops"
                        st.session_state["show_custom_loader"] = True
                    b_col1, b_col2, b_col3 = st.columns(3)
                    with b_col1:
                        label_t3 = "Top 3 Drops" if lang == "EN" else "Top 3 Abstürze"
                        st.button(label_t3, key="goto_top3_btn", on_click=select_top3_tab_sis, type="secondary", use_container_width=True)
                    with b_col2:
                        label_t10 = "Top 10 Drops" if lang == "EN" else "Top 10 Abstürze"
                        st.button(label_t10, key="goto_top10_btn", on_click=select_top10_tab_sis, type="secondary", use_container_width=True)
                    with b_col3:
                        st.button("Low Hanging Fruits", key="goto_lhf_btn", on_click=select_lhf_tab_sis, type="secondary", use_container_width=True)

            with kpi_col2:
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    st.metric(t["kpi_net_change_sv"], net_sv_val_str, delta=pct_sv_val_str)
                with row1_col2:
                    st.metric(t["kpi_net_change"], net_clicks_val_str, delta=pct_clicks_val_str)
                row2_col1, row2_col2 = st.columns(2)
                with row2_col1:
                    st.metric(t["kpi_lost_total_sv"], loss_sv_val_str, delta=loss_sv_pct_str, delta_color="normal")
                with row2_col2:
                    st.metric(t["kpi_gained_total_sv"], gain_sv_val_str, delta=gain_sv_pct_str, delta_color="normal")
                row3_col1, row3_col2 = st.columns(2)
                with row3_col1:
                    st.metric(t["kpi_top3_drops"], format_num(top3_count), delta=top3_loss_str, delta_color="normal")
                with row3_col2:
                    st.metric(t["kpi_top10_drops"], format_num(top10_count), delta=top10_loss_str, delta_color="normal")
                row4_col1, row4_col2 = st.columns(2)
                with row4_col1:
                    st.metric(t["kpi_total_loss"], format_num(total_loss_count), delta=total_loss_loss_str, delta_color="normal", help=t.get("kpi_total_loss_help", ""))
                with row4_col2:
                    st.metric(t["kpi_value_total"], value_val_str, delta=value_pct_str, delta_color="normal")
                row5_col1, row5_col2 = st.columns(2)
                with row5_col1:
                    st.metric(t["kpi_avg_pos_change"], avg_pos_change_val_str, delta=avg_pos_change_delta_str, delta_color="off")
                with row5_col2:
                    st.metric(t["kpi_lhf"], format_num(lhf_count), delta=lhf_delta_str, delta_color="off", help=t["kpi_lhf_help_sistrix"])

            st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)

            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                st.markdown("#### " + t["kpi_cluster_title"])
                cluster_net = df.groupby('Cluster')['Metric Change'].sum().reset_index()
                cluster_net = cluster_net[cluster_net['Cluster'] != "undefined"]
                if not cluster_net.empty:
                    best_cluster = cluster_net.loc[cluster_net['Metric Change'].idxmax()]
                    worst_cluster = cluster_net.loc[cluster_net['Metric Change'].idxmin()]
                    best_pct = (best_cluster['Metric Change'] / total_metric_old * 100) if total_metric_old > 0 else 0.0
                    worst_pct = (worst_cluster['Metric Change'] / total_metric_old * 100) if total_metric_old > 0 else 0.0
                    best_sign = "+" if best_cluster['Metric Change'] > 0 else ""
                    worst_sign = "+" if worst_cluster['Metric Change'] > 0 else ""
                    best_pct_sign = "+" if best_pct > 0 else ""
                    worst_pct_sign = "+" if worst_pct > 0 else ""
                    best_delta = f"{best_sign}{format_num(int(best_cluster['Metric Change']))} SV ({best_pct_sign}{format_num(best_pct, 1)}{pct_sign})"
                    worst_delta = f"{worst_sign}{format_num(int(worst_cluster['Metric Change']))} SV ({worst_pct_sign}{format_num(worst_pct, 1)}{pct_sign})"
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(t["kpi_best_cluster"], best_cluster['Cluster'], delta=best_delta)
                    with c2:
                        st.metric(t["kpi_worst_cluster"], worst_cluster['Cluster'], delta=worst_delta)
                    top_bottom = pd.concat([cluster_net.nlargest(3, 'Metric Change'), cluster_net.nsmallest(3, 'Metric Change')]).drop_duplicates().sort_values('Metric Change')
                    fig_net = px.bar(top_bottom, x='Metric Change', y='Cluster', orientation='h',
                                     color='Metric Change', color_continuous_scale=[[0.0, '#993333'], [0.5, '#dfdfdf'], [1.0, '#90c274']], height=200)
                    style_plotly_fig(fig_net)
                    fig_net.update_layout(margin=dict(l=10, r=10, t=25, b=10))
                    st.plotly_chart(fig_net, use_container_width=True)

            with viz_col2:
                st.markdown("#### " + t["kpi_top3_title"])
                if not top3_drops.empty:
                    worst_top3 = top3_drops.nlargest(5, 'Metric Loss').sort_values('Metric Loss', ascending=True)
                    fig_t3 = px.bar(worst_top3, x='Metric Loss', y='Keyword', orientation='h',
                                    color_discrete_sequence=['#2ea3f2'], height=270)
                    style_plotly_fig(fig_t3)
                    fig_t3.update_layout(margin=dict(l=10, r=10, t=25, b=10))
                    st.plotly_chart(fig_t3, use_container_width=True)
                else:
                    st.info(t["rd_t3_empty"])

            st.write("")
            if intent_skipped:
                st.info(t["intent_not_analyzed_msg"])
            else:
                viz_col3, viz_col4 = st.columns(2)
                with viz_col3:
                    st.markdown("#### " + t["kpi_intent_title"])
                    intent_df = df.assign(Intent=df['Search Intent'].str.split(', ')).explode('Intent')
                    intent_counts = intent_df['Intent'].value_counts().reset_index()
                    intent_counts.columns = ['Search Intent', 'Count']
                    color_map = {"DO (Transactional)": "#1f86cf", "KNOW": "#2ea3f2",
                                 "regional:CITY": "#0f5a90", "regional:COUNTRY": "#535353", "undefined": "#dfdfdf"}
                    fig_pie = px.pie(intent_counts, values='Count', names='Search Intent',
                                     color='Search Intent', color_discrete_map=color_map, hole=0.4, height=280)
                    style_plotly_fig(fig_pie)
                    fig_pie.update_layout(margin=dict(l=10, r=10, t=25, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True)
                with viz_col4:
                    st.markdown("#### Details")
                    intent_pct = intent_df['Intent'].value_counts(normalize=True).reset_index()
                    intent_pct.columns = ['Search Intent', 'Percentage']
                    intent_pct['Percentage'] = intent_pct['Percentage'] * 100
                    intent_summary = pd.merge(intent_counts, intent_pct, on='Search Intent')
                    col_intent = 'Search Intent' if lang == 'EN' else 'Suchintent'
                    col_count = 'Keywords (Count)' if lang == 'EN' else 'Keywords (Anzahl)'
                    col_share = 'Share (%)' if lang == 'EN' else 'Anteil (%)'
                    intent_summary.columns = [col_intent, col_count, col_share]
                    formatted_intent_summary = intent_summary.copy()
                    formatted_intent_summary[col_count] = formatted_intent_summary[col_count].apply(lambda x: format_num(x))
                    formatted_intent_summary[col_share] = formatted_intent_summary[col_share].apply(lambda x: f"{format_num(x, 1)}{pct_sign}")
                    st.write("")
                    st.dataframe(formatted_intent_summary, use_container_width=True, hide_index=True)


        with tab_d:
            st.subheader(t["dir_sub"])
            if not top10_drops.empty:
                dir_vol = top10_drops.groupby('Directory').agg(
                    Metric_Loss=('Metric Loss', 'sum'),
                    Value_Loss=('Lost Value €', 'sum')
                ).reset_index()
                dir_vol = dir_vol[dir_vol['Metric_Loss'] > 0].sort_values('Metric_Loss', ascending=False).head(15)
                
                # Treemap Chart
                fig_tree = px.treemap(dir_vol, path=['Directory'], values='Metric_Loss',
                                      title=t["dir_chart_title_tree"],
                                      labels={'Directory': t["dir_chart_label_d"], 'Metric_Loss': t["dir_chart_label_t_sv"]},
                                      color='Metric_Loss', color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#2ea3f2']])
                style_plotly_fig(fig_tree)
                st.plotly_chart(fig_tree, use_container_width=True)

                fig_dir = px.bar(dir_vol, x='Directory', y='Metric_Loss',
                                 title=t["dir_chart_title_sv"],
                                 labels={'Directory': t["dir_chart_label_d"], 'Metric_Loss': t["dir_chart_label_t_sv"]},
                                 color='Metric_Loss', color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#2ea3f2']])
                style_plotly_fig(fig_dir)
                st.plotly_chart(fig_dir, use_container_width=True)
            else:
                st.info(t["dir_empty"])

        with tab1:
            st.subheader(t["cl_sub"])
            st.markdown(t["cl_desc"])
            if not losers.empty:
                cluster_vol = losers.groupby('Cluster').agg(
                    Metric_Loss=('Metric Loss', 'sum'),
                    Value_Loss=('Lost Value €', 'sum'),
                    Keyword_Count=('Keyword', 'count')
                ).reset_index()
                cluster_vol = cluster_vol[cluster_vol['Metric_Loss'] > 0].sort_values('Metric_Loss', ascending=False)
                fig_cluster = px.bar(cluster_vol, x='Cluster', y='Metric_Loss',
                                     title=t["cl_chart_title_sv"],
                                     labels={'Cluster': t["cl_chart_label_c"], 'Metric_Loss': t["cl_chart_label_t_sv"]},
                                     color='Metric_Loss', color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#2ea3f2']])
                style_plotly_fig(fig_cluster)
                st.plotly_chart(fig_cluster, use_container_width=True)
                st.markdown(t["cl_detail"])
                opts = [c for c in cluster_vol['Cluster'].tolist() if c != "undefined"] + (["undefined"] if "undefined" in cluster_vol['Cluster'].tolist() else [])
                selected_clusters = st.multiselect(t["cl_select"], options=opts)
                if selected_clusters:
                    cluster_df = losers[losers['Cluster'].isin(selected_clusters)]
                    st.write(f"{t['cl_sum_sv']} **{format_num(int(cluster_df['Search Volume'].sum()))}**")
                    display_styled_dataframe(cluster_df[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume')
            else:
                st.info(t["cl_empty"])

        with tab2:
            st.subheader(t["rd_sub"])
            kw_filter = st.text_input(t["rd_filter"]).strip().lower()
            f_top3 = top3_drops[top3_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top3_drops
            f_top10 = top10_drops[top10_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top10_drops
            f_page2 = page2_drops[page2_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else page2_drops
            f_total = total_loss[total_loss['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else total_loss

            st.markdown("<div id='top3-drops'></div>", unsafe_allow_html=True)
            st.markdown(t["rd_t3_title"])
            if not f_top3.empty:
                t_vol = format_num(int(f_top3['Search Volume'].sum()))
                t_traffic = format_num(int(f_top3['Traffic Loss'].sum()))
                t_val = f"{format_num(f_top3['Lost Value €'].sum(), 2)} €" if lang == "DE" else f"€{format_num(f_top3['Lost Value €'].sum(), 2)}"
                t_count = format_num(len(f_top3))
                desc_text = t["rd_t3_desc"].format(count=t_count, vol=t_vol, traffic=t_traffic, val=t_val)
                st.markdown(desc_text)
                st.write(f"{t['rd_sum_vol']} **{format_num(int(f_top3['Search Volume'].sum()))}**")
                display_styled_dataframe(f_top3[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume')
            else:
                st.info(t["rd_t3_empty"])

            st.markdown("<div id='top10-drops'></div>", unsafe_allow_html=True)
            st.markdown(t["rd_t10_title"])
            if not f_top10.empty:
                t_vol = format_num(int(f_top10['Search Volume'].sum()))
                t_traffic = format_num(int(f_top10['Traffic Loss'].sum()))
                t_val = f"{format_num(f_top10['Lost Value €'].sum(), 2)} €" if lang == "DE" else f"€{format_num(f_top10['Lost Value €'].sum(), 2)}"
                t_count = format_num(len(f_top10))
                desc_text = t["rd_t10_desc"].format(count=t_count, vol=t_vol, traffic=t_traffic, val=t_val)
                st.markdown(desc_text)
                st.write(f"{t['rd_sum_vol']} **{format_num(int(f_top10['Search Volume'].sum()))}**")
                display_styled_dataframe(f_top10[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume')
            else:
                st.info(t["rd_t10_empty"])

            st.markdown(t["rd_p2_title"])
            if not f_page2.empty:
                t_vol = format_num(int(f_page2['Search Volume'].sum()))
                t_traffic = format_num(int(f_page2['Traffic Loss'].sum()))
                t_val = f"{format_num(f_page2['Lost Value €'].sum(), 2)} €" if lang == "DE" else f"€{format_num(f_page2['Lost Value €'].sum(), 2)}"
                t_count = format_num(len(f_page2))
                desc_text = t["rd_p2_desc"].format(count=t_count, vol=t_vol, traffic=t_traffic, val=t_val)
                st.markdown(desc_text)
                st.write(f"{t['rd_sum_vol']} **{format_num(int(f_page2['Search Volume'].sum()))}**")
                display_styled_dataframe(f_page2[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume')
            else:
                st.info(t["rd_p2_empty"])

            st.markdown(t["rd_100_title"])
            if not f_total.empty:
                t_vol = format_num(int(f_total['Search Volume'].sum()))
                t_traffic = format_num(int(f_total['Traffic Loss'].sum()))
                t_val = f"{format_num(f_total['Lost Value €'].sum(), 2)} €" if lang == "DE" else f"€{format_num(f_total['Lost Value €'].sum(), 2)}"
                t_count = format_num(len(f_total))
                desc_text = t["rd_100_desc"].format(count=t_count, vol=t_vol, traffic=t_traffic, val=t_val)
                st.markdown(desc_text)
                st.write(f"{t['rd_sum_vol']} **{format_num(int(f_total['Search Volume'].sum()))}**")
                display_styled_dataframe(f_total[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume')
            else:
                st.info(t["rd_100_empty"])

        with tab3:
            st.subheader(t["lhf_sub"], anchor="low-hanging-fruits")
            st.markdown(t["lhf_desc_sistrix"])
            if not low_hanging.empty:
                lhf_df = low_hanging.copy()
                lhf_df[['Potential Score', 'Difficulty']] = lhf_df.apply(calculate_lhf_sistrix, axis=1)
                cols_to_show = ['Keyword', 'Difficulty', 'Potential Score', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory']
                styler = lhf_df[cols_to_show].sort_values('Search Volume', ascending=False).style
                format_dict = {}
                format_dict['Potential Score'] = lambda x: f"{x:.1f}"
                for c in ['Search Volume']:
                    format_dict[c] = lambda x: format_num(x) if pd.notnull(x) else ""
                for c in ['Position#1', 'Position#2']:
                    format_dict[c] = lambda x: "-" if pd.notnull(x) and x == 101 else (format_num(x, 2) if pd.notnull(x) else "")
                loss_cols = [c for c in ['Traffic Loss', 'Lost Value €'] if c in lhf_df.columns]
                if loss_cols:
                    styler = styler.map(lambda x: 'color: #993333; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=loss_cols)
                    for c in loss_cols:
                        if c == 'Lost Value €':
                            if lang == "EN":
                                format_dict[c] = lambda x: f"▼ -€{format_num(x, 2)}" if pd.notnull(x) and x > 0 else ("€0.00" if pd.notnull(x) else "")
                            else:
                                format_dict[c] = lambda x: f"▼ -{format_num(x, 2)} €" if pd.notnull(x) and x > 0 else ("0,00 €" if pd.notnull(x) else "")
                        else:
                            format_dict[c] = lambda x: f"▼ -{format_num(x)}" if pd.notnull(x) and x > 0 else ("0" if pd.notnull(x) else "")
                styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else ('color: #993333; font-weight: bold;' if pd.notnull(x) and x < 0 else ''), subset=['Position Change'])
                format_dict['Position Change'] = lambda x: f"▲ +{format_num(abs(x), 2)}" if pd.notnull(x) and x > 0 else (f"▼ -{format_num(abs(x), 2)}" if pd.notnull(x) and x < 0 else format_num(0.0, 2))
                styler = styler.format(format_dict)
                st.dataframe(
                    styler,
                    column_config={
                        "Potential Score": st.column_config.ProgressColumn(
                            "Potential Score",
                            help=t.get("lhf_pot_help", "Calculated potential (0-10)"),
                            format="%.1f",
                            min_value=0.0,
                            max_value=10.0,
                        ),
                        "Difficulty": st.column_config.TextColumn(
                            t.get("lhf_diff_label", "Difficulty"),
                            help=t.get("lhf_diff_help", "Estimated difficulty")
                        )
                    },
                    use_container_width=True
                )
            else:
                st.info(t["lhf_empty"])

        with tab4:
            st.subheader(t["win_sub_sistrix"])
            if not winners.empty:
                fig_win = px.scatter(winners, x="Search Volume", y="Position#2",
                                     size="Search Volume", color="Directory",
                                     hover_name="Keyword", title=t["win_chart_title"],
                                     labels={'Position#2': t["win_chart_label_pos"]},
                                     color_discrete_sequence=['#2ea3f2', '#1f86cf', '#0f5a90', '#8c96c6', '#535353', '#797979'])
                fig_win.update_yaxes(autorange="reversed")
                style_plotly_fig(fig_win)
                st.plotly_chart(fig_win, use_container_width=True)
                display_styled_dataframe(winners[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Gain', 'Directory']], sort_col='Search Volume')
            else:
                st.info(t["win_empty"])

        with tab5:
            st.subheader(t["ad_sub"])
            f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
            all_clusters_sis = sorted([c for c in df['Cluster'].dropna().unique() if c != 'undefined']) + ['undefined']
            with f_col1:
                sel_clusters = st.multiselect(t["ad_filter_cluster"], options=all_clusters_sis)
            with f_col2:
                is_disabled = intent_skipped
                all_intents_sis = set()
                for val in df['Search Intent'].dropna().unique():
                    for piece in val.split(', '):
                        all_intents_sis.add(piece)
                sel_intents = st.multiselect(t["ad_filter_intent"], options=sorted(list(all_intents_sis)), disabled=is_disabled)
            all_changes_sis = sorted(df['Change'].unique().tolist())
            with f_col3:
                sel_changes = st.multiselect(t["ad_filter_change"], options=all_changes_sis)
            all_dirs = sorted(df['Directory'].unique().tolist())
            with f_col4:
                sel_dirs = st.multiselect(t["ad_filter_dir"], options=all_dirs)
            with f_col5:
                search_kw = st.text_input(t["ad_filter_kw"]).strip().lower()

            all_cols_sis = ['Cluster', 'Search Intent', 'Directory', 'Keyword', 'Change', 'Position Change',
                            'Traffic Change', 'Lost Value €', 'Position#1', 'Position#2', 'Search Volume',
                            'Traffic#1', 'Traffic#2', 'URL']
            all_cols_sis = [c for c in all_cols_sis if c in df.columns]

            filtered_df = df.copy()
            if sel_clusters:
                filtered_df = filtered_df[filtered_df['Cluster'].isin(sel_clusters)]
            if sel_intents:
                filtered_df = filtered_df[filtered_df['Search Intent'].apply(lambda x: any(c in x for c in sel_intents))]
            if sel_changes:
                filtered_df = filtered_df[filtered_df['Change'].isin(sel_changes)]
            if sel_dirs:
                filtered_df = filtered_df[filtered_df['Directory'].isin(sel_dirs)]
            if search_kw:
                filtered_df = filtered_df[filtered_df['Keyword'].astype(str).str.lower().str.contains(search_kw, na=False)]
            display_styled_dataframe(filtered_df[all_cols_sis], sort_col='Position Change', ascending=True)

else:
    info_key = f"info_upload_{mode_key}"
    st.info(t.get(info_key, "Please upload a file and click 'Analyze'."))

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)

version = "v2.0.0"
try:
    commit_count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    if commit_count and commit_hash:
        version = f"v2.0.{commit_count} ({commit_hash})"
except Exception:
    pass

footer_text = f"{t['footer']} | <span style='opacity: 0.8;'>Version {version}</span>"
st.markdown(f"<div style='text-align: center; color: #797979; font-size: 0.9em;'>{footer_text}</div>", unsafe_allow_html=True)

# Clear custom loader state at the end of the run
if st.session_state.get("show_custom_loader"):
    st.session_state["show_custom_loader"] = False
    loading_placeholder.empty()

# Smooth scroll to target if set
if st.session_state.get("scroll_target"):
    target_id = st.session_state["scroll_target"]
    components.html(
        f"""<script>
        setTimeout(function() {{
            var el = window.parent.document.getElementById("{target_id}");
            if (el) {{
                el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        }}, 300);
        </script>""",
        height=0
    )
    st.session_state["scroll_target"] = None

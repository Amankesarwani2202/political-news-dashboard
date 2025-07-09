import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import fetch_articles, cluster_themes, analyze_bias, RSS_FEEDS

st.set_page_config(layout="wide", page_title="🇮🇳 Political News Analyzer")

st.title("🧠 Ground.News-style Political Bias Dashboard (India)")
st.markdown("Analyze political media coverage across 10 major Indian news outlets.")

# --- Load full data first
days = st.sidebar.slider("Days to include", 1, 14, 7)

with st.spinner("Scraping articles..."):
    df_full = fetch_articles(last_days=days)

# Fix sidebar crash when df is empty
all_sources = list(df_full['source'].unique()) if not df_full.empty else list(RSS_FEEDS.keys())
selected_sources = st.sidebar.multiselect("Select sources", all_sources, default=all_sources)
selected_bias = st.sidebar.multiselect("Select bias", ['Left', 'Left-Center', 'Center', 'Center-Right', 'Right'], default=None)

# Filter
df = df_full.copy()
if selected_sources:
    df = df[df['source'].isin(selected_sources)]
if selected_bias:
    df = df[df['bias'].isin(selected_bias)]

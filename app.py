# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import fetch_articles, cluster_themes, analyze_bias

st.set_page_config(layout="wide", page_title="🇮🇳 Political News Analyzer")

st.title("🧠 Ground.News-style Political Bias Dashboard (India)")
st.markdown("Analyze political media coverage across 10 major Indian news outlets.")

# Sidebar controls
days = st.sidebar.slider("Days to include", 1, 14, 7)
selected_sources = st.sidebar.multiselect("Select sources", list(fetch_articles(0)['source'].unique()), default=None)
selected_bias = st.sidebar.multiselect("Select bias", ['Left', 'Left-Center', 'Center', 'Center-Right', 'Right'], default=None)

# Fetch and filter
with st.spinner("Scraping articles..."):
    df = fetch_articles(last_days=days)
    df, model = cluster_themes(df)

    if selected_sources:
        df = df[df['source'].isin(selected_sources)]
    if selected_bias:
        df = df[df['bias'].isin(selected_bias)]

if df.empty:
    st.warning("No political articles found.")
    st.stop()

st.success(f"✅ {len(df)} political articles from last {days} days")

# Bias Analysis
summary, percent, blindspots = analyze_bias(df)

# Main layout
col1, col2 = st.columns([2, 1])

# === Bias Distribution (Bar) ===
with col1:
    st.subheader("🧱 Bias % per Topic (Stacked Bar)")
    fig, ax = plt.subplots(figsize=(10, 6))
    percent.plot(kind='bar', stacked=True, ax=ax, colormap='coolwarm')
    ax.set_ylabel("Coverage %")
    ax.set_xlabel("Topic")
    ax.set_title("Media Bias Distribution by Topic")
    st.pyplot(fig)

# === Pie for Selected Topic ===
with col2:
    selected_topic = st.selectbox("📌 Select topic for pie view", df['topic_name'].unique())
    st.subheader("🎯 Bias breakdown for selected topic")
    pie_data = percent.loc[selected_topic]
    fig2, ax2 = plt.subplots()
    pie_data.plot(kind='pie', autopct='%1.1f%%', ax=ax2, startangle=140)
    ax2.set_ylabel("")
    st.pyplot(fig2)

# === Source Chart ===
st.subheader("📰 Article Count by Source")
st.bar_chart(df['source'].value_counts())

# === Blind Spot Detector ===
st.subheader("🚨 Blind Spot Topics")
if blindspots:
    st.dataframe(pd.DataFrame(blindspots))
else:
    st.info("No blind spots detected.")

# === Raw Articles ===
st.subheader("🗞️ Raw Articles List")
st.dataframe(df[['timestamp', 'title', 'source', 'bias', 'topic_name']])

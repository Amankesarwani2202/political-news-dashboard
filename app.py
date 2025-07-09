import streamlit as st
from utils import fetch_articles, cluster_themes, analyze_bias
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="🧠 Political Bias Explorer")

st.markdown("<h2 style='text-align: center;'>🧠 Political News Bias Dashboard (India)</h2>", unsafe_allow_html=True)

# Date slider
days = st.sidebar.slider("📅 Days to look back", 1, 7, 3)

with st.spinner("🔍 Fetching articles..."):
    df = fetch_articles(days)
    if df.empty:
        st.warning("No political news found.")
        st.stop()
    df, model = cluster_themes(df)
    summary, percent, blindspots = analyze_bias(df)

# 📊 Compact Topic Cards
st.markdown("### 📰 Topics with Bias Distribution")
for topic in df['topic_name'].unique():
    tdf = df[df['topic_name'] == topic]
    bdist = tdf['bias'].value_counts(normalize=True).mul(100).round(1).to_dict()
    total_articles = len(tdf)

    # Layout
    with st.expander(f"📌 {topic} ({total_articles} articles)"):
        st.markdown(f"**Bias Distribution:** " +
                    ", ".join([f"{b}: {p}%" for b, p in bdist.items()]))

        if topic in [b['topic'] for b in blindspots]:
            st.markdown("🚨 **Blind Spot Detected!**")

        for _, row in tdf.iterrows():
            st.markdown(f"- [{row['title']}]({row['link']}) — *{row['source']}*")

# 📈 Overall Bias Chart
st.markdown("### 📊 Overall Bias Percentage by Topic")
fig, ax = plt.subplots(figsize=(10, 5))
percent.plot(kind="barh", stacked=True, ax=ax, colormap="coolwarm")
ax.set_xlabel("Coverage %")
st.pyplot(fig)

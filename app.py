import streamlit as st
from utils import fetch_articles, cluster_themes, analyze_bias
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="🧠 Political Bias Explorer")

st.markdown("<h2 style='text-align: center;'>🧠 Political News Bias Dashboard (India)</h2>", unsafe_allow_html=True)

# Sidebar config
days = st.sidebar.slider("📅 Days to look back", 1, 7, 3)

# Fetch & process
with st.spinner("🔍 Fetching articles..."):
    df = fetch_articles(days)
    if df.empty:
        st.warning("No political news found.")
        st.stop()
    df, model = cluster_themes(df)
    summary, percent, blindspots = analyze_bias(df)

# Topic grid view
st.markdown("### 📰 Topics with Bias Distribution")
topics = df['topic_name'].unique()
num_cols = 2
for i in range(0, len(topics), num_cols):
    cols = st.columns(num_cols)
    for j in range(num_cols):
        if i + j < len(topics):
            topic = topics[i + j]
            tdf = df[df['topic_name'] == topic]
            bdist = tdf['bias'].value_counts(normalize=True).mul(100).round(1).to_dict()
            total = len(tdf)
            with cols[j]:
                st.markdown(f"#### 📌 {topic} ({total} articles)")
                st.markdown(", ".join([f"{b}: {p}%" for b, p in bdist.items()]))
                for _, row in tdf.head(5).iterrows():
                    st.markdown(f"- [{row['title']}]({row['link']}) — *{row['source']}*")
                st.markdown("---")

# Bias summary chart
st.markdown("### 📊 Overall Bias Percentage by Topic")
fig, ax = plt.subplots(figsize=(10, 5))
percent.plot(kind="barh", stacked=True, ax=ax, colormap="coolwarm")
ax.set_xlabel("Coverage %")
st.pyplot(fig)

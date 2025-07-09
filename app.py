import streamlit as st
from utils import fetch_articles, cluster_themes, analyze_bias
from visual import render_bias_plot

st.set_page_config(layout="wide", page_title="🧠 Political Bias Dashboard")

st.markdown("<h2 style='text-align: center;'>🧠 Political News Bias Dashboard (India)</h2>", unsafe_allow_html=True)

days = st.sidebar.radio("📅 Days to look back", [1, 3, 5, 7], index=1)

with st.spinner("Fetching articles..."):
    df = fetch_articles(days)
    if df.empty:
        st.warning("No articles found.")
        st.stop()

    df, model = cluster_themes(df)
    summary, percent, blindspots = analyze_bias(df)

# Topics grid
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

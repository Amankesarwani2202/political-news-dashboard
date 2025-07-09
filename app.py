import streamlit as st
import pandas as pd
from visual import render_bias_plot

st.set_page_config(layout="wide", page_title="🧠 Political Bias Dashboard")

# === Load your processed article data ===
@st.cache_data
def load_articles(days=7):
    df = pd.read_csv("final_articles.csv")  # Your cleaned + labeled article dataset
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['published'] = pd.to_datetime(df['published'], errors='coerce')
    df = df[df['timestamp'] >= pd.Timestamp.now() - pd.Timedelta(days=days)]
    return df

# === UI Sidebar ===
st.sidebar.header("📅 Days to look back")
days = st.sidebar.radio("Select:", [1, 3, 7], index=2)
df = load_articles(days)

if df.empty:
    st.warning("No articles found for the selected time window.")
    st.stop()

# === Topic summaries ===
st.title("🧠 Political News Bias Dashboard (India)")
topics = df['clean_topic'].unique()

for topic in topics:
    topic_df = df[df['clean_topic'] == topic]
    if topic_df.empty: continue

    bias_counts = topic_df['bias'].value_counts(normalize=True).mul(100).round(1).to_dict()
    total_sources = len(topic_df)
    headline = topic_df.iloc[0]['title']  # First headline from topic

    with st.expander(f"📌 {topic}"):
        # === Bias bar inline ===
        st.markdown("**Bias Distribution:** " + ", ".join(f"{b}: {v}%" for b, v in bias_counts.items()))
        st.markdown(f"**Top Headline:** {headline}")
        st.markdown(f"**Articles: {total_sources}**")

        for _, row in topic_df.iterrows():
            st.markdown(
                f"""
                - 📰 [{row['title']}]({row['link']})  
                  <span style="color:gray">({row['source']}, {row['bias']})</span>
                """, unsafe_allow_html=True)

# === Optional: Global Bias Plot ===
st.divider()
st.subheader("📊 Overall Bias Chart")
render_bias_plot(df)

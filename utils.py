import pandas as pd
import feedparser
from datetime import datetime, timedelta
from bertopic import BERTopic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

RSS_FEEDS = {
    "Hindustan Times": ("https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "Left-Center"),
    "Times of India": ("https://timesofindia.indiatimes.com/rssfeeds/1221656.cms", "Center"),
    "The Wire": ("https://thewire.in/politics/feed", "Left"),
    "NDTV": ("https://feeds.feedburner.com/ndtvnews-national", "Left-Center"),
    "India Today": ("https://www.indiatoday.in/rss/1206578", "Center"),
    "The Hindu": ("https://www.thehindu.com/news/national/feeder/default.rss", "Center-Left"),
    "OpIndia": ("https://www.opindia.com/feed/", "Right"),
    "Deccan Herald": ("https://www.deccanherald.com/rss-feeds", "Center"),
    "Times Now": ("https://www.timesnownews.com/rssfeeds/288956", "Right-Center"),
    "Indian Express": ("https://indianexpress.com/section/india/feed/", "Center")
}

def fetch_articles(last_days=3):
    articles = []
    cutoff = datetime.now() - timedelta(days=last_days)
    for source, (url, bias) in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = getattr(entry, 'title', '')
            link = getattr(entry, 'link', '')
            summary = getattr(entry, 'summary', title)
            published = getattr(entry, 'published', None)
            if not title or not link or not published:
                continue
            try:
                pub_dt = datetime(*entry.published_parsed[:6])
                if pub_dt < cutoff:
                    continue
            except:
                continue
            articles.append({
                'title': title,
                'summary': summary,
                'link': link,
                'published': pub_dt,
                'source': source,
                'bias': bias
            })
    return pd.DataFrame(articles)

def cluster_themes(df):
    texts = df['summary'].tolist()
    if len(texts) < 10:
        df['topic_id'] = 0
        df['topic_name'] = "Other"
        return df, None
    try:
        model = BERTopic(language="english", embedding_model=SentenceTransformer("all-MiniLM-L6-v2"), min_topic_size=3)
        topics, _ = model.fit_transform(texts)
        df['topic_id'] = topics
        df['topic_name'] = df['topic_id'].apply(lambda t: model.get_topic(t)[0][0] if t != -1 else "Other")
        if df['topic_id'].nunique() <= 1:
            raise ValueError("Too many -1 topics")
        return df, model
    except:
        tfidf = TfidfVectorizer(stop_words="english")
        X = tfidf.fit_transform(texts)
        kmeans = KMeans(n_clusters=5, random_state=42)
        df['topic_id'] = kmeans.fit_predict(X)
        df['topic_name'] = df['topic_id'].apply(lambda x: f"Cluster {x}")
        return df, None

def analyze_bias(df):
    summary = df.groupby(['topic_name', 'bias']).size().unstack(fill_value=0)
    percent = summary.div(summary.sum(axis=1), axis=0) * 100
    blindspots = []
    for topic, row in summary.iterrows():
        total = row.sum()
        mx = row.max()
        if (row > 0).sum() == 1 or mx / total > 0.7:
            blindspots.append({'topic': topic, 'dominant_bias': row.idxmax(), 'percent': round(mx / total * 100, 2)})
    return summary, percent, blindspots

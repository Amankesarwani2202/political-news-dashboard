import pandas as pd
import feedparser
from datetime import datetime, timedelta
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# RSS Sources
RSS_FEEDS = {
    "Hindustan Times": ("https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "Left-Center"),
    "Times of India": ("https://timesofindia.indiatimes.com/rssfeeds/1221656.cms", "Center"),
    "The Wire": ("https://thewire.in/politics/feed", "Left"),
    "NDTV": ("https://feeds.feedburner.com/ndtvnews-india-news", "Center-Left"),
    "India Today": ("https://www.indiatoday.in/rss/home", "Center"),
    "The Hindu": ("https://www.thehindu.com/news/national/feeder/default.rss", "Left-Center"),
    "OpIndia": ("https://www.opindia.com/feed/", "Right"),
    "The Print": ("https://theprint.in/feed/", "Center"),
    "Deccan Herald": ("https://www.deccanherald.com/rss-feed/", "Center-Left"),
    "Economic Times": ("https://economictimes.indiatimes.com/rssfeedsdefault.cms", "Center-Right")
}

def fetch_articles(last_days=3):
    articles = []
    cutoff = datetime.now() - timedelta(days=last_days)
    for source, (url, bias) in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = getattr(entry, 'title', '')
            link = getattr(entry, 'link', '')
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
                'link': link,
                'published': pub_dt,
                'source': source,
                'bias': bias
            })
    return pd.DataFrame(articles)

def cluster_themes(df):
    titles = df['title'].tolist()
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    topic_model = BERTopic(language="english", embedding_model=embedding_model, min_topic_size=4)
    topics, _ = topic_model.fit_transform(titles)
    df['topic_id'] = topics
    df['topic_name'] = df['topic_id'].apply(
        lambda t: topic_model.get_topic(t)[0][0] if t != -1 else "Other"
    )
    return df, topic_model

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

POLITICAL_KEYWORDS = ['modi','bjp','congress','election','parliament','minister','politic','vote','neet','russia','china']

def fetch_articles(last_days=7):
    rows = []
    cutoff = datetime.now() - timedelta(days=last_days)
    for src, (url, bias) in RSS_FEEDS.items():
        for e in feedparser.parse(url).entries:
            title, link = getattr(e, 'title', ''), getattr(e, 'link', '')
            pub = getattr(e, 'published_parsed', None)
            ts = datetime(*pub[:6]) if pub else datetime.now()
            if not title or not link or ts < cutoff:
                continue
            if not any(k in title.lower() for k in POLITICAL_KEYWORDS):
                continue
            rows.append({'title': title, 'link': link, 'timestamp': ts, 'source': src, 'bias': bias})
    return pd.DataFrame(rows)

def cluster_themes(df):
    titles = df['title'].tolist()
    try:
        model = BERTopic(language="english", verbose=False)
        topics, _ = model.fit_transform(titles)
        df['topic_id'] = topics
        df['topic_name'] = df['topic_id'].apply(
            lambda t: model.get_topic(t)[0][0] if t != -1 else "Other"
        )
        return df, model
    except:
        tfidf = TfidfVectorizer(stop_words='english')
        X = tfidf.fit_transform(titles)
        km = KMeans(n_clusters=min(5, len(df)), random_state=42)
        df['topic_id'] = km.fit_predict(X)
        df['topic_name'] = df['topic_id'].astype(str)
        return df, None

def analyze_bias(df):
    summary = df.groupby(['topic_name','bias']).size().unstack(fill_value=0)
    percent = summary.div(summary.sum(axis=1), axis=0)*100
    blindspots = []
    for topic, row in summary.iterrows():
        total = row.sum()
        if (row > 0).sum() == 1 or row.max() / total > 0.7:
            blindspots.append({
                "topic": topic,
                "dominant_bias": row.idxmax(),
                "coverage_pct": round(row.max() / total * 100, 2)
            })
    return summary, percent, blindspots

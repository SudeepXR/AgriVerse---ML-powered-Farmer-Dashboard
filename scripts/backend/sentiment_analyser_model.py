import requests
import numpy as np
import torch
import feedparser
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datetime import datetime, timedelta
from html import unescape
from functools import lru_cache

# =====================================================
# CONFIG
# =====================================================
MODEL_NAME = "yiyanghkust/finbert-tone"
GNEWS_API_KEY = "1a704e2d75662c77ac29f62ad1626a2c"

LOOKBACK_DAYS = 60

FACTUAL_WEIGHT = 0.4   # GNews
OPINION_WEIGHT = 0.6   # RSS + Blogs
KARNATAKA_BONUS = 0.4

MARKET_KEYWORDS = [
    "price", "market", "mandi", "procurement", "msp",
    "export", "import", "arrival", "supply", "demand"
]

KARNATAKA_KEYWORDS = [
    "karnataka", "bengaluru", "bangalore",
    "mysuru", "hubli", "dharwad",
    "belagavi", "ballari", "kalaburagi",
    "mandya", "raichur", "hassan",
    "shivamogga", "tumakuru", "udupi",
    "dakshina kannada", "chikkamagaluru"
]

# =====================================================
# LOAD MODEL ONCE
# =====================================================
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

# =====================================================
# UTILITIES
# =====================================================
def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(text).strip()

def is_karnataka_related(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in KARNATAKA_KEYWORDS)

def bert_sentiment(text):
    if not isinstance(text, str) or len(text) < 25:
        return None
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        probs = torch.softmax(model(**inputs).logits, dim=1)[0].numpy()
    return float(probs[2] - probs[0])  # range [-1, +1]

def relevance_weight(text, crop):
    text = text.lower()
    if crop not in text:
        return 0.0

    w = 1.0
    if any(k in text for k in MARKET_KEYWORDS):
        w += 0.5
    if any(k in text for k in ["farmer", "harvest", "yield", "production"]):
        w += 0.3
    if is_karnataka_related(text):
        w += KARNATAKA_BONUS
    return w

def weighted_avg(items):
    if not items:
        return 0.0
    num = sum(s * w for s, w in items)
    den = sum(w for _, w in items)
    return num / den if den else 0.0

# =====================================================
# NEWS FETCHERS
# =====================================================
@lru_cache(maxsize=64)
def fetch_gnews(crop):
    start = (datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    end = datetime.utcnow().strftime("%Y-%m-%d")

    params = {
        "q": f"{crop} Karnataka agriculture market mandi",
        "from": start,
        "to": end,
        "lang": "en",
        "country": "in",
        "max": 100,
        "apikey": GNEWS_API_KEY
    }

    r = requests.get("https://gnews.io/api/v4/search", params=params, timeout=10)
    articles = r.json().get("articles", [])

    items, texts = [], []
    for a in articles:
        text = clean_text(f"{a.get('title','')} {a.get('description','')}")
        if not is_karnataka_related(text):
            continue

        s = bert_sentiment(text)
        if s is None:
            continue

        w = relevance_weight(text, crop)
        if w > 0:
            items.append((s, w))
            texts.append(("GNews", text))

    return items, texts

@lru_cache(maxsize=64)
def fetch_google_rss(crop):
    url = (
        f"https://news.google.com/rss/search?"
        f"q={crop}+karnataka+price+market&hl=en-IN&gl=IN&ceid=IN:en"
    )
    feed = feedparser.parse(url)

    items, texts = [], []
    for e in feed.entries:
        text = clean_text(e.title + " " + e.get("summary", ""))

        if not is_karnataka_related(text):
            continue

        s = bert_sentiment(text)
        if s is None:
            continue

        w = relevance_weight(text, crop)
        if w > 0:
            items.append((s, w))
            texts.append(("Google News RSS", text))

    return items, texts

@lru_cache(maxsize=64)
def fetch_blogs(crop):
    url = (
        f"https://news.google.com/rss/search?"
        f"q={crop}+karnataka+production+yield+market&hl=en-IN&gl=IN&ceid=IN:en"
    )
    feed = feedparser.parse(url)

    items, texts = [], []
    for e in feed.entries:
        text = clean_text(e.title + " " + e.get("summary", ""))

        if not is_karnataka_related(text):
            continue

        s = bert_sentiment(text)
        if s is None:
            continue

        w = relevance_weight(text, crop)
        if w > 0:
            items.append((s, w))
            texts.append(("Commodity Blog", text))

    return items, texts

# =====================================================
# HEADLINES
# =====================================================
def extract_top_headlines(all_texts, crop, top_n=2):
    scored = []
    for source, text in all_texts:
        for s in re.split(r'(?<=[.!?])\s+', text):
            s_low = s.lower()
            if (
                crop in s_low
                and any(k in s_low for k in MARKET_KEYWORDS)
                and is_karnataka_related(s_low)
                and len(s) > 40
            ):
                score = bert_sentiment(s)
                if score is not None:
                    scored.append((abs(score), score, source, s.strip()))
    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_n]

# =====================================================
# SIGNAL LOGIC
# =====================================================
def trade_signal(score):
    if score > 0.20:
        return "BUY"
    elif score < -0.20:
        return "SELL"
    else:
        return "HOLD"

#  NUMERIC PRICE IMPACT (USED BY FRONTEND)
def price_impact(score):
    if score > 0.4:
        return 0.035      # +3.5%
    elif score > 0.15:
        return 0.015      # +1.5%
    elif score > -0.15:
        return -0.005     # -0.5%
    elif score > -0.4:
        return -0.02      # -2%
    else:
        return -0.04      # -4%

# =====================================================
# MAIN API FUNCTION
# =====================================================
def analyze_crop(crop: str):
    crop = crop.lower().strip()

    gnews_items, gnews_texts = fetch_gnews(crop)
    rss_items, rss_texts = fetch_google_rss(crop)
    blog_items, blog_texts = fetch_blogs(crop)

    factual_sentiment = weighted_avg(gnews_items)
    opinion_sentiment = weighted_avg(rss_items + blog_items)

    current_sentiment = (
        FACTUAL_WEIGHT * factual_sentiment +
        OPINION_WEIGHT * opinion_sentiment
    )

    forecast_sentiment = float(np.clip(current_sentiment * 0.9, -1, 1))
    signal = trade_signal(forecast_sentiment)
    impact = price_impact(forecast_sentiment)

    total_weight = (
        sum(w for _, w in gnews_items) +
        sum(w for _, w in rss_items) +
        sum(w for _, w in blog_items)
    ) or 1

    contributions = {
        "gnews": round(sum(w for _, w in gnews_items) / total_weight * 100, 1),
        "rss": round(sum(w for _, w in rss_items) / total_weight * 100, 1),
        "blogs": round(sum(w for _, w in blog_items) / total_weight * 100, 1),
    }

    top_headlines = extract_top_headlines(
        gnews_texts + rss_texts + blog_texts, crop
    )

    return {
        "crop": crop.upper(),
        "current_sentiment": round(current_sentiment, 3),
        "forecast_sentiment": round(forecast_sentiment, 3),

        #  USED BY FRONTEND
        "signal": signal,
        "price_impact": impact,           # numeric
        "price_impact_pct": impact * 100, # optional UI use

        "source_contribution": contributions,
        "headlines": [
            {
                "source": src,
                "sentiment_score": round(score, 3),
                "text": text
            }
            for _, score, src, text in top_headlines
        ]
    }
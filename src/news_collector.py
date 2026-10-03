"""
news_collector.py
─────────────────
Fetches current affairs articles from RSS feeds and (optionally) NewsAPI.
Returns a deduplicated list of articles from the past 24 hours,
grouped by category: India, World, Economy, Science & Tech, Sports.
"""

import os
import json
import hashlib
import sqlite3
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR   = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR   = BASE_DIR / "data"
DB_PATH    = DATA_DIR / "processed_articles.db"

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Database helpers  (SQLite — tracks seen URLs)
# ─────────────────────────────────────────────

def init_db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_articles (
            url_hash TEXT PRIMARY KEY,
            url      TEXT,
            title    TEXT,
            seen_at  TEXT
        )
    """)
    conn.commit()
    return conn


def article_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def is_seen(conn: sqlite3.Connection, url: str) -> bool:
    h = article_hash(url)
    row = conn.execute("SELECT 1 FROM seen_articles WHERE url_hash=?", (h,)).fetchone()
    return row is not None


def mark_seen(conn: sqlite3.Connection, url: str, title: str) -> None:
    h = article_hash(url)
    conn.execute(
        "INSERT OR IGNORE INTO seen_articles VALUES (?,?,?,?)",
        (h, url, title, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()


# ─────────────────────────────────────────────
# RSS collector
# ─────────────────────────────────────────────

def _parse_published(entry) -> datetime:
    """Return a timezone-aware datetime from a feedparser entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)   # fallback


def fetch_rss_articles(cutoff_hours: int = 24) -> list[dict]:
    """Fetch articles from all enabled RSS feeds published within the last N hours."""
    feeds_path = CONFIG_DIR / "rss_feeds.json"
    with open(feeds_path, encoding="utf-8") as f:
        feeds = json.load(f)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=cutoff_hours)
    articles: list[dict] = []

    for feed in feeds:
        if not feed.get("enabled", True):
            continue
        log.info(f"Fetching RSS: {feed['name']}")
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries:
                pub = _parse_published(entry)
                if pub < cutoff:
                    continue
                # Try to extract an image URL from media_content or enclosures
                image_url = ""
                if "media_content" in entry and len(entry.media_content) > 0:
                    image_url = entry.media_content[0].get("url", "")
                elif "links" in entry:
                    for link in entry.links:
                        if "image" in link.get("type", "") or link.get("href", "").endswith((".jpg", ".png", ".jpeg")):
                            image_url = link.get("href")
                            break
                            
                articles.append({
                    "title":     entry.get("title", "").strip(),
                    "url":       entry.get("link", ""),
                    "image_url": image_url,
                    "summary":   entry.get("summary", entry.get("description", "")).strip(),
                    "category":  feed["category"],
                    "source":    feed["name"],
                    "published": pub.isoformat(),
                })
        except Exception as e:
            log.warning(f"Failed to fetch {feed['name']}: {e}")

    log.info(f"RSS: found {len(articles)} raw articles")
    return articles


# ─────────────────────────────────────────────
# NewsAPI collector (optional)
# ─────────────────────────────────────────────

def fetch_newsapi_articles() -> list[dict]:
    """Fetch top Indian headlines from NewsAPI (optional enrichment)."""
    if not NEWSAPI_KEY:
        return []

    log.info("Fetching from NewsAPI …")
    try:
        resp = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"country": "in", "pageSize": 20, "apiKey": NEWSAPI_KEY},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title":     item.get("title", "").strip(),
                "url":       item.get("url", ""),
                "summary":   item.get("description", "").strip(),
                "category":  "India",
                "source":    item.get("source", {}).get("name", "NewsAPI"),
                "published": item.get("publishedAt", ""),
            })
        log.info(f"NewsAPI: found {len(articles)} articles")
        return articles
    except Exception as e:
        log.warning(f"NewsAPI failed: {e}")
        return []


# ─────────────────────────────────────────────
# Deduplication & grouping
# ─────────────────────────────────────────────

CATEGORIES = ["India", "World", "Economy", "Science & Tech", "Sports"]


def deduplicate(articles: list[dict], conn: sqlite3.Connection) -> list[dict]:
    """Remove already-seen articles and articles with empty titles."""
    fresh: list[dict] = []
    seen_titles: set[str] = set()

    for art in articles:
        if not art["title"] or not art["url"]:
            continue
        if art["title"].lower() in seen_titles:
            continue
        if is_seen(conn, art["url"]):
            continue
        fresh.append(art)
        seen_titles.add(art["title"].lower())

    log.info(f"After deduplication: {len(fresh)} fresh articles")
    return fresh


def group_by_category(articles: list[dict], max_per_cat: int = 2) -> dict[str, list[dict]]:
    """Group articles by category, keeping only the top N per category."""
    grouped: dict[str, list[dict]] = {cat: [] for cat in CATEGORIES}

    for art in articles:
        cat = art.get("category", "India")
        if cat not in grouped:
            cat = "India"
        if len(grouped[cat]) < max_per_cat:
            grouped[cat].append(art)

    # Remove empty categories
    return {k: v for k, v in grouped.items() if v}


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def collect_todays_news(max_per_category: int = 2) -> dict[str, list[dict]]:
    """
    Main entry point.
    Returns a dict mapping category → list of fresh article dicts.
    Also marks collected articles as seen in the DB.
    """
    conn = init_db()

    rss_articles   = fetch_rss_articles(cutoff_hours=24)
    api_articles   = fetch_newsapi_articles()
    all_articles   = rss_articles + api_articles
    fresh_articles = deduplicate(all_articles, conn)
    grouped        = group_by_category(fresh_articles, max_per_category)

    # Mark all selected articles as seen
    for cat_articles in grouped.values():
        for art in cat_articles:
            mark_seen(conn, art["url"], art["title"])

    conn.close()
    return grouped


# ─────────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────────

if __name__ == "__main__":
    news = collect_todays_news()
    for cat, arts in news.items():
        print(f"\n{'='*50}")
        print(f"  {cat} ({len(arts)} articles)")
        print(f"{'='*50}")
        for a in arts:
            print(f"  • {a['title']}")
            print(f"    Source: {a['source']}")

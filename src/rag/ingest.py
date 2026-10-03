"""
ingest.py — Fetches official documents (like PIB), chunks them, and stores them in ChromaDB.
"""

import os
import json
import logging
import feedparser
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "chroma")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "rss_feeds.json")

# Initialize ChromaDB & Embedding Model
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="exam_knowledge")

# We use a lightweight local embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def ingest_trusted_sources():
    """Scrape official RAG sources and embed them into the database."""
    log.info("Starting Trusted Sources Ingestion...")
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        feeds = json.load(f)

    # Filter for strictly official/trusted sources to build the knowledge base
    # (e.g. PIB, Ministries, Govt bodies)
    trusted_feeds = [f for f in feeds if "PIB" in f["name"] or "Govt" in f["name"]]

    for feed_info in trusted_feeds:
        log.info(f"Ingesting {feed_info['name']}...")
        parsed = feedparser.parse(feed_info["url"])
        
        for entry in parsed.entries[:10]:  # limit for demo purposes
            title = entry.get("title", "")
            link = entry.get("link", "")
            raw_summary = entry.get("summary", "")
            content = clean_html(raw_summary)

            if not content:
                continue
                
            # Chunking
            chunks = text_splitter.split_text(content)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{link}#chunk{i}"
                
                # Check if exists
                existing = collection.get(ids=[chunk_id])
                if existing and existing['ids']:
                    continue
                
                # Create embedding
                embedding = model.encode(chunk).tolist()
                
                # Insert into DB
                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source": feed_info["name"], "title": title, "url": link}]
                )
                log.info(f"Inserted chunk: {chunk_id}")

    log.info("Ingestion complete. Vector DB updated.")

if __name__ == "__main__":
    ingest_trusted_sources()

"""
retriever.py — Searches ChromaDB to ground the LLM in official facts.
"""

import os
import logging
import chromadb
from sentence_transformers import SentenceTransformer

log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "chroma")

try:
    chroma_client = chromadb.PersistentClient(path=DB_PATH)
    collection = chroma_client.get_or_create_collection(name="exam_knowledge")
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    log.warning(f"Failed to initialize ChromaDB or model. RAG may be disabled. Error: {e}")
    collection = None
    model = None

def retrieve_facts(query: str, top_k: int = 3) -> str:
    """
    Search the vector database for chunks relevant to the query.
    Returns a formatted string of the retrieved facts.
    """
    if not collection or not model:
        return "No trusted facts retrieved (Database unavailable)."

    embedding = model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    if not results or not results['documents'] or not results['documents'][0]:
        return "No relevant official facts found."

    facts = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        source = meta.get("source", "Unknown")
        facts.append(f"[{source}]: {doc}")
        
    return "\n".join(facts)

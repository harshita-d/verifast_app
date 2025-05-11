#!/usr/bin/env python3
"""
• Fetch RSS (HTTPS → HTTP fallback).
• Embed cleaned news content with LangChain + JinaEmbeddings.
• Store into persistent Chroma vector database.
"""

import os, uuid
import feedparser, httpx
from dotenv import load_dotenv

# LangChain / Chroma integrations
from langchain.vectorstores import Chroma
from chromadb.config import Settings
from langchain_community.embeddings.jina import JinaEmbeddings

# ─── Load environment variables ─────────────────────────────────────────────
load_dotenv()  # Reads from .env file

# Required from .env
RSS_FEED         = os.getenv("RSS_FEED")
COLLECTION_NAME  = os.getenv("CHROMA_COLLECTION")
JINAAI_API_KEY   = os.getenv("JINAAI_API_KEY")
MODEL_NAME       = os.getenv("JINAAI_MODEL")
CHROMA_DIR       = os.getenv("CHROMA_DIR", "./chroma_db")  # Optional fallback

# Basic user-agent for RSS feed requests
USER_AGENT = "Mozilla/5.0 (rss-ingest script)"

# ─── RSS Fetcher ────────────────────────────────────────────────────────────
def fetch_rss(url: str) -> str:
    """
    Fetch RSS XML using httpx. Retry over HTTP if HTTPS fails.
    """
    try:
        r = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=10, verify=False)
        r.raise_for_status()
        return r.text
    except httpx.HTTPError:
        if url.startswith("https://"):
            print("HTTPS failed – retrying over plain HTTP …")
            http_url = "http://" + url[len("https://"):]
            r = httpx.get(http_url, headers={"User-Agent": USER_AGENT}, timeout=10, verify=False)
            r.raise_for_status()
            return r.text
        raise

# ─── Main ingestion logic ───────────────────────────────────────────────────
def ingest(max_items: int = 50):
    print(f"Fetching RSS from: {RSS_FEED}")
    xml = fetch_rss(RSS_FEED)
    parsed = feedparser.parse(xml)
    entries = parsed.entries[:max_items]

    docs = []
    for entry in entries:
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        description = entry.get("description", "").strip()
        content = ""

        if isinstance(entry.get("content"), list) and "value" in entry.content[0]:
            content = entry.content[0]["value"].strip()

        # Combine multiple fields into one document
        combined = " ".join([title, summary, description, content]).strip()

        # Skip unwanted boilerplate or short docs
        if "RSS Channel" in title or "CNN.com" in title:
            continue
        if not combined or len(combined.split()) < 20:
            continue

        docs.append(combined)

    if not docs:
        print("No usable documents found. Check RSS content.")
        return

    # Embed documents using Jina
    embedder = JinaEmbeddings(jina_api_key=JINAAI_API_KEY, model_name=MODEL_NAME)

    # Store in persistent Chroma vector store
    db = Chroma(
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embedder,
    )

    db.add_texts(docs)
    db.persist()

    print(f"Indexed {len(docs)} docs into Chroma collection '{COLLECTION_NAME}'")

    # Show first doc as preview
    print("\nSample embedded document:\n")
    print(docs[0][:300] + "...")

# ─── Entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Fail fast if key is missing
    if not JINAAI_API_KEY:
        raise RuntimeError("Set JINAAI_API_KEY in .env or environment variables")
    ingest()

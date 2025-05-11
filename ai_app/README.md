# ai_app Script – News to Chroma Vector DB

This script fetches recent news articles from an RSS feed, generates embeddings using **Jina AI**, and stores them in a **Chroma vector database** so they can be retrieved later via semantic search.

---

## Environment Setup

We have a `.env` file with the following:

```env
RSS_FEED=https://rss.cnn.com/rss/edition.rss
CHROMA_COLLECTION=news
JINAAI_API_KEY=your_actual_jina_key_here
JINAAI_MODEL=jina-embeddings-v3
CHROMA_DIR=./chroma_db
```

## 1. Load Configuration from .env

- load_dotenv(): to load all necessary environment variables like:

- RSS_FEED: the URL of the news source (e.g. CNN RSS).

- JINAAI_API_KEY: secret key to access Jina embeddings.

- CHROMA_COLLECTION: the name of the vector database collection.

- JINAAI_MODEL: which Jina model to use (default is jina-embeddings-v3).

- CHROMA_DIR: where to store the Chroma database on disk.

```python
# ─── Load environment variables ─────────────────────────────────────────────
load_dotenv()  # Reads from .env file

# Required from .env
RSS_FEED         = os.getenv("RSS_FEED")
COLLECTION_NAME  = os.getenv("CHROMA_COLLECTION")
JINAAI_API_KEY   = os.getenv("JINAAI_API_KEY")
MODEL_NAME       = os.getenv("JINAAI_MODEL") # jina-embeddings-v3
CHROMA_DIR       = os.getenv("CHROMA_DIR", "./chroma_db") 
```

## 2. Fetch the RSS Feed

- Tries to make a secure (HTTPS) request to the RSS URL using httpx.
- If HTTPS fails, automatically retries over plain HTTP.
- Returns the XML text content of the RSS feed.

- fetch_rss: This defines a function called fetch_rss. It takes a single argument: url (which should be a string — ideally, an RSS feed URL). It returns a string — the raw XML content of the RSS feed.
    ```python
    def fetch_rss(url: str) -> str:
    ```

- The bekow code uses the httpx library to make a GET request to the URL. A custom User-Agent is passed so we look like a real browser and don’t get blocked. The request has a timeout of 10 seconds.verify=False disables SSL verification 
    ```python
    r = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=10, verify=False)
    ```
- Than it checks if the response was successful.If the server returned an error (like 404 or 500), this will raise an exception and jump to the except block.
    ```python 
    r.raise_for_status()
    ```

- If no exception was raised, return the raw response text (RSS XML) so it can be parsed later.
    ```python
    return r.text
    ```

- Retry with HTTP if HTTPS fails. The below code catches any errors that occurred during the HTTPS request (e.g. SSL errors, timeouts, or 500 status codes).
    ```python
    except httpx.HTTPError:
    ```

- The below code checks whether the original URL was using HTTPS. If it wasn’t, there's no point in retrying with HTTP, so we only continue if it's safe to do so.
    ```python
    if url.startswith("https://"):
    ```

- now convert the HTTPS URL to HTTP by replacing the scheme.
    ```python
    http_url = "http://" + url[len("https://"):]
    ```

- now repeats the request — but over plain HTTP.Same headers, same timeout. If this succeeds, we return the RSS feed content.

    ```python
    r = httpx.get(http_url, headers={"User-Agent": USER_AGENT}, timeout=10, verify=False)
    r.raise_for_status()
    return r.text
    ```
-  If the original URL didn’t start with HTTPS, or the retry also fails, re-raise the error so the user knows something broke.
    ```python 
    raise
    ```

## 3. Ingest()

- Ingest function processes news articles. It will fetch and embed up to 50 articles by default, unless specified otherwise.
    ```python 
    def ingest(max_items: int = 50):
    ```

- Calls the fetch_rss function. This returns the raw XML string from the feed.
    ```python
    xml = fetch_rss(RSS_FEED)
    ```

- Parses the raw XML using feedparser. Extracts the first max_items entries from the feed, these represent the latest articles.
    ```python
    parsed = feedparser.parse(xml)
    entries = parsed.entries[:max_items]
    ```
- Loop through each news entries. Initializes an emptylist to store cleaned documents. Iterates through every article entry.
    ```python
    docs = []
    for entry in entries:
    ```

- Extracts the title, summary, and description of the article (if they exist). Uses .get() to avoid errors if a field is missing and .strip() removes unwanted whitespace.
    ```python
    title = entry.get("title", "").strip()
    summary = entry.get("summary", "").strip()
    description = entry.get("description", "").strip()
    content = ""
    ```

- Some RSS entries also include a content field, which is a list of dicts. This line checks for it and extracts the actual text inside value.
    ```python
    if isinstance(entry.get("content"), list) and "value" in entry.content[0]:
    content = entry.content[0]["value"].strip()
    ```

- Merges all available text fields into a single string.This combined string represents one complete document for embedding.
    ```python
    combined = " ".join([title, summary, description, content]).strip()
    ```

- Skips RSS boilerplate entries or items with unhelpful titles. Also skips any documents that are too short to be useful (less than 20 words).
    ```python
    if "RSS Channel" in title or "CNN.com" in title:
        continue
    if not combined or len(combined.split()) < 20:
        continue
    ```

- Adds the cleaned and valid document to the docs list.
    ```python
    docs.append(combined)
    ```

- If, after processing, no good documents were found, the script exits with a warning.
    ```python
    if not docs:
        print("No usable documents found. Check RSS content.")
        return
    ```

- This creates an instance of the Jina embedder. It will send each document to the Jina API and get back a numerical vector for it.
    ```python
    embedder = JinaEmbeddings(jina_api_key=JINAAI_API_KEY, model_name=MODEL_NAME)
    ```

- Creates (or connects to) a persistent Chroma database using the specified directory and collection name. Tells Chroma to use the Jina embedder when adding documents.
    ```python
    db = Chroma(
    persist_directory=CHROMA_DIR,
    collection_name=COLLECTION_NAME,
    embedding_function=embedder,
    )
    ```

- Adds all documents into the vector store. add_texts() handles embedding + indexing. persist() ensures everything is saved to disk (especially if the server restarts).
    ```python
    db.add_texts(docs)
    db.persist()
    ```

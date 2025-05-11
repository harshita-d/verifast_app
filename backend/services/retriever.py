import os
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.jina import JinaEmbeddings

load_dotenv()

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "news")
JINAAI_API_KEY = os.getenv("JINAAI_API_KEY")
JINAAI_MODEL = os.getenv("JINAAI_MODEL", "jina-embeddings-v3")

embedder = JinaEmbeddings(
    jina_api_key=JINAAI_API_KEY,
    model_name=JINAAI_MODEL
)

db = Chroma(
    persist_directory=CHROMA_DIR,
    collection_name=COLLECTION_NAME,
    embedding_function=embedder
)

def top_k(query: str, k: int = 3) -> list[str]:
    """Return top-k relevant documents' text using LangChain Chroma."""
    try:
        results = db.similarity_search(query, k)
        if not results:
            print(f"No documents found for query: {query}")
            return []
        print(f"Retrieved {len(results)} docs for: {query}")
        return [doc.page_content for doc in results]
    except Exception as e:
        print(f"Error in retriever.top_k: {e}")
        return []

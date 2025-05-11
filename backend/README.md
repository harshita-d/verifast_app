# Verifast Chat Backend (FastAPI)

## Overview
The backend is built with FastAPI, providing REST APIs to handle real-time chat interactions. It integrates with a Retrieval-Augmented Generation (RAG) pipeline, using **Chroma DB** for document retrieval, **Gemini API** as the Language Model, and **Redis** for caching session histories.

---

## Features
- **Real-time Chat**: REST and WebSocket-based communication
- **RAG Pipeline**: Uses Chroma Vector DB for document retrieval and Gemini API for generating responses
- **Session Management**: Maintains conversation context per session using Redis cache
- **Endpoints**:
  - `/chat/send`: Send a user query and get an AI-generated reply
  - `/chat/history`: Retrieve chat history
  - `/chat/reset`: Clear chat history

---

## Technology Stack

| Technology            | Purpose                             |
|-----------------------|-------------------------------------|
| **FastAPI**           | REST API & WebSocket handling       |
| **Gemini (Google)**   | Large Language Model (LLM)          |
| **Chroma DB**         | Embedding storage & vector retrieval|
| **Redis**             | Session caching and quick retrieval |

---

## Prerequisites
- Python 3.10+
- Redis installed and running locally or remotely

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <Verifast_APP>
cd backend
```
### 2. Setup Virtual Environment
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables (.env)
```bash 
# create .env and set env variables
JINAAI_API_KEY=JINAAI_KEY
CHROMA_COLLECTION=COLLECTION_NAME
REDIS_URL=redis://localhost:6379/0
GEMINI_KEY=GEMENI_KEY
CHROMA_COLLECTION=news
RSS_FEED=https://rss.cnn.com/rss/edition.rss
JINAAI_MODEL=jina-embeddings-v3
```

### 4. Run the Backend Server
```
uvicorn backend.main:app --reload --port 8000
```

### 5. API Docs 

(Swagger): http://localhost:8000/docs

### 6 API Usage

#### 1. Send Chat Message
- Endpoint: POST /chat/send
    - Payload
    ```
    {
  "session_id": "demo",
  "message": "What did CNN report about Trump?,
  "top_k": 3
    }
    ```
    - Response
    ```
    {
  "reply": "CNN political contributor Maggie Haberman explains the reasoning behind Donald Trump's attacks on the judge and his family during a speech at his Mar-a-Lago resort after he was arraigned on felony charges."
    }
    ```
#### 2. Get Chat History
- Endpoint: GET /chat/history?session_id=demo
    - Response
    ```
    [
  {"role": "user", "content": "Hi"},
  {"role": "assistant", "content": "Hello!"}
    ]
    ```

#### 3. Reset Session
- Endpoint: POST /chat/reset
    - Payload
    ```
    {"session_id": "demo"}
    ```
    - Response
    ```
    {"status": "cleared"}
    ```
### 7. Testing Redis Connectivity
```
redis-cli ping
# Expected Output: PONG
```

### 8. Project Structure
```
backend/
├── cache.py             # Redis caching helpers
├── main.py              # FastAPI application entry-point
├── models_api.py        # Pydantic models
├── routers/
│   ├── chat_rest.py     # REST API routes
│   └── chat_ws.py       # WebSocket routes
├── services/
│   ├── llm.py           # Gemini API interaction
│   └── retriever.py     # Chroma retrieval helpers
├── requirements.txt
└── README.md
```

## Code Overview

### 1. main.py
- Main entry point of the FastAPI backend.
- Loads environment variables (load_dotenv). Sets up CORS middleware to allow React frontend. Mounts the REST and WebSocket routers for chat endpoints

### 2. cache.py
- Handles in-memory session history caching using Redis. It Pushes user/assistant messages to Redis. Retrieves the full chat history per session. Clears session-specific cache on reset

### 3. models_api.py
- Defines request/response schemas for API endpoints using Pydantic models.
- ChatReq: structure for a user request
- ChatRes: structure for assistant response
- Turn: structure for a single chat turn (user or assistant)

### 4. routers
- Contains FastAPI route definitions — each a separate microservice layer.
  #### 1. chat_rest.py
    - Handles chat over HTTP POST using /chat/send, /chat/history, and /chat/reset.
    - Builds the full prompt from top-k context. Sends the prompt to Gemini. Stores messages in Redis. Returns structured response

  #### 2. chat_ws.py
  - Handles WebSocket-based live chat via /ws.
  - Accepts a connection. Streams messages back and forth. Maintains per-session chat using UUID

### 5. services
- Contains utility modules for AI-specific features.
  #### 1. llm.py
  - Sends prompts to Google Gemini API and receives responses.
  - Makes authenticated HTTP request to Gemini endpoint. Parses and returns the AI-generated reply

  #### 2. retriever.py
  - Retrieves top-k relevant documents from the Chroma vector DB based on user query.
  - Loads the persisted Chroma collection. Queries it using vector similarity search. Returns list of relevant document chunks

### 6. requirements.txt
- List of all Python dependencies required to run the app.
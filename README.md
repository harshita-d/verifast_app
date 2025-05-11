# Verifast RAG Chat – Full Stack AI Chatbot

This is a full-stack AI-powered chatbot that answers user queries over the latest news articles using a **Retrieval-Augmented Generation (RAG)** pipeline.

this project demonstrates:
- End-to-end ingestion of real-world data (RSS feeds)
- Vector-based search using Chroma DB
- Embedding with Jina AI
- Semantic response generation using **Gemini**
- Stateful chat interface with frontend/backend integration

---

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Frontend     | React.js, plain CSS               |
| Backend      | FastAPI, Redis, Gemini API        |
| Embeddings   | LangChain + JinaEmbeddings        |
| Vector Store | Chroma DB (local persistent)      |
| State Cache  | Redis                             |

---

## Quickstart

### 1. Setup Python backend
```bash
cd backend/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### 2. Setup frontend
```bash
cd frontend/
npm install
npm start
```

### 3. ai_app News Articles
```bash
cd ai_app
python ai_app.py
```

## Detailed

| Part      | Description                                  | Link                                         |
| --------- | -------------------------------------------- | -------------------------------------------- |
| ai_app | Fetch, embed, and index news data            | [`ai_app/README.md`](./ai_app/README.md)     |
| Backend   | API endpoints, WebSocket, Gemini integration | [`backend/README.md`](./backend/README.md)   |
| Frontend  | UI chat interface + session management       | [`frontend/README.md`](./frontend/README.md) |

## Features

- News-based chatbot with semantic understanding

- Stateless frontend + stateful backend (session-based)

- Embedding pipeline with fallback error handling

- Redis caching for chat history

- Clean architecture for extensibility

## Flow

- Start the backend server at 8000 port 

- Start the frontend (React dev server) at 3000 port

- Ingest RSS news articles to build the vector DB

- Open the app → Ask any news-related question

- Responses are retrieved, contextualized, and streamed using Gemini

## Notes

- Designed to run locally
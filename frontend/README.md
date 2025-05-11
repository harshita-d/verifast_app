# Verifast Chat Frontend (ReactJS)

## Overview
The frontend for the Verifast Chat application is built using **ReactJS** and styled with **custom CSS**. It provides a smooth user interface to interact with the AI-powered backend built with FastAPI. Users can ask questions about news, view chat history, and reset their session.

---

## Features
- Clean, modern chat UI
- Real-time AI responses via streaming
- Persistent sessions via localStorage
- Manual styling with CSS (no Tailwind)

---

## Tech Stack

| Tool/Library    | Purpose                          |
|-----------------|----------------------------------|
| **React**       | Frontend library                 |
| **UUID**        | Session ID generation            |
| **Fetch API**   | Async communication with backend |
| **CSS**         | Layout and chat bubble styling   |

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone <your-frontend-repo>
cd frontend
```

### 2.  Install Dependencies

```bash
npm install
```

### 3. Run Server
```bash
npm start
```
> Open http://localhost:3000 in your browser.

#### 1. Backend Configuration

- src/api.js
```bash
const BASE = "http://localhost:8000/chat";
```


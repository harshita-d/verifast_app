from dotenv import load_dotenv    
load_dotenv()                     

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat_rest, chat_ws 

app = FastAPI(title="Verifast RAG Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # React dev-server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_rest.router, prefix="/chat")
app.include_router(chat_ws.router)

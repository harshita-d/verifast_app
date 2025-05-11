import os, httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = (
    "https://generativelanguage.googleapis.com/v1/"
    "models/gemini-2.0-flash:generateContent"
)
API_KEY = os.getenv("GEMINI_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_KEY not set")

async def ask(prompt: str) -> str:
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    async with httpx.AsyncClient(timeout=30) as c:
        resp = await c.post(f"{BASE_URL}?key={API_KEY}", json=payload)
    resp.raise_for_status()
    
    return (
        resp.json()
        .get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )

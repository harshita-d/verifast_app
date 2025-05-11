from fastapi import APIRouter
from backend.models_api import ChatReq, ChatRes, Turn
from backend.cache import push, history, clear
from backend.services import retriever, llm

router = APIRouter()

def build_prompt(q: str, k: int):
    docs = retriever.top_k(q, k)
    ctx = "\n---\n".join(docs)

    return f"""You are a helpful assistant. Answer the question using ONLY the context below.

Context:
{ctx}

Question: {q}
Answer:"""


@router.post("/send", response_model=ChatRes)
async def send(req: ChatReq):
    prompt = build_prompt(req.message, req.top_k)
    print("\nPrompt to Gemini:\n")
    print(prompt[:1000])  # limit long print

    answer = await llm.ask(prompt)
    await push(req.session_id, "user", req.message)
    await push(req.session_id, "assistant", answer)
    return ChatRes(reply=answer)

@router.get("/history", response_model=list[Turn])
async def hist(session_id: str):
    return await history(session_id)

@router.post("/reset")
async def reset(session_id: str):
    await clear(session_id)
    return {"status": "cleared"}

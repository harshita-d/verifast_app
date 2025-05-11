from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services import retriever, llm
from backend.cache import push
import uuid, json, asyncio

router = APIRouter()

def rag(query:str,k:int=3):
    ctx="\n---\n".join(retriever.top_k(query,k))
    return f"Answer ONLY from context.\nContext:\n{ctx}\nQuestion:{query}\nAnswer:"

@router.websocket("/ws")
async def chat_ws(ws: WebSocket):
    await ws.accept()
    sid = str(uuid.uuid4())
    try:
        while True:
            data = await ws.receive_text()
            await push(sid,"user",data)
            prompt = rag(data)
            answer = await llm.ask(prompt)
            await push(sid,"assistant",answer)
            await ws.send_text(answer)
    except WebSocketDisconnect:
        pass

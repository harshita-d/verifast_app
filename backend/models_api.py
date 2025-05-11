import uuid
from pydantic import BaseModel, Field

class ChatReq(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str
    top_k: int = 3

class Turn(BaseModel):
    role: str
    content: str

class ChatRes(BaseModel):
    reply: str

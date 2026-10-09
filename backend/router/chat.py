from fastapi import APIRouter
from pydantic import BaseModel

from backend.modules.agent import Agents

router = APIRouter(tags=["chat"])

load_agent = Agents()


class ChatRequest(BaseModel):
    user_input: str


@router.post("/chat")
def post_chat(request: ChatRequest):
    return load_agent.ai_agent(request.user_input)
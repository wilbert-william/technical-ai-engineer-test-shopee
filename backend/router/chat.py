from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from backend.modules.agent import Agents
import json

router = APIRouter(tags=["chat"])
load_agent = Agents()


class ChatRequest(BaseModel):
    user_input: str


@router.post("/chat")
def post_chat(request: ChatRequest):
    def event_stream():
        try:
            for token in load_agent.ai_agent(request.user_input):
                payload = json.dumps({"answer": token})
                yield f"data: {payload}\n\n"

            yield 'data: {"completed": true}\n\n'

        except Exception:
            yield 'data: {"error": "Streaming failed"}\n\n'

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
import json

from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from backend.modules.agent import Agents
from backend.utils import session_manage

router = APIRouter(tags=["chat"])
load_agent = Agents()


class ChatRequest(BaseModel):
    user_input: str
    session_id: str | None = None


@router.post("/chat")
def post_chat(request: ChatRequest):
    session_id = request.session_id

    if not session_id or not session_manage.session_exists(session_id):
        session_id = session_manage.create_session()

    session_manage.save_message(
        session_id,
        "user",
        request.user_input,
    )

    def event_stream():
        answer = ""

        try:
            yield f"data: {json.dumps({'session_id': session_id})}\n\n"

            for token in load_agent.ai_agent(
                request.user_input,
                session_id,
            ):
                answer += token
                payload = json.dumps({"answer": token})
                yield f"data: {payload}\n\n"

            session_manage.save_message(
                session_id,
                "assistant",
                answer,
            )

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

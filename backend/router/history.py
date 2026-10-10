from fastapi import APIRouter, HTTPException

from backend.utils import session_manage

router = APIRouter(tags=["history"])

@router.get("/sessions/{session_id}/messages")
def get_chat_history(session_id: str):
    messages = session_manage.get_messages(session_id)

    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    return {
        "session_id": session_id,
        "messages": messages,
    }
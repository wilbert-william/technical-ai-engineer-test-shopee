from fastapi import APIRouter
from backend.utils import session_manage

router = APIRouter(tags=["session"])


@router.get("/sessions")
def get_chat_sessions():
    return session_manage.get_sessions()
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from backend.utils.database import Base, SessionLocal


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    session_id = Column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    session = relationship(
        "ChatSession",
        back_populates="messages",
    )


def create_session() -> str:
    """Create a new chat session."""
    with SessionLocal() as db:
        session = ChatSession()
        db.add(session)
        db.commit()
        db.refresh(session)

        return session.id


def session_exists(session_id: str) -> bool:
    """Check whether a session exists."""
    with SessionLocal() as db:
        return db.get(ChatSession, session_id) is not None


def save_message(
    session_id: str,
    role: str,
    content: str,
) -> dict:
    """Save a user or assistant message."""
    if role not in {"user", "assistant"}:
        raise ValueError("Role must be 'user' or 'assistant'.")

    with SessionLocal() as db:
        if db.get(ChatSession, session_id) is None:
            raise ValueError("Session not found.")

        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return {
            "id": message.id,
            "session_id": message.session_id,
            "role": message.role,
            "content": message.content,
        }


def get_messages(session_id: str) -> list[dict]:
    """Retrieve conversation history for a session."""
    with SessionLocal() as db:
        if db.get(ChatSession, session_id) is None:
            raise ValueError("Session not found.")

        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at, ChatMessage.id)
            .all()
        )

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]
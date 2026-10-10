from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from backend.utils.database import Base, SessionLocal


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


def create_session() -> str:
    with SessionLocal() as db:
        session = ChatSession()
        db.add(session)
        db.commit()
        return session.id


def session_exists(session_id: str) -> bool:
    with SessionLocal() as db:
        return db.get(ChatSession, session_id) is not None


def save_message(session_id: str, role: str, content: str) -> None:
    if role not in {"user", "assistant"}:
        raise ValueError("Invalid message role.")

    with SessionLocal() as db:
        db.add(
            ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
            )
        )
        db.commit()


def get_messages(session_id: str) -> list[dict]:
    with SessionLocal() as db:
        messages = (
            db.query(ChatMessage)
            .filter_by(session_id=session_id)
            .order_by(ChatMessage.created_at, ChatMessage.id)
            .all()
        )

        return [
            {"role": message.role, "content": message.content}
            for message in messages
        ]

def get_sessions() -> list[dict]:
    with SessionLocal() as db:
        sessions = (
            db.query(ChatSession)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

        result = []

        for session in sessions:
            first_message = (
                db.query(ChatMessage)
                .filter_by(session_id=session.id, role="user")
                .order_by(ChatMessage.created_at, ChatMessage.id)
                .first()
            )

            name = "New chat"

            if first_message:
                name = " ".join(first_message.content.split()[:5])

            result.append({
                "session_id": session.id,
                "name": name,
                "created_at": session.created_at,
            })

        return result

def get_messages(session_id: str) -> list[dict] | None:
    with SessionLocal() as db:
        session = db.get(ChatSession, session_id)

        if not session:
            return None

        messages = (
            db.query(ChatMessage)
            .filter_by(session_id=session_id)
            .order_by(ChatMessage.created_at, ChatMessage.id)
            .all()
        )

        return [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ]
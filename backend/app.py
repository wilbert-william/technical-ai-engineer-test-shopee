from fastapi import FastAPI

from backend.router import health, live, chat

app = FastAPI(
    title="Food Receipt AI Agent",
    description="API for receipt OCR, expense tracking, and AI-powered insights.",
    version="0.1.0",
)

app.include_router(health.router, prefix="")
app.include_router(live.router, prefix="")
app.include_router(chat.router, prefix="/api")

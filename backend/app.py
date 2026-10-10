import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.router import health, live, chat, upload_receipt, session, history
from backend.utils.checkpointer import close_checkpointer
from backend.utils.init_qdrant import init_qdrant
from backend.utils.init_postgre import init_postgre
from backend.utils.langfuse import flush_langfuse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing services...")

    logger.info("[1/2] Initializing PostgreSQL...")
    init_postgre()
    logger.info("[1/2] PostgreSQL initialized successfully.")

    logger.info("[2/2] Initializing Qdrant...")
    init_qdrant()
    logger.info("[2/2] Qdrant initialized successfully.")

    logger.info("All services initialized successfully.")

    yield

    logger.info("Flushing Langfuse...")
    flush_langfuse()

    logger.info("Closing PostgreSQL connection pool...")
    close_checkpointer()

    logger.info("Application stopped.")


app = FastAPI(
    title="Food Receipt AI Agent",
    description="API for receipt OCR, expense tracking, and AI-powered insights.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router, prefix="")
app.include_router(live.router, prefix="")
app.include_router(chat.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(upload_receipt.router, prefix="/api")

import os
import logging

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

logger = logging.getLogger(__name__)
logging.getLogger("psycopg.pool").setLevel(logging.DEBUG)

DATABASE_URL = os.getenv("DATABASE_URL", "").replace(
    "postgresql+psycopg://", "postgresql://"
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not configured.")

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    kwargs={
        "autocommit": True,
        "row_factory": dict_row,
    },
    open=False,
)

checkpointer = PostgresSaver(pool)


def setup_checkpointer():
    logger.info("Opening PostgreSQL connection pool...")
    pool.open(wait=True, timeout=10)
    logger.info("Setting up LangGraph checkpoint tables...")
    checkpointer.setup()
    logger.info("LangGraph checkpointer initialized.")


def close_checkpointer():
    if not pool.closed:
        pool.close()
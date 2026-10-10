from backend.utils.database import Base, engine
from backend.utils.checkpointer import setup_checkpointer
import logging

logger = logging.getLogger(__name__)

def init_postgre():
    Base.metadata.create_all(bind=engine)
    setup_checkpointer()
    logger.info("PostgreSQL initialized successfully.")
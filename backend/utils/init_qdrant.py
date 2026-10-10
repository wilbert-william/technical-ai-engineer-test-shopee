
from backend.modules.vector_db import VectorDB
from qdrant_client.models import VectorParams

import logging

logger = logging.getLogger(__name__)


def init_qdrant():
    vector_db = VectorDB()

    if vector_db.qdrant_client.collection_exists(
        collection_name=vector_db.collection_name
    ):
        logger.info("Collection 'receipt_data' already exists.")
        return

    vector_db.qdrant_client.create_collection(
        collection_name=vector_db.collection_name,
        vectors_config=VectorParams(
            size=vector_db.vector_size,
            distance=vector_db.distance,
        ),
    )

    logger.info("Collection 'receipt_data' created.")

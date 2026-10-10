import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if not qdrant_url:
    raise ValueError("QDRANT_URL is not configured.")

if not qdrant_api_key:
    raise ValueError("QDRANT_API_KEY is not configured.")

qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
)
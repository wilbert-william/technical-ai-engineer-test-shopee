from typing import Any

from qdrant_client.models import Distance, VectorParams, PointStruct

from backend.utils.qdrant import qdrant_client
from backend.utils.llm import load_embedding_model


class VectorDB:
    def __init__(self):
        self.qdrant_client = qdrant_client
        self.embedding_model = load_embedding_model

        self.collection_name = "receipt_data"
        self.vector_size = 1536
        self.distance = Distance.COSINE

    # Convert text into an embedding vector
    def data_embeddings(self, text: str) -> list[float]:
        return self.embedding_model.embed_query(text)

    def qdrant_insert_data(self, point_id, vector: list[float], payload: dict[str, Any]) -> dict:
        try:
            # Create collection if it does not exist
            if not self.qdrant_client.collection_exists(
                collection_name=self.collection_name
            ):
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=self.distance,
                    ),
                )

            # Insert or update data
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                ],
                wait=True,
            )

            return {
                "success": True,
                "message": f"Data '{point_id}' inserted successfully.",
            }

        except Exception as e:
            raise RuntimeError(
                f"Failed to insert data into Qdrant: {e}"
            ) from e

    def qdrant_retrieve(self, text: str, limit: int = 3) -> list[dict]:
        if not self.qdrant_client.collection_exists(
            collection_name=self.collection_name
        ):
            return []

        try:
            # Convert query text into an embedding vector
            vector = self.data_embeddings(text)

            # Search for similar vectors
            response = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=limit,
                with_payload=True,
            )

            return [
                {
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload,
                }
                for point in response.points
            ]

        except Exception as e:
            raise RuntimeError(
                f"Failed to retrieve data from Qdrant: {e}"
            ) from e
from fastapi import APIRouter
from backend.modules.vector_db import VectorDB

router = APIRouter(tags=["Upload Receipt"])


@router.get("/upload_receipt")
def upload_receipt():
    return {"status": "healthy"}
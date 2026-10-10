from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from backend.modules.vector_db import VectorDB
from backend.utils.ocr import extract_text

router = APIRouter(tags=["Upload Receipt"])
load_vector_db = VectorDB()


@router.post("/upload_receipt")
async def upload_receipt(file: UploadFile = File(...)):
    image_bytes = await file.read()
    text = extract_text(image_bytes)

    point_id = str(uuid4())
    vector = load_vector_db.data_embeddings(text)
    result = load_vector_db.qdrant_insert_data(
        point_id=point_id,
        vector=vector,
        payload={"filename": file.filename, "text": text},
    )

    return {
        "id": point_id,
        "filename": file.filename,
        "text": text,
        **result,
    }

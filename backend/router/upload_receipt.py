from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.modules.vector_db import VectorDB
from backend.utils.llm import load_llm
from backend.utils.ocr import extract_text
from backend.utils.prompt import receipt_classifier_prompt

router = APIRouter(tags=["Upload Receipt"])
load_vector_db = VectorDB()


class ReceiptClassification(BaseModel):
    is_receipt: bool = Field(
        description="Whether the OCR text looks like it came from a shopping/food receipt"
    )


receipt_classifier = load_llm.with_structured_output(ReceiptClassification)


def is_receipt(text: str) -> bool:
    classification = receipt_classifier.invoke(
        [
            {"role": "system", "content": receipt_classifier_prompt},
            {"role": "user", "content": text},
        ]
    )

    return classification.is_receipt


@router.post("/upload_receipt")
async def upload_receipt(file: UploadFile = File(...)):
    image_bytes = await file.read()
    text = extract_text(image_bytes)

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found in the image.",
        )

    if not is_receipt(text):
        raise HTTPException(
            status_code=422,
            detail="The uploaded image does not look like a receipt.",
        )

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

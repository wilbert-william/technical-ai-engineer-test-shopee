from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.modules.vector_db import VectorDB
from backend.utils.llm import load_llm
from backend.utils.ocr import extract_text
from backend.utils.prompt import receipt_parser_prompt

router = APIRouter(tags=["Upload Receipt"])
load_vector_db = VectorDB()


class ReceiptItem(BaseModel):
    name: str = Field(description="Name of the purchased item")
    price: float = Field(description="Price of the item")


class ReceiptData(BaseModel):
    is_receipt: bool = Field(
        description="Whether the OCR text looks like it came from a shopping/food receipt"
    )
    merchant_name: str | None = Field(
        default=None, description="Name of the store or merchant"
    )
    date: str | None = Field(
        default=None, description="Purchase date as written on the receipt"
    )
    items: list[ReceiptItem] = Field(
        default_factory=list, description="List of purchased items with prices"
    )
    total: float | None = Field(default=None, description="Total amount paid")


receipt_parser = load_llm.with_structured_output(ReceiptData)


def parse_receipt(text: str) -> ReceiptData:
    return receipt_parser.invoke(
        [
            {"role": "system", "content": receipt_parser_prompt},
            {"role": "user", "content": text},
        ]
    )


@router.post("/upload_receipt")
async def upload_receipt(file: UploadFile = File(...)):
    image_bytes = await file.read()
    text = extract_text(image_bytes)

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found in the image.",
        )

    parsed = parse_receipt(text)

    if not parsed.is_receipt:
        raise HTTPException(
            status_code=422,
            detail="The uploaded image does not look like a receipt.",
        )

    point_id = str(uuid4())
    input_datetime = datetime.now(timezone.utc).isoformat()
    vector = load_vector_db.data_embeddings(text)
    result = load_vector_db.qdrant_insert_data(
        point_id=point_id,
        vector=vector,
        payload={
            "text": text,
            "input_datetime": input_datetime,
            "merchant_name": parsed.merchant_name,
            "date": parsed.date,
            "items": [item.model_dump() for item in parsed.items],
            "total": parsed.total,
        },
    )

    return {
        "id": point_id,
        "text": text,
        "input_datetime": input_datetime,
        "merchant_name": parsed.merchant_name,
        "date": parsed.date,
        "items": [item.model_dump() for item in parsed.items],
        "total": parsed.total,
        **result,
    }

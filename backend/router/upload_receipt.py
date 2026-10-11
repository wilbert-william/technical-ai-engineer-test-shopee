from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from backend.modules.vector_db import VectorDB
from backend.utils.llm import load_llm
from backend.utils.ocr import extract_text
from backend.utils.prompt import receipt_parser_prompt

router = APIRouter(tags=["Upload Receipt"])
load_vector_db = VectorDB()
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
MAX_PROCESSED_IMAGE_SIZE = 500 * 1024


def compress_receipt_image(image_bytes: bytes) -> bytes:
    with Image.open(BytesIO(image_bytes)) as source:
        if source.format not in {"PNG", "JPEG"}:
            raise ValueError("File must be a PNG or JPEG image.")

        source.verify()

    if len(image_bytes) <= MAX_PROCESSED_IMAGE_SIZE:
        return image_bytes

    with Image.open(BytesIO(image_bytes)) as source:
        image = ImageOps.exif_transpose(source)
        if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
            rgba_image = image.convert("RGBA")
            background = Image.new("RGB", rgba_image.size, "white")
            background.paste(rgba_image, mask=rgba_image.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")

    while True:
        for quality in (88, 80, 72, 64, 56, 48, 40, 32):
            output = BytesIO()
            image.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
            )
            compressed = output.getvalue()
            if len(compressed) <= MAX_PROCESSED_IMAGE_SIZE:
                return compressed

        width, height = image.size
        if max(width, height) <= 256:
            raise ValueError("Image could not be compressed below 500 KB.")

        new_size = (max(1, int(width * 0.8)), max(1, int(height * 0.8)))
        image = image.resize(new_size, Image.Resampling.LANCZOS)


class ReceiptItem(BaseModel):
    name: str = Field(description="Name of the purchased item")
    quantity: int = Field(default=1, description="Quantity of the item purchased")
    unit_price: float = Field(description="Unit price of a single item")


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
    image_bytes = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(image_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must be 5 MB or less.",
        )

    try:
        image_bytes = compress_receipt_image(image_bytes)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc) or "File must be a valid PNG or JPEG image.",
        ) from exc

    text = await run_in_threadpool(extract_text, image_bytes)

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found in the image.",
        )

    parsed = await run_in_threadpool(parse_receipt, text)

    if not parsed.is_receipt:
        raise HTTPException(
            status_code=422,
            detail="The uploaded image does not look like a receipt.",
        )

    point_id = str(uuid4())
    input_datetime = datetime.now(timezone.utc).isoformat()
    vector = await run_in_threadpool(load_vector_db.data_embeddings, text)

    result = await run_in_threadpool(
        load_vector_db.qdrant_insert_data,
        point_id,
        vector,
        {
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

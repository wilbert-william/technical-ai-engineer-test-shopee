import numpy as np
from paddleocr import PaddleOCR
from PIL import Image
from io import BytesIO

_ocr = None


def extract_text(image_bytes: bytes) -> str:
    global _ocr

    if _ocr is None:
        _ocr = PaddleOCR(lang="id")

    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image_array = np.array(image)

    results = _ocr.predict(image_array)

    extracted_text = []

    for result in results:
        result_data = result.json
        data = result_data.get("res", {}).get("rec_texts", [])

        extracted_text.extend(
            text for text in data if text.strip()
        )

    return "\n".join(extracted_text)
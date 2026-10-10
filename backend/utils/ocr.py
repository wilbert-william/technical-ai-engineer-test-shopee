import numpy as np
from paddleocr import PaddleOCR
from PIL import Image
from io import BytesIO


ocr = PaddleOCR(
    lang="en",
)


def extract_text(image_bytes: bytes) -> str:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image_array = np.array(image)

    results = ocr.predict(image_array)

    extracted_text = []

    for result in results:
        data = result.get("rec_texts", [])
        extracted_text.extend(data)

    return "\n".join(extracted_text)
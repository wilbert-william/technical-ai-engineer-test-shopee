import numpy as np
from paddleocr import PaddleOCR
from PIL import Image, ImageOps
from io import BytesIO

ocr = None


def initialize_ocr():
    global ocr

    if ocr is None:
        ocr = PaddleOCR(lang="id", enable_mkldnn=False)


def preprocess_receipt_image(image: Image.Image) -> Image.Image:
    
    image = ImageOps.exif_transpose(image).convert("RGB")

    image = ImageOps.autocontrast(image)

    if max(image.size) < 1000:
        scale = 1000 / max(image.size)
        new_size = (round(image.width * scale), round(image.height * scale))
        image = image.resize(new_size, Image.LANCZOS)

    return image


def extract_text(image_bytes: bytes) -> str:
    initialize_ocr()

    image = Image.open(BytesIO(image_bytes))
    image = preprocess_receipt_image(image)
    image_array = np.array(image)

    results = ocr.predict(image_array)

    extracted_text = []

    for result in results:
        result_data = result.json
        data = result_data.get("res", {}).get("rec_texts", [])

        extracted_text.extend(
            text for text in data if text.strip()
        )

    return "\n".join(extracted_text)

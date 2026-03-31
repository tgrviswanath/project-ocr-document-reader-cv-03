"""
OCR extractor.
- Images (JPG/PNG/BMP/WEBP): OpenCV preprocess → Tesseract
- PDFs: PyMuPDF renders each page → Tesseract per page
Returns: extracted text, word count, page count, word bounding boxes
"""
import pytesseract
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io
from app.core.preprocess import preprocess_for_ocr, load_raw
from app.core.config import settings

if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def _ocr_array(arr: np.ndarray) -> dict:
    pil_img = Image.fromarray(arr)
    text = pytesseract.image_to_string(pil_img, lang=settings.OCR_LANG).strip()

    # Word-level bounding boxes
    data = pytesseract.image_to_data(
        pil_img, lang=settings.OCR_LANG,
        output_type=pytesseract.Output.DICT,
    )
    words = []
    for i, word in enumerate(data["text"]):
        if word.strip() and int(data["conf"][i]) > 30:
            words.append({
                "text": word,
                "x": data["left"][i],
                "y": data["top"][i],
                "width": data["width"][i],
                "height": data["height"][i],
                "confidence": int(data["conf"][i]),
            })
    return {"text": text, "words": words}


def extract_image(image_bytes: bytes) -> dict:
    if settings.PREPROCESS:
        arr = preprocess_for_ocr(image_bytes)
    else:
        arr = load_raw(image_bytes)
    result = _ocr_array(arr)
    return {
        "pages": 1,
        "text": result["text"],
        "word_count": len(result["text"].split()),
        "words": result["words"],
        "page_texts": [result["text"]],
    }


def extract_pdf(pdf_bytes: bytes) -> dict:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_text, page_texts, all_words = [], [], []

    for page_num, page in enumerate(doc):
        # Render page to image at DPI
        mat = fitz.Matrix(settings.DPI / 72, settings.DPI / 72)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)

        result = _ocr_array(arr)
        all_text.append(result["text"])
        page_texts.append(result["text"])
        for w in result["words"]:
            w["page"] = page_num + 1
            all_words.append(w)

    full_text = "\n\n".join(all_text)
    return {
        "pages": len(doc),
        "text": full_text,
        "word_count": len(full_text.split()),
        "words": all_words,
        "page_texts": page_texts,
    }

from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.extractor import extract_image, extract_pdf

router = APIRouter(prefix="/api/v1/cv", tags=["ocr"])

IMAGE_EXTS = {"jpg", "jpeg", "png", "bmp", "webp"}
PDF_EXTS = {"pdf"}
ALLOWED = IMAGE_EXTS | PDF_EXTS


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


@router.post("/extract")
async def extract(file: UploadFile = File(...)):
    ext = _ext(file.filename)
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported format: .{ext}")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if ext in PDF_EXTS:
        return extract_pdf(content)
    return extract_image(content)

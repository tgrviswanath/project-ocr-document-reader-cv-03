import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.extractor import extract_image, extract_pdf
from app.core.validate import validate_image, _check_ext, _check_size

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
        raise HTTPException(status_code=400, detail=f"Unsupported format: .{ext}. Allowed: {sorted(ALLOWED)}")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    _check_size(content)
    if ext in PDF_EXTS:
        try:
            return await asyncio.get_running_loop().run_in_executor(None, extract_pdf, content)
        except FileNotFoundError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF extraction error: {e}")
    from app.core.validate import _check_resolution
    _check_resolution(content)
    try:
        return await asyncio.get_running_loop().run_in_executor(None, extract_image, content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR error: {e}")

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from PIL import Image
import io
from app.main import app

client = TestClient(app)


def _sample_image() -> bytes:
    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


MOCK_OCR_DATA = {
    "text": ["", "Hello", "World", ""],
    "conf": ["-1", "95", "88", "-1"],
    "left": [0, 10, 60, 0],
    "top": [0, 5, 5, 0],
    "width": [0, 40, 45, 0],
    "height": [0, 20, 20, 0],
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@patch("pytesseract.image_to_string", return_value="Hello World")
@patch("pytesseract.image_to_data", return_value=MOCK_OCR_DATA)
def test_extract_image(mock_data, mock_str):
    r = client.post(
        "/api/v1/cv/extract",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")},
    )
    assert r.status_code == 200
    data = r.json()
    assert "text" in data
    assert "word_count" in data
    assert "pages" in data
    assert data["pages"] == 1


def test_extract_unsupported():
    r = client.post(
        "/api/v1/cv/extract",
        files={"file": ("test.gif", b"GIF89a", "image/gif")},
    )
    assert r.status_code == 400


def test_extract_empty():
    r = client.post(
        "/api/v1/cv/extract",
        files={"file": ("test.jpg", b"", "image/jpeg")},
    )
    assert r.status_code == 400

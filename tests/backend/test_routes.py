from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "pages": 1,
    "text": "Hello World this is a test document.",
    "word_count": 7,
    "words": [{"text": "Hello", "x": 10, "y": 5, "width": 40, "height": 20, "confidence": 95}],
    "page_texts": ["Hello World this is a test document."],
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.extract_text", new_callable=AsyncMock, return_value=MOCK_RESULT)
def test_extract_endpoint(mock_extract):
    r = client.post(
        "/api/v1/extract",
        files={"file": ("test.jpg", b"fake", "image/jpeg")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["word_count"] == 7
    assert data["pages"] == 1
    assert "Hello" in data["text"]

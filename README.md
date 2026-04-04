# Project CV-03 - OCR Document Reader

Microservice CV system that extracts text from images and PDFs using Tesseract OCR with OpenCV preprocessing (grayscale, denoise, adaptive threshold, deskew).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (React - Port 3000)                              │
│  axios POST /api/v1/ocr                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  BACKEND  (FastAPI - Port 8000)                             │
│  httpx POST /api/v1/cv/ocr  →  calls cv-service             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  CV SERVICE  (FastAPI - Port 8001)                          │
│  PyMuPDF renders PDF → images                               │
│  OpenCV preprocess → Tesseract OCR                          │
│  Returns { text, word_count, pages, words[] }               │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works

```
Image / PDF uploaded
    ↓
PyMuPDF renders PDF pages → images (300 DPI)
    ↓
OpenCV preprocessing:
  grayscale → denoise → adaptive threshold → deskew
    ↓
Tesseract OCR extracts text + word bounding boxes
    ↓
Return: text, word_count, pages, page_texts[], words[]
```

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, MUI |
| Backend | FastAPI, httpx |
| CV | OpenCV, Tesseract OCR, PyMuPDF, Pillow |
| Input | Images (PNG, JPG, TIFF) + PDFs |
| Deployment | Docker, docker-compose |

---

## Prerequisites

- Python 3.12+
- Node.js — run `nvs use 20.14.0` before starting the frontend
- **Tesseract OCR** must be installed:

```bash
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Ubuntu:  sudo apt-get install tesseract-ocr
# macOS:   brew install tesseract
```

---

## Local Run

### Step 1 — Start CV Service (Terminal 1)

```bash
cd cv-service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Verify: http://localhost:8001/health → `{"status":"ok"}`

### Step 2 — Start Backend (Terminal 2)

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 3 — Start Frontend (Terminal 3)

```bash
cd frontend
npm install && npm start
```

Opens at: http://localhost:3000

---

## Environment Files

### `backend/.env`

```
APP_NAME=OCR Document Reader API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
CV_SERVICE_URL=http://localhost:8001
```

### `frontend/.env`

```
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Run

```bash
docker-compose up --build
# Tesseract is installed inside the Docker image automatically
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| CV Service docs | http://localhost:8001/docs |

---

## Run Tests

```bash
cd cv-service && venv\Scripts\activate
pytest ../tests/cv-service/ -v

cd backend && venv\Scripts\activate
pytest ../tests/backend/ -v
```

---

## Project Structure

```
project-ocr-document-reader-cv-03/
├── frontend/                    ← React (Port 3000)
├── backend/                     ← FastAPI (Port 8000)
├── cv-service/                  ← FastAPI CV (Port 8001)
│   └── app/
│       ├── api/routes.py
│       ├── core/ocr.py          ← OpenCV + Tesseract pipeline
│       ├── core/pdf.py          ← PyMuPDF PDF rendering
│       └── main.py
├── samples/                     ← test documents and images
├── tests/
├── docker/
└── docker-compose.yml
```

---

## API Reference

```
POST /api/v1/ocr
Body:     multipart/form-data  { file: image or PDF }
Response: { "text": "...", "word_count": 245, "pages": 1, "words": [{ "text": "...", "confidence": 95.2 }] }
```

---

## Dataset

Use any scanned document, receipt, or text image.
Try IIIT5K Word Dataset from Kaggle for testing.

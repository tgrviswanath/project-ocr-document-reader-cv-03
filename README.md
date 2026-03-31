# Project 03 - OCR Document Reader (CV)

Extract text from images and PDFs using Tesseract OCR with OpenCV preprocessing.

## Architecture

```
Frontend :3000  →  Backend :8000  →  CV Service :8001
  React/MUI        FastAPI/httpx      FastAPI/OpenCV/Tesseract/PyMuPDF
```

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

## What's Different from Projects 01 & 02

| | Project 01 | Project 02 | Project 03 |
|---|---|---|---|
| Task | Classify image | Detect faces | Extract text |
| Model | SVM | OpenCV DNN | Tesseract OCR |
| Input | Image only | Image only | Image + PDF |
| Output | Label | Bounding boxes | Text + word tokens |
| New concept | sklearn pipeline | DNN inference | OCR + preprocessing |

## Prerequisites — Install Tesseract

```bash
# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

## Local Run

```bash
# Terminal 1 - CV Service
cd cv-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

- CV Service docs: http://localhost:8001/docs
- Backend docs:   http://localhost:8000/docs
- UI:             http://localhost:3000

## Docker

```bash
docker-compose up --build
# Tesseract is installed inside the Docker image automatically
```

## Dataset
Use any scanned document, receipt, or text image.
Try IIIT5K Word Dataset from Kaggle for testing.

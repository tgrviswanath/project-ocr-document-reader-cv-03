# Azure Deployment Guide — Project CV-03 OCR Document Reader

---

## Azure Services for OCR Document Reading

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Document Intelligence**   | Extract text, tables, and forms from images and PDFs — replace Tesseract     | Replace your OpenCV + Tesseract + PyMuPDF pipeline |
| **Azure AI Vision — Read API**       | High-accuracy OCR for printed and handwritten text in images and PDFs        | When you need fast OCR without form extraction     |
| **Azure OpenAI Vision**              | GPT-4V for intelligent document understanding via prompt                     | When you need semantic understanding of documents  |

> **Azure AI Vision Read API** is the direct replacement for your OpenCV + Tesseract pipeline. It handles skewed images and PDFs with no preprocessing required.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, cv-service)        | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 4. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store uploaded documents and extracted text results                      |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track OCR latency, word counts, request volume                       |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure AI Vision Read API           │
│ CV Service :8001  │    │ Managed OCR — no Tesseract needed  │
│ OpenCV+Tesseract  │    │ Handles PDFs + images natively     │
│ +PyMuPDF          │    │                                    │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-ocr-reader --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-ocr-reader --name ocrreaderacr --sku Basic --admin-enabled true
az acr login --name ocrreaderacr
ACR=ocrreaderacr.azurecr.io
docker build -f docker/Dockerfile.cv-service -t $ACR/cv-service:latest ./cv-service
docker push $ACR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name ocr-env --resource-group rg-ocr-reader --location uksouth

az containerapp create \
  --name cv-service --resource-group rg-ocr-reader \
  --environment ocr-env --image $ACR/cv-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-ocr-reader \
  --environment ocr-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars CV_SERVICE_URL=http://cv-service:8001
```

---

## Option B — Use Azure AI Vision Read API

```python
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

client = ImageAnalysisClient(
    endpoint=os.getenv("AZURE_VISION_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_VISION_KEY"))
)

def extract_text(image_bytes: bytes) -> dict:
    result = client.analyze(
        image_data=image_bytes,
        visual_features=[VisualFeatures.READ]
    )
    lines, words = [], []
    if result.read:
        for block in result.read.blocks:
            for line in block.lines:
                lines.append(line.text)
                for word in line.words:
                    words.append({"text": word.text, "confidence": round(word.confidence * 100, 2)})
    return {"text": "\n".join(lines), "word_count": len(words), "words": words}
```

Add to requirements.txt: `azure-ai-vision-imageanalysis>=1.0.0`

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (cv-svc)  | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Azure AI Vision Read     | F0 free   | $0 (5k calls)     |
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$15–20/month** |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-ocr-reader --yes --no-wait
```

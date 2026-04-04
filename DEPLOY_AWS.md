# AWS Deployment Guide — Project CV-03 OCR Document Reader

---

## AWS Services for OCR Document Reading

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Textract**        | Extract text, tables, and forms from images and PDFs — replace Tesseract     | Replace your OpenCV + Tesseract + PyMuPDF pipeline |
| **Amazon Textract**        | Returns word-level bounding boxes, confidence scores, and page structure     | When you need structured text extraction           |
| **Amazon Bedrock**         | Claude Vision for intelligent document understanding via prompt              | When you need semantic understanding of documents  |

> **Amazon Textract** is the direct replacement for your OpenCV + Tesseract pipeline. It handles skewed images, tables, and forms with no preprocessing required.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + cv-service containers in a private VPC                | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 4. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded documents and extracted text results                       |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track OCR latency, word counts, request volume                            |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Textract                    │
│ CV Service :8001  │    │ Managed OCR — no Tesseract needed  │
│ OpenCV+Tesseract  │    │ Handles PDFs + images natively     │
│ +PyMuPDF          │    │                                    │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name ocrdoc/cv-service --region $AWS_REGION
aws ecr create-repository --repository-name ocrdoc/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.cv-service -t $ECR/ocrdoc/cv-service:latest ./cv-service
docker push $ECR/ocrdoc/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/ocrdoc/backend:latest ./backend
docker push $ECR/ocrdoc/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name ocrdoc-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/ocrdoc/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CV_SERVICE_URL": "http://cv-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Textract

```python
import boto3

textract = boto3.client("textract", region_name="eu-west-2")

def extract_text(file_bytes: bytes) -> dict:
    response = textract.detect_document_text(Document={"Bytes": file_bytes})
    lines = [b["Text"] for b in response["Blocks"] if b["BlockType"] == "LINE"]
    words = [
        {"text": b["Text"], "confidence": round(b["Confidence"], 2),
         "bounding_box": b["Geometry"]["BoundingBox"]}
        for b in response["Blocks"] if b["BlockType"] == "WORD"
    ]
    text = "\n".join(lines)
    return {"text": text, "word_count": len(words), "words": words, "pages": 1}
```

Add to requirements.txt: `boto3>=1.34.0`

---

## CI/CD — GitHub Actions

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-2
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -f docker/Dockerfile.backend \
            -t ${{ secrets.ECR_REGISTRY }}/ocrdoc/backend:${{ github.sha }} ./backend
          docker push ${{ secrets.ECR_REGISTRY }}/ocrdoc/backend:${{ github.sha }}
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (cv-service)    | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Amazon Textract            | Pay per page      | ~$1.50/1000 pages  |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$23–32/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name ocrdoc/backend --force
aws ecr delete-repository --repository-name ocrdoc/cv-service --force
```

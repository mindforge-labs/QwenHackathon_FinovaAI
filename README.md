# Finova AI

Finova AI is an AI-powered document intelligence platform designed to automate loan verification and KYC workflows for modern fintech systems.

The platform enables financial institutions to process customer documents such as ID cards, payslips, and bank statements with high accuracy and speed. By combining OCR, computer vision, and large language models, Finova AI transforms unstructured documents into structured, validated data ready for decision-making.

## 🚀 Key Features

- 📄 Intelligent document processing (IDP)
- 🔍 OCR with layout-aware text extraction
- 🧠 AI-powered structured data extraction (LLM-based)
- 🛡️ Validation engine for data consistency and risk flags
- 📊 Reviewer dashboard for human-in-the-loop verification
- ☁️ Scalable storage with S3-compatible object storage (MinIO)

## 🏗️ Tech Stack

- Frontend: Next.js
- Backend: FastAPI
- OCR: PaddleOCR
- Image Processing: OpenCV
- AI Extraction: LLM (structured JSON output)
- Database: PostgreSQL
- Storage: MinIO (S3-compatible)

## ☁️ Cloud Architecture

The Alibaba Cloud architecture set is organized as a multi-diagram narrative so each view stays readable and purpose-specific.

### 1. Cloud Overview

High-level view of the production footprint on Alibaba Cloud: edge entry, application tier, worker tier, and core managed services.

![Finova Cloud Overview](docs/cloud_architecture/img/01_finova_cloud_overview.png)

### 2. Async Processing Architecture

Core upload-to-processing path showing how Finova moves from synchronous API calls into asynchronous OCR, extraction, and validation.

![Finova Async Processing Architecture](docs/cloud_architecture/img/02_finova_async_processing_architecture.png)

### 3. Data Storage Architecture

Data placement view for transactional state, raw uploads, page artifacts, OCR outputs, extraction outputs, backup, and encryption boundaries.

![Finova Data Storage Architecture](docs/cloud_architecture/img/03_finova_data_storage_architecture.png)

### 4. Security Traffic Flow

North-south request path through DNS, CDN, WAF, Cloud Firewall, public entry, and user-facing runtime.

![Finova Security Traffic Flow](docs/cloud_architecture/img/04_finova_security_traffic_flow.png)

### 5. Security Architecture

Security control view for protected runtime, KMS, Security Center, audit logging, bastion access, and protected data services.

![Finova Security Architecture](docs/cloud_architecture/img/05_finova_security_architecture.png)

### 6. Deployment Architecture

Build and delivery view covering source control, pipeline, registry, infrastructure orchestration, and deployment targets.

![Finova Deployment Architecture](docs/cloud_architecture/img/06_finova_deployment_architecture.png)

Architecture sources and render scripts live in [docs/cloud_architecture/script](docs/cloud_architecture/script), and generated images live in [docs/cloud_architecture/img](docs/cloud_architecture/img).

## 🎯 Use Case

Finova AI is built to streamline loan application workflows by:
- reducing manual data entry
- accelerating document verification
- improving data accuracy
- enabling faster credit decisioning

## 💡 Vision

To become the intelligent infrastructure layer for document-driven financial services.

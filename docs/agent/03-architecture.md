---
title: Architecture
purpose: Describe the high-level system shape, end-to-end product flow, and the architectural constraints that keep the MVP simple.
load_when:
  - Load when changing system boundaries, backend/frontend integration, or end-to-end flow design.
depends_on:
  - 01-product-overview.md
  - 02-scope-priorities.md
source_of_truth: true
---

# Architecture

## High-Level Architecture

```text
Next.js Frontend
    |
    v
FastAPI Backend
    |
    +--> PostgreSQL
    +--> MinIO
    |
    +--> Processing Pipeline
          |- File normalization
          |- Image preprocessing (OpenCV)
          |- OCR (PaddleOCR)
          |- Document classification
          |- LLM structured extraction
          |- Validation engine
```

## Architecture Style

Use a modular monolith for the MVP.

Why this is the default:

- easier local development
- easier debugging
- simpler Docker Compose setup
- faster hackathon delivery
- less coordination overhead across incomplete services

Do not split the product into real microservices unless the scope and deployment model change materially.

## Core System Responsibilities

- The Next.js frontend handles application creation, upload flow, status visibility, and document review.
- The FastAPI backend owns orchestration, persistence, storage integration, and API contracts.
- PostgreSQL stores applications, documents, page artifacts, extraction results, validation flags, and review history.
- MinIO stores raw uploads, derived page images, processed images, and OCR or extraction artifacts.
- The processing pipeline normalizes files, runs OCR, classifies documents, extracts fields, and validates outcomes.

## End-To-End Product Flow

1. A user creates a loan application.
2. The user uploads one or more supporting documents.
3. The backend stores the raw file in MinIO and creates database records.
4. The backend triggers the processing pipeline for the document.
5. PDFs are converted into page images, while images are normalized into the same page model.
6. Each page is preprocessed with OpenCV before OCR.
7. PaddleOCR produces text, bounding boxes, and confidence signals.
8. OCR output is aggregated across pages and persisted.
9. The system classifies the document type.
10. An LLM extracts structured JSON fields using the document-specific schema.
11. Validation rules generate warnings or errors, including cross-document checks when relevant.
12. Results are persisted and exposed to the review UI.
13. A reviewer can correct fields, approve, reject, or request re-upload.

## Dependency Boundaries

- Keep API handlers thin and push business logic into services.
- Keep database access in repositories rather than route handlers.
- Keep document-processing steps composable so pipeline stages can be tested independently.
- Keep design-system concerns in frontend docs instead of mixing them into backend or API guidance.

## Architecture Reading Map

- Read [04-backend-structure.md](04-backend-structure.md) for service and repository boundaries.
- Read [08-storage-pipeline.md](08-storage-pipeline.md) for the document-processing stages.
- Read [07-api-contract.md](07-api-contract.md) for the public interface between frontend and backend.

## See Also

- [04-backend-structure.md](04-backend-structure.md)
- [07-api-contract.md](07-api-contract.md)
- [08-storage-pipeline.md](08-storage-pipeline.md)

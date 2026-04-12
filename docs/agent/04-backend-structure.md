---
title: Backend Structure
purpose: Define the recommended FastAPI project layout, layer ownership, and design rules for backend work.
load_when:
  - Load when implementing or refactoring backend routes, services, repositories, models, or prompts.
depends_on:
  - 03-architecture.md
  - 06-data-model.md
  - 07-api-contract.md
source_of_truth: true
---

# Backend Structure

## Recommended Folder Structure

```text
backend/
  app/
    main.py
    api/
      applications.py
      documents.py
      review.py
      health.py
    core/
      config.py
      db.py
      logging.py
      security.py
      s3.py
    models/
      application.py
      document.py
      document_page.py
      extraction.py
      validation.py
      review_action.py
    schemas/
      application.py
      document.py
      extraction.py
      review.py
      common.py
    services/
      application_service.py
      upload_service.py
      storage_service.py
      pdf_service.py
      preprocess_service.py
      ocr_service.py
      classification_service.py
      extraction_service.py
      validation_service.py
      review_service.py
      pipeline_service.py
    repositories/
      application_repository.py
      document_repository.py
      extraction_repository.py
      validation_repository.py
      review_repository.py
    utils/
      image_utils.py
      pdf_utils.py
      normalization_utils.py
      hashing_utils.py
    prompts/
      id_card_extraction.txt
      payslip_extraction.txt
      bank_statement_extraction.txt
    tests/
      ...
  Dockerfile
  requirements.txt
```

## Layer Responsibilities

- `api/`: HTTP routing, request validation, response serialization, status codes
- `core/`: configuration, database session setup, logging, security, MinIO helpers
- `models/`: SQLAlchemy ORM entities mapped to the persistence model
- `schemas/`: Pydantic request and response contracts
- `services/`: business logic and orchestration across repositories and external dependencies
- `repositories/`: focused persistence access for each aggregate or record type
- `utils/`: narrow helpers for image, PDF, normalization, and hashing tasks
- `prompts/`: extraction prompt templates per document type

## Design Rules

- Keep the API layer thin.
- Put business logic in services.
- Put database access in repositories.
- Use Pydantic schemas for API contracts.
- Use SQLAlchemy ORM for database models.
- Use Alembic for migrations.
- Prefer explicit names like `process_document`, `extract_fields_from_ocr`, and `store_file_to_minio`.
- Avoid vague function names such as `handle_data` or `do_task`.

## Backend Ownership Boundaries

- `upload_service.py` should stop at storage and document-record creation, then delegate pipeline orchestration.
- `pipeline_service.py` should coordinate normalization, preprocessing, OCR, classification, extraction, and validation.
- `review_service.py` should own reviewer corrections, decisions, and audit history persistence.
- Extraction prompt templates should stay separate from the parser and normalization code.

## Related Canonical Docs

- Read [06-data-model.md](06-data-model.md) for entity fields and statuses.
- Read [07-api-contract.md](07-api-contract.md) for endpoint behavior.
- Read [08-storage-pipeline.md](08-storage-pipeline.md) for file-processing stages.
- Read [09-classification-extraction.md](09-classification-extraction.md) for classification and JSON extraction rules.

## See Also

- [03-architecture.md](03-architecture.md)
- [06-data-model.md](06-data-model.md)
- [07-api-contract.md](07-api-contract.md)
- [08-storage-pipeline.md](08-storage-pipeline.md)

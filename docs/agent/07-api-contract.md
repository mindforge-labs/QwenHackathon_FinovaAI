---
title: API Contract
purpose: Define the required application, document, and review endpoints and their minimum response expectations.
load_when:
  - Load when designing or consuming FastAPI endpoints, frontend API clients, or integration tests.
depends_on:
  - 06-data-model.md
source_of_truth: true
---

# API Contract

## General API Rules

- Use typed request and response schemas.
- Return meaningful HTTP status codes and graceful API errors.
- Do not invent a separate API surface for the MVP beyond the required application, document, and review flows.
- Entity field names and status values come from [06-data-model.md](06-data-model.md).

## Applications

### `POST /applications`

Creates a new application.

Minimum response expectation:

- application identifier
- current application status
- created timestamp or equivalent metadata

### `GET /applications`

Lists applications.

Minimum response expectation:

- application summaries
- status per application
- created and updated timestamps

### `GET /applications/{application_id}`

Returns application detail with documents.

Minimum response expectation:

- application metadata
- related documents
- document status and type summary
- enough data to power the application detail page

## Documents

### `POST /applications/{application_id}/documents`

Uploads a document for an application.

Rules:

- accept multipart upload
- validate supported MIME type and file emptiness
- create the document record
- store the raw file in MinIO

Response should include:

- document id
- upload status

### `POST /documents/{document_id}/process`

Triggers processing for a document.

Minimum response expectation:

- document id
- current processing status
- acknowledgment that pipeline execution was requested

### `GET /documents/{document_id}`

Returns full document detail.

Minimum response expectation:

- document metadata
- OCR summary
- extraction JSON
- validation flags
- document status
- confidence values when available

### `GET /documents/{document_id}/pages`

Returns page previews or page metadata.

Minimum response expectation:

- page number
- preview or storage references for raw and processed images
- OCR availability per page

## Review

### `PATCH /documents/{document_id}/review`

Allows a reviewer to correct extracted fields.

Minimum response expectation:

- document id
- updated normalized extraction payload
- persisted review-action acknowledgment

### `POST /documents/{document_id}/decision`

Creates a review decision.

Supported actions:

- `approve`
- `reject`
- `request_reupload`

Minimum response expectation:

- document id
- resulting document status
- persisted review-action acknowledgment

## Contract Boundaries

- Validation rules live in [10-validation-edge-cases.md](10-validation-edge-cases.md).
- Storage and processing stages live in [08-storage-pipeline.md](08-storage-pipeline.md).
- Frontend rendering expectations live in [05-frontend-review-ui.md](05-frontend-review-ui.md).

## See Also

- [05-frontend-review-ui.md](05-frontend-review-ui.md)
- [06-data-model.md](06-data-model.md)
- [08-storage-pipeline.md](08-storage-pipeline.md)

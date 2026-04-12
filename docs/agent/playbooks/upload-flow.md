---
title: Upload Flow Playbook
purpose: Guide recurring work on application document upload, raw file persistence, status transitions, and intake API behavior.
load_when:
  - Load when implementing or changing application creation, document upload, storage handoff, or intake validation.
depends_on:
  - ../../../AGENTS.md
  - ../00-index.md
  - ../04-backend-structure.md
  - ../06-data-model.md
  - ../07-api-contract.md
  - ../08-storage-pipeline.md
status: active
last_updated: 2026-04-12
source_of_truth: false
---

# Upload Flow Playbook

## Goal

Change or implement the upload path without breaking application creation, raw-file storage, document-record creation, or initial status handling.

## Load This Context

- `AGENTS.md`
- `docs/agent/00-index.md`
- `docs/agent/04-backend-structure.md`
- `docs/agent/06-data-model.md`
- `docs/agent/07-api-contract.md`
- `docs/agent/08-storage-pipeline.md`

## Use This Playbook When

- adding or changing `POST /applications`
- adding or changing `POST /applications/{application_id}/documents`
- changing upload validation rules
- changing raw-file storage behavior or storage-key conventions
- changing the initial document lifecycle before OCR starts

## Entry Checklist

- confirm the task is still within MVP scope
- confirm supported file types remain `.jpg`, `.jpeg`, `.png`, `.pdf`
- confirm raw uploads must be preserved in MinIO
- confirm document and application statuses come from `docs/agent/06-data-model.md`

## Canonical Constraints

- the API layer stays thin and delegates business logic to services
- repositories own persistence access
- raw file must be stored before downstream processing depends on it
- initial document status should start at `uploaded`
- empty files and unsupported types must fail gracefully

## Recommended Execution Order

1. Review the affected endpoint contract in `docs/agent/07-api-contract.md`.
2. Review entity fields and statuses in `docs/agent/06-data-model.md`.
3. Review upload and storage requirements in `docs/agent/08-storage-pipeline.md`.
4. Place orchestration in `upload_service.py` and keep route handlers thin.
5. Persist the raw upload to MinIO with deterministic storage keys.
6. Create or update the document record and link it to the application.
7. Return the minimal upload response shape expected by the API contract.
8. Trigger downstream processing separately from the core upload persistence path.

## Implementation Checklist

- validate file emptiness and supported MIME type
- sanitize the incoming filename before persistence decisions
- compute a file hash when practical
- create or fetch the target application safely
- store the raw file under the canonical MinIO layout
- persist `file_name`, `mime_type`, `storage_key`, and `status`
- initialize document status as `uploaded`
- return `document id` and `upload status`

## Review Questions

- Does the upload still preserve the raw file even if later pipeline steps fail?
- Is any business logic leaking into the FastAPI route layer?
- Is storage-key generation deterministic and easy to inspect?
- Does the response payload match the documented minimum contract?
- Are failure cases visible through clear API errors instead of silent partial success?

## Common Failure Patterns

- writing directly from the route handler into storage and DB without a service boundary
- creating a document row before validating basic file constraints
- skipping raw-file preservation because processed pages also exist
- mutating status names ad hoc instead of using canonical values
- coupling upload success to synchronous OCR completion

## Minimum Validation Before Merge

- create an application successfully
- upload a supported image successfully
- upload a supported PDF successfully
- reject an unsupported file type with a meaningful error
- reject an empty file with a meaningful error
- verify MinIO received the raw object at the expected key
- verify PostgreSQL received the linked document metadata

## Done Criteria

- a caller can create an application and upload a document
- the raw file is preserved in MinIO
- the document record is persisted with the correct initial status
- the API response matches the documented contract
- upload failures are explicit and recoverable

## Refresh This Playbook When

- the upload endpoint contract changes
- the storage layout changes
- the status model changes
- the team introduces asynchronous job orchestration for upload handoff

## See Also

- [../07-api-contract.md](../07-api-contract.md)
- [../08-storage-pipeline.md](../08-storage-pipeline.md)
- [../../../roadmap.md](../../../roadmap.md)

# Finova AI Roadmap

This file is the end-to-end development plan for the MVP. Use the markdown checkboxes to track progress as we move from documentation and scaffolding to a full demo-ready intake and review flow.

## How To Use

- Keep this file high level and execution-oriented.
- Mark a task `[x]` only when the outcome is actually usable, not just partially started.
- Add child tasks in the relevant implementation doc or issue tracker if a checkbox becomes too large.
- Use `docs/agent/` as the source of truth for scope, architecture, API, pipeline, and validation rules.

## Current Status Snapshot

- [x] AI documentation split into task-oriented files under `docs/agent/`
- [x] `AGENTS.md` reduced to a short context router
- [x] Extraction schemas moved to `docs/agent/schemas/*.json`
- [x] Frontend design guidance moved to `docs/design/frontend-design-system.md`
- [x] `docs/agent/playbooks/` added for recurring task workflows
- [x] Backend application scaffold created
- [x] Frontend application scaffold created
- [ ] End-to-end demo flow implemented

## Milestone 0: Documentation Foundation

- [x] Replace monolithic `AGENTS.md` with a router + doc map
- [x] Create domain-focused docs under `docs/agent/`
- [x] Separate machine-readable extraction schemas from narrative docs
- [x] Move frontend design system into `docs/design/`
- [x] Validate task-based doc bundles for backend, frontend, and QA/demo work
- [x] Add `docs/agent/playbooks/` for common execution paths
- [x] Add one playbook for upload flow implementation
- [x] Add one playbook for OCR or pipeline debugging
- [x] Add one playbook for review UI changes

## Milestone 1: Local Dev And Project Scaffolding

- [x] Scaffold `backend/` with FastAPI app structure from `docs/agent/04-backend-structure.md`
- [x] Scaffold `frontend/` with Next.js app structure from `docs/agent/05-frontend-review-ui.md`
- [x] Add Dockerfiles for backend and frontend
- [x] Add `docker-compose.yml` with `frontend`, `backend`, `postgres`, `minio`
- [x] Add environment-variable configuration for DB, MinIO, and LLM settings
- [x] Add MinIO bucket initialization flow
- [x] Confirm the full stack boots locally with one command

## Milestone 2: Core Persistence And Storage

- [ ] Implement SQLAlchemy models for applications, documents, document pages, extracted fields, validation flags, and review actions
- [ ] Add Alembic migrations for the initial schema
- [ ] Implement database session and repository base patterns
- [x] Implement application and document repositories
- [x] Implement MinIO storage client and deterministic storage-key generation
- [x] Persist raw uploads to MinIO and document metadata to PostgreSQL

## Milestone 3: Upload And Intake API

- [x] Implement `POST /applications`
- [x] Implement `GET /applications`
- [x] Implement `GET /applications/{application_id}`
- [x] Implement `POST /applications/{application_id}/documents`
- [x] Validate supported file types and reject empty files
- [x] Compute file hash and prepare duplicate-upload detection hooks
- [x] Set initial document status to `uploaded`

## Milestone 4: File Normalization And OCR Pipeline

- [x] Implement `POST /documents/{document_id}/process`
- [x] Convert PDF uploads into page images
- [x] Normalize image uploads into the same page model
- [x] Preprocess pages with OpenCV
- [ ] Run PaddleOCR page by page
- [x] Persist `document_pages` records with OCR text and OCR JSON
- [x] Store OCR artifacts in MinIO
- [x] Compute and persist aggregate OCR confidence
- [x] Handle corrupted PDF, empty OCR output, and incomplete page conversion gracefully

## Milestone 5: Classification, Extraction, And Normalization

- [x] Implement rule-based document classification for `id_card`, `payslip`, and `bank_statement`
- [x] Support `unknown` classification with validation flags
- [x] Add document-specific extraction prompts
- [x] Integrate LLM extraction with strict JSON-only output validation
- [x] Validate extraction output against `docs/agent/schemas/*.json`
- [x] Retry once on invalid JSON output
- [x] Fall back to rule-based partial extraction when parsing still fails
- [x] Normalize dates, salary or balance fields, account numbers, and names
- [x] Persist raw and normalized extraction payloads

## Milestone 6: Validation And Confidence Routing

- [x] Implement field-level validation for ID card, payslip, and bank statement
- [x] Implement completeness warnings for important missing fields
- [x] Implement quality flags for low-quality image and OCR cases
- [x] Implement cross-document name checks across application documents
- [x] Compute `quality_score`, `ocr_confidence`, and `extraction_confidence`
- [x] Route documents into `processed`, `needs_review`, or `failed` based on outcome
- [x] Persist validation flags for reviewer visibility

## Milestone 7: Review API And Reviewer Actions

- [x] Implement `GET /documents/{document_id}`
- [x] Implement `GET /documents/{document_id}/pages`
- [x] Implement `PATCH /documents/{document_id}/review`
- [x] Implement `POST /documents/{document_id}/decision`
- [x] Persist reviewer corrections into review history
- [x] Persist reviewer decisions for `approve`, `reject`, and `request_reupload`
- [x] Keep review actions auditable in `review_actions`

## Milestone 8: Frontend Review Experience

- [x] Build applications list page
- [x] Build application detail page
- [x] Build document review page
- [x] Show upload status, document type, and warning summary on the application detail page
- [x] Show document preview, editable extracted fields, validation flags, and OCR raw text on the review page
- [x] Allow manual field correction before decision
- [x] Allow approve, reject, and request-reupload actions
- [x] Apply `docs/design/frontend-design-system.md` to the review workflow

## Milestone 9: Testing, QA, And Demo Readiness

- [x] Add upload endpoint test
- [x] Add PDF and image normalization test
- [x] Add OCR service integration-boundary test
- [x] Add extraction parser test
- [x] Add validation rule tests
- [ ] Add repository tests for the core persistence flow
- [x] Prepare sample documents for all three supported document types
- [ ] Rehearse the demo story from `docs/agent/02-scope-priorities.md`
- [ ] Verify reviewer can correct at least one field and approve successfully
- [ ] Verify low-confidence or invalid cases surface visible warnings instead of silent failure

## Stretch Goals

- [ ] OCR bounding-box overlay on the review screen
- [ ] Duplicate upload detection
- [ ] Simple image quality scoring heuristic
- [ ] Extraction retry observability or diagnostics
- [ ] Lightweight background-job orchestration if synchronous processing becomes too slow

## Done Definition For MVP

The MVP is done when all of these are true:

- [ ] A user can create an application
- [ ] A user can upload an ID card, a payslip, and a bank statement
- [ ] The system stores raw files and derived artifacts
- [ ] The system runs normalization, OCR, classification, extraction, and validation
- [ ] The review UI displays extracted fields, confidence signals, and validation flags
- [ ] A reviewer can correct a field and approve a document
- [x] The project runs locally with Docker Compose
- [ ] Core tests for upload, normalization, extraction, validation, and persistence exist

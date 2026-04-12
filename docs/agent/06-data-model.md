---
title: Data Model
purpose: Define the core entities, fields, statuses, and confidence signals used across the product.
load_when:
  - Load when designing persistence, API payloads, validation, or review UI data binding.
depends_on:
  - 01-product-overview.md
source_of_truth: true
---

# Data Model

## Entity Overview

The MVP data model centers on applications, uploaded documents, per-page OCR artifacts, structured extractions, validation flags, and human review history.

Primary relationships:

- one application has many documents
- one document has many document pages
- one document may have one current extracted field record plus review history
- one document may have many validation flags
- one document may have many review actions

## `applications`

Represents a loan application.

- `id`
- `applicant_name` nullable
- `phone` nullable
- `email` nullable
- `status`
- `created_at`
- `updated_at`

## `documents`

Represents an uploaded file.

- `id`
- `application_id`
- `file_name`
- `mime_type`
- `storage_key`
- `document_type` nullable
- `status`
- `quality_score` nullable
- `ocr_confidence` nullable
- `extraction_confidence` nullable
- `created_at`
- `updated_at`

Notes:

- `document_type` should ultimately resolve to `id_card`, `payslip`, `bank_statement`, or `unknown`.
- `storage_key` points to the raw uploaded object in MinIO.

## `document_pages`

Represents a single page or image artifact derived from a document.

- `id`
- `document_id`
- `page_number`
- `raw_image_storage_key`
- `processed_image_storage_key`
- `ocr_text`
- `ocr_json`
- `created_at`

## `extracted_fields`

Stores extraction results.

- `id`
- `document_id`
- `schema_version`
- `raw_extraction_json`
- `normalized_extraction_json`
- `created_at`
- `updated_at`

## `validation_flags`

Stores validation warnings and errors.

- `id`
- `document_id`
- `flag_code`
- `severity`
- `message`
- `field_name` nullable
- `created_at`

## `review_actions`

Stores human review history.

- `id`
- `document_id`
- `reviewer_name`
- `action`
- `comment`
- `corrected_json`
- `created_at`

## Status Model

Document statuses:

- `uploaded`
- `processing`
- `processed`
- `needs_review`
- `approved`
- `rejected`
- `failed`

Application statuses:

- `draft`
- `processing`
- `under_review`
- `approved`
- `rejected`

This file is the source of truth for status names. Other docs may refer to statuses but should not redefine them.

## Confidence Model

Track three confidence layers on each document:

1. `quality_score`
   Derived from image-quality checks such as blur, skew, rotation, or page completeness.
2. `ocr_confidence`
   Derived from PaddleOCR output, for example average line confidence or a weighted text-based aggregate.
3. `extraction_confidence`
   Derived heuristically from OCR quality, classification certainty, parse success, and field completeness.

Suggested routing:

- high confidence -> ready for review
- medium confidence -> needs review
- low confidence -> recommend re-upload or manual inspection

## Related Canonical Docs

- Read [07-api-contract.md](07-api-contract.md) for endpoint usage of these entities.
- Read [08-storage-pipeline.md](08-storage-pipeline.md) for how raw files and page artifacts map to storage keys.
- Read [10-validation-edge-cases.md](10-validation-edge-cases.md) for flag creation rules.

## See Also

- [07-api-contract.md](07-api-contract.md)
- [08-storage-pipeline.md](08-storage-pipeline.md)
- [10-validation-edge-cases.md](10-validation-edge-cases.md)

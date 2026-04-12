---
title: Storage And Pipeline
purpose: Define MinIO layout and the canonical upload-to-OCR pipeline, including artifact persistence expectations.
load_when:
  - Load when working on file uploads, MinIO integration, PDF or image normalization, preprocessing, OCR, or artifact storage.
depends_on:
  - 06-data-model.md
  - 09-classification-extraction.md
  - 10-validation-edge-cases.md
source_of_truth: true
---

# Storage And Pipeline

## MinIO Storage Layout

Use the bucket layout below:

```text
loan-docs/
  applications/{application_id}/raw/{document_id}/original
  applications/{application_id}/pages/{document_id}/{page_number}.jpg
  applications/{application_id}/processed/{document_id}/{page_number}.jpg
  applications/{application_id}/artifacts/{document_id}/ocr.json
  applications/{application_id}/artifacts/{document_id}/extraction.json
```

Storage requirements:

- raw file must always be preserved
- processed pages must be stored separately from raw page images
- OCR and extraction artifacts should also be saved
- use deterministic storage keys where possible

## Pipeline Overview

The document-processing pipeline should move a file from raw upload to persisted OCR, extraction, and validation outcomes.

Status names come from [06-data-model.md](06-data-model.md).

## Step 1: Upload

- accept multipart file upload
- validate MIME type and reject unsupported files
- reject empty files
- compute a file hash when possible
- store the raw file in MinIO
- create database records for the document
- initialize document status as `uploaded`

## Step 2: Normalize File

- if input is a PDF, convert all pages into images
- if input is an image, normalize it into the supported page-image format
- output should be a list of page images
- handle corrupted PDFs without crashing the service

## Step 3: Preprocess Image

Use OpenCV for page preparation:

- grayscale conversion
- denoise
- contrast enhancement
- thresholding when helpful
- deskew
- rotation correction
- optional document crop
- optional resize

## Step 4: OCR

Run PaddleOCR on each page and persist per-page OCR output with:

- `page_number`
- recognized `text`
- `bbox`
- confidence score per line or block

## Step 5: Aggregate OCR

- combine OCR text across pages
- preserve page number associations
- preserve bounding boxes
- persist raw OCR output as an artifact

Aggregate OCR confidence should be derived from PaddleOCR results, for example by averaging line confidence or using a weighted text-based heuristic.

## Step 6: Classification And Extraction Handoff

- pass aggregated OCR text to the document classifier
- pass the resolved document type and OCR text to the extraction stage
- if classification is unclear, allow `unknown` and raise a validation flag

Classification and extraction behavior is defined in [09-classification-extraction.md](09-classification-extraction.md).

## Step 7: Normalize Extracted Fields

Normalize extracted values after parsing:

- date format
- numeric salary or balance fields
- account number spacing
- name spacing or casing when helpful

## Step 8: Validation

- run field-level validation
- run completeness checks
- run cross-document checks when the application has multiple documents
- create validation flags instead of silently discarding issues

Validation rules are defined in [10-validation-edge-cases.md](10-validation-edge-cases.md).

## Step 9: Save Results

Persist:

- page artifacts
- OCR artifacts
- raw extraction JSON
- normalized extraction JSON
- validation flags
- confidence indicators
- final document status

## Failure And Recovery Expectations

- failed processing should not crash the backend service
- persist failure state on the document when pipeline execution cannot complete
- invalid extraction JSON should trigger retry and fallback behavior instead of a silent drop
- incomplete page conversion, empty OCR, and low-confidence OCR should generate reviewable signals

## Related Canonical Docs

- Read [06-data-model.md](06-data-model.md) for the fields that store artifacts and confidence values.
- Read [09-classification-extraction.md](09-classification-extraction.md) for classification and extraction behavior.
- Read [10-validation-edge-cases.md](10-validation-edge-cases.md) for flag creation and edge-case handling.

## See Also

- [06-data-model.md](06-data-model.md)
- [09-classification-extraction.md](09-classification-extraction.md)
- [10-validation-edge-cases.md](10-validation-edge-cases.md)

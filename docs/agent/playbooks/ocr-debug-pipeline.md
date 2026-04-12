---
title: OCR Debug Pipeline Playbook
purpose: Guide recurring debugging and implementation work across normalization, preprocessing, OCR, classification, extraction, and validation handoff.
load_when:
  - Load when OCR output is wrong, empty, low-confidence, or when the document-processing pipeline is being changed.
depends_on:
  - ../../../AGENTS.md
  - ../00-index.md
  - ../06-data-model.md
  - ../08-storage-pipeline.md
  - ../09-classification-extraction.md
  - ../10-validation-edge-cases.md
status: active
last_updated: 2026-04-12
source_of_truth: false
---

# OCR Debug Pipeline Playbook

## Goal

Diagnose and change the document-processing pipeline without losing page fidelity, OCR artifacts, classification signals, extraction integrity, or reviewer-visible flags.

## Load This Context

- `AGENTS.md`
- `docs/agent/00-index.md`
- `docs/agent/06-data-model.md`
- `docs/agent/08-storage-pipeline.md`
- `docs/agent/09-classification-extraction.md`
- `docs/agent/10-validation-edge-cases.md`

## Use This Playbook When

- OCR text is empty, low-quality, or misordered
- PDF pages do not convert correctly
- preprocessing hurts OCR more than it helps
- classification resolves to the wrong document type
- extraction returns invalid JSON or low-fill outputs
- validation flags are missing for obviously bad cases

## Pipeline Stages To Check In Order

1. raw upload availability
2. page normalization output
3. processed image quality after OpenCV steps
4. per-page PaddleOCR output with text, bbox, and confidence
5. aggregated OCR artifact
6. classification result and fallback behavior
7. extraction JSON parsing and normalization
8. validation flags and final status routing

## Stage-by-Stage Questions

### Normalization

- Did the PDF convert into the expected number of pages?
- Did image uploads normalize into the same page model as PDFs?
- Are page numbers stable and ordered?

### Preprocessing

- Did grayscale, denoise, thresholding, or deskew make text easier to read?
- Did rotation correction accidentally rotate a valid image into a worse orientation?
- Did cropping or resizing remove important fields?

### OCR

- Is there per-page OCR output for every page?
- Are bbox and confidence values persisted, not just plain text?
- Is OCR confidence low because the input is bad, or because preprocessing is harmful?

### Classification

- Do keyword and pattern rules still match the OCR text realistically?
- Should the document be `unknown` rather than incorrectly forced into a type?

### Extraction

- Does the LLM output parse as valid JSON?
- Does the output obey the target schema exactly?
- Did fallback extraction run after parse failure?

### Validation

- Are missing required fields generating visible warnings?
- Are low OCR confidence and empty OCR results generating quality flags?
- Are multi-page bank statements merged correctly before validation?

## Common Failure Patterns

- debugging extraction before checking whether OCR text is usable
- looking only at aggregated text and ignoring per-page artifacts
- forcing classification when `unknown` would be safer
- treating parse failure as a transport error instead of a reviewable extraction issue
- forgetting to persist OCR or extraction artifacts needed for later diagnosis

## Debug Checklist

- verify raw upload exists in MinIO
- verify page images exist for every expected page
- compare raw and processed page images
- inspect per-page OCR text and confidence
- inspect aggregated OCR artifact
- inspect document classification output
- inspect raw extraction JSON and normalized extraction JSON
- inspect validation flags and final document status

## Minimum Validation Before Merge

- single-image `id_card` processes end to end
- single-image `payslip` processes end to end
- multi-page `bank_statement` processes page by page and merges correctly
- invalid extraction JSON triggers retry and fallback behavior
- low-quality OCR produces reviewer-visible flags
- unclear classification can resolve to `unknown` without breaking review

## Done Criteria

- pipeline bugs can be localized to a specific stage quickly
- artifacts are persisted well enough to explain failures
- extraction failures do not disappear silently
- validation flags reflect real quality and completeness issues

## Refresh This Playbook When

- preprocessing strategy changes materially
- OCR provider or output shape changes
- extraction retry policy changes
- status routing or validation semantics change

## See Also

- [../08-storage-pipeline.md](../08-storage-pipeline.md)
- [../09-classification-extraction.md](../09-classification-extraction.md)
- [../10-validation-edge-cases.md](../10-validation-edge-cases.md)

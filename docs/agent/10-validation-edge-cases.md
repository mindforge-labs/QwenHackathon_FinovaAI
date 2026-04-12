---
title: Validation And Edge Cases
purpose: Define field validation, completeness checks, cross-document comparisons, quality flags, and edge cases the MVP must handle.
load_when:
  - Load when implementing validation logic, QA coverage, review workflows, or low-confidence handling.
depends_on:
  - 06-data-model.md
  - 09-classification-extraction.md
source_of_truth: true
---

# Validation And Edge Cases

## Validation Layers

The system should validate documents at multiple layers:

- field-level validation
- completeness validation
- quality validation
- cross-document validation when an application has multiple documents

## Field-Level Validation

### ID Card

- `id_number` should be 12 digits if present
- `dob` must be a valid date
- `issue_date` must be a valid date and not in the future

### Payslip

- `gross_salary` and `net_salary` must be positive numbers if present
- `net_salary <= gross_salary` if both are present
- `pay_period` must be parseable as a date or month period if present

### Bank Statement

- `account_number` should match an expected numeric or string pattern
- `ending_balance` should be numeric if present

## Completeness Validation

Create warnings when important fields are missing.

Examples:

- missing `full_name`
- missing `id_number`
- missing `net_salary`
- missing `account_holder`

## Quality Validation

Create quality-oriented flags for issues such as:

- blurry image
- low-light image
- skewed image
- rotated image
- cropped document
- glare or reflections
- OCR confidence too low
- empty OCR result
- incomplete page conversion

## Cross-Document Validation

If an application has multiple documents, compare:

- ID card `full_name` vs payslip `employee_name`
- ID card `full_name` vs bank statement `account_holder`

Suggested comparison strategy:

- normalize strings before comparison
- use string-similarity checks
- raise `NAME_MISMATCH` when similarity is too low

## Edge Cases That Must Be Handled

### Input Issues

- unsupported file type
- empty file
- corrupted PDF
- duplicate upload

### OCR Issues

- empty OCR output
- low OCR confidence
- broken line ordering
- OCR confusion between `0` and `O`
- OCR confusion between `1` and `I`

### Extraction Issues

- invalid JSON from the LLM
- missing required fields
- incorrect numeric parsing
- ambiguous dates

### Multi-Page Issues

- bank statements may have multiple pages
- OCR should run page by page
- final extraction must merge page results correctly

### Classification Issues

- document type unclear
- mixed-content pages
- unsupported document layout

### Review Issues

- reviewer edits field values
- reviewer can approve even when warnings exist
- review history must be persisted

## Validation Outcome Guidance

- Prefer visible validation flags over silent failure.
- Low-confidence or incomplete outcomes should route toward manual review.
- Validation should not block reviewers from correcting and approving a document when business judgment allows it.

## See Also

- [06-data-model.md](06-data-model.md)
- [08-storage-pipeline.md](08-storage-pipeline.md)
- [09-classification-extraction.md](09-classification-extraction.md)

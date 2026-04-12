---
title: Classification And Extraction
purpose: Define document classification rules, extraction behavior, JSON-only constraints, and retry or fallback handling.
load_when:
  - Load when working on classification heuristics, extraction prompts, parser validation, or schema alignment.
depends_on:
  - 06-data-model.md
  - schemas/id_card.schema.json
  - schemas/payslip.schema.json
  - schemas/bank_statement.schema.json
source_of_truth: true
---

# Classification And Extraction

## Supported Output Schemas

The extraction stage must target these machine-readable schemas:

- [schemas/id_card.schema.json](schemas/id_card.schema.json)
- [schemas/payslip.schema.json](schemas/payslip.schema.json)
- [schemas/bank_statement.schema.json](schemas/bank_statement.schema.json)

These schema files are the source of truth for extraction output shape.

## Classification Strategy

Use rules first, then fall back to an LLM only when the rule-based classifier is unclear.

Supported document-type outputs:

- `id_card`
- `payslip`
- `bank_statement`
- `unknown`

## Classification Hints

### `id_card`

- `CĂN CƯỚC`
- `CÔNG DÂN`
- 12-digit ID number patterns
- date-of-birth patterns

### `payslip`

- `salary`
- `basic salary`
- `net salary`
- `gross salary`
- `pay period`
- employer or employee wording

### `bank_statement`

- `statement`
- `account number`
- `balance`
- `transaction`
- bank names

## Unknown Handling

If confidence is low or no rule matches:

- set `document_type = unknown`
- create a validation flag
- allow manual review to continue

## Extraction Engine Rules

The LLM must behave like an extraction engine, not a chatbot.

Hard requirements:

- return valid JSON only
- obey the schema exactly
- use `null` when data is missing
- do not invent values
- do not infer unsupported facts
- do not return explanations, markdown, or commentary

## Prompting Guidance

Each supported document type should have its own extraction prompt template.

Prompt pattern:

> You are an information extraction engine.
> Extract structured fields from OCR text for document type X.
> Return valid JSON only.
> If a field cannot be found, use null.
> Do not guess.

## Post-Processing Rules

- always parse and validate LLM output server-side
- normalize dates after parsing
- normalize salary and balance fields into numeric form when possible
- normalize account number spacing
- normalize name spacing or casing when useful

## Retry And Fallback Logic

If JSON parsing fails:

- retry once with a stricter formatting prompt
- if parsing still fails, fall back to rule-based partial extraction
- create a validation flag so the issue is visible in review

If classification is unclear, prefer `unknown` over hallucinated document labels.

## Related Canonical Docs

- Read [08-storage-pipeline.md](08-storage-pipeline.md) for where classification and extraction sit in the pipeline.
- Read [10-validation-edge-cases.md](10-validation-edge-cases.md) for the flags and completeness checks applied after extraction.

## See Also

- [08-storage-pipeline.md](08-storage-pipeline.md)
- [10-validation-edge-cases.md](10-validation-edge-cases.md)
- [schemas/id_card.schema.json](schemas/id_card.schema.json)
- [schemas/payslip.schema.json](schemas/payslip.schema.json)
- [schemas/bank_statement.schema.json](schemas/bank_statement.schema.json)

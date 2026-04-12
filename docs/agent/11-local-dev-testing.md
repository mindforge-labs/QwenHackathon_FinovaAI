---
title: Local Dev And Testing
purpose: Define local setup, Docker Compose topology, environment variables, testing expectations, and non-functional engineering rules.
load_when:
  - Load when setting up the project locally, changing dev infrastructure, adding tests, or checking quality guardrails.
depends_on:
  - 02-scope-priorities.md
  - 03-architecture.md
source_of_truth: true
---

# Local Dev And Testing

## Local Development Requirements

The project must be runnable locally with Docker Compose.

Required services:

- frontend
- backend
- postgres
- minio

Optional services:

- `minio-init` for bucket initialization
- redis or a background worker only if it becomes truly necessary

## Environment Variables

The backend should support environment-based configuration for:

- postgres connection
- minio endpoint
- minio access key
- minio secret key
- minio bucket name
- llm api key
- llm model name

## Testing Expectations

Minimum automated coverage should include:

- upload endpoint test
- PDF and image normalization test
- OCR service integration boundary test
- extraction parser test
- validation rule tests
- repository tests for the core persistence flow

Do not over-invest in giant test suites for the hackathon, but core logic should remain testable and easy to verify.

## Non-Functional Requirements

### Code Quality

- readable code
- modular services
- type hints where practical
- clear naming
- no dead code
- no unnecessary abstractions

### Logging

Log key pipeline events:

- upload success
- MinIO storage success or failure
- OCR start and end
- extraction start and end
- validation results
- review actions

### Error Handling

- return graceful API errors
- use meaningful HTTP status codes
- failed processing should not crash the service
- persist failure state for documents

### Performance

This is an MVP, but avoid obviously slow or blocking designs where possible.

### Security

- validate upload type
- sanitize file names
- avoid arbitrary path writes
- keep secrets in environment variables

## Coding Conventions

General rules:

- prefer explicit code over clever code
- avoid premature optimization
- keep functions focused
- keep services composable
- return typed schemas where possible

Naming examples to prefer:

- `process_document`
- `extract_fields_from_ocr`
- `validate_id_card_fields`
- `store_file_to_minio`

Names to avoid:

- `handle_data`
- `do_task`
- `process_everything`

## See Also

- [02-scope-priorities.md](02-scope-priorities.md)
- [03-architecture.md](03-architecture.md)
- [07-api-contract.md](07-api-contract.md)

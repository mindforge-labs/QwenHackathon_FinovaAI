---
title: Scope And Priorities
purpose: Define what the MVP must include, what it may include later, and which trade-offs win when time is limited.
load_when:
  - Load when planning scope, making trade-offs, or preparing the demo story.
depends_on:
  - 01-product-overview.md
source_of_truth: true
---

# Scope And Priorities

## Core Features In Scope

The MVP should support these user-facing capabilities:

- create a loan application
- upload one or more application documents
- store raw files in MinIO
- normalize PDFs and images into page artifacts
- preprocess images for OCR with OpenCV
- run PaddleOCR with text and bounding boxes
- classify documents into the supported types
- extract structured JSON fields
- validate extracted data with business rules
- display results in a review UI
- allow reviewer correction and approval decisions

## Implementation Priorities

### Priority 1: Must Have

- upload flow
- MinIO storage
- PostgreSQL persistence
- PDF and image normalization
- OpenCV preprocessing
- PaddleOCR integration
- document classification
- LLM structured extraction
- validation flags
- basic review UI

### Priority 2: Strongly Recommended

- OCR artifact storage
- confidence scores
- cross-document validation
- review correction persistence

### Priority 3: Nice To Have

- OCR bounding box overlay
- duplicate upload detection
- simple quality scoring
- retry handling for extraction failures

## Trade-Off Rule

When time or complexity forces a choice, prioritize:

- working upload, process, and review flow
- simple architecture
- clarity
- demo reliability

Do not prioritize:

- over-engineering
- unnecessary microservices
- excessive abstractions
- speculative features

## Out Of Scope

Do not implement these for the MVP unless the scope is explicitly expanded:

- full user authentication or RBAC
- production-grade distributed queueing
- advanced fraud detection
- model training pipelines
- full observability stack
- complicated access control
- enterprise workflow engines
- support for many document types beyond the defined three

## Demo Expectations

The demo should tell this exact story:

1. Create an application.
2. Upload an ID card, a payslip, and a bank statement.
3. Let the system process the files.
4. Open the review page.
5. Show extracted structured fields.
6. Show validation flags.
7. Correct a field if needed.
8. Approve the document or application.

This story matters more than fancy infrastructure or speculative automation.

## See Also

- [01-product-overview.md](01-product-overview.md)
- [03-architecture.md](03-architecture.md)
- [11-local-dev-testing.md](11-local-dev-testing.md)

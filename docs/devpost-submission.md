# Finova AI Devpost Submission Draft

This file converts the canonical `docs/agent` context into Devpost-ready content. Public-facing fields are written in English for direct paste into the submission form.

## Project Overview

### Project name

Finova AI

### Elevator pitch

Finova AI turns loan documents into structured, validated data with OCR, AI extraction, and a human review workflow built for fast, reliable lending operations.

## Project Details

### About the project

```md
## Inspiration

Loan operations still spend too much time manually reading ID cards, payslips, and bank statements before an application can move forward. We wanted to build something more useful than a generic OCR demo: a focused intake and verification workflow that helps lending teams turn messy uploaded files into structured, reviewable data with clear validation signals.

## What it does

Finova AI is an AI-powered document intake and verification platform for lending workflows. A reviewer can create an application, upload supported documents, and let the system process them end to end. The platform preserves the raw files, converts PDFs and images into page artifacts, preprocesses them with OpenCV, runs PaddleOCR, classifies each document, extracts structured JSON fields, applies validation rules, and presents the results in a review UI where a human can correct and approve the outcome.

In this MVP, we focus on three high-value document types: ID cards, payslips, and bank statements. The system extracts key fields such as identity information, salary details, and bank account data, then surfaces confidence signals and validation flags so low-quality or inconsistent cases do not stay hidden.

## How we built it

We built Finova AI as a modular monolith optimized for hackathon delivery and demo reliability. The frontend is built with Next.js and the backend is built with FastAPI. PostgreSQL stores applications, documents, extraction results, validation flags, and review history. MinIO stores raw uploads plus OCR and extraction artifacts.

Our processing pipeline follows a clear sequence:

1. Upload and store the raw file.
2. Normalize PDF or image inputs into per-page images.
3. Preprocess each page with OpenCV.
4. Run PaddleOCR to capture text, bounding boxes, and confidence signals.
5. Aggregate OCR results across pages.
6. Classify the document type.
7. Extract schema-aligned JSON fields with an LLM.
8. Normalize values and run validation checks.
9. Send everything to the review UI for correction and approval.

This architecture keeps the product simple to run locally with Docker Compose while still covering the full intake-to-review story.

## Challenges we ran into

The hardest part was not OCR alone, but building a reliable pipeline around it. Lending documents arrive as different file types, page counts, and quality levels, so we had to handle normalization, preprocessing, and multi-page aggregation carefully. We also had to make the extraction stage strict enough to return valid JSON only, because free-form model output is not acceptable in a financial workflow.

Another challenge was deciding where automation should stop. Instead of pretending every extraction is perfect, we designed the product to expose low-confidence OCR, missing fields, and cross-document mismatches so human reviewers can make the final call.

## Accomplishments that we're proud of

We are proud that Finova AI is shaped like a real lending operations tool instead of a one-off AI prototype. The MVP supports the complete demo path: create an application, upload documents, process them, inspect extracted fields, review validation flags, correct data, and approve or reject the result.

We are also proud of the product boundaries we kept. We limited the scope to the three most important document types, preserved raw files and derived artifacts separately, and kept the architecture simple enough to be locally runnable while still demonstrating OCR, AI extraction, validation, and human-in-the-loop review.

## What we learned

We learned that the most valuable AI workflow is not the one with the most automation, but the one that makes uncertainty visible. Confidence scores, validation flags, and review history matter just as much as extraction accuracy when the output is used for credit and verification decisions.

We also learned that a modular monolith is the right trade-off for an MVP like this. It is easier to debug, easier to demo, and much faster to iterate on than a more fragmented architecture.

## What's next for Finova AI

Next, we want to improve extraction robustness on noisy real-world documents, expand duplicate and quality detection, strengthen cross-document validation, and make the reviewer experience faster with better page previews and overlays. After the MVP, we also want to evaluate production-grade deployment patterns, deeper risk signals, and broader financial document support without losing the clarity of the current intake-to-review workflow.
```

### Built with

Next.js, FastAPI, PaddleOCR, OpenCV, PostgreSQL, MinIO, LLM structured extraction, Docker Compose

### Try it out links

- GitHub repository: https://github.com/mindforge-labs/QwenHackathon_FinovaAI
- Public demo URL: `TBD` (no hosted URL found in `docs/agent` or `README.md`)

## Media And Assets

### Suggested image gallery shots

- Application creation and document upload flow
- OCR and extracted field review screen
- Validation flags and confidence signals
- End-to-end pipeline or architecture diagram

### Video demo link

`TBD` (no YouTube, Vimeo, or other public video URL found in the repo context)

## Additional Info

### Upload a file

No canonical file was defined in `docs/agent`. If Devpost requires an attachment, the safest option is a short architecture or demo PDF exported from the repo materials.

### Sponsor / Special Prizes

Track Winner - Financial Services Track by Shinhan Future's Lab

### In-person attendance on 21 April 2026 in Ho Chi Minh City

Needs team confirmation. This cannot be derived from `docs/agent`, so do not submit a final answer for this field without checking with the team.

## Source Basis

This draft was derived from:

- `AGENTS.md`
- [docs/agent/01-product-overview.md](./agent/01-product-overview.md)
- [docs/agent/02-scope-priorities.md](./agent/02-scope-priorities.md)
- [docs/agent/03-architecture.md](./agent/03-architecture.md)
- [docs/agent/06-data-model.md](./agent/06-data-model.md)
- [docs/agent/07-api-contract.md](./agent/07-api-contract.md)
- [docs/agent/08-storage-pipeline.md](./agent/08-storage-pipeline.md)
- [docs/agent/09-classification-extraction.md](./agent/09-classification-extraction.md)
- [docs/agent/10-validation-edge-cases.md](./agent/10-validation-edge-cases.md)
- [docs/agent/11-local-dev-testing.md](./agent/11-local-dev-testing.md)

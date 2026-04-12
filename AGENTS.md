---
title: AI Context Router
purpose: Route agents to the minimum useful context set and define repo-wide hard constraints.
load_when:
  - Always load first for any task in this repo.
depends_on: []
source_of_truth: false
---

# AI Context Router

## Mission

Build Finova AI as an MVP document intake and verification platform for lending workflows. Optimize for a reliable end-to-end demo, not a generic OCR playground.

## Hard Constraints

- Required stack: Next.js, FastAPI, PaddleOCR, OpenCV, PostgreSQL, MinIO S3.
- Keep a modular monolith. Do not split into microservices for the MVP.
- Support only `id_card`, `payslip`, and `bank_statement`.
- Support only `.jpg`, `.jpeg`, `.png`, and `.pdf` uploads.
- LLM extraction must return valid JSON only. No markdown, no commentary, no free-form answers.
- Preserve raw uploaded files and store OCR and extraction artifacts separately.
- The app must run locally with Docker Compose.
- `README.md` stays human-facing. AI operating rules live in `AGENTS.md` and `docs/agent/`.
- `docs/design/frontend-design-system.md` is not default context for backend, OCR, pipeline, or API tasks.

## MVP Priorities

- Keep the upload -> process -> review flow working end to end.
- Prefer clarity, demo reliability, and simple architecture over extra infrastructure.
- Keep one source of truth per rule. Link to the canonical file instead of duplicating it.
- Narrative guidance lives in `docs/agent/*.md`. Machine-readable extraction contracts live in `docs/agent/schemas/*.json`.
- If trade-offs are unclear, follow [docs/agent/02-scope-priorities.md](docs/agent/02-scope-priorities.md).

## Load The Right Docs

- Start with [docs/agent/00-index.md](docs/agent/00-index.md) for the task map.
- Backend pipeline, OCR, classification, or extraction tasks:
  `00-index`, `06-data-model`, `08-storage-pipeline`, `09-classification-extraction`, `10-validation-edge-cases`
- Backend API or service-structure tasks:
  `00-index`, `04-backend-structure`, `06-data-model`, `07-api-contract`, plus any domain-specific doc
- Frontend review UI tasks:
  `00-index`, `05-frontend-review-ui`, `06-data-model`, `07-api-contract`, `docs/design/frontend-design-system.md`
- QA, demo, acceptance, or release-readiness tasks:
  `00-index`, `02-scope-priorities`, `07-api-contract`, `10-validation-edge-cases`, `11-local-dev-testing`
- Local setup or infra tasks:
  `00-index`, `08-storage-pipeline`, `11-local-dev-testing`

## Global Do

- Load only the smallest relevant bundle, usually 2-5 files plus this router.
- Treat [docs/agent/06-data-model.md](docs/agent/06-data-model.md) as the source of truth for entities, statuses, and confidence fields.
- Treat [docs/agent/07-api-contract.md](docs/agent/07-api-contract.md) as the source of truth for API endpoints and response expectations.
- Treat [docs/agent/09-classification-extraction.md](docs/agent/09-classification-extraction.md) and `docs/agent/schemas/*.json` as the source of truth for extraction behavior and output shape.
- Add cross-links when a new doc depends on another canonical doc.

## Global Don't

- Don't re-introduce a single mega-spec that mixes product, architecture, API, testing, and UI rules.
- Don't duplicate priorities, out-of-scope rules, or the demo story across multiple files.
- Don't load the frontend design system for non-frontend tasks unless the task explicitly changes visuals.
- Don't add new document types, speculative infrastructure, or production-grade workflow engines to the MVP baseline.

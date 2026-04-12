---
title: AI Docs Index
purpose: Map tasks to the smallest useful documentation bundle and explain when each AI doc should be loaded.
load_when:
  - Load after AGENTS.md for any non-trivial task.
depends_on:
  - ../../AGENTS.md
source_of_truth: true
---

# AI Docs Index

## How To Use This Set

- Load [../../AGENTS.md](../../AGENTS.md) first.
- Then load only the docs that answer the active task.
- Prefer the canonical domain doc instead of scanning everything.
- If a rule already exists elsewhere, link to it instead of copying it.
- Machine-readable extraction output lives in [schemas/](schemas/), not in narrative markdown.

## Recommended Load Bundles

- Product framing or task scoping:
  [01-product-overview.md](01-product-overview.md), [02-scope-priorities.md](02-scope-priorities.md), [03-architecture.md](03-architecture.md)
- Backend API design:
  [04-backend-structure.md](04-backend-structure.md), [06-data-model.md](06-data-model.md), [07-api-contract.md](07-api-contract.md)
- File intake, OCR, and extraction pipeline:
  [06-data-model.md](06-data-model.md), [08-storage-pipeline.md](08-storage-pipeline.md), [09-classification-extraction.md](09-classification-extraction.md), [10-validation-edge-cases.md](10-validation-edge-cases.md)
- Frontend review dashboard:
  [05-frontend-review-ui.md](05-frontend-review-ui.md), [06-data-model.md](06-data-model.md), [07-api-contract.md](07-api-contract.md), [../design/frontend-design-system.md](../design/frontend-design-system.md)
- QA, demo rehearsal, and acceptance checks:
  [02-scope-priorities.md](02-scope-priorities.md), [07-api-contract.md](07-api-contract.md), [10-validation-edge-cases.md](10-validation-edge-cases.md), [11-local-dev-testing.md](11-local-dev-testing.md)
- Local setup and developer experience:
  [03-architecture.md](03-architecture.md), [08-storage-pipeline.md](08-storage-pipeline.md), [11-local-dev-testing.md](11-local-dev-testing.md)

## File Map

| File | Primary Questions Answered | Load When |
| --- | --- | --- |
| [01-product-overview.md](01-product-overview.md) | What product are we building? Who is it for? Which docs and inputs are in scope? | Business framing, onboarding, planning |
| [02-scope-priorities.md](02-scope-priorities.md) | What is in scope for the MVP? What matters most for the demo? What is out of scope? | Trade-off decisions, roadmap pruning, demo prep |
| [03-architecture.md](03-architecture.md) | How does the system fit together? Why a modular monolith? What is the end-to-end product flow? | Architecture, system design, integration planning |
| [04-backend-structure.md](04-backend-structure.md) | How should the FastAPI backend be organized? Which layer owns which responsibility? | Backend refactors, API/service/repository work |
| [05-frontend-review-ui.md](05-frontend-review-ui.md) | Which frontend pages and behaviors are required? What must the review UI show? | Next.js app structure and review workflow changes |
| [06-data-model.md](06-data-model.md) | Which entities, fields, statuses, and confidence signals exist? | Persistence, schemas, status handling, UI data binding |
| [07-api-contract.md](07-api-contract.md) | Which endpoints must exist, and what do they return? | API design, integration, mock generation, FE-BE alignment |
| [08-storage-pipeline.md](08-storage-pipeline.md) | How are files stored and processed from upload through OCR artifacts? | Storage, normalization, preprocessing, OCR pipeline work |
| [09-classification-extraction.md](09-classification-extraction.md) | How are docs classified and how must extraction behave? | Classification rules, prompt design, parser logic |
| [10-validation-edge-cases.md](10-validation-edge-cases.md) | Which validation rules and edge cases must be handled? | Validation engine, quality flags, QA coverage |
| [11-local-dev-testing.md](11-local-dev-testing.md) | How should local setup, env vars, testing, logging, and conventions work? | Docker Compose, onboarding, tests, quality guardrails |

## Default Exclusions

- Do not load [../design/frontend-design-system.md](../design/frontend-design-system.md) for backend, OCR, API, storage, or validation tasks.
- Do not load every domain file "just in case"; the point is selective context.
- `README.md` is for human overview, not AI operating instructions.

## Acceptance Bundles

- Backend pipeline task should be solvable with:
  `AGENTS.md`, `00-index`, `06`, `08`, `09`, `10`
- Frontend review task should be solvable with:
  `AGENTS.md`, `00-index`, `05`, `07`, `06`, `docs/design/frontend-design-system.md`
- QA or demo task should be solvable with:
  `AGENTS.md`, `02`, `07`, `10`, `11`

## See Also

- [01-product-overview.md](01-product-overview.md)
- [03-architecture.md](03-architecture.md)

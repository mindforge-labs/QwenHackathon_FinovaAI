---
title: Playbooks Index
purpose: Define what playbooks are for, how to track them, and which playbooks should exist for the MVP.
load_when:
  - Load when creating, updating, or choosing a task-specific execution playbook.
depends_on:
  - ../../../AGENTS.md
  - ../00-index.md
  - ../02-scope-priorities.md
source_of_truth: true
---

# Playbooks Index

## What A Playbook Is

A playbook is a task-specific execution guide for recurring engineering work.

Use a playbook when a task type shows up repeatedly and benefits from a stable checklist, a fixed doc bundle, and a predictable validation path.

Examples:

- implementing the upload flow
- debugging the OCR or extraction pipeline
- changing the review UI without breaking API expectations

## What A Playbook Is Not

- It is not the end-to-end product plan. That lives in [`roadmap.md`](../../../roadmap.md).
- It is not the source of truth for product rules. Canonical rules live in `docs/agent/*.md`.
- It is not a dumping ground for design notes or one-off debugging logs.

## Relationship To `roadmap.md`

- [`roadmap.md`](../../../roadmap.md) tracks product delivery progress across the whole MVP.
- `docs/agent/playbooks/` tracks reusable execution guides for recurring task types.
- A roadmap item can link to one or more playbooks.
- A playbook can stay useful even after the related roadmap item is complete.

## How To Track Playbook Status

Each playbook should have:

- a markdown checkbox in this index for creation status
- a `status` field inside the playbook metadata
- a `last_updated` date inside the playbook metadata when it becomes active

Recommended status values:

- `planned`
- `drafting`
- `active`
- `stable`
- `needs_refresh`

Meaning:

- `planned`: playbook does not exist yet, but we know we need it
- `drafting`: file exists and is being shaped
- `active`: usable now, but likely to evolve as the implementation moves
- `stable`: routinely usable and aligned with the current architecture
- `needs_refresh`: exists, but no longer fully aligned with the current codebase or docs

## Playbook Creation Rule

Create a playbook only if the task type is:

- likely to repeat
- cross-cutting across multiple docs or layers
- easy to get wrong without a checklist
- important enough to merit a stable workflow

Do not create a playbook for every small task. The goal is a compact, high-value library.

## Recommended MVP Playbooks

### Priority 1

- [x] [`upload-flow.md`](upload-flow.md)
  Current status: `active`
  Covers application document upload, storage, status transitions, and intake API behavior.
- [x] [`ocr-debug-pipeline.md`](ocr-debug-pipeline.md)
  Current status: `active`
  Covers normalization, preprocessing, OCR, extraction handoff, and artifact debugging.
- [x] [`review-ui-change.md`](review-ui-change.md)
  Current status: `active`
  Covers review-page changes, API alignment, data binding, and design-system usage.

### Priority 2

- [ ] `api-contract-change.md`
  Status target: `planned`
  Covers endpoint changes, schema updates, and frontend-backend contract checks.
- [ ] `validation-rules-change.md`
  Status target: `planned`
  Covers validation logic updates, cross-document checks, and reviewer-visible flags.

### Optional

- [ ] `local-dev-debug.md`
  Status target: `planned`
  Covers Docker Compose bring-up, env issues, storage connectivity, and local troubleshooting.

## Suggested Load Bundles Per Playbook

### `upload-flow.md`

- `AGENTS.md`
- `docs/agent/00-index.md`
- `docs/agent/04-backend-structure.md`
- `docs/agent/06-data-model.md`
- `docs/agent/07-api-contract.md`
- `docs/agent/08-storage-pipeline.md`

### `ocr-debug-pipeline.md`

- `AGENTS.md`
- `docs/agent/00-index.md`
- `docs/agent/06-data-model.md`
- `docs/agent/08-storage-pipeline.md`
- `docs/agent/09-classification-extraction.md`
- `docs/agent/10-validation-edge-cases.md`

### `review-ui-change.md`

- `AGENTS.md`
- `docs/agent/00-index.md`
- `docs/agent/05-frontend-review-ui.md`
- `docs/agent/06-data-model.md`
- `docs/agent/07-api-contract.md`
- `docs/design/frontend-design-system.md`

## Maintenance Rules

- Update this index when a playbook is added, renamed, or retired.
- If a playbook conflicts with a canonical doc, fix the playbook and keep the canonical doc as the source of truth.
- If architecture or API changes invalidate a playbook, set it to `needs_refresh`.
- Prefer 3-5 high-value playbooks for the MVP instead of a large library.

## Next Recommended Step

Use and refine the active playbooks above. Add the next playbooks only when the task pattern becomes recurring:

1. `api-contract-change.md`
2. `validation-rules-change.md`
3. `local-dev-debug.md` if local troubleshooting becomes a recurring bottleneck

## See Also

- [../../../roadmap.md](../../../roadmap.md)
- [../00-index.md](../00-index.md)
- [../02-scope-priorities.md](../02-scope-priorities.md)

---
title: Review UI Change Playbook
purpose: Guide recurring work on the review experience, including data binding, API alignment, reviewer actions, and design-system consistency.
load_when:
  - Load when changing the applications list, application detail page, document review page, or reviewer actions.
depends_on:
  - ../../../AGENTS.md
  - ../00-index.md
  - ../05-frontend-review-ui.md
  - ../06-data-model.md
  - ../07-api-contract.md
  - ../../design/frontend-design-system.md
status: active
last_updated: 2026-04-12
source_of_truth: false
---

# Review UI Change Playbook

## Goal

Change the frontend review experience without breaking required page behavior, API expectations, reviewer actions, or the intended visual system.

## Load This Context

- `AGENTS.md`
- `docs/agent/00-index.md`
- `docs/agent/05-frontend-review-ui.md`
- `docs/agent/06-data-model.md`
- `docs/agent/07-api-contract.md`
- `docs/design/frontend-design-system.md`

## Use This Playbook When

- changing the applications list page
- changing the application detail page
- changing the document review page
- adding or updating field-edit forms
- changing reviewer decision actions
- restyling the review workflow

## Canonical UI Constraints

- the application detail page must show uploaded documents, per-document status, document type, and warning summary
- the review page must show document preview, editable extracted fields, validation flags, OCR raw text, and reviewer actions
- reviewers must be able to correct values before making a decision
- reviewers must be able to approve even when warnings exist
- design guidance comes from `docs/design/frontend-design-system.md`, but product behavior comes from `docs/agent/*.md`

## Recommended Execution Order

1. Review the target page requirements in `docs/agent/05-frontend-review-ui.md`.
2. Review the data shape and status names in `docs/agent/06-data-model.md`.
3. Review the endpoint contract in `docs/agent/07-api-contract.md`.
4. Map the UI change to the affected page, component, hook, and API client surfaces.
5. Apply design-system updates only after confirming the interaction and data flow.
6. Re-check reviewer correction and decision flows end to end.

## Implementation Checklist

- keep required page content visible after the change
- preserve explicit status and warning visibility
- preserve editable extracted fields on the review page
- preserve OCR raw text visibility for reviewer inspection
- keep approve, reject, and request-reupload actions reachable
- reflect canonical status names and confidence values correctly
- avoid introducing visual patterns that conflict with the design system

## Review Questions

- Does the UI still expose the full review context, not just extracted fields?
- Did any API assumption drift away from the backend contract?
- Can a reviewer still correct data and approve from the same workflow?
- Are low-confidence and validation states clearly visible?
- Did the visual change stay within the intended frontend design language?

## Common Failure Patterns

- hiding OCR raw text because the page feels crowded
- replacing warning visibility with subtle styling that reviewers miss
- hardcoding field shapes that drift from the canonical data model
- shipping a UI-only edit state without persisting corrections through the review API
- importing the design system into non-frontend tasks as if it were a behavior spec

## Minimum Validation Before Merge

- applications list still renders application summaries cleanly
- application detail still shows documents, statuses, types, and warning summary
- review page still shows preview, editable extracted fields, flags, OCR text, and actions
- reviewer can submit a correction through `PATCH /documents/{document_id}/review`
- reviewer can approve, reject, or request reupload through `POST /documents/{document_id}/decision`
- visual changes remain consistent with the design-system guidance

## Done Criteria

- required pages and behaviors remain intact
- API-backed review actions still work end to end
- validation and confidence states are visible to the reviewer
- visual updates feel intentional and consistent with the established design direction

## Refresh This Playbook When

- frontend routing or page structure changes materially
- review API contract changes
- the data model for reviewable fields changes
- the design system is replaced or heavily revised

## See Also

- [../05-frontend-review-ui.md](../05-frontend-review-ui.md)
- [../07-api-contract.md](../07-api-contract.md)
- [../../design/frontend-design-system.md](../../design/frontend-design-system.md)

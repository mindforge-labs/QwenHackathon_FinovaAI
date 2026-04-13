---
title: Frontend Review UI
purpose: Define the Next.js app structure, required pages, review behaviors, and when to load the design-system reference.
load_when:
  - Load when building or changing the Next.js application, especially the application detail and review experience.
depends_on:
  - 06-data-model.md
  - 07-api-contract.md
  - ../design/frontend-design-system.md
source_of_truth: true
---

# Frontend Review UI

## Recommended Frontend Structure

```text
frontend/
  src/
    app/
      applications/
        page.tsx
        [id]/
          page.tsx
      review/
        [documentId]/
          page.tsx
    components/
      upload/
      document/
      review/
      common/
    lib/
      api.ts
      types.ts
      utils.ts
    hooks/
      useApplications.ts
      useDocument.ts
      useReview.ts
```

## Required Pages

- Applications list page
- Application detail page
- Document review page

## Required Behaviors

- upload one or more files for an application
- show processing status per document
- show the detected document type
- show extracted fields in structured form
- show validation flags and warning summaries
- show document preview for image or PDF content
- allow manual correction and approval decisions

## Application Detail Requirements

The application detail page must show:

- uploaded documents
- processing status per document
- document type
- quality or warning summary
- aggregate counters that match the dashboard and come from backend responses, not client-side mock calculations

This page should let reviewers understand which documents are ready, still processing, or need review before they open the full review screen.

## Review Page Requirements

The review page must show:

- document preview
- extracted fields in editable form
- validation flags
- OCR raw text section
- reviewer actions
- backend-backed timeline of upload, OCR, extraction, validation, and review events
- backend-backed field highlight metadata when OCR geometry is available

Nice to have, but not required for the MVP:

- richer OCR bounding box overlay on the image
- highlighting of suspicious or missing fields

## Frontend Data Dependencies

- Use [06-data-model.md](06-data-model.md) as the source of truth for fields, statuses, and confidence values.
- Use [07-api-contract.md](07-api-contract.md) as the source of truth for route shapes and response payload expectations.
- Use [../design/frontend-design-system.md](../design/frontend-design-system.md) only for frontend visual and interaction work.

## UI Behavior Notes

- Reviewers should be able to correct extracted values before making a decision.
- Reviewers should be able to approve even when warnings exist.
- Review history must remain visible through backend-backed data, not only local UI state.
- The UI should surface low-confidence and validation issues rather than hiding them behind success states.
- Dashboard metrics and next-review shortcuts should prefer enriched backend summaries over frontend N+1 fetching or inferred mock-like counters.

## See Also

- [06-data-model.md](06-data-model.md)
- [07-api-contract.md](07-api-contract.md)
- [../design/frontend-design-system.md](../design/frontend-design-system.md)

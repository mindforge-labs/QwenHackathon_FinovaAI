---
title: Product Overview
purpose: Define the product mission, business goal, and hard in-scope document and input boundaries for Finova AI.
load_when:
  - Load when you need project framing, business context, or scope boundaries.
depends_on:
  - 02-scope-priorities.md
  - 03-architecture.md
source_of_truth: true
---

# Product Overview

## What We Are Building

Finova AI is an AI-powered document intake and verification platform for consumer lending and loan application workflows.

The system accepts uploaded customer documents such as:

- ID card / CCCD
- payslip / salary slip
- bank statement

It turns those raw files into structured, validated data that reviewers can inspect, correct, and approve.

## Business Goal

The primary goal is to reduce manual effort in loan document review by transforming uploaded documents into structured data with clear validation signals.

Key business value:

- reduce manual data entry
- reduce review time
- reduce extraction errors
- surface risky or low-confidence cases for manual review
- improve straight-through processing

## Product Boundary

- This is not just an OCR demo.
- The product should behave like a document intake engine used by loan officers.
- Human review is part of the core workflow, not a fallback afterthought.
- The MVP should prioritize demo reliability and correctness on the core intake-to-review path.

## Supported Document Types

Only these document types are in scope for the MVP:

- `id_card`
- `payslip`
- `bank_statement`

Do not expand the MVP to additional document categories unless the scope is explicitly changed.

Extraction contracts live in:

- [schemas/id_card.schema.json](schemas/id_card.schema.json)
- [schemas/payslip.schema.json](schemas/payslip.schema.json)
- [schemas/bank_statement.schema.json](schemas/bank_statement.schema.json)

## Supported Inputs

Accepted upload formats:

- image upload: `.jpg`, `.jpeg`, `.png`
- pdf upload: `.pdf`

Expected intake behavior:

- a loan application can contain one or more documents
- a bank statement may contain multiple pages
- image and PDF inputs should converge into the same downstream processing pipeline

## Core Product Promise

For every uploaded document, the platform should:

1. preserve the raw file
2. produce OCR-ready page artifacts
3. extract structured fields
4. validate the result against business rules
5. expose a reviewable record for human correction and approval

## Success Definition For The MVP

- A reviewer can create an application, upload the three supported document types, and see structured extraction results.
- Validation flags and confidence signals are visible before approval.
- Low-confidence or unclear cases are surfaced instead of hidden.
- The demo story works end to end without requiring speculative infrastructure.

## See Also

- [02-scope-priorities.md](02-scope-priorities.md)
- [03-architecture.md](03-architecture.md)

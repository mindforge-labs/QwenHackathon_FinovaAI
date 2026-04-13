# Finova AI – Dashboard Chart Strategy

## Goal

Add charts that do more than decorate the dashboard. Each chart should help judges and users understand the product quickly by showing:

* where risk is concentrated
* how much intake is being processed
* how AI review activity is evolving

The charts should support the product story of an **AI-powered risk review dashboard**, not feel like generic analytics.

---

## Core Principle

Charts should answer three questions within a few seconds:

1. How many cases are being handled?
2. Where is the risk?
3. What is the system doing over time?

Avoid adding too many charts. For a hackathon demo, a small number of clear charts is stronger than a crowded dashboard.

---

## Recommended Chart Set

### 1. Risk Distribution Chart

#### Purpose

Show the current spread of cases by status so the user immediately sees where attention is needed.

#### Suggested statuses

* Clean
* Under Review
* High Risk
* Re-upload Requested

#### Best chart types

* Donut chart for compact and polished presentation
* Stacked bar if you want a more operational look

#### Why this matters

This is the fastest chart for telling the product story. A judge can instantly understand whether the system is mostly clearing cases or surfacing risky ones.

#### Placement

Place it below the top stats row or beside the portfolio queue section.

#### Example demo data

* Clean: 12
* Under Review: 5
* High Risk: 3
* Re-upload Requested: 2

---

### 2. Processing Trend Chart

#### Purpose

Show how many documents or applications have been processed over time.

#### Suggested metrics

* Documents processed per day
* Flagged cases per day
* Review completions per day

#### Best chart types

* Line chart for a clean analytical look
* Area chart for more visual impact while keeping readability

#### Why this matters

This chart makes the dashboard feel alive. It shows the system is actively handling intake rather than just storing records.

#### Placement

Place it next to the risk distribution chart in a 2-column analytics section.

#### Example demo data

* Mon: 8
* Tue: 13
* Wed: 10
* Thu: 15
* Fri: 11
* Sat: 6
* Sun: 4

---

### 3. Pipeline Funnel Visualization

#### Purpose

Show how cases move through the workflow from upload to final decision.

#### Suggested stages

* Uploaded
* OCR Completed
* AI Extracted
* Human Review
* Approved / Rejected

#### Best chart types

* Horizontal step cards
* Funnel-style stacked layout
* Progress row with counts per stage

#### Why this matters

This chart explains the entire system flow. It is especially useful in a demo because it connects the dashboard with the rest of the application journey.

#### Placement

Place it near the hero panel or in the right-side operations panel.

#### Example demo data

* Uploaded: 16
* OCR Completed: 14
* AI Extracted: 10
* Human Review: 5
* Approved: 3
* Rejected: 2

---

### 4. AI Confidence / Extraction Quality Chart

#### Purpose

Make the AI visible by showing confidence and low-confidence extraction patterns.

#### Suggested metrics

* Average OCR confidence
* Average extraction confidence
* Number of low-confidence fields
* Number of mismatch detections

#### Best chart types

* Bar chart by document type
* Radial chart for average confidence score
* Small grouped bars for field quality comparison

#### Example categories

* Payslip
* ID Card
* Bank Statement

#### Why this matters

This chart turns the product into an AI system rather than a standard document dashboard. It directly supports the “make the AI visible” positioning.

#### Placement

Use this only if there is enough space and the first two charts are already implemented well.

---

## Best Layout Recommendation

### Safe and effective layout

Create one analytics section below the top stat cards with 2 columns:

* Left: Risk Distribution
* Right: Processing Trend

This is the best first step because:

* it adds intelligence without clutter
* it fits the current dashboard structure
* it balances the page visually
* it is easy to explain during demo

---

## Alternative Layout

If the right side of the dashboard feels empty, add smaller charts there:

* mini chart: Cases by Status
* mini chart: 7-Day Processing

This helps fill empty space without making the main content too dense.

---

## Visual Style Guidelines

The charts should match the current Finova AI dashboard style:

* light background
* clean cards
* soft borders
* rounded corners
* minimal labels
* subtle grid lines
* one visual focus per chart

### Suggested color mapping

* Green: Approved / Clean
* Amber: Under Review / Warning
* Red or rose: High Risk / Flagged
* Gray: Draft / Waiting

Avoid:

* too many colors
* heavy legends
* excessive axis labels
* overly technical chart styling

---

## Demo Data Strategy

For hackathon demos, use believable data instead of random values.

### Risk distribution sample

* Clean: 12
* Under Review: 5
* High Risk: 3
* Re-upload Requested: 2

### 7-day processing sample

* Mon: 8
* Tue: 13
* Wed: 10
* Thu: 15
* Fri: 11
* Sat: 6
* Sun: 4

### Document type sample

* Payslip: 14
* ID Card: 9
* Bank Statement: 11

Use values that support your demo story:

* enough completed cases to show value
* enough flagged cases to show the need for review
* enough variation to make the charts visually interesting

---

## Interaction Enhancements

To make the dashboard feel more product-like, add light controls above the chart area:

### Filter ideas

* All
* Payslip
* ID Card
* Bank Statement

### Time range ideas

* Today
* 7 Days
* 30 Days

Use pill buttons or segmented controls. Keep them small and clear.

---

## What to Build First

Recommended implementation order:

### Phase 1

* Risk Distribution Donut Chart
* Processing Trend Line or Area Chart

### Phase 2

* Pipeline Funnel Visualization

### Phase 3

* AI Confidence / Extraction Quality Chart

This order gives the strongest impact with the least UI complexity.

---

## Final Recommendation

For the current Finova AI dashboard, the best combination is:

1. Donut chart for risk distribution
2. Line or area chart for processing trend
3. Optional mini funnel for workflow visibility

This creates a dashboard that feels intelligent, active, and demo-ready without overwhelming the screen.

---

## Summary

Charts should not be added just because dashboards usually have them. They should strengthen the narrative:

* the system is processing real intake
* the AI is surfacing risk
* humans are stepping in where needed

If the charts support that story, they will improve both the UI and the hackathon presentation.

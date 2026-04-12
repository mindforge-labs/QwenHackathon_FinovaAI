# Sample Documents

This folder contains demo-ready sample files for the three MVP-supported document types:

- `id_card_sample.png`
- `payslip_sample.png`
- `bank_statement_sample.pdf`

## Intended Demo Order

1. Create one application in the UI.
2. Upload the ID card sample.
3. Upload the payslip sample.
4. Upload the bank statement sample.
5. Trigger processing for each document.
6. Open the review page and inspect extracted fields, confidence signals, and validation flags.

## Data Profile

- The ID card and payslip use the same person name to support the happy path for cross-document validation.
- The bank statement uses the same account holder name for the same reason.
- The bank statement PDF has two pages so the demo also covers multi-page normalization.

## Notes

- These files are synthetic demo fixtures, not real personal data.
- They are designed to be OCR-friendly and easy to use during local development or hackathon demos.

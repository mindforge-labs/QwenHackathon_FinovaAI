# AGENT.md

## 1. Project Overview

This project is an **AI-powered Document Intake & Verification Platform** for consumer lending / loan application workflows.

The system accepts uploaded customer documents such as:
- ID card / CCCD
- Payslip / salary slip
- Bank statement

It then:
1. Stores raw files in object storage
2. Converts PDFs into page images
3. Preprocesses images for OCR
4. Runs OCR to extract text and bounding boxes
5. Classifies document type
6. Uses an LLM to extract structured JSON fields
7. Validates extracted data with business rules
8. Persists results for reviewer verification
9. Exposes a review dashboard for manual correction and approval

This is a **hackathon MVP**, so the implementation should prioritize:
- clean architecture
- demo readiness
- correctness on core flows
- easy local setup with Docker Compose
- clear separation of concerns
- extensibility for later productionization

---

## 2. Business Goal

The goal is to reduce manual effort in loan document review by transforming raw documents into structured, validated data.

### Key business value
- reduce manual data entry
- reduce review time
- reduce extraction errors
- surface risky / low-confidence cases for manual review
- improve straight-through processing

### Important note
This is **not just an OCR demo**.  
The system must behave like a **document intake engine** used by loan officers.

---

## 3. Required Tech Stack

The implementation must use exactly these technologies unless there is a strong technical reason otherwise.

### Frontend
- Next.js

### Backend
- FastAPI

### OCR
- PaddleOCR

### Image preprocessing
- OpenCV

### LLM extraction
- structured JSON output
- LLM must return JSON only
- no free-form responses in extraction flow

### Database
- PostgreSQL running in a container

### Object storage
- MinIO S3

---

## 4. Target Scope

### Supported document types in MVP
Only support these 3 document types:
1. `id_card`
2. `payslip`
3. `bank_statement`

Do not try to support too many document types in MVP.

### Supported input types
- image upload: `.jpg`, `.jpeg`, `.png`
- pdf upload: `.pdf`

### Core features
- upload application documents
- store raw files in MinIO
- process files into OCR-ready pages
- OCR page text + bounding boxes
- classify document type
- extract structured fields
- validate field consistency
- display results in review UI
- allow reviewer correction and approval

---

## 5. Product Flow

### End-to-end flow
1. User creates a loan application
2. User uploads one or more documents
3. Backend stores raw file in MinIO
4. Backend creates DB records for application and document
5. Backend triggers processing pipeline
6. PDFs are converted into page images
7. Each page is preprocessed with OpenCV
8. OCR runs using PaddleOCR
9. OCR text is aggregated
10. Document type is classified
11. LLM extracts structured fields into JSON
12. Validation engine runs:
   - field-level validation
   - completeness checks
   - cross-document checks
13. Results are saved in PostgreSQL
14. Frontend review screen displays:
   - raw document preview
   - extracted fields
   - confidence signals
   - validation flags
15. Reviewer can:
   - correct fields
   - approve
   - reject
   - request re-upload

---

## 6. Architecture

### High-level architecture

```text
Next.js Frontend
    |
    v
FastAPI Backend
    |
    +--> PostgreSQL
    +--> MinIO
    |
    +--> Processing Pipeline
          |- File normalization
          |- Image preprocessing (OpenCV)
          |- OCR (PaddleOCR)
          |- Document classification
          |- LLM structured extraction
          |- Validation engine
```

### Architecture style

Use a modular monolith.

Do NOT split into real microservices for the MVP.

Reason:
- easier local development
- easier debugging
- easier Docker Compose setup
- faster hackathon delivery

---

## 7. Backend Structure

Recommended backend folder structure:

```text
backend/
  app/
    main.py
    api/
      applications.py
      documents.py
      review.py
      health.py
    core/
      config.py
      db.py
      logging.py
      security.py
      s3.py
    models/
      application.py
      document.py
      document_page.py
      extraction.py
      validation.py
      review_action.py
    schemas/
      application.py
      document.py
      extraction.py
      review.py
      common.py
    services/
      application_service.py
      upload_service.py
      storage_service.py
      pdf_service.py
      preprocess_service.py
      ocr_service.py
      classification_service.py
      extraction_service.py
      validation_service.py
      review_service.py
      pipeline_service.py
    repositories/
      application_repository.py
      document_repository.py
      extraction_repository.py
      validation_repository.py
      review_repository.py
    utils/
      image_utils.py
      pdf_utils.py
      normalization_utils.py
      hashing_utils.py
    prompts/
      id_card_extraction.txt
      payslip_extraction.txt
      bank_statement_extraction.txt
    tests/
      ...
  Dockerfile
  requirements.txt
```

### Design rules

- keep API layer thin  
- business logic belongs in services  
- DB access belongs in repositories  
- Pydantic schemas for API contracts  
- SQLAlchemy ORM for DB models  
- Alembic for migrations  

---

## 8. Frontend Structure

Recommended frontend folder structure:

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

### Required frontend pages

- Applications list  
- Application detail  
- Document review page  

### Required frontend behavior

- upload file(s)  
- show processing status  
- show extracted fields in structured form  
- show validation flags  
- show image or PDF preview  
- allow manual correction and decision  

---

## 9. Data Model

### applications

Represents a loan application.

Fields:
- id
- applicant_name nullable
- phone nullable
- email nullable
- status
- created_at
- updated_at

### documents

Represents an uploaded file.

Fields:
- id
- application_id
- file_name
- mime_type
- storage_key
- document_type nullable
- status
- quality_score nullable
- ocr_confidence nullable
- extraction_confidence nullable
- created_at
- updated_at

### document_pages

Represents a single page or image artifact.

Fields:
- id
- document_id
- page_number
- raw_image_storage_key
- processed_image_storage_key
- ocr_text
- ocr_json
- created_at

### extracted_fields

Stores extraction results.

Fields:
- id
- document_id
- schema_version
- raw_extraction_json
- normalized_extraction_json
- created_at
- updated_at

### validation_flags

Stores validation warnings/errors.

Fields:
- id
- document_id
- flag_code
- severity
- message
- field_name nullable
- created_at

### review_actions

Stores human review history.

Fields:
- id
- document_id
- reviewer_name
- action
- comment
- corrected_json
- created_at

---

## 10. Document Types and Extraction Schemas

### 10.1 ID Card Schema

Document type: `id_card`

Target fields:

```json
{
  "document_type": "id_card",
  "full_name": null,
  "dob": null,
  "id_number": null,
  "address": null,
  "issue_date": null
}
```

### 10.2 Payslip Schema

Document type: `payslip`

Target fields:

```json
{
  "document_type": "payslip",
  "employee_name": null,
  "employer_name": null,
  "pay_period": null,
  "gross_salary": null,
  "net_salary": null
}
```

### 10.3 Bank Statement Schema

Document type: `bank_statement`

Target fields:

```json
{
  "document_type": "bank_statement",
  "account_holder": null,
  "bank_name": null,
  "account_number": null,
  "statement_period": null,
  "ending_balance": null
}
```

---

## 11. File Storage Layout in MinIO

Use bucket structure like this:

```text
loan-docs/
  applications/{application_id}/raw/{document_id}/original
  applications/{application_id}/pages/{document_id}/{page_number}.jpg
  applications/{application_id}/processed/{document_id}/{page_number}.jpg
  applications/{application_id}/artifacts/{document_id}/ocr.json
  applications/{application_id}/artifacts/{document_id}/extraction.json
```

### Requirements

- raw file must always be preserved  
- processed pages must be stored separately  
- OCR and extraction artifacts should also be saved  
- use deterministic storage keys where possible  

---

## 12. Processing Pipeline

### Step 1: Upload

- accept multipart file upload  
- validate mime type  
- compute file hash  
- store file in MinIO  
- create DB records  
- initialize document status as `uploaded`  

### Step 2: Normalize file

- if PDF: convert all pages into images  
- if image: normalize to supported image format  
- output should be a list of page images  

### Step 3: Preprocess image

Use OpenCV for:
- grayscale conversion  
- denoise  
- contrast enhancement  
- thresholding if helpful  
- deskew  
- rotation correction  
- optional document crop  
- optional resize  

### Step 4: OCR

Run PaddleOCR on each page and return:
- recognized text  
- bounding boxes  
- confidence score per line/block  

### Step 5: Aggregate OCR

- combine per-page OCR text  
- preserve page number  
- preserve bounding boxes  
- persist OCR raw output  

### Step 6: Document classification

Classify into:
- `id_card`
- `payslip`
- `bank_statement`
- `unknown`

Use simple rules first:
- keyword matching  
- pattern matching  

Fallback to LLM if unclear.

### Step 7: Structured extraction

Use OCR text as input to an LLM and request JSON only.

Strict requirements:
- valid JSON only  
- no markdown  
- no commentary  
- missing field must be null  
- do not hallucinate  

### Step 8: Normalize extracted fields

Normalize:
- date format  
- numeric salary / balance fields  
- account number spacing  
- name spacing / casing if needed  

### Step 9: Validation

Run:
- field-level validation  
- completeness validation  
- cross-document validation if multiple docs exist in same application  

### Step 10: Save results

Persist:
- OCR artifacts  
- extracted JSON  
- normalized JSON  
- flags  
- confidence indicators  
- final document status  

---

## 13. OCR Requirements

### OCR engine

Use PaddleOCR.

### OCR output requirements

For each page, keep:
- page_number  
- text  
- bbox  
- confidence  

### OCR quality strategy

Compute a simple aggregate OCR confidence:
- average line confidence  
- or weighted confidence by text length  

Store it in the `documents` table.

---

## 14. LLM Extraction Rules

### General rules

The LLM must behave like an extraction engine, not a chatbot.

### Hard requirements

- return valid JSON only  
- obey the schema exactly  
- use null when data is missing  
- do not invent values  
- do not infer unsupported facts  
- do not return explanations  

### Prompting guidance

Each document type should have its own extraction prompt template.

Example instruction pattern:

> You are an information extraction engine.  
> Extract structured fields from OCR text for document type X.  
> Return valid JSON only.  
> If a field cannot be found, use null.  
> Do not guess.

### Post-processing

Always parse and validate LLM output server-side.

If parsing fails:
- retry once with stricter formatting prompt  
- fallback to rule-based partial extraction  
- mark a validation flag  

---

## 15. Document Classification Rules

### Classification strategy

Use rules first.

### ID Card hints

- "CĂN CƯỚC"  
- "CÔNG DÂN"  
- 12-digit ID number patterns  
- date of birth patterns  

### Payslip hints

- "salary"  
- "basic salary"  
- "net salary"  
- "gross salary"  
- "pay period"  
- employer / employee wording  

### Bank statement hints

- "statement"  
- "account number"  
- "balance"  
- "transaction"  
- bank names  

### Unknown handling

If confidence is low or no rule matches:
- set `document_type = unknown`  
- create validation flag  
- allow manual review  

---

## 16. Validation Rules

### 16.1 Field-level validation

**ID card**
- `id_number` should be 12 digits if present  
- `dob` must be a valid date  
- `issue_date` must be a valid date and not in the future  

**Payslip**
- `gross_salary` and `net_salary` must be positive numbers if present  
- `net_salary <= gross_salary` if both are present  
- `pay_period` must be parseable as a date/month period if present  

**Bank statement**
- `account_number` should match expected numeric/string pattern  
- `ending_balance` should be numeric if present  

### 16.2 Completeness validation

Create warnings when important fields are missing.

Examples:
- missing `full_name`  
- missing `id_number`  
- missing `net_salary`  
- missing `account_holder`  

### 16.3 Quality validation

Flag low quality cases:
- blurry image  
- skewed image  
- OCR confidence too low  
- empty OCR result  
- incomplete page conversion  

### 16.4 Cross-document validation

If multiple docs exist in one application, compare:
- ID card `full_name` vs payslip `employee_name`  
- ID card `full_name` vs bank statement `account_holder`  

Suggested check:
- normalized string similarity  

Possible flag:
- `NAME_MISMATCH`  

---

## 17. Status Model

### Document statuses

- `uploaded`  
- `processing`  
- `processed`  
- `needs_review`  
- `approved`  
- `rejected`  
- `failed`  

### Application statuses

- `draft`  
- `processing`  
- `under_review`  
- `approved`  
- `rejected`  

---

## 18. Confidence Strategy

Track 3 levels of confidence:

1. **Quality score**  
   - Derived from image quality checks.

2. **OCR confidence**  
   - Derived from PaddleOCR output.

3. **Extraction confidence**  
   - Derived heuristically from:
     - OCR quality  
     - number of filled required fields  
     - parse success  
     - classification certainty  

### Suggested routing

- high confidence -> ready for review  
- medium confidence -> needs review  
- low confidence -> recommend re-upload or manual inspection  

---

## 19. Edge Cases That Must Be Handled

The implementation must explicitly handle these cases:

### Input issues

- unsupported file type  
- empty file  
- corrupted PDF  
- duplicate upload  

### Image issues

- blurry image  
- low-light image  
- skewed image  
- rotated image  
- cropped document  
- glare / reflections  

### OCR issues

- empty OCR output  
- low OCR confidence  
- broken line ordering  
- OCR confusion between similar characters like 0/O, 1/I  

### Extraction issues

- invalid JSON from LLM  
- missing required fields  
- incorrect numeric parsing  
- ambiguous dates  

### Multi-page issues

- bank statement has multiple pages  
- OCR should run page by page  
- final result must merge correctly  

### Classification issues

- document type unclear  
- mixed content pages  
- unsupported document layout  

### Review issues

- reviewer edits field values  
- reviewer should be able to approve even if warnings exist  
- review history must be persisted  

---

## 20. API Requirements

### Applications

**POST** `/applications`  
Create a new application.

**GET** `/applications`  
List applications.

**GET** `/applications/{application_id}`  
Get application detail with documents.

### Documents

**POST** `/applications/{application_id}/documents`  
Upload a document for an application.

Response should include:
- document id  
- upload status  

**POST** `/documents/{document_id}/process`  
Trigger processing for a document.

**GET** `/documents/{document_id}`  
Get document detail:
- metadata  
- OCR summary  
- extraction JSON  
- validation flags  
- status  

**GET** `/documents/{document_id}/pages`  
Get page previews / page metadata.

### Review

**PATCH** `/documents/{document_id}/review`  
Allow reviewer to correct extracted fields.

**POST** `/documents/{document_id}/decision`  
Decision actions:
- `approve`  
- `reject`  
- `request_reupload`  

---

## 21. Frontend Requirements

### Application detail page must show

- uploaded documents  
- processing status per document  
- document type  
- quality / warning summary  

### Review page must show

- document preview  
- extracted fields in editable form  
- validation flags  
- OCR raw text section  
- reviewer actions  

### Nice to have

- display OCR boxes over image  
- highlight suspicious / missing fields  

---

## 22. Non-Functional Requirements

### Code quality

- readable code  
- modular services  
- type hints where practical  
- clear naming  
- no dead code  
- no unnecessary abstractions  

### Logging

Log key pipeline events:
- upload success  
- MinIO storage success/failure  
- OCR start/end  
- extraction start/end  
- validation result  
- review actions  

### Error handling

- graceful API errors  
- meaningful HTTP status codes  
- failed processing should not crash the service  
- persist failure state for documents  

### Performance

This is an MVP, but avoid obviously slow or blocking design where possible.

### Security

Basic only for MVP:
- validate upload type  
- sanitize file names  
- avoid arbitrary path writes  
- keep secrets in environment variables  

---

## 23. Local Development Requirements

The project must be runnable locally with Docker Compose.

### Required services

- frontend  
- backend  
- postgres  
- minio  

### Optional

- redis / worker only if truly necessary  

### Environment variables

Backend should support env-based config for:
- postgres connection  
- minio endpoint  
- minio access key  
- minio secret key  
- minio bucket name  
- llm api key  
- llm model name  

---

## 24. Suggested Docker Compose Topology

### Services:

- frontend  
- backend  
- postgres  
- minio  

### Optional:

- minio-init for bucket initialization  

---

## 25. Testing Expectations

Minimum tests:
- upload endpoint test  
- PDF/image normalization test  
- OCR service integration boundary test  
- extraction parser test  
- validation rule tests  
- repository tests for core persistence flow  

Do not over-invest in huge test suites for the hackathon, but core logic should be testable.

---

## 26. Implementation Priorities

### Priority 1: Must have

- upload flow  
- MinIO storage  
- PostgreSQL persistence  
- PDF/image normalization  
- OpenCV preprocess  
- PaddleOCR integration  
- document classification  
- LLM structured extraction  
- validation flags  
- basic review UI  

### Priority 2: Strongly recommended

- OCR artifact storage  
- confidence scores  
- cross-document validation  
- review correction persistence  

### Priority 3: Nice to have

- OCR bounding box overlay  
- duplicate upload detection  
- simple quality scoring  
- retry handling for extraction failures  

---

## 27. Out of Scope

Do NOT implement these unless there is extra time:

- full user authentication / RBAC  
- production-grade distributed queueing  
- advanced fraud detection  
- model training pipelines  
- full observability stack  
- complicated access control  
- enterprise workflow engine  
- too many document types  

---

## 28. Demo Expectations

The demo should show this exact story:

1. Create application  
2. Upload:
   - ID card
   - payslip
   - bank statement
3. System processes the files  
4. User opens review page  
5. UI shows extracted structured fields  
6. UI shows validation flags  
7. Reviewer corrects a field if needed  
8. Reviewer approves the document/application  

This demo flow is more important than fancy infrastructure.

---

## 29. Coding Conventions

### General

- prefer explicit code over clever code  
- avoid premature optimization  
- keep functions focused  
- keep services composable  
- return typed schemas where possible  

### Naming

Use clear names such as:
- `process_document`  
- `extract_fields_from_ocr`  
- `validate_id_card_fields`  
- `store_file_to_minio`  

Avoid vague names like:
- `handle_data`  
- `do_task`  
- `process_everything`  

---

## 30. Final Instruction for Coding Agent

Implement the system exactly as an MVP document intake platform for lending workflows, not as a generic OCR playground.

The coding agent should optimize for:
- end-to-end working demo  
- correctness of document processing pipeline  
- structured extraction and validation  
- clean local developer experience  
- maintainable code organization  

When trade-offs happen, prioritize:
- working upload/process/review flow  
- simple architecture  
- clarity  
- demo reliability  

over:
- over-engineering  
- unnecessary microservices  
- excessive abstractions  
- speculative features
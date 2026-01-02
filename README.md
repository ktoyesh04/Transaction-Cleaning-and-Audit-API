## Transaction Cleaning & Audit API

A rule-driven CSV data cleaning service with full auditability.
Users upload raw transaction data and receive cleaned, flagged, and rejected outputs, along with detailed audit logs 
explaining every decision.

## Why this project exists

In real-world data pipelines, CSV validation often fails silently:
- Invalid rows disappear
- Fixes are applied without traceability
- Business users can’t explain why data was rejected

This service makes data quality explicit, explainable, and auditable.

## Key Features

- CSV upload via REST API or web UI
- Rule-based validation and normalization
- Automatic fixes (e.g. currency symbols, lakh notation)
- Row-level audit trail explaining fixes and rejections
- Job-level summary with processing metadata
- Downloadable outputs:
  - Cleaned records
  - Flagged records 
  - Rejected records

## High-Level Architecture

Client
  └── Upload CSV
        └── FastAPI
              ├── Processor
              │     ├── Validators (rule-based)
              │     └── Audit generator
              ├── Job-scoped file storage
              └── API / UI responses

Each upload creates an isolated job, identified by a unique job ID.

## Audit Model

1. Row-Level Audit (audit.jsonl)
Explains _what happened_ to individual rows.

Example:

json 
```
{
  "row_number": 3,
  "status": "FIXED",
  "rule_code": "AMOUNT_LAKH_CONVERSION",
  "field": "amount",
  "original_value": "1.5L",
  "new_value": 150000,
  "message": "Converted lakh notation to number",
  "timestamp": "2025-12-31T15:46:56Z"
}
```

2. Job-Level Summary (summary.json)

json
```commandline
{
  "job_id": "97727a91",
  "total": 5,
  "cleaned": 2,
  "flagged": 1,
  "rejected": 2,
  "processing_time_ms": 14
}

```

## API Endpoints

- POST /upload – Upload CSV and receive job summary
- GET /download/{job_id}/{type} – Download cleaned / flagged / rejected files
- GET /summary/{job_id} – Retrieve job summary
- GET /ui – Web interface for uploads and downloads

## Tech Stack

- FastAPI
- Pandas
- Jinja2
- Python logging
- Pytest
- File-based job storage

## How to Run

pip install -r requirements.txt
uvicorn app.main:app --reload

or 

pip install .
pip install .[dev]
uvicorn app.main:app --reload

Then open:

API docs: http://127.0.0.1:8000/docs
UI: http://127.0.0.1:8000/ui

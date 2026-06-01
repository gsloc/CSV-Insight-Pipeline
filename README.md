# CSV Insight Pipeline

A production-grade pipeline that ingests CSV files, validates & cleans the data, runs
statistical analysis, and renders interactive visualizations with automated insights.

Heavy data processing (Python / Pandas) is fully decoupled from the presentation layer
(Next.js), so each tier scales independently.

```
┌─────────────────────────┐         multipart upload          ┌──────────────────────────────┐
│   Next.js + Recharts     │  ──────────────────────────────▶ │   FastAPI + Pandas/NumPy       │
│   (client/, port 3000)   │ ◀──────────────────────────────  │   (server/, port 8000)         │
│   upload · dashboard     │            JSON report            │   ingest→validate→clean→analyze │
└─────────────────────────┘                                   └──────────────────────────────┘
```

## Pipeline flow

```
Upload (multipart)
  → Ingestion      encoding detection · chunked size-capped read · bad-row skip · header auto-gen
  → Validation     schema inference · missing/duplicate/outlier detection · Data Quality report
  → Cleaning       Strategy-Pattern imputation · string normalization · type standardization (logged)
  → Analysis       summary stats · correlation matrix · auto chart specs · executive insights
  → JSON contract  { meta, schema, data_quality, cleaning, analysis, insights, preview }
```

## Architecture

The backend follows a strict layered architecture so the pure data logic stays
framework-free and unit-testable:

```
Routes (HTTP)  →  Controllers (orchestration)  →  Services (use-cases)  →  Core (pure data logic)
app/api/routes    app/controllers                 app/services             app/core
```

- **`core/`** — pure functions over pandas/numpy (schema inference, outlier math, cleaning
  strategies, statistics, insights, chart specs). No HTTP imports → trivially testable and
  reusable from a CLI or a Celery/RQ worker.
- **Strategy Pattern** — `core/cleaning_strategies.py` registers missing-value strategies
  (`mean` / `median` / `mode` / `drop`); new strategies drop in without touching services.
- **Scalability** — uploads are streamed in chunks with a hard size cap so large files never
  blow up memory. To scale further, lift `run_analysis_pipeline` into a task queue + object
  storage with a job-polling endpoint — `core/` needs zero changes.

```
csv-insight-pipeline/
├── server/                       # FastAPI backend
│   ├── app/
│   │   ├── main.py               # app, CORS, exception handlers, router mounting
│   │   ├── config.py             # env-driven settings
│   │   ├── api/routes/           # health.py, ingestion.py  (HTTP layer)
│   │   ├── controllers/          # analysis_controller.py   (orchestration)
│   │   ├── services/             # ingestion / validation / cleaning / analysis
│   │   ├── core/                 # schema_inference, outlier_detection, cleaning_strategies,
│   │   │                         #   statistics, insights, chart_specs  (pure logic)
│   │   ├── models/schemas.py     # Pydantic enums + response docs
│   │   └── utils/                # logging, exceptions, serialization (NaN/numpy → JSON-safe)
│   ├── tests/                    # 47 pytest tests
│   └── requirements.txt
├── client/                       # Next.js (App Router) + Tailwind + Recharts
│   ├── app/                      # layout.tsx, page.tsx, globals.css
│   ├── components/               # FileUpload, ResultsDashboard, charts/, ui/, …
│   └── lib/                      # api.ts, types.ts, format.ts
└── sample_data/sample_sales.csv
```

## Quick start

### 1. Backend (FastAPI, port 8000)

```bash
cd server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Interactive API docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/api/v1/health>

### 2. Frontend (Next.js, port 3000)

```bash
cd client
npm install
npm run dev          # http://localhost:3000
```

If port 3000 is taken, run on another port and point the app + CORS at it:

```bash
# client
NEXT_PUBLIC_API_BASE=http://localhost:8000 npx next dev -p 3100
# server (allow the new origin)
ALLOWED_ORIGINS="http://localhost:3100" uvicorn app.main:app --reload --port 8000
```

## API contract

### `POST /api/v1/analyze`  (multipart/form-data)

| field             | type   | default  | notes                              |
|-------------------|--------|----------|------------------------------------|
| `file`            | file   | —        | `.csv` / `.tsv` / `.txt`, ≤ 50 MB  |
| `missing_strategy`| string | `median` | `mean` · `median` · `mode` · `drop`|
| `outlier_method`  | string | `iqr`    | `iqr` · `zscore`                   |

Returns `{ meta, schema, data_quality, cleaning, analysis, insights, preview }`.

| status | meaning                                  |
|--------|------------------------------------------|
| 200    | success                                  |
| 400    | empty / unparseable dataset              |
| 413    | file exceeds size limit                  |
| 415    | unsupported file extension               |
| 422    | invalid strategy / outlier method        |

### `GET /api/v1/health`
Returns service status and the available strategies/methods.

## Testing

```bash
cd server && pytest          # 47 tests
```

Coverage focuses on the required areas: **schema detection**, **missing-value imputation
strategies**, and **outlier detection math**, plus statistics, the ingestion layer
(encoding / headerless / malformed rows), and a full end-to-end API test.

## Edge cases handled

- **Empty datasets** → `400` with a clear message and a UI empty state.
- **Single-column datasets** → correlation matrix is skipped (UI shows an explanatory state).
- **Large files** → chunked, size-capped upload reads.
- **Missing headers** → auto-generated `column_1…N` (heuristic on the first row).
- **Encoding issues** → `chardet` detection with a UTF-8 → ISO-8859-1 fallback chain.
- **Malformed rows** → skipped via the C parser and counted in the report.
- **NaN / numpy types** → recursively converted to strictly-valid JSON before responding.

## Tech stack

- **Backend:** FastAPI · Pandas · NumPy · chardet · Pydantic · Pytest
- **Frontend:** Next.js 14 (App Router) · React 18 · TypeScript · Tailwind CSS · Recharts

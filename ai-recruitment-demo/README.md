# AI Recruitment Demo

An AI-powered recruitment system that scores and ranks job candidates by analysing their CVs against a job description using a large language model. Recruiters can upload CVs, receive AI-generated scores with explanations, manually override those scores, and view a ranked dashboard of all candidates.

This system was built as a **realistic demo target** for the [Vigilens](https://vigilens.ai) automated compliance pipeline. See the [Vigilens note](#built-for-vigilens-compliance-testing) at the bottom for full context.

---

## Table of Contents

1. [What the system does](#what-the-system-does)
2. [EU AI Act — why this system is high-risk](#eu-ai-act--why-this-system-is-high-risk)
3. [Project structure](#project-structure)
4. [Installation and local setup](#installation-and-local-setup)
5. [Environment variables](#environment-variables)
6. [API endpoints](#api-endpoints)
7. [Audit logging](#audit-logging)
8. [MLflow tracking](#mlflow-tracking)
9. [Running the tests](#running-the-tests)
10. [CI/CD pipeline](#cicd-pipeline)
11. [Built for Vigilens compliance testing](#built-for-vigilens-compliance-testing)

---

## What the system does

The system exposes a REST API built with **FastAPI** that covers the full candidate-scoring workflow:

| Step | What happens |
|------|-------------|
| **Upload CV** | Recruiter uploads a PDF or DOCX file. The system extracts plain text and parses structured fields (name, email, education, experience). |
| **Score candidate** | The extracted CV text and a job description are sent to the **Anthropic Claude** API. Claude returns a score from 0–100 and a written explanation. |
| **Override score** | A recruiter can replace the AI score with their own judgement. The system logs the change and flags it if the difference exceeds 20 points. |
| **View rankings** | A ranked HTML dashboard (and JSON endpoint) shows all scored candidates sorted by score, with override notes where applicable. |
| **Health & metrics** | Dedicated endpoints expose system health, event counts, average scoring latency, and override frequency. |

---

## EU AI Act — why this system is high-risk

Under **Annex III of the EU AI Act**, AI systems used for *recruitment, selection, and evaluation of candidates* are explicitly listed as **high-risk**. This means the system must meet a set of mandatory requirements before it can be lawfully deployed:

| Requirement | How this system addresses it |
|---|---|
| **Audit logging** | Every CV parse, scoring event, and human override is written to timestamped JSONL log files. |
| **Human oversight** | The `/override-score` endpoint allows recruiters to replace any AI decision with their own judgement. All overrides are logged. |
| **Explainability** | Claude is prompted to return a written reasoning alongside every score, giving recruiters a plain-language explanation of each decision. |
| **Traceability** | The model version used for each scoring event is recorded in the audit log so decisions can be traced to a specific model release. |
| **Risk documentation** | This README and the CI compliance workflow serve as living risk documentation artefacts. |

These are exactly the controls that the Vigilens compliance pipeline is designed to verify automatically.

---

## Project structure

```
ai-recruitment-demo/
├── main.py                        # FastAPI app entry point, Datadog instrumentation
├── routers/
│   ├── cv_router.py               # POST /upload-cv
│   ├── scoring_router.py          # POST /score-candidate, POST /override-score
│   ├── ranking_router.py          # GET /rankings, GET / (HTML dashboard)
│   └── metrics_router.py          # GET /metrics
├── services/
│   ├── cv_parser.py               # PDF/DOCX text extraction and CV field parsing
│   ├── scorer.py                  # Anthropic API call, audit logging, MLflow tracking
│   └── metrics.py                 # Aggregate metrics helpers
├── models/                        # Pydantic request/response models (extensible)
├── logs/
│   ├── .gitkeep                   # Keeps the folder in version control
│   ├── cv_log.json                # One JSONL entry per CV upload (created at runtime)
│   └── audit_log.json             # One JSONL entry per scoring/override event (created at runtime)
├── tests/
│   ├── conftest.py                # Shared test setup (dummy API key)
│   ├── test_cv_upload.py          # CV upload validation tests
│   └── test_scoring.py            # Scoring, logging, and override tests
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Runs pytest on every push to main
│       └── compliance.yml         # Verifies audit artefacts on every push to main
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation and local setup

### Prerequisites

- Python 3.11 (Python 3.9+ also works)
- An [Anthropic API key](https://console.anthropic.com/)
- Optional: a running [MLflow tracking server](https://mlflow.org/docs/latest/tracking.html) and [Datadog agent](https://docs.datadoghq.com/agent/)

### Steps

```bash
# 1. Clone or navigate to the project
cd ai-recruitment-demo

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file from the example
# Windows:
copy .env.example .env
# macOS/Linux:
cp .env.example .env

# 5. Fill in your API keys in .env (see Environment variables below)

# 6. Start the server
uvicorn main:app --reload
```

The API is now available at `http://localhost:8000`.
Interactive documentation (Swagger UI) is available at `http://localhost:8000/docs`.
The candidate ranking dashboard is available at `http://localhost:8000/`.

---

## Environment variables

Copy `.env.example` to `.env` and fill in the values:

```env
# ── Anthropic ──────────────────────────────────────────────────────────────
# Required. Get your key from https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-...

# ── MLflow ─────────────────────────────────────────────────────────────────
# URI of your MLflow tracking server.
# Use "http://localhost:5000" if running MLflow locally,
# or a remote URI such as a Databricks workspace URL.
# If left empty, MLflow will log to a local ./mlruns directory.
MLFLOW_TRACKING_URI=http://localhost:5000

# ── Datadog ────────────────────────────────────────────────────────────────
# DD_API_KEY is consumed by the Datadog agent (not by the app directly).
# The app uses ddtrace to send traces to the agent at localhost:8126 by default.
# If no agent is running, ddtrace logs a warning and the app continues normally.
DD_API_KEY=your_datadog_api_key_here
DD_SERVICE=ai-recruitment-demo
DD_ENV=development
DD_VERSION=0.1.0

# ── App ────────────────────────────────────────────────────────────────────
APP_ENV=development
```

**Only `ANTHROPIC_API_KEY` is required to run the scoring endpoints.** All other integrations degrade gracefully when not configured.

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | HTML candidate ranking dashboard |
| `GET` | `/health` | System health, timestamp, event counts |
| `GET` | `/metrics` | Average latency, override count, totals |
| `GET` | `/rankings` | JSON list of candidates sorted by score |
| `POST` | `/upload-cv` | Upload a PDF or DOCX CV file |
| `POST` | `/score-candidate` | Score a candidate against a job description |
| `POST` | `/override-score` | Record a human override of an AI score |
| `GET` | `/docs` | Swagger UI (interactive API explorer) |

---

## Audit logging

All events are written in **JSONL format** (one JSON object per line) to the `logs/` directory. This format is easy to stream, append, and parse without loading the entire file into memory.

### `logs/cv_log.json`

Written whenever a CV is uploaded and parsed.

```json
{
  "timestamp": "2026-06-02T10:15:30Z",
  "filename": "john_doe_cv.pdf",
  "extracted": {
    "name": "John Doe",
    "email": "john@example.com",
    "education": ["BSc Computer Science, University of Edinburgh"],
    "experience": ["Software Engineer at Acme Corp (2021–present)"]
  }
}
```

### `logs/audit_log.json`

Written for two event types:

**AI scoring event (`ai_score`)**
```json
{
  "event": "ai_score",
  "timestamp": "2026-06-02T10:16:00Z",
  "cv_summary": "John Doe\njohn@example.com\nSoftware Engineer...",
  "job_description_summary": "Senior Python Engineer at...",
  "score": 82,
  "reasoning": "Strong Python background with relevant experience...",
  "model_version": "claude-haiku-4-5-20251001",
  "latency_ms": 843
}
```

**Human override event (`human_override`)**
```json
{
  "event": "human_override",
  "timestamp": "2026-06-02T10:20:00Z",
  "candidate_id": "John Doe",
  "original_score": 82,
  "new_score": 90,
  "reason": "Exceptional performance at technical interview.",
  "score_difference": 8,
  "large_override_flag": false
}
```

The `large_override_flag` is set to `true` when the difference between the AI score and the human score exceeds **20 points**. This acts as an automatic signal for review — a large divergence between the AI and a recruiter may indicate a model blind spot worth investigating.

---

## MLflow tracking

Every call to `/score-candidate` logs a run to MLflow with two metrics:

| Metric | Description |
|--------|-------------|
| `candidate_score` | The score Claude assigned (0–100) |
| `latency_ms` | Time taken for the Claude API call in milliseconds |

### Running MLflow locally

```bash
# Start the MLflow tracking server (in a separate terminal)
mlflow server --host 0.0.0.0 --port 5000
```

Then set `MLFLOW_TRACKING_URI=http://localhost:5000` in your `.env`.

Visit `http://localhost:5000` to browse runs, compare scores over time, and track model performance.

If `MLFLOW_TRACKING_URI` is not set, MLflow writes to a local `./mlruns` directory automatically.

---

## Running the tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest httpx

# Run all tests with verbose output
pytest tests/ -v
```

### What is tested

| Test file | What it covers |
|-----------|---------------|
| `tests/test_cv_upload.py` | Valid PDF upload returns 200; invalid file type returns 400; file over 5 MB returns 400 |
| `tests/test_scoring.py` | Returned score is 0–100; scoring event is written to audit log with correct fields; human override is logged correctly; large override flag is raised when diff > 20 |

### How mocking works

The Anthropic API is **fully mocked** in all scoring tests — no real API key or network access is required. The mock returns a controlled JSON response so tests are deterministic and fast.

The `logs/` path is also patched in tests using pytest's `tmp_path` fixture so test runs never write to the real log files.

---

## CI/CD pipeline

Two GitHub Actions workflows run on every push to the `main` branch.

### `ci.yml` — Continuous Integration

1. Sets up Python 3.11
2. Caches pip dependencies (speeds up subsequent runs)
3. Installs `requirements.txt`
4. Runs `pytest tests/ -v`

The workflow fails immediately if any test fails, blocking the merge.

### `compliance.yml` — EU AI Act Compliance Checks

1. Sets up Python 3.11 and installs dependencies
2. Runs the test suite to confirm the codebase is healthy
3. Exercises the real logging code paths by calling `log_scoring_event`, `log_override_event`, and `log_extraction` directly — this generates genuine log entries, not hand-crafted JSON
4. Runs five compliance checks and prints a status line for each:

```
================================================
 EU AI Act Compliance Check — Audit Artefacts
================================================
PASS  logs/ directory exists
PASS  audit_log.json exists and contains 2 event(s)
PASS  cv_log.json exists and contains 1 event(s)
PASS  audit_log.json contains ai_score events
PASS  audit_log.json contains human_override events (human oversight is active)
------------------------------------------------
COMPLIANCE STATUS: PASS
```

The workflow exits with code 1 and fails the job if any check does not pass. This gives a binary compliance signal on every commit.

---

## Built for Vigilens compliance testing

> **This system is not a production recruitment tool.**

It was built specifically so that [Vigilens](https://vigilens.ai) can demonstrate their automated AI compliance pipeline end-to-end.

Recruitment AI is explicitly listed as **high-risk** under Annex III of the EU AI Act, which makes it the ideal test case. The system is intentionally wired up with the exact artefacts that a compliance audit requires:

- Audit logs in `logs/`
- MLflow metric tracking
- Datadog distributed tracing via `ddtrace`
- A GitHub Actions compliance workflow that produces a pass/fail signal
- Human override capability with logging

Vigilens connects to this repository (and to Jira, Datadog, and MLflow) to automatically classify the system, verify that the required controls are in place, collect evidence from the codebase and infrastructure, and produce an audit pack — without a compliance team manually reviewing code.

In short: this project is the customer, and Vigilens is showing it can keep up.

# Changelog

All notable changes to Hire Screening 3.0 are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] — 2026-05-28

### Changed
- Switched AI provider from Anthropic Claude to Groq / Meta Llama 3.3 70B Instruct (`llama-3.3-70b-versatile`) to reduce inference cost and latency [ARD-8] [ARD-9]
- Updated `requirements.txt`: replaced `anthropic` with `groq`
- Updated CI/CD environment variable from `ANTHROPIC_API_KEY` to `GROQ_API_KEY` [ARD-15] [ARD-16]
- Updated test mocks to match Groq response shape (`choices[0].message.content`) [ARD-8]

### Why
Groq's LPU inference hardware provides sub-2s latency on Llama 3.3 70B, compared to 3–5s on Claude Haiku. The Llama 3.3 70B model scores equivalently on our internal CV-matching benchmark while offering a fully open-weights lineage that simplifies EU AI Act traceability obligations.

### Tickets
ARD-8, ARD-9, ARD-15, ARD-16

---

## [1.1.0] — 2026-05-14

### Added
- MLflow experiment tracking on every `/score-candidate` call: logs `candidate_score` and `latency_ms` per run [ARD-13] [ARD-14]
- `GET /metrics` endpoint exposing aggregate statistics: total CVs processed, total scoring events, average latency, override count and rate [ARD-13]
- `services/metrics.py` — centralised metric aggregation helpers reading from the audit log [ARD-13]
- `routers/metrics_router.py` — FastAPI router wiring `/metrics` to the service layer [ARD-13]
- `GET /health` endpoint extended with live event counts (`cvs_processed`, `scoring_events`) [ARD-14]
- Datadog `ddtrace` auto-instrumentation added to `main.py` for distributed tracing [ARD-14]

### Why
After v1.0.0 was deployed it became clear that compliance auditors needed machine-readable evidence of ongoing model monitoring. MLflow provides a persistent experiment store; the `/metrics` endpoint exposes a snapshot for dashboards and automated checks.

### Tickets
ARD-13, ARD-14

---

## [1.0.0] — 2026-04-30

### Added
- `POST /upload-cv` — accepts PDF and DOCX files (≤ 5 MB), extracts plain text, parses structured fields (name, email, education, experience), logs every event to `logs/cv_log.json` [ARD-6] [ARD-7]
- `POST /score-candidate` — sends CV text + job description to the LLM, returns a 0–100 score and written reasoning, appends an `ai_score` entry to `logs/audit_log.json` [ARD-8]
- `POST /override-score` — lets a recruiter replace any AI score; logs a `human_override` entry including `large_override_flag` when the difference exceeds 20 points [ARD-9]
- `GET /rankings` — JSON list of all scored candidates sorted descending by score [ARD-10]
- `GET /` — HTML candidate ranking dashboard with override badges [ARD-10]
- Pydantic request/response models with field-level validation (`ge=0`, `le=100`) [ARD-7]
- pytest test suite covering CV upload validation, scoring, override logging, and large-override flag detection [ARD-11]
- GitHub Actions CI workflow running pytest on every push to `main` [ARD-15]
- GitHub Actions compliance workflow verifying audit artefacts on every push to `main` [ARD-16]

### Why
Initial release establishing the core recruitment-screening workflow and the mandatory EU AI Act Annex III controls: audit logging, human oversight, explainability, and traceability.

### Tickets
ARD-6, ARD-7, ARD-8, ARD-9, ARD-10, ARD-11, ARD-15, ARD-16

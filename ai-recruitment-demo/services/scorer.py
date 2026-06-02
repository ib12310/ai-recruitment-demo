import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import mlflow
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

AUDIT_LOG = Path(__file__).parent.parent / "logs" / "audit_log.json"
MODEL = "claude-haiku-4-5-20251001"

# Client is initialised only when an API key is present.
# In stub/demo mode the key is not required and client will be None.
_api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=_api_key) if _api_key else None

# Prompt instructs Claude to return strict JSON so we can parse it reliably
SCORING_PROMPT = """\
You are an expert technical recruiter. Given a candidate CV and a job description, \
score how well the candidate fits the role on a scale of 0-100.

CV:
{cv_text}

Job Description:
{job_description}

Respond with valid JSON only — no markdown, no extra text — in exactly this format:
{{
  "score": <integer 0-100>,
  "reasoning": "<two or three sentences explaining the score>"
}}"""


def score_candidate(cv_text: str, job_description: str) -> dict:
    """
    Score a candidate against a job description.
    Returns a dict with score, reasoning, model_version, and latency_ms.

    NOTE: This returns a stub response so the system can be run and tested
    without an Anthropic API key. Replace with a real API call when needed.
    """
    start = time.time()

    # Stub response — no API call is made
    parsed = {
        "score": 75,
        "reasoning": (
            "Demo mode: candidate appears to meet the core requirements of the role "
            "based on experience and qualifications listed in the CV."
        ),
    }

    latency_ms = round((time.time() - start) * 1000)

    return {
        "score": int(parsed["score"]),
        "reasoning": parsed["reasoning"],
        "model_version": MODEL,
        "latency_ms": latency_ms,
    }


def log_scoring_event(cv_text: str, job_description: str, result: dict) -> None:
    """Append one AI-scoring audit entry to audit_log.json."""
    entry = {
        "event": "ai_score",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        # Store a short summary rather than the full text to keep logs readable
        "cv_summary": cv_text[:300],
        "job_description_summary": job_description[:300],
        "score": result["score"],
        "reasoning": result["reasoning"],
        "model_version": result["model_version"],
        "latency_ms": result["latency_ms"],
    }
    _append_log(entry)


def log_override_event(
    candidate_id: str,
    original_score: int,
    new_score: int,
    reason: Optional[str],
) -> dict:
    """
    Append a human-override audit entry to audit_log.json.
    Returns flag info so the router can include it in the response.
    """
    diff = abs(new_score - original_score)
    # A difference greater than 20 points is worth flagging for review
    large_override = diff > 20

    entry = {
        "event": "human_override",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "candidate_id": candidate_id,
        "original_score": original_score,
        "new_score": new_score,
        "reason": reason,
        "score_difference": diff,
        "large_override_flag": large_override,
    }
    _append_log(entry)

    return {"large_override_flag": large_override, "score_difference": diff}


def track_with_mlflow(score: int, latency_ms: int) -> None:
    """Log a single scoring run to MLflow as metrics."""
    with mlflow.start_run():
        mlflow.log_metric("candidate_score", score)
        mlflow.log_metric("latency_ms", latency_ms)


def _append_log(entry: dict) -> None:
    """Write one JSON line to the audit log (JSONL format)."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

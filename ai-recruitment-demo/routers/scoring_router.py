from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.scorer import (
    log_override_event,
    log_scoring_event,
    score_candidate,
    track_with_mlflow,
)

router = APIRouter(tags=["Scoring"])


# ── Request / response models ─────────────────────────────────────────────────

class ScoreCandidateRequest(BaseModel):
    cv_text: str = Field(..., description="Full extracted text from the candidate's CV.")
    job_description: str = Field(..., description="Full text of the job description.")


class OverrideScoreRequest(BaseModel):
    candidate_id: str = Field(..., description="Unique identifier for the candidate.")
    original_score: int = Field(..., ge=0, le=100, description="AI-generated score (0-100).")
    new_score: int = Field(..., ge=0, le=100, description="Recruiter's revised score (0-100).")
    reason: Optional[str] = Field(None, description="Optional explanation for the override.")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/score-candidate")
def score_candidate_endpoint(request: ScoreCandidateRequest):
    """
    Score a candidate against a job description using Claude.
    Returns the score (0-100), reasoning, model version, and latency.
    """
    try:
        result = score_candidate(request.cv_text, request.job_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {e}")

    # Audit log and MLflow tracking happen after a successful score
    log_scoring_event(request.cv_text, request.job_description, result)
    track_with_mlflow(result["score"], result["latency_ms"])

    return result


@router.post("/override-score")
def override_score(request: OverrideScoreRequest):
    """
    Record a recruiter's manual override of an AI-generated score.
    Flags the override in the audit log if the difference exceeds 20 points.
    """
    flag_info = log_override_event(
        request.candidate_id,
        request.original_score,
        request.new_score,
        request.reason,
    )

    return {
        "candidate_id": request.candidate_id,
        "original_score": request.original_score,
        "new_score": request.new_score,
        "reason": request.reason,
        **flag_info,
    }

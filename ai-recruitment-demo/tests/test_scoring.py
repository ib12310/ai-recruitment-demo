import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mock_claude_response(score: int = 78, reasoning: str = "Strong technical background."):
    """Return a MagicMock that looks like an Anthropic messages.create() response."""
    content = MagicMock()
    content.text = json.dumps({"score": score, "reasoning": reasoning})
    message = MagicMock()
    message.content = [content]
    return message


def _post_score(cv_text: str = "John Smith\nPython developer.", job_desc: str = "Senior Python Engineer."):
    return client.post(
        "/score-candidate",
        json={"cv_text": cv_text, "job_description": job_desc},
    )


# ── Scoring endpoint tests ────────────────────────────────────────────────────

def test_score_is_between_0_and_100(tmp_path):
    """The returned score must be an integer in the valid 0-100 range."""
    with (
        patch("services.scorer.client.messages.create", return_value=_mock_claude_response(score=78)),
        patch("services.scorer.AUDIT_LOG", tmp_path / "audit_log.json"),
        patch("routers.scoring_router.track_with_mlflow"),
    ):
        response = _post_score()

    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["score"] <= 100
    assert isinstance(body["reasoning"], str)
    assert "model_version" in body
    assert "latency_ms" in body


def test_scoring_event_written_to_audit_log(tmp_path):
    """Every successful scoring call must append an ai_score entry to audit_log.json."""
    audit_log = tmp_path / "audit_log.json"

    with (
        patch("services.scorer.client.messages.create", return_value=_mock_claude_response(score=65)),
        patch("services.scorer.AUDIT_LOG", audit_log),
        patch("routers.scoring_router.track_with_mlflow"),
    ):
        _post_score(cv_text="Alice Brown\nData scientist.")

    assert audit_log.exists(), "audit_log.json was not created after scoring"

    with open(audit_log) as f:
        entry = json.loads(f.readline())

    assert entry["event"] == "ai_score"
    assert entry["score"] == 65
    assert "timestamp" in entry
    assert "cv_summary" in entry
    assert "reasoning" in entry
    assert "model_version" in entry


# ── Override endpoint tests ───────────────────────────────────────────────────

def test_human_override_is_logged_correctly(tmp_path):
    """An override within 20 points must be logged with the correct fields and no flag."""
    audit_log = tmp_path / "audit_log.json"

    with patch("services.scorer.AUDIT_LOG", audit_log):
        response = client.post(
            "/override-score",
            json={
                "candidate_id": "Alice Brown",
                "original_score": 65,
                "new_score": 80,
                "reason": "Strong portfolio noted during interview.",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["new_score"] == 80
    assert body["score_difference"] == 15
    assert body["large_override_flag"] is False  # 15 ≤ 20, should not be flagged

    # Verify the log entry matches the request
    with open(audit_log) as f:
        entry = json.loads(f.readline())

    assert entry["event"] == "human_override"
    assert entry["candidate_id"] == "Alice Brown"
    assert entry["original_score"] == 65
    assert entry["new_score"] == 80
    assert entry["reason"] == "Strong portfolio noted during interview."
    assert entry["large_override_flag"] is False


def test_large_override_flag_is_raised(tmp_path):
    """A score change greater than 20 points must set large_override_flag to True."""
    with patch("services.scorer.AUDIT_LOG", tmp_path / "audit_log.json"):
        response = client.post(
            "/override-score",
            json={
                "candidate_id": "Bob Jones",
                "original_score": 30,
                "new_score": 90,
                "reason": "Exceptional in-person performance.",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["score_difference"] == 60
    assert body["large_override_flag"] is True  # 60 > 20

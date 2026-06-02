import json
from pathlib import Path

CV_LOG = Path(__file__).parent.parent / "logs" / "cv_log.json"
AUDIT_LOG = Path(__file__).parent.parent / "logs" / "audit_log.json"


def _read_jsonl(path: Path) -> list:
    """Read all JSONL lines from a log file. Returns [] if the file does not exist."""
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def count_cvs_processed() -> int:
    """Number of CVs that have been uploaded and parsed."""
    return len(_read_jsonl(CV_LOG))


def count_scoring_events() -> int:
    """Number of AI scoring runs recorded in the audit log."""
    return sum(1 for e in _read_jsonl(AUDIT_LOG) if e.get("event") == "ai_score")


def count_override_events() -> int:
    """Number of times a recruiter manually overrode an AI score."""
    return sum(1 for e in _read_jsonl(AUDIT_LOG) if e.get("event") == "human_override")


def average_scoring_latency_ms() -> float:
    """Mean Claude API latency in milliseconds across all scoring events."""
    latencies = [
        e["latency_ms"]
        for e in _read_jsonl(AUDIT_LOG)
        if e.get("event") == "ai_score" and "latency_ms" in e
    ]
    if not latencies:
        return 0.0
    return round(sum(latencies) / len(latencies), 2)


def get_metrics() -> dict:
    """Aggregate all metrics into a single dict for the /metrics endpoint."""
    return {
        "total_cvs_processed": count_cvs_processed(),
        "total_scoring_events": count_scoring_events(),
        "total_human_overrides": count_override_events(),
        "average_scoring_latency_ms": average_scoring_latency_ms(),
    }

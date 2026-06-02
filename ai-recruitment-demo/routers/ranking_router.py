import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Rankings"])

AUDIT_LOG = Path(__file__).parent.parent / "logs" / "audit_log.json"


# ── Data helpers ──────────────────────────────────────────────────────────────

def _read_events() -> list:
    """Read all JSONL lines from the audit log. Returns [] if file does not exist."""
    if not AUDIT_LOG.exists():
        return []
    events = []
    with open(AUDIT_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def _build_rankings() -> list:
    """
    Merge ai_score and human_override events into a ranked list.

    Overrides are matched to scoring events by candidate name, which is
    extracted as the first line of cv_summary (mirrors parse_cv_data logic).
    The displayed score is the human score when an override exists.
    """
    events = _read_events()

    scoring_events = [e for e in events if e.get("event") == "ai_score"]

    # Build a lookup of overrides keyed by candidate_id (the name the recruiter supplied)
    override_map = {
        e["candidate_id"]: e
        for e in events
        if e.get("event") == "human_override"
    }

    candidates = []
    for event in scoring_events:
        # First line of cv_summary is the candidate's name (see parse_cv_data)
        name = (event.get("cv_summary") or "").splitlines()[0].strip() or "Unknown"

        override = override_map.get(name)
        effective_score = override["new_score"] if override else event["score"]

        candidates.append({
            "name": name,
            "score": effective_score,
            "ai_score": event["score"],
            "reasoning": event.get("reasoning", ""),
            "overridden": override is not None,
            "override_reason": override.get("reason") if override else None,
            "timestamp": event.get("timestamp", ""),
            "model_version": event.get("model_version", ""),
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/rankings")
def get_rankings():
    """Return all scored candidates sorted by score (highest first)."""
    return _build_rankings()


@router.get("/", response_class=HTMLResponse)
def dashboard():
    """Serve a simple HTML dashboard showing the candidate rankings table."""
    candidates = _build_rankings()
    return _render_html(candidates)


# ── HTML renderer ─────────────────────────────────────────────────────────────

def _render_html(candidates: list) -> str:
    if candidates:
        rows = ""
        for rank, c in enumerate(candidates, start=1):
            # Build the override badge if this score was manually changed
            badge = ""
            if c["overridden"]:
                note = f"Human override &mdash; AI score was {c['ai_score']}"
                if c["override_reason"]:
                    note += f": {c['override_reason']}"
                badge = f'<span class="badge">{note}</span>'

            rows += f"""
            <tr>
                <td class="rank">{rank}</td>
                <td>{c["name"]}</td>
                <td class="score">{c["score"]}</td>
                <td>{c["reasoning"]}{("<br>" + badge) if badge else ""}</td>
                <td class="ts">{c["timestamp"]}</td>
            </tr>"""
        tbody = rows
    else:
        tbody = '<tr><td colspan="5" class="empty">No candidates have been scored yet.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Recruitment &mdash; Candidate Rankings</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      background: #f0f2f5;
      color: #222;
      margin: 0;
      padding: 2rem;
    }}
    header {{ margin-bottom: 1.5rem; }}
    h1 {{ margin: 0 0 0.25rem; font-size: 1.6rem; }}
    p.sub {{ margin: 0; color: #666; font-size: 0.95rem; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: #fff;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,.08);
    }}
    thead tr {{ background: #1a1a2e; color: #fff; }}
    th {{ padding: 0.8rem 1rem; text-align: left; font-weight: 600; }}
    td {{ padding: 0.75rem 1rem; border-bottom: 1px solid #eee; vertical-align: top; }}
    tr:last-child td {{ border-bottom: none; }}
    tbody tr:hover td {{ background: #f7f8ff; }}
    .rank {{ text-align: center; font-weight: 700; color: #555; width: 3rem; }}
    .score {{
      text-align: center;
      font-size: 1.25rem;
      font-weight: 700;
      color: #1a1a2e;
      width: 5rem;
    }}
    .ts {{ font-size: 0.8rem; color: #888; white-space: nowrap; }}
    .badge {{
      display: inline-block;
      margin-top: 0.4rem;
      padding: 0.2rem 0.55rem;
      background: #fff8e1;
      border: 1px solid #f9a825;
      border-radius: 4px;
      font-size: 0.78rem;
      color: #7a5000;
    }}
    .empty {{
      text-align: center;
      padding: 3rem 1rem;
      color: #aaa;
      font-style: italic;
    }}
  </style>
</head>
<body>
  <header>
    <h1>AI Recruitment &mdash; Candidate Rankings</h1>
    <p class="sub">Sorted by score (highest first). Human overrides are highlighted in amber.</p>
  </header>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Candidate</th>
        <th>Score</th>
        <th>Reasoning</th>
        <th>Scored At</th>
      </tr>
    </thead>
    <tbody>
      {tbody}
    </tbody>
  </table>
</body>
</html>"""

# Human Oversight Procedure — Hire Screening 3.0

**Version:** 1.0
**Owner:** Hire With Ali — Recruitment Operations
**Last reviewed:** 2026-05-28
**EU AI Act reference:** Article 14 (Human oversight)

---

## Purpose

This procedure defines how human recruiters exercise meaningful oversight over Hire Screening 3.0's AI-generated candidate scores, in compliance with EU AI Act Article 14. The system is classified as high-risk under Annex III; human oversight is therefore a mandatory legal obligation, not an optional feature.

---

## Mandatory Review

**No AI-generated score may be used as the basis for any hiring action without prior human review.**

This means:
- A recruiter must review every score and its reasoning before advancing, rejecting, or shortlisting a candidate
- Scores must not be displayed to candidates or used in external communications without recruiter sign-off
- Automated downstream actions triggered by score thresholds alone (without human review) are prohibited

The recruiter review requirement is enforced procedurally, not technically. Hire With Ali managers are responsible for ensuring recruiters follow this procedure.

---

## Override Logging

When a recruiter disagrees with an AI score, they must submit an override via the `POST /override-score` endpoint. The system will:

1. Record the override in `logs/audit_log.json` with:
   - `candidate_id` — identifier provided by the recruiter
   - `original_score` — the AI-generated score
   - `new_score` — the recruiter's revised score
   - `reason` — mandatory written justification
   - `timestamp` — UTC timestamp of the override
   - `score_difference` — absolute difference between original and new score
   - `large_override_flag` — set to `true` if the difference exceeds 20 points

2. Return a confirmation response including the `large_override_flag` value

**Overrides without a written reason are permitted by the API but discouraged.** A future release will make the `reason` field mandatory.

---

## Escalation

The following conditions trigger automatic escalation for senior review:

| Condition | Flag | Required action |
|-----------|------|----------------|
| Override difference > 20 points | `large_override_flag: true` | Senior recruiter or hiring manager must review the override and document agreement or disagreement |
| AI score < 20 or > 90 | Extreme score range | Recruiter must manually verify the CV was correctly parsed before acting on the score |
| Three or more overrides for the same candidate within 24 hours | Manual monitoring | Escalate to recruitment team lead |

Escalations are logged in the audit trail by convention (add a note in the override `reason` field referencing the escalation). Automated escalation routing is planned for a future release.

---

## Recruiter Responsibilities

Recruiters using Hire Screening 3.0 are responsible for:

1. **Reading the reasoning** — every score comes with a written explanation; recruiters must read it, not just the number
2. **Challenging the score** — if the reasoning seems incorrect or the score seems inconsistent with the CV, submit an override
3. **Documenting overrides** — always provide a clear, honest reason for an override; this is audit evidence
4. **Reporting anomalies** — if the system produces obviously wrong scores (e.g. all candidates scoring 50, nonsensical reasoning), report immediately to compliance@hirewithali.no

---

## Audit and Review

- The compliance team reviews the `logs/audit_log.json` file monthly to check override rates and patterns
- An override rate above 30% in any 30-day period triggers an internal review of model performance
- All audit logs are retained for 5 years (see [data-governance.md](data-governance.md))

---

## EU AI Act Reference

This procedure implements the requirements of **EU AI Act Article 14 (Human oversight)**:

- Article 14(1): Measures enabling natural persons to oversee and intervene — covered by `/override-score` endpoint
- Article 14(2): Oversight measures built into the system by the provider — covered by `large_override_flag` and escalation thresholds
- Article 14(4)(a): Awareness of system capabilities and limitations — covered by recruiter training (see MODEL_CARD.md Limitations section)
- Article 14(4)(c): Ability to interpret system output — covered by mandatory reasoning field in every score response
- Article 14(4)(d): Ability to decide not to use the system — covered by override capability and mandatory human review requirement

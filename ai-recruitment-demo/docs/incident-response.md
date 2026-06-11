# Incident Response — Hire Screening 3.0

**Version:** 1.0
**Owner:** Hire With Ali — Engineering & Compliance
**Last reviewed:** 2026-05-28
**EU AI Act reference:** Article 62 (Reporting of serious incidents)

---

## Purpose

This document defines how Hire With Ali identifies, classifies, responds to, and reports incidents involving Hire Screening 3.0. It fulfils the incident-response documentation requirement implied by EU AI Act Article 62 for providers of high-risk AI systems.

---

## Incident Classification

### P1 — Critical: Scoring failure affecting live candidates

**Definition:** The system produces AI scores for real candidates that are demonstrably incorrect, systematically biased, or otherwise unsuitable as decision-support inputs, and those scores have been or may have been acted upon.

**Examples:**
- All candidates in a batch receive the same score regardless of CV content
- The LLM returns scores outside the 0–100 range or non-numeric values
- Evidence that protected characteristics (age, gender, ethnicity) are driving scores
- Complete scoring service unavailability (API returning 5xx errors) during an active recruitment campaign

**Response time:** 2 hours from detection to initial containment action

---

### P2 — High: Audit log unavailable

**Definition:** The audit logging system is not writing to `logs/audit_log.json` or `logs/cv_log.json`, meaning scoring and override events are not being recorded.

**Examples:**
- Log files missing or empty after confirmed scoring activity
- Disk full preventing log writes
- File permissions preventing the application from writing logs
- Log files deleted or corrupted

**Response time:** 4 hours from detection to audit log restoration

---

### P3 — Medium: Performance degradation

**Definition:** The system is operational but performing below acceptable thresholds, creating a degraded experience without an immediate compliance risk.

**Examples:**
- Scoring latency (p95) exceeds 5 000 ms for more than 15 minutes
- Groq API error rate exceeds 5% over a 10-minute window
- MLflow logging failing (scoring still works but monitoring data is lost)
- CI/CD compliance workflow failing without a code change

**Response time:** 24 hours from detection to resolution or accepted risk

---

## Response Timelines

| Priority | Initial response | Containment | Resolution |
|----------|-----------------|-------------|-----------|
| P1 | 2 hours | 2 hours | 24 hours |
| P2 | 4 hours | 4 hours | 24 hours |
| P3 | 24 hours | 48 hours | 5 business days |

*Initial response* = incident owner identified, impact assessed, stakeholders notified.
*Containment* = immediate risk to candidates or compliance mitigated (e.g. scoring disabled, audit log restored).
*Resolution* = root cause fixed, monitoring confirms normal operation.

---

## Notification

### Internal notification
- **P1/P2:** Engineering lead and compliance officer notified immediately via direct message; all-hands engineering alert within 30 minutes
- **P3:** Engineering team notified via standard channel; no immediate escalation required

### Vigilens notification
- **P1 incidents:** Vigilens (our compliance monitoring provider) is notified within **24 hours** of detection. Contact: as per Vigilens account dashboard.
- Vigilens notification is required so that any automated compliance evidence collected during the incident window can be flagged as potentially unreliable.

### Regulatory notification
- If a P1 incident constitutes a **serious incident** under EU AI Act Article 62 (i.e. it poses a risk to health, safety, or fundamental rights), the relevant national market surveillance authority must be notified. This determination is made by the compliance officer in consultation with legal counsel.

---

## Post-Incident Review

A post-incident review (PIR) is required for all P1 and P2 incidents. The PIR must be completed within **5 business days** of incident resolution and must include:

1. **Timeline** — chronological sequence of events from first detection to resolution
2. **Root cause** — what failed and why
3. **Impact assessment** — how many candidates or recruiter actions were affected; whether any hiring decisions were made based on incorrect data
4. **Remediation** — what was changed to fix the root cause
5. **Prevention** — what monitoring, tests, or process changes will prevent recurrence
6. **Evidence** — relevant log excerpts, MLflow run IDs, GitHub commit hashes

PIR documents are stored in the internal compliance drive and referenced in the next Vigilens audit pack update.

---

## EU AI Act Reference

This procedure implements the incident-management obligations of **EU AI Act Article 62**:

- Article 62(1): Providers of high-risk AI systems placed on the market must report serious incidents to the relevant national market surveillance authority
- Article 62(3): Reports must be made without undue delay and in any case within 15 days of becoming aware of the incident (P1 notification timeline above is more conservative)
- Article 11 (Technical documentation): Incident response procedures form part of the required technical documentation for high-risk AI systems

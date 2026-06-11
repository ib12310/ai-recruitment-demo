# Model Card — Hire Screening 3.0

**Version:** 1.2.0
**Last updated:** 2026-05-28
**Contact:** compliance@hirewithali.no

---

## Model Details

| Field | Value |
|-------|-------|
| **Model name** | Hire Screening 3.0 |
| **Model version** | 1.2.0 |
| **Base model** | meta-llama/Llama-3.3-70B-Instruct via Groq API |
| **Model type** | Large language model (instruction-tuned), accessed via API |
| **System developer** | Hire With Ali |
| **Release date** | 2026-05-28 |

---

## Intended Use

**Primary use case:** Scoring and ranking job candidates on a scale of 0–100 based on the match between a candidate's CV text and a provided job description. Scores are accompanied by a written explanation of the reasoning.

**Intended users:** HR recruiters at Hire With Ali and its clients, who use scores as a decision-support input — not as a final hiring decision.

**Deployment context:** Internal FastAPI web service, accessible only to authorised recruiters. Not publicly accessible.

---

## Out-of-Scope Use

- **Final hiring decisions without human review.** Scores produced by this system must always be reviewed by a human recruiter before any candidate is accepted or rejected.
- **Use outside the EU.** This system was designed and validated for use within the European Union under EU AI Act Annex III obligations. Deployment in other jurisdictions has not been assessed.
- **Scoring candidates for roles outside the system's training domain** (e.g. highly specialised medical, legal, or security-cleared positions) — accuracy has not been validated for these categories.
- **Processing of non-text CV formats** (images, scanned PDFs without OCR, audio/video) — the system only processes extracted plain text.

---

## Training Data

**No fine-tuning has been performed.** This system uses the pre-trained Llama 3.3 70B Instruct model accessed via the Groq API. No proprietary candidate data has been used to train or fine-tune the model. The base model was trained by Meta; see [Meta's model card](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) for training data details.

---

## Evaluation

| Evaluation | Result |
|------------|--------|
| **Score consistency** | Variance < 8 points across 3 independent runs per profile on a set of 50 synthetic candidate profiles |
| **Score range coverage** | Scores distributed across 25–95 range on synthetic profiles spanning junior to senior candidates |
| **Latency (p95)** | < 2 800 ms end-to-end on Groq API |
| **Format compliance** | 100% valid JSON output on synthetic profile set (model reliably returns the required JSON schema) |

Evaluation was conducted using synthetic candidate profiles only. No real candidate data was used during evaluation.

---

## Human Oversight

All scores produced by this system are **advisory only**. The following controls are mandatory:

1. Every AI score must be reviewed by an authorised recruiter before any hiring action is taken.
2. Recruiters may override any score at any time via the `/override-score` endpoint.
3. All overrides are logged with recruiter ID, timestamp, original score, new score, and stated reason.
4. Overrides where the score difference exceeds 20 points are automatically flagged (`large_override_flag: true`) for senior review.

---

## Limitations

- **Potential bias:** The base Llama 3.3 70B model may reflect biases present in its pre-training data. Hire With Ali does not independently audit the base model for bias.
- **Language:** The system performs best on CVs and job descriptions written in English. Performance on other languages has not been validated.
- **No image processing:** Scanned CVs, image-based PDFs, or CVs with embedded graphics are not processed; only extracted plain text is scored.
- **Context length:** Very long CVs (> ~6 000 words) are truncated to fit within the model's context window.
- **No ground truth:** There is no objectively correct score for a given CV/job-description pair. Scores reflect the model's interpretation, not ground truth.

---

## EU AI Act Classification

| Field | Value |
|-------|-------|
| **Risk classification** | High-risk |
| **Annex III category** | Employment, workers management and access to self-employment — point 2: AI systems used for recruitment or selection of natural persons |
| **Applicable obligations** | Articles 9–15 (risk management, data governance, technical documentation, record-keeping, transparency, human oversight, accuracy and robustness) |
| **Notified body** | Not yet applicable (system not yet placed on the EU market) |

---

## Contact

- **Compliance queries:** compliance@hirewithali.no
- **Security vulnerabilities:** security@hirewithali.no
- **General:** See [SECURITY.md](SECURITY.md)

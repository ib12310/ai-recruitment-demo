# Security Policy — Hire Screening 3.0

## Supported Versions

Only the current stable release receives security patches.

| Version | Supported |
|---------|-----------|
| 1.2.x   | Yes       |
| 1.1.x   | No        |
| 1.0.x   | No        |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Send a description of the vulnerability to **security@hirewithali.no**. Include:

- A description of the issue and its potential impact
- Steps to reproduce (proof-of-concept code is helpful but not required)
- Which version of the system is affected
- Any suggested remediation if you have one

### What we commit to

| Timeline | Commitment |
|----------|-----------|
| 48 hours | Acknowledge receipt of your report |
| 7 days   | Patch or mitigate critical vulnerabilities (CVSS ≥ 9.0) |
| 30 days  | Patch high-severity vulnerabilities (CVSS 7.0–8.9) |
| 90 days  | Patch or accept risk for medium/low vulnerabilities |

We will keep you informed of progress throughout. If we need more time for a complex fix, we will notify you and agree a disclosure date.

We do not operate a bug bounty programme at this time.

## Out of Scope

The following are outside the scope of this security policy:

- **Groq API / LLM provider** — security issues with the underlying Groq inference service should be reported directly to [Groq Security](https://groq.com)
- **General phishing or social engineering** targeting Hire With Ali employees
- **Third-party dependencies** — vulnerabilities in packages we consume (e.g. FastAPI, MLflow) should be reported to their respective maintainers; we will update our dependencies in response to published CVEs
- **Issues requiring physical access** to our infrastructure
- **Denial-of-service attacks** — rate limiting is handled at the infrastructure layer

## EU AI Act Incident Notification

In addition to security vulnerabilities, if you discover behaviour of the Hire Screening system that could constitute a **serious incident** under EU AI Act Article 62 (e.g. systematic scoring errors, evidence of discriminatory output patterns), please also contact **compliance@hirewithali.no**.

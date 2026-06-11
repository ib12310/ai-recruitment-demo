"""
Seed 15 realistic historical MLflow runs for the hire-screening-production
experiment, simulating 3 weeks of production monitoring activity.

Run once to populate the MLflow tracking server:
    python scripts/seed_mlflow_runs.py

Uses a fixed random seed so output is reproducible.
"""

import random
import sys
from datetime import datetime, timedelta

import mlflow

random.seed(42)

EXPERIMENT_NAME = "hire-screening-production"
REVIEWERS = ["recruiter_01", "recruiter_02", "recruiter_03"]
NUM_RUNS = 15
DAYS_BACK = 21

ANOMALY_INDICES = {3, 11}  # two of the 15 runs will be flagged as anomalies

ANOMALY_REASONS = [
    "Score variance exceeded threshold — manual review triggered",
    "Latency spike detected — Groq API degradation",
]


def _simulated_date(run_index: int) -> datetime:
    """Spread runs evenly across DAYS_BACK days, newest run today."""
    base = datetime.utcnow()
    offset_days = DAYS_BACK - (run_index * DAYS_BACK / (NUM_RUNS - 1))
    return base - timedelta(days=offset_days)


def seed_runs() -> None:
    mlflow.set_tracking_uri("http://localhost:5000")

    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        experiment_id = mlflow.create_experiment(EXPERIMENT_NAME)
        print(f"Created experiment '{EXPERIMENT_NAME}' (id: {experiment_id})")
    else:
        experiment_id = experiment.experiment_id
        print(f"Using existing experiment '{EXPERIMENT_NAME}' (id: {experiment_id})")

    mlflow.set_experiment(EXPERIMENT_NAME)

    for i in range(NUM_RUNS):
        run_date = _simulated_date(i)
        date_str = run_date.strftime("%Y%m%d")
        run_name = f"batch-{date_str}-{i + 1:03d}"
        is_anomaly = i in ANOMALY_INDICES

        candidates_processed = random.randint(3, 12)
        human_overrides = random.randint(0, min(3, candidates_processed))
        override_rate = round(human_overrides / candidates_processed, 2)

        if is_anomaly:
            score_mean = round(random.uniform(40.0, 78.0), 2)
            score_std = round(random.uniform(12.1, 18.5), 2)
            latency_ms = round(random.uniform(2400.0, 4200.0), 2)
        else:
            score_mean = round(random.uniform(52.0, 71.0), 2)
            score_std = round(random.uniform(4.2, 9.8), 2)
            latency_ms = round(random.uniform(1100.0, 2800.0), 2)

        with mlflow.start_run(run_name=run_name) as run:
            # Metrics
            mlflow.log_metric("score_mean", score_mean)
            mlflow.log_metric("score_std", score_std)
            mlflow.log_metric("latency_ms", latency_ms)
            mlflow.log_metric("candidates_processed", candidates_processed)
            mlflow.log_metric("human_overrides", human_overrides)
            mlflow.log_metric("override_rate", override_rate)

            # Params
            mlflow.log_param("model_version", "1.2.0")
            mlflow.log_param("llm_provider", "groq")
            mlflow.log_param("llm_model", "llama-3.3-70b-versatile")
            mlflow.log_param("environment", "production")
            mlflow.log_param("reviewer", REVIEWERS[i % len(REVIEWERS)])

            # Tags
            mlflow.set_tag("mlflow.runName", run_name)
            mlflow.set_tag("run_date", run_date.strftime("%Y-%m-%d"))
            mlflow.set_tag("compliance.reviewed", "true")
            mlflow.set_tag("compliance.framework", "EU-AI-ACT-ANNEX-III")
            mlflow.set_tag("system.version", "hire-screening-3.0")

            if is_anomaly:
                anomaly_reason = ANOMALY_REASONS[list(ANOMALY_INDICES).index(i)]
                mlflow.set_tag("compliance.anomaly", "true")
                mlflow.set_tag("compliance.anomaly_reason", anomaly_reason)

        status = "ANOMALY" if is_anomaly else "OK"
        print(
            f"  [{status:7s}] run {i + 1:02d}/{NUM_RUNS}  {run_name}"
            f"  score_mean={score_mean:.1f}  std={score_std:.1f}"
            f"  latency={latency_ms:.0f}ms  overrides={human_overrides}/{candidates_processed}"
        )

    print(f"\nDone. Logged {NUM_RUNS} runs to experiment '{EXPERIMENT_NAME}'.")
    print(f"View at: http://localhost:5000/#/experiments/{experiment_id}")


if __name__ == "__main__":
    try:
        seed_runs()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

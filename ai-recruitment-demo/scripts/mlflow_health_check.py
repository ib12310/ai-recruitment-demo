"""
MLflow health check utility for Hire Screening 3.0.

Connects to the MLflow tracking server, verifies the hire-screening-production
experiment exists, and prints a summary of recent run activity.

Usage:
    python scripts/mlflow_health_check.py

Exit codes:
    0 — experiment exists and server is reachable
    1 — experiment not found or server unreachable
"""

import sys
from datetime import datetime

import mlflow
from mlflow.tracking import MlflowClient

TRACKING_URI = "http://localhost:5000"
EXPERIMENT_NAME = "hire-screening-production"


def health_check() -> int:
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient()

    print(f"MLflow Health Check — {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Tracking URI : {TRACKING_URI}")
    print(f"Experiment   : {EXPERIMENT_NAME}")
    print("-" * 60)

    try:
        experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    except Exception as exc:
        print(f"ERROR: Cannot reach MLflow server at {TRACKING_URI}: {exc}")
        return 1

    if experiment is None:
        print(f"FAIL: Experiment '{EXPERIMENT_NAME}' not found.")
        print("      Run scripts/seed_mlflow_runs.py to create it.")
        return 1

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
    )

    if not runs:
        print(f"WARN: Experiment '{EXPERIMENT_NAME}' exists but contains no runs.")
        return 0

    # Aggregate metrics across all runs
    latencies = []
    score_means = []
    most_recent_ts = None

    for run in runs:
        metrics = run.data.metrics
        if "latency_ms" in metrics:
            latencies.append(metrics["latency_ms"])
        if "score_mean" in metrics:
            score_means.append(metrics["score_mean"])
        if most_recent_ts is None:
            start_ms = run.info.start_time
            if start_ms:
                most_recent_ts = datetime.utcfromtimestamp(start_ms / 1000)

    avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else None
    avg_score = round(sum(score_means) / len(score_means), 2) if score_means else None
    most_recent_str = most_recent_ts.strftime("%Y-%m-%d %H:%M UTC") if most_recent_ts else "unknown"

    print(f"STATUS       : PASS")
    print(f"Total runs   : {len(runs)}")
    print(f"Most recent  : {most_recent_str}")
    print(f"Avg latency  : {avg_latency} ms" if avg_latency else "Avg latency  : n/a")
    print(f"Avg score    : {avg_score}" if avg_score else "Avg score    : n/a")

    anomaly_runs = [
        r for r in runs if r.data.tags.get("compliance.anomaly") == "true"
    ]
    if anomaly_runs:
        print(f"Anomaly runs : {len(anomaly_runs)}")
        for r in anomaly_runs:
            reason = r.data.tags.get("compliance.anomaly_reason", "no reason recorded")
            print(f"  - {r.info.run_name}: {reason}")
    else:
        print("Anomaly runs : 0")

    return 0


if __name__ == "__main__":
    sys.exit(health_check())

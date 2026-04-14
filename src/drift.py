from pathlib import Path
from typing import Optional
from .metrics import get_latest_metrics, get_baseline_metrics, get_metrics_history

# --- Drift Thresholds ---
ACCURACY_DRIFT_THRESHOLD = 0.05      # alert if accuracy drops more than 5%
F1_DRIFT_THRESHOLD = 0.05            # alert if f1 drops more than 5%
LATENCY_DRIFT_THRESHOLD = 0.30       # alert if latency increases more than 30%
RECALL_DRIFT_THRESHOLD = 0.05        # alert if recall drops more than 5%


def calculate_drift(baseline: dict, current: dict) -> dict:
    drifts = []

    # accuracy drift
    if baseline.get("accuracy") and current.get("accuracy"):
        accuracy_drop = baseline["accuracy"] - current["accuracy"]
        if accuracy_drop >= ACCURACY_DRIFT_THRESHOLD:
            drifts.append({
                "metric": "accuracy",
                "baseline": baseline["accuracy"],
                "current": current["accuracy"],
                "delta": round(-accuracy_drop, 4),
                "threshold": ACCURACY_DRIFT_THRESHOLD,
                "severity": "CRITICAL" if accuracy_drop >= 0.10 else "WARNING",
            })

    # f1 drift
    if baseline.get("f1_score") and current.get("f1_score"):
        f1_drop = baseline["f1_score"] - current["f1_score"]
        if f1_drop >= F1_DRIFT_THRESHOLD:
            drifts.append({
                "metric": "f1_score",
                "baseline": baseline["f1_score"],
                "current": current["f1_score"],
                "delta": round(-f1_drop, 4),
                "threshold": F1_DRIFT_THRESHOLD,
                "severity": "CRITICAL" if f1_drop >= 0.10 else "WARNING",
            })

    # recall drift
    if baseline.get("recall") and current.get("recall"):
        recall_drop = baseline["recall"] - current["recall"]
        if recall_drop >= RECALL_DRIFT_THRESHOLD:
            drifts.append({
                "metric": "recall",
                "baseline": baseline["recall"],
                "current": current["recall"],
                "delta": round(-recall_drop, 4),
                "threshold": RECALL_DRIFT_THRESHOLD,
                "severity": "CRITICAL" if recall_drop >= 0.10 else "WARNING",
            })

    # latency drift
    if baseline.get("latency_ms") and current.get("latency_ms"):
        latency_increase = (current["latency_ms"] - baseline["latency_ms"]) / baseline["latency_ms"]
        if latency_increase >= LATENCY_DRIFT_THRESHOLD:
            drifts.append({
                "metric": "latency_ms",
                "baseline": baseline["latency_ms"],
                "current": current["latency_ms"],
                "delta": round(latency_increase, 4),
                "threshold": LATENCY_DRIFT_THRESHOLD,
                "severity": "WARNING",
            })

    overall_drift_detected = len(drifts) > 0
    overall_severity = "CRITICAL" if any(d["severity"] == "CRITICAL" for d in drifts) else (
        "WARNING" if drifts else "HEALTHY"
    )

    return {
        "model_id": current.get("model_id"),
        "drift_detected": overall_drift_detected,
        "overall_severity": overall_severity,
        "baseline_run": baseline.get("run_id"),
        "current_run": current.get("run_id"),
        "drifts": drifts,
    }


def check_drift(model_id: str) -> dict:
    baseline = get_baseline_metrics(model_id)
    current = get_latest_metrics(model_id)

    if not baseline or not current:
        return {
            "model_id": model_id,
            "drift_detected": False,
            "overall_severity": "UNKNOWN",
            "message": "Insufficient metrics data",
            "drifts": [],
        }

    return calculate_drift(baseline, current)


if __name__ == "__main__":
    models = ["fraud_detector_v1", "churn_predictor_v1", "credit_scorer_v1", "payment_router_v1"]

    for model_id in models:
        result = check_drift(model_id)
        print(f"\nModel: {model_id}")
        print(f"Drift detected: {result['drift_detected']} | Severity: {result['overall_severity']}")
        for d in result["drifts"]:
            print(f"  [{d['severity']}] {d['metric']}: {d['baseline']} → {d['current']} (delta: {d['delta']})")
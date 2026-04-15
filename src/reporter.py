from typing import List, Dict
from .llm_client import generate_narrative
from .drift import check_drift
from .alerts import generate_alerts_from_drift


def build_prompt(model_summaries: List[Dict]) -> str:
    lines = []
    for m in model_summaries:
        drift = m["drift"]
        alerts = m["alerts"]
        drift_list = [f"{d['metric']}: {d['baseline']} -> {d['current']}" for d in drift['drifts']]
        alert_list = [a['alert_type'] for a in alerts]
        lines.append(
            f"Model: {m['model_id']}\n"
            f"  Status: {drift['overall_severity']}\n"
            f"  Drift detected: {drift['drift_detected']}\n"
            f"  Drifts: {drift_list}\n"
            f"  Alerts: {alert_list}\n"
        )

    return (
        "You are an MLOps engineer at a fintech company.\n"
        "Write a concise 4-5 sentence model health summary covering: "
        "overall fleet health, which models need immediate attention, "
        "what metrics are drifting, and one recommended action.\n\n"
        "=== Model Health Report ===\n" +
        "\n".join(lines)
    )


def generate_fleet_report(model_ids: List[str]) -> Dict:
    model_summaries = []
    for model_id in model_ids:
        drift = check_drift(model_id)
        alerts = generate_alerts_from_drift(drift)
        model_summaries.append({
            "model_id": model_id,
            "drift": drift,
            "alerts": alerts,
        })

    prompt = build_prompt(model_summaries)
    narrative = generate_narrative(prompt)

    return {
        "models_checked": len(model_ids),
        "models_drifting": sum(1 for m in model_summaries if m["drift"]["drift_detected"]),
        "model_summaries": model_summaries,
        "narrative": narrative,
    }


if __name__ == "__main__":
    result = generate_fleet_report([
        "fraud_detector_v1",
        "churn_predictor_v1",
        "credit_scorer_v1",
        "payment_router_v1",
    ])
    print(f"\nModels checked: {result['models_checked']}")
    print(f"Models drifting: {result['models_drifting']}")
    print(f"\nNARRATIVE:\n{result['narrative']}")
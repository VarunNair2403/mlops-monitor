from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .registry import list_models, get_model, register_model
from .drift import check_drift
from .alerts import get_active_alerts, get_alert_stats, generate_alerts_from_drift
from .reporter import generate_fleet_report
from .metrics import log_metrics, get_latest_metrics, get_metrics_history

app = FastAPI(
    title="MLOps Monitor",
    description="Model performance monitoring, drift detection and LLM-powered fleet reporting",
    version="0.1.0",
)


class MetricsRequest(BaseModel):
    model_id: str
    run_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    latency_ms: float
    sample_size: int
    environment: Optional[str] = "production"


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/models")
def get_models():
    models = list_models()
    return {
        "count": len(models),
        "models": models,
    }


@app.get("/models/{model_id}")
def get_model_detail(model_id: str):
    model = get_model(model_id)
    if not model:
        return {"error": f"Model {model_id} not found"}
    latest = get_latest_metrics(model_id)
    drift = check_drift(model_id)
    return {
        "model": model,
        "latest_metrics": latest,
        "drift": drift,
    }


@app.post("/metrics")
def submit_metrics(request: MetricsRequest):
    log_metrics(
        request.model_id, request.run_id, request.accuracy,
        request.precision, request.recall, request.f1_score,
        request.latency_ms, request.sample_size, request.environment
    )
    drift = check_drift(request.model_id)
    alerts = generate_alerts_from_drift(drift)
    return {
        "message": "Metrics logged successfully",
        "drift": drift,
        "alerts_generated": len(alerts),
        "alerts": alerts,
    }


@app.get("/drift")
def get_drift_status():
    models = list_models()
    results = []
    for m in models:
        drift = check_drift(m["model_id"])
        results.append(drift)
    return {
        "models_checked": len(results),
        "models_drifting": sum(1 for r in results if r["drift_detected"]),
        "results": results,
    }


@app.get("/alerts")
def get_alerts(limit: Optional[int] = 20):
    return {
        "stats": get_alert_stats(),
        "alerts": get_active_alerts(limit=limit),
    }


@app.get("/report")
def get_fleet_report():
    models = list_models()
    model_ids = [m["model_id"] for m in models]
    result = generate_fleet_report(model_ids)
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "models_checked": result["models_checked"],
        "models_drifting": result["models_drifting"],
        "narrative": result["narrative"],
    }
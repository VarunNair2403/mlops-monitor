import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "mlops.db"

DDL = """
CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  model_id TEXT NOT NULL,
  alert_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  message TEXT NOT NULL,
  drift_details TEXT,
  resolved INTEGER DEFAULT 0
);
"""


def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    conn.commit()
    conn.close()


def create_alert(model_id: str, alert_type: str, severity: str, message: str, drift_details: dict = None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO alerts
        (timestamp, model_id, alert_type, severity, message, drift_details, resolved)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """,
        (
            datetime.utcnow().isoformat() + "Z",
            model_id,
            alert_type,
            severity,
            message,
            json.dumps(drift_details or {}),
        )
    )
    conn.commit()
    conn.close()


def generate_alerts_from_drift(drift_result: dict) -> List[Dict]:
    alerts = []
    model_id = drift_result.get("model_id")

    if not drift_result.get("drift_detected"):
        return alerts

    severity = drift_result.get("overall_severity")
    drifts = drift_result.get("drifts", [])

    if severity == "CRITICAL":
        message = (
            f"CRITICAL drift detected in {model_id}. "
            f"Immediate retraining required. "
            f"Affected metrics: {[d['metric'] for d in drifts]}"
        )
        create_alert(model_id, "retraining_required", "CRITICAL", message, drift_result)
        alerts.append({
            "model_id": model_id,
            "alert_type": "retraining_required",
            "severity": "CRITICAL",
            "message": message,
        })

    elif severity == "WARNING":
        message = (
            f"WARNING drift detected in {model_id}. "
            f"Monitor closely and schedule retraining. "
            f"Affected metrics: {[d['metric'] for d in drifts]}"
        )
        create_alert(model_id, "drift_warning", "WARNING", message, drift_result)
        alerts.append({
            "model_id": model_id,
            "alert_type": "drift_warning",
            "severity": "WARNING",
            "message": message,
        })

    return alerts


def get_active_alerts(limit: int = 20) -> List[Dict]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, timestamp, model_id, alert_type, severity, message, resolved
        FROM alerts
        WHERE resolved = 0
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "timestamp": r[1],
            "model_id": r[2],
            "alert_type": r[3],
            "severity": r[4],
            "message": r[5],
            "resolved": bool(r[6]),
        }
        for r in rows
    ]


def get_alert_stats() -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
          COUNT(*) as total,
          SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical,
          SUM(CASE WHEN severity = 'WARNING' THEN 1 ELSE 0 END) as warning,
          SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END) as unresolved
        FROM alerts
        """
    )
    row = cur.fetchone()
    conn.close()
    return {
        "total_alerts": row[0],
        "critical": row[1] or 0,
        "warning": row[2] or 0,
        "unresolved": row[3] or 0,
    }


if __name__ == "__main__":
    from src.drift import check_drift

    models = ["fraud_detector_v1", "churn_predictor_v1", "credit_scorer_v1", "payment_router_v1"]

    all_alerts = []
    for model_id in models:
        drift_result = check_drift(model_id)
        alerts = generate_alerts_from_drift(drift_result)
        all_alerts.extend(alerts)

    print(f"\nAlerts generated: {len(all_alerts)}")
    for a in all_alerts:
        print(f"  [{a['severity']}] {a['model_id']} — {a['alert_type']}")

    print("\nActive Alerts:")
    for a in get_active_alerts():
        print(f"  [{a['severity']}] {a['model_id']} | {a['alert_type']} | {a['timestamp']}")

    print("\nAlert Stats:", get_alert_stats())
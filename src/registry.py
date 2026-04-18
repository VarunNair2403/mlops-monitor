#registry
import sqlite3
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "mlops.db"

DDL = """
CREATE TABLE IF NOT EXISTS model_registry (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_id TEXT UNIQUE NOT NULL,
  model_name TEXT NOT NULL,
  model_type TEXT NOT NULL,
  version TEXT NOT NULL,
  description TEXT,
  registered_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active'
);
"""


def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    conn.commit()
    conn.close()


def register_model(model_id: str, model_name: str, model_type: str, version: str, description: str = ""):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO model_registry
            (model_id, model_name, model_type, version, description, registered_at, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
            """,
            (model_id, model_name, model_type, version, description, datetime.utcnow().isoformat() + "Z")
        )
        conn.commit()
        print(f"Registered model: {model_id} v{version}")
    finally:
        conn.close()


def get_model(model_id: str) -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM model_registry WHERE model_id = ?", (model_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return {
        "id": row[0],
        "model_id": row[1],
        "model_name": row[2],
        "model_type": row[3],
        "version": row[4],
        "description": row[5],
        "registered_at": row[6],
        "status": row[7],
    }


def list_models() -> list:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM model_registry ORDER BY registered_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "model_id": r[1],
            "model_name": r[2],
            "model_type": r[3],
            "version": r[4],
            "description": r[5],
            "registered_at": r[6],
            "status": r[7],
        }
        for r in rows
    ]


if __name__ == "__main__":
    register_model("fraud_detector_v1", "Fraud Detector", "classification", "1.0", "Detects fraudulent transactions")
    register_model("churn_predictor_v1", "Churn Predictor", "classification", "1.0", "Predicts customer churn")
    register_model("credit_scorer_v1", "Credit Scorer", "regression", "1.0", "Scores credit risk")
    register_model("payment_router_v1", "Payment Router", "classification", "1.0", "Routes payments to optimal processor")

    print("\nRegistered Models:")
    for m in list_models():
        print(f"  {m['model_id']} | {m['model_type']} | v{m['version']} | {m['status']}")
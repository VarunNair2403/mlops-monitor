import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "mlops.db"

DDL = """
CREATE TABLE IF NOT EXISTS model_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  logged_at TEXT NOT NULL,
  accuracy REAL,
  precision REAL,
  recall REAL,
  f1_score REAL,
  latency_ms REAL,
  sample_size INTEGER,
  environment TEXT DEFAULT 'production'
);
"""


def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    conn.commit()
    conn.close()


def log_metrics(model_id: str, run_id: str, accuracy: float, precision: float,
                recall: float, f1_score: float, latency_ms: float,
                sample_size: int, environment: str = "production"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO model_metrics
        (model_id, run_id, logged_at, accuracy, precision, recall,
         f1_score, latency_ms, sample_size, environment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (model_id, run_id, datetime.utcnow().isoformat() + "Z",
         accuracy, precision, recall, f1_score, latency_ms, sample_size, environment)
    )
    conn.commit()
    conn.close()


def get_latest_metrics(model_id: str) -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM model_metrics
        WHERE model_id = ?
        ORDER BY logged_at DESC
        LIMIT 1
        """,
        (model_id,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return {
        "model_id": row[1],
        "run_id": row[2],
        "logged_at": row[3],
        "accuracy": row[4],
        "precision": row[5],
        "recall": row[6],
        "f1_score": row[7],
        "latency_ms": row[8],
        "sample_size": row[9],
        "environment": row[10],
    }


def get_metrics_history(model_id: str, limit: int = 10) -> list:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM model_metrics
        WHERE model_id = ?
        ORDER BY logged_at DESC
        LIMIT ?
        """,
        (model_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "model_id": r[1],
            "run_id": r[2],
            "logged_at": r[3],
            "accuracy": r[4],
            "precision": r[5],
            "recall": r[6],
            "f1_score": r[7],
            "latency_ms": r[8],
            "sample_size": r[9],
            "environment": r[10],
        }
        for r in rows
    ]


def get_baseline_metrics(model_id: str) -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM model_metrics
        WHERE model_id = ?
        ORDER BY logged_at ASC
        LIMIT 1
        """,
        (model_id,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return {
        "model_id": row[1],
        "run_id": row[2],
        "logged_at": row[3],
        "accuracy": row[4],
        "precision": row[5],
        "recall": row[6],
        "f1_score": row[7],
        "latency_ms": row[8],
        "sample_size": row[9],
        "environment": row[10],
    }


if __name__ == "__main__":
    import uuid

    log_metrics("fraud_detector_v1", str(uuid.uuid4())[:8], 0.95, 0.94, 0.93, 0.935, 120.0, 10000)
    log_metrics("fraud_detector_v1", str(uuid.uuid4())[:8], 0.93, 0.92, 0.91, 0.915, 135.0, 10000)
    log_metrics("fraud_detector_v1", str(uuid.uuid4())[:8], 0.89, 0.88, 0.87, 0.875, 158.0, 10000)

    print("Latest metrics for fraud_detector_v1:")
    print(get_latest_metrics("fraud_detector_v1"))

    print("\nMetrics history:")
    for m in get_metrics_history("fraud_detector_v1"):
        print(f"  {m['logged_at']} | accuracy: {m['accuracy']} | f1: {m['f1_score']}")
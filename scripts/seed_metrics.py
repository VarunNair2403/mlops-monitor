import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import log_metrics

# fraud_detector_v1 — drifting
log_metrics("fraud_detector_v1", str(uuid.uuid4())[:8], 0.95, 0.94, 0.93, 0.935, 120.0, 10000)
log_metrics("fraud_detector_v1", str(uuid.uuid4())[:8], 0.93, 0.92, 0.91, 0.915, 135.0, 10000)
log_metrics("fraud_detector_v1", str(uuid.uuid4())[:8], 0.89, 0.88, 0.87, 0.875, 158.0, 10000)

# churn_predictor_v1 — stable
log_metrics("churn_predictor_v1", str(uuid.uuid4())[:8], 0.88, 0.87, 0.86, 0.865, 95.0, 8000)
log_metrics("churn_predictor_v1", str(uuid.uuid4())[:8], 0.87, 0.86, 0.85, 0.855, 98.0, 8000)
log_metrics("churn_predictor_v1", str(uuid.uuid4())[:8], 0.87, 0.86, 0.85, 0.855, 100.0, 8000)

# credit_scorer_v1 — critical drift
log_metrics("credit_scorer_v1", str(uuid.uuid4())[:8], 0.92, 0.91, 0.90, 0.905, 200.0, 15000)
log_metrics("credit_scorer_v1", str(uuid.uuid4())[:8], 0.88, 0.87, 0.86, 0.865, 220.0, 15000)
log_metrics("credit_scorer_v1", str(uuid.uuid4())[:8], 0.81, 0.80, 0.79, 0.795, 310.0, 15000)

# payment_router_v1 — slight drift
log_metrics("payment_router_v1", str(uuid.uuid4())[:8], 0.96, 0.95, 0.94, 0.945, 80.0, 20000)
log_metrics("payment_router_v1", str(uuid.uuid4())[:8], 0.95, 0.94, 0.93, 0.935, 85.0, 20000)
log_metrics("payment_router_v1", str(uuid.uuid4())[:8], 0.94, 0.93, 0.92, 0.925, 88.0, 20000)

print("Seeded metrics for all 4 models.")
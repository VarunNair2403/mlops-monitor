# PRD: MLOps Monitor

**Author:** Varun Nair
**Status:** v1.0 — Complete
**Last Updated:** April 2026

---

## Problem Statement

Machine learning models deployed in production degrade over time. This is called model drift — the gradual deterioration of model performance as the real-world data the model encounters diverges from the data it was trained on.

In financial services this has direct business consequences:

- A fraud detection model with drifting recall misses more fraudulent transactions, increasing chargeback losses
- A credit scoring model with drifting accuracy approves loans it should decline, increasing default rates
- A payment routing model with increasing latency degrades transaction success rates and customer experience

Despite these consequences, most ML teams have no systematic monitoring in place. They discover drift reactively — after a business metric drops, after a compliance audit, or after a customer complaint. By then the damage is done.

The NIST AI RMF, OCC Model Risk Management guidance (SR 11-7), and emerging AI governance regulations all require financial institutions to have model monitoring and validation processes in place. Most firms cannot demonstrate compliance because the tooling does not exist.

This project builds that tooling.

---

## Target Users

- **MLOps engineers** — need automated drift detection across a fleet of models without manually querying metrics databases
- **Data scientists** — need to know when their models need retraining before business metrics are impacted
- **AI product managers** — need plain-English model health summaries to share with non-technical stakeholders
- **Model risk managers** — need an audit trail of model performance over time for SR 11-7 compliance
- **Chief Risk Officers** — need a dashboard view of AI model health across the firm with clear escalation paths

---

## Goals

**Primary Goals**
- Track model performance metrics over time across a fleet of ML models
- Detect drift automatically by comparing current metrics against baseline with configurable thresholds
- Generate CRITICAL and WARNING alerts when drift exceeds thresholds
- Produce plain-English fleet health narratives using GPT for non-technical stakeholders
- Expose model health data as MCP tools for agentic LLM queries

**Secondary Goals**
- Build a reusable MLOps monitoring architecture that can be extended to any model type
- Demonstrate MCP agentic pattern where GPT autonomously investigates fleet health
- Map to SR 11-7 model risk management guidance for financial services

**Non-Goals for v1**
- Real model training or evaluation pipelines
- Data drift detection (only metric drift in v1)
- Automated retraining triggers
- Multi-environment tracking (dev, staging, production)
- Integration with MLflow, SageMaker, or other managed model registries
- Frontend dashboard UI

---

## Success Metrics

- **Drift detection accuracy** — WARNING and CRITICAL correctly fire for models with simulated degradation
- **Alert precision** — healthy models (churn_predictor, payment_router) correctly show no alerts
- **Narrative quality** — GPT fleet report correctly identifies drifting models and recommends actions
- **MCP tool discovery** — GPT correctly discovers and calls the right tools for each question
- **API response time** — all endpoints return in under 5 seconds
- **Audit completeness** — all metrics and alerts logged with no data loss

---

## Scope — What Is In v1

- Model registry with model ID, name, type, version, description, and status
- Metrics logging: accuracy, precision, recall, F1 score, latency, sample size, environment
- Drift detection comparing latest vs baseline with per-metric severity classification
- Configurable thresholds: 5% drop for WARNING, 10% drop for CRITICAL, 30% latency increase for WARNING
- Alert generation and persistence: retraining_required and drift_warning alert types
- Alert statistics: total, critical, warning, unresolved counts
- GPT-powered fleet health narrative via reporter.py
- Interactive CLI with status, alerts, and report commands
- FastAPI REST API with seven endpoints
- MCP server exposing five MLOps tools
- MCP client demo with GPT acting as agentic MLOps investigator
- Synthetic metrics seeder for four realistic fintech models

## Scope — What Is Out of v1

- Real model training or evaluation integration
- Data drift detection using statistical tests
- Automated retraining pipeline triggers
- Multi-environment metric tracking
- MLflow or SageMaker registry integration
- PagerDuty or Slack alert delivery
- RBAC and user authentication
- Frontend dashboard UI
- Historical trend visualization

---

## Feature Breakdown

**1. Model Registry (registry.py)**
SQLite-backed registry storing model metadata. Each model has a unique model_id, human-readable name, type (classification or regression), version, description, registration timestamp, and status. Simulates the model registry functionality of MLflow or AWS SageMaker Model Registry.

**2. Metrics Logging (metrics.py)**
Logs performance metrics per model per evaluation run. Tracks accuracy, precision, recall, F1 score, latency in milliseconds, sample size, and environment. Provides retrieval of latest metrics, full history, and the original baseline run for drift comparison.

**3. Drift Detection (drift.py)**
Compares the latest metrics run against the first baseline run for each model. Calculates absolute delta for accuracy, precision, recall, and F1. Calculates percentage increase for latency. Applies configurable thresholds to classify each drift as WARNING or CRITICAL. Returns a structured drift report with per-metric details and overall severity.

**4. Alert Generation (alerts.py)**
Generates alerts from drift results and persists them to SQLite. CRITICAL overall severity triggers a retraining_required alert. WARNING severity triggers a drift_warning alert. Healthy models generate no alerts. Provides active alert retrieval and aggregate statistics for dashboard use.

**5. LLM Fleet Report (reporter.py + llm_client.py)**
Aggregates drift results across all models into a structured prompt and sends to GPT-4o-mini. Prompt instructs GPT to act as an MLOps engineer and produce a 4-5 sentence fleet health summary identifying which models need immediate attention and recommending a specific action.

**6. MCP Server (mcp_server.py)**
Exposes five MLOps tools via the Model Context Protocol: get_model_status, get_fleet_status, get_drift_report, get_active_alerts, and get_metrics_history. Any MCP-compatible LLM client can connect, discover these tools, and call them dynamically.

**7. MCP Client (mcp_client.py)**
GPT connects as an MCP client, discovers the five available tools, and autonomously decides which to call based on a natural language question. Demonstrates agentic behavior — GPT investigates the model fleet the same way a human MLOps engineer would, starting with fleet overview and drilling into specific models as needed.

**8. CLI (cli.py)**
Interactive terminal interface. Status command shows all models with health icons. Alerts command shows active alerts with stats. Report command generates the full LLM fleet narrative.

**9. REST API (api.py)**
Seven FastAPI endpoints covering health check, model listing, model detail, metrics submission, drift status, active alerts, and fleet report.

---

## Technical Architecture

Data flows in one direction:

Model runs → metrics.py → SQLite → drift.py → delta calculation → alerts.py → alert persistence → reporter.py → GPT-4o-mini → fleet narrative → cli.py or api.py → output

MCP path: mcp_server.py exposes tools → mcp_client.py connects → GPT discovers tools → GPT calls tools → GPT synthesizes answer

Stack: Python 3.11+, SQLite, OpenAI GPT-4o-mini, MCP, FastAPI, Uvicorn, python-dotenv

---

## Regulatory Alignment

- **SR 11-7** — OCC Model Risk Management guidance requires ongoing model monitoring and validation. This tool produces the audit trail and drift reports SR 11-7 expects.
- **NIST AI RMF** — MEASURE function requires quantitative evaluation of AI model performance over time. Drift detection and metrics logging directly address this requirement.
- **DORA** — EU Digital Operational Resilience Act requires financial firms to monitor AI systems for performance degradation. Fleet monitoring and alerting address this requirement.

---

## Production Roadmap

- **Real model integration** — connect to scikit-learn, TensorFlow, or PyTorch evaluation pipelines to log real metrics automatically after each training run
- **MLflow integration** — replace SQLite registry with MLflow for versioning, artifact storage, and experiment tracking
- **Data drift detection** — add statistical tests (KS test, PSI) to detect changes in input data distributions, not just output metrics
- **Automated retraining** — trigger Airflow DAG or SageMaker Pipeline when CRITICAL drift is detected
- **Alerting** — pipe CRITICAL alerts to PagerDuty or Slack with on-call escalation
- **Multi-environment** — track metrics separately across dev, staging, and production with promotion gates
- **Auth** — OAuth2 so model owners only see their own models and risk managers see the full fleet
- **Dashboard UI** — Grafana dashboard over /drift and /alerts endpoints for real-time fleet visibility
- **Evaluation evals** — benchmark GPT narrative quality against human-written model health summaries

---

## Open Questions

1. Should drift be calculated against a fixed baseline or a rolling window of recent runs?
2. At what model fleet size does SQLite need to be replaced with PostgreSQL for concurrent writes?
3. Should CRITICAL alerts automatically pause model serving until retraining is complete?
4. How should the system handle models with insufficient history for meaningful drift calculation?
5. Should the MCP server be deployed as a standalone service or embedded in the main API process?
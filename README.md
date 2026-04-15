# MLOps Monitor

## The Problem

Machine learning models degrade over time. A fraud detection model trained on last year's data will perform worse on today's transactions. A credit scoring model's accuracy drops as economic conditions shift. A payment router's latency increases as traffic patterns change.

This is called model drift — and it's one of the most common silent failures in production AI systems. Most teams only discover drift after it has already caused real damage: missed fraud, incorrect credit decisions, or degraded customer experience.

The challenge is that monitoring ML models in production requires tracking multiple metrics across multiple models, comparing current performance against baselines, firing alerts when thresholds are breached, and communicating findings to both technical and non-technical stakeholders. Most teams do this manually or not at all.

This tool automates the entire workflow.

---

## Why I Built This

I built this as a portfolio project to demonstrate:

- "Implement and manage MLOps practices"
- "Deployment, monitoring, and maintenance of ML models"
- "Knowledge of operationalizing LLMs responsibly through MLOps pipeline"

The goal was to demonstrate:

- **MLOps domain knowledge** — model registry, metrics logging, drift detection, retraining alerts
- **LLM-augmented reporting** — GPT generates plain-English fleet health narratives for non-technical stakeholders
- **MCP agentic architecture** — GPT discovers and calls MLOps tools dynamically, deciding which models to investigate and in what order
- **Production-ready design** — the same architecture a real MLOps platform team would build

---

## How It Works

1. Models are registered in a model registry with type, version, and metadata
2. Performance metrics (accuracy, precision, recall, F1, latency) are logged after each model run
3. drift.py compares the latest metrics against the baseline run and flags degradation
4. alerts.py generates CRITICAL or WARNING alerts when drift exceeds configurable thresholds
5. reporter.py builds a structured prompt and sends it to GPT-4o-mini for a plain-English fleet summary
6. mcp_server.py exposes all MLOps checks as MCP tools
7. mcp_client.py lets GPT act as an agent — discovering tools, deciding which models to investigate, and synthesizing findings
8. cli.py and api.py deliver output via terminal or REST API

---

## Project Structure and File Explanations

**src/registry.py** — Model registry backed by SQLite. Stores model ID, name, type, version, description, and status. Simulates the model registry you would find in MLflow or SageMaker in production.

**src/metrics.py** — Logs performance metrics per model per run. Stores accuracy, precision, recall, F1 score, latency, sample size, and environment. Provides latest metrics, historical metrics, and baseline metrics retrieval.

**src/drift.py** — Compares latest metrics against baseline and calculates delta for each metric. Flags WARNING when a metric drops more than 5% and CRITICAL when it drops more than 10%. Also tracks latency increases above 30%. Returns structured drift report with per-metric severity.

**src/alerts.py** — Generates and persists alerts from drift results. CRITICAL drift triggers a retraining_required alert. WARNING drift triggers a drift_warning alert. Provides active alert retrieval and aggregate statistics.

**src/reporter.py** — Builds a structured prompt from all model drift results and sends to GPT-4o-mini. Returns a 4-5 sentence fleet health narrative identifying which models need attention and recommending actions.

**src/llm_client.py** — OpenAI API wrapper. Isolated so the model can be swapped without touching other files.

**src/mcp_server.py** — Exposes five MLOps tools via MCP: get_model_status, get_fleet_status, get_drift_report, get_active_alerts, get_metrics_history. Any MCP-compatible LLM client can discover and call these tools dynamically.

**src/mcp_client.py** — GPT acts as an MCP client, discovering the five tools and autonomously deciding which to call based on a natural language question. Demonstrates agentic MLOps — GPT investigates the fleet the same way a human MLOps engineer would.

**src/cli.py** — Interactive terminal interface with status, alerts, and report commands.

**src/api.py** — FastAPI REST API with endpoints for models, metrics submission, drift status, alerts, and fleet report.

**scripts/seed_metrics.py** — Seeds realistic metric histories for four fintech models with different health profiles: stable, drifting, and critical.

---

## Quickstart (Local)

**1. Clone and set up environment**

```bash
git clone https://github.com/VarunNair2403/mlops-monitor.git
cd mlops-monitor
python3.11 -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv fastapi uvicorn mcp
```

**2. Add your OpenAI key**

```env
OPENAI_API_KEY=sk-...
```

**3. Seed the database**

```bash
python -m src.registry
python scripts/seed_metrics.py
```

**4. Run via CLI**

```bash
python -m src.cli
```

Commands: status, alerts, report, exit

**5. Run via API**

```bash
uvicorn src.api:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger UI.

**6. Run MCP agentic demo**

```bash
python -m src.mcp_client
```

---

## API Endpoints

- GET /health — Service liveness check
- GET /models — List all registered models
- GET /models/{model_id} — Model detail with latest metrics and drift status
- POST /metrics — Submit new metrics for a model, triggers drift check automatically
- GET /drift — Drift status across all models
- GET /alerts — Active alerts with stats
- GET /report — Full LLM-generated fleet health narrative

---

## Drift Detection Thresholds

- Accuracy drop > 5% → WARNING
- Accuracy drop > 10% → CRITICAL
- F1 score drop > 5% → WARNING
- F1 score drop > 10% → CRITICAL
- Recall drop > 5% → WARNING
- Latency increase > 30% → WARNING

All thresholds are configurable in src/drift.py.

---

## MCP Architecture

Five MLOps tools are exposed via MCP in src/mcp_server.py:

- get_model_status — health status and drift for a specific model
- get_fleet_status — health overview of all models
- get_drift_report — detailed drift analysis for a specific model
- get_active_alerts — all unresolved alerts across the fleet
- get_metrics_history — historical performance runs for a model

GPT connects as an MCP client, discovers these tools, and autonomously decides which to call based on a natural language question — the same way a human MLOps engineer would investigate a fleet health issue.

To run the MCP server standalone:

```bash
python -m src.mcp_server
```

To run GPT as an agentic MCP client:

```bash
python -m src.mcp_client
```

---

## Taking This to Production

- **Real model integration** — replace synthetic metrics with actual model evaluation runs from scikit-learn, TensorFlow, or PyTorch pipelines
- **MLflow or SageMaker** — replace SQLite registry with a managed model registry
- **Airflow pipeline** — schedule drift checks after every model evaluation batch
- **PagerDuty or Slack** — pipe CRITICAL alerts to on-call engineers in real time
- **Auto-retraining** — trigger retraining jobs automatically when CRITICAL drift is detected
- **Data drift** — extend beyond metric drift to detect changes in input data distributions using statistical tests
- **Multi-environment** — track metrics separately across dev, staging, and production
- **Auth** — add OAuth2 so only authorized teams can view model metrics and trigger retraining
- **Dashboard UI** — Grafana or Retool dashboard over the /drift and /alerts endpoints

---

## Tech Stack

- Python 3.11+
- SQLite — model registry, metrics store, and alert log
- OpenAI GPT-4o-mini — fleet narrative generation and MCP agentic client
- MCP — tool exposure for agentic MLOps queries
- FastAPI + Uvicorn — REST API layer
- python-dotenv — environment config
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .registry import list_models, get_model
from .metrics import get_latest_metrics, get_metrics_history
from .drift import check_drift
from .alerts import get_active_alerts, get_alert_stats

app = Server("mlops-monitor-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_model_status",
            description="Get the current health status and drift analysis for a specific ML model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string", "description": "The model ID to check"}
                },
                "required": ["model_id"]
            }
        ),
        Tool(
            name="get_fleet_status",
            description="Get the health status of all registered ML models in the fleet.",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_drift_report",
            description="Get detailed drift analysis for a specific model comparing baseline vs current metrics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string", "description": "The model ID to check for drift"}
                },
                "required": ["model_id"]
            }
        ),
        Tool(
            name="get_active_alerts",
            description="Get all active unresolved alerts across the model fleet.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of alerts to return", "default": 10}
                },
            }
        ),
        Tool(
            name="get_metrics_history",
            description="Get historical performance metrics for a specific model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string", "description": "The model ID"},
                    "limit": {"type": "integer", "description": "Number of historical runs to return", "default": 5}
                },
                "required": ["model_id"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_model_status":
        model = get_model(arguments["model_id"])
        latest = get_latest_metrics(arguments["model_id"])
        drift = check_drift(arguments["model_id"])
        result = {"model": model, "latest_metrics": latest, "drift": drift}
        return [TextContent(type="text", text=json.dumps(result))]

    elif name == "get_fleet_status":
        models = list_models()
        fleet = []
        for m in models:
            drift = check_drift(m["model_id"])
            fleet.append({
                "model_id": m["model_id"],
                "version": m["version"],
                "severity": drift["overall_severity"],
                "drift_detected": drift["drift_detected"],
            })
        return [TextContent(type="text", text=json.dumps(fleet))]

    elif name == "get_drift_report":
        drift = check_drift(arguments["model_id"])
        return [TextContent(type="text", text=json.dumps(drift))]

    elif name == "get_active_alerts":
        limit = arguments.get("limit", 10)
        alerts = get_active_alerts(limit=limit)
        stats = get_alert_stats()
        return [TextContent(type="text", text=json.dumps({"stats": stats, "alerts": alerts}))]

    elif name == "get_metrics_history":
        from .metrics import get_metrics_history as _get_history
        history = _get_history(arguments["model_id"], limit=arguments.get("limit", 5))
        return [TextContent(type="text", text=json.dumps(history))]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
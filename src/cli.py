import sys
from .registry import list_models
from .drift import check_drift
from .alerts import get_active_alerts, get_alert_stats
from .reporter import generate_fleet_report


def main():
    print("\n=== MLOps Monitor ===")
    print("Commands: 'status', 'alerts', 'report', 'exit'\n")

    while True:
        command = input(">> ").strip().lower()

        if not command:
            continue

        if command == "exit":
            print("Goodbye.")
            break

        elif command == "status":
            models = list_models()
            if not models:
                print("No models registered.\n")
                continue

            print(f"\nModel Fleet Status ({len(models)} models):")
            for m in models:
                drift = check_drift(m["model_id"])
                severity = drift["overall_severity"]
                icon = "🚨" if severity == "CRITICAL" else "⚠️" if severity == "WARNING" else "✅"
                print(f"  {icon} {m['model_id']} | {m['model_type']} | v{m['version']} | {severity}")
            print()

        elif command == "alerts":
            stats = get_alert_stats()
            print(f"\nAlert Stats: {stats['total_alerts']} total | {stats['critical']} critical | {stats['warning']} warning | {stats['unresolved']} unresolved")
            active = get_active_alerts()
            if not active:
                print("No active alerts.\n")
            else:
                print("\nActive Alerts:")
                for a in active:
                    icon = "🚨" if a["severity"] == "CRITICAL" else "⚠️"
                    print(f"  {icon} [{a['severity']}] {a['model_id']} — {a['alert_type']}")
                    print(f"     {a['message']}")
            print()

        elif command == "report":
            models = list_models()
            model_ids = [m["model_id"] for m in models]
            print("\nGenerating fleet report...")
            result = generate_fleet_report(model_ids)
            print(f"\nModels checked: {result['models_checked']}")
            print(f"Models drifting: {result['models_drifting']}")
            print(f"\nNARRATIVE:\n{result['narrative']}\n")

        else:
            print("Unknown command. Try: status, alerts, report, exit\n")


if __name__ == "__main__":
    main()
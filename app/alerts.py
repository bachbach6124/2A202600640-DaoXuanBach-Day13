from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ALERT_RULES_PATH = Path("config/alert_rules.yaml")


def load_alert_rules() -> list[dict[str, Any]]:
    document = yaml.safe_load(ALERT_RULES_PATH.read_text(encoding="utf-8"))
    return document.get("alerts", [])


def evaluate_alerts(metrics: dict[str, Any], demo: bool = False) -> list[dict[str, Any]]:
    results = []
    for rule in load_alert_rules():
        threshold_key = "demo_threshold" if demo else "threshold"
        threshold = float(rule[threshold_key])
        current_value = float(metrics.get(rule["metric"], 0.0))
        operator = rule.get("operator", ">")
        firing = current_value > threshold if operator == ">" else current_value < threshold
        results.append(
            {
                "name": rule["name"],
                "severity": rule["severity"],
                "metric": rule["metric"],
                "current_value": current_value,
                "threshold": threshold,
                "operator": operator,
                "for": rule["for"],
                "firing": firing,
                "owner": rule["owner"],
                "runbook": rule["runbook"],
                "mode": "demo" if demo else "production",
            }
        )
    return results

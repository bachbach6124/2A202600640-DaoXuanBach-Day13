from __future__ import annotations

import concurrent.futures
import json
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")
OUTPUT = Path("docs/evidence/p0-verification.json")


def post(client: httpx.Client, path: str, payload: dict | None = None) -> httpx.Response:
    response = client.post(f"{BASE_URL}{path}", json=payload)
    return response


def send_queries(client: httpx.Client, queries: list[dict]) -> list[int]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        responses = list(
            executor.map(lambda query: post(client, "/chat", query), queries)
        )
    return [response.status_code for response in responses]


def alert_by_name(client: httpx.Client, name: str) -> dict:
    alerts = client.get(f"{BASE_URL}/alerts", params={"demo": "true"}).json()
    return next(alert for alert in alerts if alert["name"] == name)


def main() -> None:
    queries = [
        json.loads(line)
        for line in QUERIES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    report: dict[str, object] = {}
    with httpx.Client(timeout=30.0) as client:
        report["health"] = client.get(f"{BASE_URL}/health").json()

        post(client, "/metrics/reset")
        report["baseline_statuses"] = send_queries(client, queries)
        report["baseline_metrics"] = client.get(f"{BASE_URL}/metrics").json()

        post(client, "/metrics/reset")
        post(client, "/incidents/rag_slow/enable")
        report["rag_slow_status"] = post(client, "/chat", queries[0]).status_code
        report["high_latency_alert"] = alert_by_name(client, "high_latency_p95")
        post(client, "/incidents/rag_slow/disable")

        post(client, "/metrics/reset")
        post(client, "/incidents/tool_fail/enable")
        report["tool_fail_status"] = post(client, "/chat", queries[1]).status_code
        report["high_error_alert"] = alert_by_name(client, "high_error_rate")
        post(client, "/incidents/tool_fail/disable")

        post(client, "/metrics/reset")
        post(client, "/incidents/cost_spike/enable")
        report["cost_spike_status"] = post(client, "/chat", queries[2]).status_code
        report["cost_alert"] = alert_by_name(client, "cost_budget_spike")
        post(client, "/incidents/cost_spike/disable")

        post(client, "/metrics/reset")
        send_queries(client, queries)
        report["final_metrics"] = client.get(f"{BASE_URL}/metrics").json()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    for key in ("high_latency_alert", "high_error_alert", "cost_alert"):
        alert = report[key]
        print(f"{alert['name']}: firing={alert['firing']} current={alert['current_value']}")
        if not alert["firing"]:
            raise SystemExit(f"Verification failed: {alert['name']} did not fire")


if __name__ == "__main__":
    main()

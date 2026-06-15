from app.alerts import evaluate_alerts


def test_all_demo_alerts_can_fire() -> None:
    metrics = {
        "latency_p95_ms": 5500,
        "error_rate_pct": 10,
        "avg_cost_usd": 0.01,
    }

    alerts = evaluate_alerts(metrics, demo=True)

    assert len(alerts) == 3
    assert all(alert["firing"] for alert in alerts)
    assert all(alert["runbook"].startswith("docs/alerts.md#") for alert in alerts)

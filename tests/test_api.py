from fastapi.testclient import TestClient

from app.main import app


def test_health_dashboard_metrics_and_alert_endpoints(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "logs.jsonl"))
    with TestClient(app) as client:
        health = client.get("/health")
        dashboard = client.get("/dashboard")
        metrics = client.get("/metrics")
        alerts = client.get("/alerts", params={"demo": "true"})
        logs = client.get("/logs/recent", params={"limit": 5})

    assert health.status_code == 200
    assert health.json()["ok"] is True
    assert "sdk_version" in health.json()["tracing"]
    assert dashboard.status_code == 200
    assert "Latency" in dashboard.text
    assert "Quality proxy" in dashboard.text
    assert metrics.status_code == 200
    assert len(metrics.json()["time_series"]) >= 0
    assert alerts.status_code == 200
    assert len(alerts.json()) == 3
    assert logs.status_code == 200
    assert isinstance(logs.json(), list)

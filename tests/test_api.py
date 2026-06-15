from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor

from app.main import app
from app.metrics import reset


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


def test_incident_error_is_counted_and_controls_work(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "logs.jsonl"))
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    reset()
    payload = {
        "user_id": "api-test",
        "session_id": "error-test",
        "feature": "qa",
        "message": "Explain metrics traces and logs",
    }
    with TestClient(app) as client:
        assert client.post("/incidents/tool_fail/enable").status_code == 200
        failed = client.post("/chat", json=payload)
        metrics = client.get("/metrics").json()
        assert client.post("/incidents/tool_fail/disable").status_code == 200

    assert failed.status_code == 500
    assert metrics["traffic"] == 1
    assert metrics["error_count"] == 1
    assert metrics["error_rate_pct"] == 100


def test_concurrent_chat_requests_have_unique_correlation_ids(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "logs.jsonl"))
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    reset()
    with TestClient(app) as client:
        def send(index: int):
            return client.post(
                "/chat",
                json={
                    "user_id": f"user-{index}",
                    "session_id": f"session-{index}",
                    "feature": "qa",
                    "message": "What is your refund policy?",
                },
            )

        with ThreadPoolExecutor(max_workers=5) as executor:
            responses = list(executor.map(send, range(10)))
        metrics = client.get("/metrics").json()

    assert all(response.status_code == 200 for response in responses)
    correlation_ids = {response.headers["x-request-id"] for response in responses}
    assert len(correlation_ids) == 10
    assert metrics["traffic"] == 10

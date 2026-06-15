from __future__ import annotations

import json
import re

from fastapi.testclient import TestClient

from app.main import app
from app.metrics import reset

PAYLOAD = {
    "user_id": "raw-user-id",
    "session_id": "session-test",
    "feature": "qa",
    "message": "Email student@vinuni.edu.vn card 4111 1111 1111 1111",
}


def test_correlation_id_and_enriched_redacted_logs(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setenv("LOG_PATH", str(log_path))
    reset()

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json=PAYLOAD,
            headers={"x-request-id": "demo-request-01"},
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "demo-request-01"
    assert float(response.headers["x-response-time-ms"]) >= 0
    assert response.json()["correlation_id"] == "demo-request-01"

    records = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
    ]
    api_records = [record for record in records if record.get("service") == "api"]
    assert api_records
    for record in api_records:
        assert record["correlation_id"] == "demo-request-01"
        assert record["session_id"] == "session-test"
        assert record["feature"] == "qa"
        assert record["model"] == "claude-sonnet-4-5"
        assert record["env"] == "dev"
        assert record["user_id_hash"] != PAYLOAD["user_id"]

    raw_logs = log_path.read_text(encoding="utf-8")
    assert "student@vinuni.edu.vn" not in raw_logs
    assert "4111 1111 1111 1111" not in raw_logs
    assert "[REDACTED_EMAIL]" in raw_logs
    assert "[REDACTED_CREDIT_CARD]" in raw_logs


def test_generates_request_id_and_does_not_leak_context(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setenv("LOG_PATH", str(log_path))

    first = {**PAYLOAD, "session_id": "session-one", "user_id": "user-one"}
    second = {**PAYLOAD, "session_id": "session-two", "user_id": "user-two"}
    with TestClient(app) as client:
        first_response = client.post("/chat", json=first)
        second_response = client.post("/chat", json=second)

    first_id = first_response.headers["x-request-id"]
    second_id = second_response.headers["x-request-id"]
    assert re.fullmatch(r"req-[0-9a-f]{8}", first_id)
    assert re.fullmatch(r"req-[0-9a-f]{8}", second_id)
    assert first_id != second_id

    records = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if '"service": "api"' in line
    ]
    by_correlation = {}
    for record in records:
        by_correlation.setdefault(record["correlation_id"], set()).add(record["session_id"])
    assert by_correlation[first_id] == {"session-one"}
    assert by_correlation[second_id] == {"session-two"}


def test_rejects_unsafe_supplied_request_id(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "logs.jsonl"))
    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={"x-request-id": "student@vinuni.edu.vn"},
        )

    assert response.status_code == 200
    assert re.fullmatch(r"req-[0-9a-f]{8}", response.headers["x-request-id"])

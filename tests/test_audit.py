import json

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from app.main import app


def test_audit_log_is_separate_schema_valid_and_redacted(tmp_path, monkeypatch) -> None:
    audit_path = tmp_path / "audit.jsonl"
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setenv("LOG_PATH", str(log_path))

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "student@vinuni.edu.vn",
                "session_id": "audit-test",
                "feature": "qa",
                "message": "What is your refund policy?",
            },
            headers={"x-request-id": "audit-request-01"},
        )
        recent = client.get("/audit/recent")

    assert response.status_code == 200
    assert audit_path.exists()
    assert audit_path != log_path
    records = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    schema = json.loads(
        open("config/audit_schema.json", encoding="utf-8").read()
    )
    validator = Draft202012Validator(schema)
    assert not list(validator.iter_errors(records[-1]))
    assert records[-1]["actor"] != "student@vinuni.edu.vn"
    assert records[-1]["correlation_id"] == "audit-request-01"
    assert recent.json()[-1]["action"] == "chat.complete"

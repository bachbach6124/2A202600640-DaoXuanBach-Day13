from app.metrics import percentile, record_error, record_request, reset, snapshot


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_contains_dashboard_metrics() -> None:
    reset()
    record_request(100, 0.001, 20, 40, 0.8, trace_id="trace-1")
    record_request(300, 0.002, 30, 60, 0.9, trace_id="trace-2")
    record_error("RuntimeError", latency_ms=50)

    result = snapshot()

    assert result["traffic"] == 3
    assert result["success_count"] == 2
    assert result["error_count"] == 1
    assert result["error_rate_pct"] == 33.33
    assert result["request_rate_per_min"] == 3.0
    assert result["latency_p95_ms"] == 300
    assert result["tokens_in_total"] == 50
    assert len(result["time_series"]) == 3

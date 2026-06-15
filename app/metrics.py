from __future__ import annotations

from collections import Counter, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from statistics import mean
from threading import Lock


@dataclass
class RequestMetric:
    timestamp: str
    success: bool
    latency_ms: int
    cost_usd: float
    tokens_in: int
    tokens_out: int
    quality_score: float | None
    error_type: str | None
    trace_id: str | None


_EVENTS: deque[RequestMetric] = deque(maxlen=5000)
_ERRORS: Counter[str] = Counter()
_LOCK = Lock()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def record_request(
    latency_ms: int,
    cost_usd: float,
    tokens_in: int,
    tokens_out: int,
    quality_score: float,
    trace_id: str | None = None,
) -> None:
    event = RequestMetric(
        timestamp=_now().isoformat(),
        success=True,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        quality_score=quality_score,
        error_type=None,
        trace_id=trace_id,
    )
    with _LOCK:
        _EVENTS.append(event)


def record_error(error_type: str, latency_ms: int = 0, trace_id: str | None = None) -> None:
    event = RequestMetric(
        timestamp=_now().isoformat(),
        success=False,
        latency_ms=latency_ms,
        cost_usd=0.0,
        tokens_in=0,
        tokens_out=0,
        quality_score=None,
        error_type=error_type,
        trace_id=trace_id,
    )
    with _LOCK:
        _ERRORS[error_type] += 1
        _EVENTS.append(event)


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def _recent(events: list[RequestMetric], duration: timedelta) -> list[RequestMetric]:
    cutoff = _now() - duration
    return [
        event
        for event in events
        if datetime.fromisoformat(event.timestamp) >= cutoff
    ]


def snapshot() -> dict:
    with _LOCK:
        events = list(_EVENTS)
        errors = dict(_ERRORS)

    successful = [event for event in events if event.success]
    latencies = [event.latency_ms for event in events]
    costs = [event.cost_usd for event in successful]
    quality = [
        event.quality_score
        for event in successful
        if event.quality_score is not None
    ]
    last_hour = _recent(events, timedelta(hours=1))
    last_day = _recent(events, timedelta(days=1))
    error_count = len(events) - len(successful)
    traffic = len(events)
    error_rate = (error_count / traffic * 100) if traffic else 0.0
    request_rate_per_min = 0.0
    if last_hour:
        first = datetime.fromisoformat(last_hour[0].timestamp)
        last = datetime.fromisoformat(last_hour[-1].timestamp)
        observed_minutes = max((last - first).total_seconds() / 60, 1.0)
        request_rate_per_min = len(last_hour) / observed_minutes

    return {
        "generated_at": _now().isoformat(),
        "traffic": traffic,
        "success_count": len(successful),
        "error_count": error_count,
        "request_rate_per_min": round(request_rate_per_min, 3),
        "latency_p50_ms": percentile(latencies, 50),
        "latency_p95_ms": percentile(latencies, 95),
        "latency_p99_ms": percentile(latencies, 99),
        "error_rate_pct": round(error_rate, 2),
        "avg_cost_usd": round(mean(costs), 6) if costs else 0.0,
        "hourly_cost_usd": round(sum(event.cost_usd for event in last_hour), 6),
        "daily_cost_usd": round(sum(event.cost_usd for event in last_day), 6),
        "total_cost_usd": round(sum(costs), 6),
        "tokens_in_total": sum(event.tokens_in for event in successful),
        "tokens_out_total": sum(event.tokens_out for event in successful),
        "error_breakdown": errors,
        "quality_avg": round(mean(quality), 4) if quality else 0.0,
        "time_series": [asdict(event) for event in events[-60:]],
    }


def reset() -> None:
    with _LOCK:
        _EVENTS.clear()
        _ERRORS.clear()

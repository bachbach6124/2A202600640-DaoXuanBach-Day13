from __future__ import annotations

import json
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from structlog.contextvars import bind_contextvars

from .agent import LabAgent
from .alerts import evaluate_alerts
from .dashboard import DASHBOARD_HTML
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger, log_path
from .metrics import record_error, reset, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import flush_traces, tracing_status

load_dotenv()
configure_logging()
log = get_logger()
agent = LabAgent()


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        correlation_id="system",
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing": tracing_status()},
    )
    yield
    flush_traces()


app = FastAPI(title="Day 13 Observability Lab", lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/health")
async def health() -> dict:
    tracing = tracing_status()
    return {
        "ok": True,
        "tracing_enabled": tracing["configured"],
        "tracing": tracing,
        "incidents": status(),
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    return DASHBOARD_HTML


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.get("/logs/recent")
async def recent_logs(
    limit: int = Query(default=20, ge=1, le=200),
    event: str | None = Query(default=None),
) -> list[dict]:
    path = log_path()
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if event:
        records = [record for record in records if record.get("event") == event]
    return records[-limit:]


@app.post("/metrics/reset")
async def reset_metric_state() -> dict:
    reset()
    log.warning("metrics_reset", service="control")
    return {"ok": True, "metrics": snapshot()}


@app.get("/alerts")
async def alerts(demo: bool = Query(default=False)) -> list[dict]:
    return evaluate_alerts(snapshot(), demo=demo)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    started = time.perf_counter()
    user_id_hash = hash_user_id(body.user_id)
    bind_contextvars(
        user_id_hash=user_id_hash,
        session_id=body.session_id,
        feature=body.feature,
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id_hash=user_id_hash,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            payload={
                "answer_preview": summarize_text(result.answer),
                "trace_id": result.trace_id,
            },
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            trace_id=result.trace_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:
        error_type = type(exc).__name__
        latency_ms = int((time.perf_counter() - started) * 1000)
        record_error(error_type, latency_ms=latency_ms)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            latency_ms=latency_ms,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

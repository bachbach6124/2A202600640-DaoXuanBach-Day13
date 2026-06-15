from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

import httpx
from dotenv import dotenv_values

ENV_PATH = Path(".env")
EVIDENCE_DIR = Path("docs/evidence")
JSON_PATH = EVIDENCE_DIR / "langfuse-traces.json"
HTML_PATH = EVIDENCE_DIR / "langfuse-report.html"
KEY_PATTERN = re.compile(r"\b(?:pk|sk)-lf-[A-Za-z0-9_-]+\b")


def main() -> None:
    values = dotenv_values(ENV_PATH)
    host = (values.get("LANGFUSE_HOST") or "https://cloud.langfuse.com").rstrip("/")
    auth = (
        values.get("LANGFUSE_PUBLIC_KEY", ""),
        values.get("LANGFUSE_SECRET_KEY", ""),
    )
    with httpx.Client(auth=auth, timeout=30.0) as client:
        response = client.get(
            f"{host}/api/public/traces",
            params={"page": 1, "limit": 50},
        )
        response.raise_for_status()
        trace_list = response.json()
        project_traces = trace_list.get("data", [])
        expected_sessions = {f"s{index:02d}" for index in range(1, 11)}
        traces = [
            trace
            for trace in project_traces
            if trace.get("sessionId") in expected_sessions
        ]
        if not traces:
            raise RuntimeError("Langfuse returned no traces")

        sample_response = client.get(
            f"{host}/api/public/traces/{traces[0]['id']}",
        )
        sample_response.raise_for_status()
        sample = sample_response.json()

    safe_traces = [
        {
            "id": trace["id"],
            "name": trace.get("name"),
            "timestamp": trace.get("timestamp"),
            "sessionId": trace.get("sessionId"),
            "userId": trace.get("userId"),
            "tags": trace.get("tags", []),
            "htmlPath": trace.get("htmlPath"),
        }
        for trace in traces
    ]
    observations = [
        {
            "id": observation.get("id"),
            "name": observation.get("name"),
            "type": observation.get("type"),
            "parentObservationId": observation.get("parentObservationId"),
            "startTime": observation.get("startTime"),
            "endTime": observation.get("endTime"),
            "model": observation.get("model"),
            "usage": observation.get("usage"),
            "metadata": sanitize(observation.get("metadata")),
        }
        for observation in sample.get("observations", [])
    ]
    evidence = {
        "source": f"{host}/api/public",
        "projectId": sample.get("projectId"),
        "traceCount": len(traces),
        "projectTraceCount": trace_list.get("meta", {}).get(
            "totalItems",
            len(project_traces),
        ),
        "traces": safe_traces,
        "sampleTrace": {
            "id": sample.get("id"),
            "name": sample.get("name"),
            "timestamp": sample.get("timestamp"),
            "sessionId": sample.get("sessionId"),
            "userId": sample.get("userId"),
            "tags": sample.get("tags", []),
            "metadata": sanitize(sample.get("metadata")),
            "htmlUrl": f"{host}{sample.get('htmlPath', '')}",
            "observations": observations,
        },
    }

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    HTML_PATH.write_text(render_html(evidence), encoding="utf-8")
    print(
        f"Exported {evidence['traceCount']} lab traces "
        f"from {evidence['projectTraceCount']} project traces"
    )
    print(f"Sample trace: {evidence['sampleTrace']['id']}")
    print(f"Wrote {JSON_PATH}")
    print(f"Wrote {HTML_PATH}")


def sanitize(value: Any) -> Any:
    if isinstance(value, str):
        return KEY_PATTERN.sub("[REDACTED_LANGFUSE_KEY]", value)
    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED_LANGFUSE_KEY]"
                if key in {"public_key", "secret_key"}
                else sanitize(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def render_html(evidence: dict) -> str:
    traces = "".join(
        f"""
        <tr>
          <td><code>{html.escape(trace['id'][:12])}</code></td>
          <td>{html.escape(trace.get('name') or '')}</td>
          <td>{html.escape(trace.get('sessionId') or '')}</td>
          <td><code>{html.escape(trace.get('userId') or '')}</code></td>
          <td>{html.escape(trace.get('timestamp') or '')}</td>
        </tr>
        """
        for trace in evidence["traces"]
    )
    observations = "".join(
        f"""
        <div class="observation {html.escape((item.get('type') or '').lower())}">
          <div><span>{html.escape(item.get('type') or '')}</span><strong>{html.escape(item.get('name') or '')}</strong></div>
          <code>{html.escape(item.get('id') or '')}</code>
          <small>parent: {html.escape(item.get('parentObservationId') or 'root')}</small>
        </div>
        """
        for item in sorted(
            evidence["sampleTrace"]["observations"],
            key=lambda item: item.get("parentObservationId") is not None,
        )
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Langfuse Trace Evidence</title>
  <style>
    :root {{ --paper:#f4f1e9; --ink:#171814; --muted:#6c6e67; --line:#cfcbc0; --accent:#d45b26; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; padding:36px 48px 56px; background:var(--paper); color:var(--ink); font-family:Inter,system-ui,sans-serif; }}
    header {{ display:flex; justify-content:space-between; align-items:flex-end; padding-bottom:22px; border-bottom:1px solid var(--ink); }}
    .eyebrow, th, .observation span {{ font-size:11px; font-weight:800; letter-spacing:.13em; text-transform:uppercase; color:var(--muted); }}
    h1 {{ margin:5px 0 0; font-size:48px; letter-spacing:-.05em; }}
    .count {{ min-width:220px; text-align:right; font-size:56px; font-weight:800; line-height:.9; letter-spacing:-.06em; }}
    .count small {{ display:block; margin-top:8px; font-size:12px; line-height:1.2; letter-spacing:0; color:var(--muted); }}
    section {{ padding-top:28px; }}
    h2 {{ margin:0 0 14px; font-size:22px; letter-spacing:-.03em; }}
    table {{ width:100%; border-collapse:collapse; background:rgba(255,255,255,.35); }}
    th, td {{ padding:11px 13px; text-align:left; border-bottom:1px solid var(--line); font-size:13px; }}
    code {{ font-family:"SFMono-Regular",Consolas,monospace; font-size:12px; }}
    .waterfall {{ display:grid; gap:9px; padding-left:0; max-width:850px; }}
    .observation {{ display:flex; justify-content:space-between; align-items:center; gap:20px; padding:15px 18px; border-left:6px solid var(--ink); background:rgba(255,255,255,.5); }}
    .observation:not(:first-child) {{ margin-left:54px; border-left-color:var(--accent); }}
    .observation strong {{ display:block; margin-top:3px; font-size:17px; }}
    .observation small {{ color:var(--muted); }}
    footer {{ margin-top:28px; padding-top:15px; border-top:1px solid var(--ink); color:var(--muted); font-size:12px; }}
  </style>
</head>
<body>
  <header>
    <div><div class="eyebrow">Verified via Langfuse Public API</div><h1>Trace evidence</h1></div>
    <div class="count">{evidence['traceCount']} <small>lab traces / {evidence['projectTraceCount']} project total</small></div>
  </header>
  <section>
    <h2>Trace list</h2>
    <table>
      <thead><tr><th>Trace ID</th><th>Name</th><th>Session</th><th>User hash</th><th>Timestamp UTC</th></tr></thead>
      <tbody>{traces}</tbody>
    </table>
  </section>
  <section>
    <h2>Sample waterfall / {html.escape(evidence['sampleTrace']['id'][:12])}</h2>
    <div class="waterfall">{observations}</div>
  </section>
  <footer>Source: {html.escape(evidence['source'])} · Project: {html.escape(evidence['projectId'])}</footer>
</body>
</html>
"""


if __name__ == "__main__":
    main()

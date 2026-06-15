# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 2A202600640 - Dao Xuan Bach
- [REPO_URL]: https://github.com/bachbach6124/2A202600640-DaoXuanBach-Day13
- [MEMBERS]:
  - Member A: Dao Xuan Bach | Role: Full implementation
  - Member B: N/A | Role: N/A
  - Member C: N/A | Role: N/A
  - Member D: N/A | Role: N/A
  - Member E: N/A | Role: N/A

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 10 lab traces verified via Langfuse Public API
- [PII_LEAKS_FOUND]: 0 across 103 validated log records

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: output/playwright/logs-correlation-pii.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: output/playwright/logs-correlation-pii.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: output/playwright/langfuse-traces-waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: Trace `a69d128e809c57de71beb09ba3c1dd56` contains root span `agent-run` with child observations `rag-retrieval` and `llm-generation`. The generation records model and token usage while trace-level metadata includes hashed user, session, feature, model, and correlation ID.
- [LANGFUSE_TRACE_URL]: https://jp.cloud.langfuse.com/project/cmqex2vmr0061ad0efsqaj54m/traces/a69d128e809c57de71beb09ba3c1dd56

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: output/playwright/dashboard-6-panels.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 158ms baseline |
| Error Rate | < 2% | 28d | 0.0% baseline |
| Cost Budget | < $2.5/day | 1d | $0.019485 demo total |
| Quality Proxy | >= 0.75 | 28d | 0.88 baseline |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: output/playwright/incident-rag-slow-alert.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency P95 increased from 158ms to 5659ms and the high-latency alert fired.
- [ROOT_CAUSE_PROVED_BY]: Correlation ID `req-473fc61e`; `tool_completed` log reports `tool_name=mock-rag` and `latency_ms=5504`. The LLM log remains near 150ms.
- [FIX_ACTION]: Disable the `rag_slow` incident toggle and use a retrieval timeout/fallback source in a production implementation.
- [PREVENTIVE_MEASURE]: Keep the 3000ms SLO line, high-latency alert, separate RAG/LLM spans, and a fallback retrieval path.

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME] Dao Xuan Bach
- [TASKS_COMPLETED]: Correlation middleware, structured logging, recursive PII redaction, Langfuse compatibility, RAG/LLM spans, grounded answer quality evaluation, cost optimization benchmark, time-series metrics, six-panel dashboard, SLOs, alerts, separate audit logs, end-to-end automation, tests, validators, and evidence.
- [EVIDENCE_LINK]: https://github.com/bachbach6124/2A202600640-DaoXuanBach-Day13/commit/3a367b3
- [LANGFUSE_EVIDENCE_COMMIT]: https://github.com/bachbach6124/2A202600640-DaoXuanBach-Day13/commit/d54ffb5

### [MEMBER_B_NAME] N/A
- [TASKS_COMPLETED]: N/A
- [EVIDENCE_LINK]: N/A

### [MEMBER_C_NAME] N/A
- [TASKS_COMPLETED]: N/A
- [EVIDENCE_LINK]: N/A

### [MEMBER_D_NAME] N/A
- [TASKS_COMPLETED]: N/A
- [EVIDENCE_LINK]: N/A

### [MEMBER_E_NAME] N/A
- [TASKS_COMPLETED]: N/A
- [EVIDENCE_LINK]: N/A

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Claimed - output tokens reduced from 1300 to 207 (84.08%) and simulated cost from $0.020679 to $0.004284 (79.28%) across 10 requests. Evidence: `docs/evidence/cost-optimization.json`.
- [BONUS_DASHBOARD]: Claimed - professional six-panel dashboard with consistent units, SLO thresholds, legends, time range, and 15-second refresh. Evidence: `output/playwright/dashboard-6-panels.png`.
- [BONUS_AUDIT_LOGS]: Claimed - separate `data/audit.jsonl` with actor/action/result/correlation ID, JSON Schema validation, and PII redaction. Verification: 34 records, 0 schema errors, 0 PII leaks.
- [BONUS_CUSTOM_METRIC]: Claimed - `scripts/verify_all.py` starts the app and automatically verifies quality, cost, three incident alerts, application logs, and audit logs.

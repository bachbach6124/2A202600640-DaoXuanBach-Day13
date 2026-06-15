# Evidence Collection Sheet

## Required screenshots
- [x] Langfuse trace list with >= 10 traces - `output/playwright/langfuse-traces-waterfall.png`
- [x] One full trace waterfall - `output/playwright/langfuse-traces-waterfall.png`
- [x] JSON logs showing correlation ID - `output/playwright/logs-correlation-pii.png`
- [x] Log line with PII redaction - `output/playwright/logs-correlation-pii.png`
- [x] Dashboard with 6 panels - `output/playwright/dashboard-6-panels.png`
- [x] Alert firing with SLO threshold - `output/playwright/incident-rag-slow-alert.png`
- [x] Three alert verification results - `docs/evidence/p0-verification.json`
- [x] Sanitized Langfuse API export - `docs/evidence/langfuse-traces.json`
- [x] Direct Langfuse UI trace list - `output/playwright/langfuse-ui-trace-list.png`

## Optional screenshots
- [x] Incident before/after - normal and `rag_slow` dashboard screenshots
- [x] Cost comparison before/after optimization - `docs/evidence/cost-optimization.json`
- [x] Quality evaluation - `docs/evidence/quality-evaluation.json`
- [x] Automated full verification - `scripts/verify_all.py`
- [x] Audit log validation - 34 records, 0 schema errors, 0 PII leaks

## P1/P2 measured results

| Measurement | Before | After | Improvement |
|---|---:|---:|---:|
| Output tokens / 10 requests | 1300 | 207 | 84.08% lower |
| Simulated cost / 10 requests | $0.020679 | $0.004284 | 79.28% lower |
| Expected-answer pass rate | N/A | 3/3 (100%) | Reproducible |
| Audit schema errors | N/A | 0/34 | Valid |
| Audit PII leaks | N/A | 0/34 | Redacted |

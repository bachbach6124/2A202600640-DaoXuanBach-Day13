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

## Optional screenshots
- [x] Incident before/after - normal and `rag_slow` dashboard screenshots
- [ ] Cost comparison before/after optimization
- [x] Automated incident verification - `scripts/verify_p0.py`

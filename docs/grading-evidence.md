# Evidence Collection Sheet

## Required screenshots
- [ ] Langfuse trace list with >= 10 traces - blocked until Langfuse keys are added to `.env`
- [ ] One full trace waterfall - blocked until Langfuse keys are added to `.env`
- [x] JSON logs showing correlation ID - `output/playwright/logs-correlation-pii.png`
- [x] Log line with PII redaction - `output/playwright/logs-correlation-pii.png`
- [x] Dashboard with 6 panels - `output/playwright/dashboard-6-panels.png`
- [x] Alert firing with SLO threshold - `output/playwright/incident-rag-slow-alert.png`
- [x] Three alert verification results - `docs/evidence/p0-verification.json`

## Optional screenshots
- [x] Incident before/after - normal and `rag_slow` dashboard screenshots
- [ ] Cost comparison before/after optimization
- [x] Automated incident verification - `scripts/verify_p0.py`

# Day 13 Observability Lab - Task Checklist

## Tong quan hien trang

| Muc | Hien trang |
|---|---|
| Unit tests | `17 passed`, gom unit, API integration, concurrency, quality va audit tests |
| Log validator | `100/100` tren 103 log records |
| Correlation ID | Da propagate qua response, logs va request context |
| Log enrichment | Da co `user_id_hash`, `session_id`, `feature`, `model`, `env` |
| PII processor | Da scrub de quy email, phone, CCCD, card va passport |
| Langfuse | Da xac thuc Japan region va tao 10 lab traces live |
| Dashboard | Da co dashboard 6 panels va screenshot |
| Alerts | Ca 3 rule da duoc script trigger thanh cong |
| Blueprint report | Da dien day du local evidence va Langfuse trace evidence |
| Git evidence | Cac commit P0 va Langfuse evidence da push len `origin/main` |
| Quality evaluation | `3/3` expected answers pass, quality trung binh `1.0` |
| Cost optimization | Giam output token `84.08%`, chi phi mo phong `79.28%` tren 10 request |
| Audit logs | `34` records, JSON Schema errors `0`, PII leaks `0` |

## P0 - Bat buoc de dat

| Done | Task | File lien quan | Tieu chi hoan thanh / bang chung |
|:---:|---|---|---|
| [x] | Cai moi truong va tao `.env` | `.env.example`, `requirements.txt` | App va `/health` OK; Langfuse Japan `auth_check=True` |
| [x] | Hoan thien correlation ID middleware | `app/middleware.py` | Clear context moi request; dung `x-request-id` neu co hoac tao `req-<8 hex>`; bind vao structlog; response co `x-request-id` va `x-response-time-ms` |
| [x] | Bind request context vao moi API log | `app/main.py` | Log `service=api` co du `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`; khong log raw user ID |
| [x] | Bat PII scrubber trong logging pipeline | `app/logging_config.py` | Dang ky `scrub_event` truoc khi ghi file va render console |
| [x] | Lam PII scrub de quy va day du hon | `app/pii.py`, `app/logging_config.py` | Redact email, SDT Viet Nam, CCCD, credit card va PII trong dict/list long nhau; exception/detail cung khong ro PII |
| [x] | Bo sung test cho logging, middleware va PII | `tests/` | `11 passed`; co regression test de correlation ID khong bi regex PII sua |
| [x] | Tao log that bang load test | `scripts/load_test.py`, `data/sample_queries.jsonl` | Da chay 10 request, gom PII va concurrency 5 |
| [x] | Dat `VALIDATE_LOGS_SCORE >= 80/100` | `scripts/validate_logs.py`, `data/logs.jsonl` | Dat `100/100`, 34 correlation ID, PII leaks = 0 |
| [x] | Xac minh Langfuse SDK tuong thich voi version pin | `requirements.txt`, `app/tracing.py` | Adapter nhan dien API v4 va ho tro legacy; `/health` bao ro SDK/config status |
| [x] | Tao trace va cac span co y nghia | `app/agent.py`, `app/mock_rag.py`, `app/mock_llm.py` | Da implement `agent-run -> rag-retrieval -> llm-generation`, khong capture raw PII input |
| [x] | Gui va xac minh it nhat 10 traces live | Langfuse, `scripts/load_test.py` | 10 lab traces; co API export, screenshot va trace URL chinh thuc |
| [x] | Hoan thien metrics phuc vu 6 panels | `app/metrics.py`, `app/main.py` | Co latency P50/P95/P99, traffic/RPM, error rate, cost, tokens, quality va time series |
| [x] | Dung dashboard 6 panels | `docs/dashboard-spec.md` | Time range 1h, refresh 15s, co don vi/SLO line va screenshot |
| [x] | Chot SLO theo so lieu thuc te | `config/slo.yaml`, `docs/blueprint-template.md` | Baseline P95 158ms, error 0%, demo cost $0.019485, quality 0.88 |
| [x] | Kiem thu 3 alert rules | `config/alert_rules.yaml`, `docs/alerts.md` | Script da trigger latency, error va cost alert; ket qua tai `docs/evidence/p0-verification.json` |
| [x] | Inject incident va debug theo flow | `scripts/inject_incident.py`, `data/incidents.json` | `rag_slow` duoc chung minh boi metric 5659ms va RAG log 5504ms |
| [x] | Dien day du blueprint report | `docs/blueprint-template.md` | Da dien metadata, score, SLO, incident va evidence; Langfuse evidence ghi pending |
| [x] | Thu thap toan bo grading evidence | `docs/grading-evidence.md` | Da co log, dashboard, alerts, trace list va waterfall |
| [x] | Tao Git evidence cho tung thanh vien | Git history, `docs/blueprint-template.md` | Commit `3a367b3` va `d54ffb5` da co link GitHub truy cap duoc |
| [x] | Rehearse live demo | README, report, dashboard, Langfuse | Da chay 10 request voi tracing live, dashboard va incident flow |

## P1 - Nen lam de tang chat luong

| Done | Task | File lien quan | Tieu chi hoan thanh / bang chung |
|:---:|---|---|---|
| [x] | Lam fake answer su dung retrieved docs | `app/mock_llm.py`, `app/agent.py`, `data/expected_answers.jsonl` | `3/3` answer dap ung `must_include`; quality grounded trung binh `1.0` |
| [x] | Bo sung quality evaluation script/test | `scripts/evaluate_quality.py`, `tests/test_quality.py` | Bao cao lap lai tai `docs/evidence/quality-evaluation.json` |
| [x] | Ghi metric cho request that bai | `app/metrics.py`, `app/main.py`, `tests/test_api.py` | Error incident tao traffic `1`, error `1`, error rate `100%` |
| [x] | Them structured log cho RAG/LLM/tool | `app/agent.py`, `app/mock_rag.py`, `app/mock_llm.py` | Co `tool_name`, model, latency, token va cung correlation ID |
| [x] | Nang cap log validator theo JSON Schema | `scripts/validate_logs.py`, `config/logging_schema.json` | `103` records, schema error `0`, PII leak `0`, score `100/100` |
| [x] | Them integration/concurrency tests | `tests/` | `17 passed`; co chat, metrics, incident, error path, audit va 10 request dong thoi |
| [x] | Chuan bi script demo lap lai duoc | `scripts/verify_all.py` | Mot lenh khoi dong app, quality/cost benchmark, inject 3 incident va validate logs/audit |

## P2 - Bonus

| Done | Task | Diem | Tieu chi hoan thanh / bang chung |
|:---:|---|---:|---|
| [x] | Toi uu chi phi | +3 | 10 request: output token `1300 -> 207` (-84.08%), cost `$0.020679 -> $0.004284` (-79.28%) |
| [x] | Lam dashboard chuyen nghiep | +3 | Dashboard 6 panel, threshold/SLO, don vi va refresh 15s; evidence `output/playwright/dashboard-6-panels.png` |
| [x] | Auto-instrumentation hoac custom automation | +2 | `scripts/verify_all.py` chay end-to-end va fail neu bat ky alert/validator nao khong dat |
| [x] | Tach audit logs | +2 | `data/audit.jsonl`, `config/audit_schema.json`; 34 records, schema/PII errors bang 0 |

## Thu tu thuc hien de xuat

1. Middleware correlation ID.
2. Log enrichment va PII scrubbing.
3. Tests, load test, sua den khi validator dat 100.
4. Langfuse trace/span va tao 10+ traces.
5. Metrics/export va dashboard 6 panels.
6. Alerts, incident drill va bang chung.
7. Blueprint, Git evidence va rehearsal demo.

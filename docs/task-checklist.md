# Day 13 Observability Lab - Task Checklist

## Tong quan hien trang

| Muc | Hien trang |
|---|---|
| Unit tests | `11 passed`, gom unit va API integration tests |
| Log validator | `100/100` tren 103 log records |
| Correlation ID | Da propagate qua response, logs va request context |
| Log enrichment | Da co `user_id_hash`, `session_id`, `feature`, `model`, `env` |
| PII processor | Da scrub de quy email, phone, CCCD, card va passport |
| Langfuse | SDK/API da san sang; con thieu key de tao 10 traces live |
| Dashboard | Da co dashboard 6 panels va screenshot |
| Alerts | Ca 3 rule da duoc script trigger thanh cong |
| Blueprint report | Da dien bang so lieu local; trace evidence dang cho key |
| Git evidence | Commit `3a367b3` da co; can push len remote truoc khi nop |

## P0 - Bat buoc de dat

| Done | Task | File lien quan | Tieu chi hoan thanh / bang chung |
|:---:|---|---|---|
| [ ] | Cai moi truong va tao `.env` | `.env.example`, `requirements.txt` | App va `/health` da OK; con thieu Langfuse public/secret key |
| [x] | Hoan thien correlation ID middleware | `app/middleware.py` | Clear context moi request; dung `x-request-id` neu co hoac tao `req-<8 hex>`; bind vao structlog; response co `x-request-id` va `x-response-time-ms` |
| [x] | Bind request context vao moi API log | `app/main.py` | Log `service=api` co du `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`; khong log raw user ID |
| [x] | Bat PII scrubber trong logging pipeline | `app/logging_config.py` | Dang ky `scrub_event` truoc khi ghi file va render console |
| [x] | Lam PII scrub de quy va day du hon | `app/pii.py`, `app/logging_config.py` | Redact email, SDT Viet Nam, CCCD, credit card va PII trong dict/list long nhau; exception/detail cung khong ro PII |
| [x] | Bo sung test cho logging, middleware va PII | `tests/` | `11 passed`; co regression test de correlation ID khong bi regex PII sua |
| [x] | Tao log that bang load test | `scripts/load_test.py`, `data/sample_queries.jsonl` | Da chay 10 request, gom PII va concurrency 5 |
| [x] | Dat `VALIDATE_LOGS_SCORE >= 80/100` | `scripts/validate_logs.py`, `data/logs.jsonl` | Dat `100/100`, 34 correlation ID, PII leaks = 0 |
| [x] | Xac minh Langfuse SDK tuong thich voi version pin | `requirements.txt`, `app/tracing.py` | Adapter nhan dien API v4 va ho tro legacy; `/health` bao ro SDK/config status |
| [x] | Tao trace va cac span co y nghia | `app/agent.py`, `app/mock_rag.py`, `app/mock_llm.py` | Da implement `agent-run -> rag-retrieval -> llm-generation`, khong capture raw PII input |
| [ ] | Gui va xac minh it nhat 10 traces live | Langfuse, `scripts/load_test.py` | Screenshot danh sach `>= 10` traces va mot trace waterfall day du |
| [x] | Hoan thien metrics phuc vu 6 panels | `app/metrics.py`, `app/main.py` | Co latency P50/P95/P99, traffic/RPM, error rate, cost, tokens, quality va time series |
| [x] | Dung dashboard 6 panels | `docs/dashboard-spec.md` | Time range 1h, refresh 15s, co don vi/SLO line va screenshot |
| [x] | Chot SLO theo so lieu thuc te | `config/slo.yaml`, `docs/blueprint-template.md` | Baseline P95 158ms, error 0%, demo cost $0.019485, quality 0.88 |
| [x] | Kiem thu 3 alert rules | `config/alert_rules.yaml`, `docs/alerts.md` | Script da trigger latency, error va cost alert; ket qua tai `docs/evidence/p0-verification.json` |
| [x] | Inject incident va debug theo flow | `scripts/inject_incident.py`, `data/incidents.json` | `rag_slow` duoc chung minh boi metric 5659ms va RAG log 5504ms |
| [x] | Dien day du blueprint report | `docs/blueprint-template.md` | Da dien metadata, score, SLO, incident va evidence; Langfuse evidence ghi pending |
| [ ] | Thu thap toan bo grading evidence | `docs/grading-evidence.md` | Da co log/dashboard/alert; con thieu 2 screenshot Langfuse |
| [x] | Tao Git evidence cho tung thanh vien | Git history, `docs/blueprint-template.md` | Thanh vien duy nhat co commit `3a367b3`; can push de remote link truy cap duoc |
| [ ] | Rehearse live demo | README, report, dashboard, Langfuse | Local demo da chay on dinh; can lap lai voi Langfuse da cau hinh |

## P1 - Nen lam de tang chat luong

| Done | Task | File lien quan | Tieu chi hoan thanh / bang chung |
|:---:|---|---|---|
| [ ] | Lam fake answer su dung retrieved docs | `app/mock_llm.py`, `app/agent.py`, `data/expected_answers.jsonl` | Cac answer dap ung `must_include`; quality score phan anh chat luong thuc thay vi chi do do dai |
| [ ] | Bo sung quality evaluation script/test | `data/expected_answers.jsonl`, `tests/` hoac `scripts/` | Bao cao pass rate/quality score co the lap lai |
| [ ] | Ghi metric cho request that bai | `app/metrics.py`, `app/main.py` | Traffic va error-rate denominator dung ke ca khi agent loi |
| [ ] | Them structured log cho RAG/LLM/tool | `app/agent.py`, `app/mock_rag.py`, `app/mock_llm.py` | Log co `tool_name`, model, latency tung buoc va cung correlation ID |
| [ ] | Nang cap log validator theo JSON Schema | `scripts/validate_logs.py`, `config/logging_schema.json` | Validator kiem tra type/required fields bang schema, scan nhieu pattern PII va tra exit code fail ro rang |
| [ ] | Them integration/concurrency tests | `tests/` | Test `/chat`, `/metrics`, incident enable/disable, error path va nhieu request dong thoi |
| [ ] | Chuan bi script demo lap lai duoc | `scripts/` | Mot lenh tao baseline, inject incident, tao traffic va in metrics truoc/sau |

## P2 - Bonus

| Done | Task | Diem | Tieu chi hoan thanh / bang chung |
|:---:|---|---:|---|
| [ ] | Toi uu chi phi | +3 | Co baseline va so lieu sau toi uu ve token/cost, kem screenshot/bang so sanh |
| [ ] | Lam dashboard chuyen nghiep | +3 | Bo cuc ro, ten panel/legend/don vi nhat quan, threshold de nhin, khong qua 6-8 panel |
| [ ] | Auto-instrumentation hoac custom automation | +2 | Co script/instrumentation chay duoc va bang chung trace/metric sinh tu dong |
| [ ] | Tach audit logs | +2 | Ghi `data/audit.jsonl`, schema ro, co actor/action/result/correlation ID, van redact PII |

## Thu tu thuc hien de xuat

1. Middleware correlation ID.
2. Log enrichment va PII scrubbing.
3. Tests, load test, sua den khi validator dat 100.
4. Langfuse trace/span va tao 10+ traces.
5. Metrics/export va dashboard 6 panels.
6. Alerts, incident drill va bang chung.
7. Blueprint, Git evidence va rehearsal demo.

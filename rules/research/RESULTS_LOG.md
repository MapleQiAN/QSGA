# RESULTS_LOG.md

---

## TLDR_STATE_FOR_AGENT

已完成实验：

- EXP-20260512-LIVE-FAILURE-BREAKDOWN
- EXP-20260512-ROUTE-B-BUILDER-SMOKE
- EXP-20260512-ROUTE-B-LIVE-SMOKE-FAILED-AUTH

关键结果：

- Saved `live_qyir_80_results.csv` was classified into 160 row-level failure labels.
- For `live_raw_qyir::qwen3.6-flash`, the largest labeled buckets are schema_failure 49/80, unsafe_intent_failure 15/80, success 6/80, alias_failure 5/80, and risk_violation 5/80.
- For `live_qsga_qyir::qwen3.6-flash`, the labeled buckets are schema_failure 40/80, success 30/80, alias_failure 5/80, risk_violation 4/80, and compilation_failure 1/80.
- Offline Route B builder smoke over QSI-Bench expected slots reaches 55/55 construct success and 80/80 terminal action correctness.

失败结果：

- Failure breakdown confirms Route B should prioritize schema/indicator output constraints, alias/reference handling, and explicit safety gating.
- Builder smoke uses expected slots and therefore must not be described as live natural-language extraction success.
- Route B live smoke could not obtain model outputs because the configured API key/endpoint returned authentication errors.

对 claim 的影响：

- Supports a conservative diagnostic claim about the saved qwen3.6-flash run only. It does not prove Route B improvement yet.
- Supports a scoped builder claim: the deterministic builder can construct valid QYIR from benchmark expected slots for the current 55 construct cases.
- Does not support any live Route B improvement claim; live run is blocked on API key/endpoint validity.

---

## Results

### EXP-20260512-LIVE-FAILURE-BREAKDOWN

```yaml
Experiment ID: EXP-20260512-LIVE-FAILURE-BREAKDOWN
Date: 2026-05-12
Task ID: TASK-20260512-003
Status: success
Code Version: 1cf03ea + working tree Route B analysis changes
Dataset Version:
  - experiments/results/live_qyir_80_results.csv
  - experiments/results/live_qyir_80_raw_outputs.jsonl
Command:
  - uv run python experiments/analyze_failure_breakdown.py
Seed: n/a
Environment:
  - Windows
  - Python 3.12.7 via uv
Raw Output Path:
  - experiments/results/live_failure_breakdown.csv
  - experiments/tables/live_failure_breakdown.md
Metrics:
  live_raw_qyir::qwen3.6-flash:
    success: 6/80
    schema_failure: 49/80
    alias_failure: 5/80
    risk_violation: 5/80
    unsafe_intent_failure: 15/80
  live_qsga_qyir::qwen3.6-flash:
    success: 30/80
    schema_failure: 40/80
    alias_failure: 5/80
    compilation_failure: 1/80
    risk_violation: 4/80
Failure:
  - This is a deterministic analysis of saved live results, not a new live model run.
  - Failure categories are rule-based labels over existing MethodResult fields and error text.
Reproducibility Level: R4
Claim Impact:
  - Enables failure-reduction analysis for Route B.
  - Does not by itself validate improved construction success.
Notes:
  - The table includes success rows so percentages sum to 1.0 per method.
```

### EXP-20260512-ROUTE-B-BUILDER-SMOKE

```yaml
Experiment ID: EXP-20260512-ROUTE-B-BUILDER-SMOKE
Date: 2026-05-12
Task ID: TASK-20260512-007
Status: success
Code Version: 1cf03ea + working tree Route B builder-smoke changes
Dataset Version:
  - benchmark/qsi_bench_v1.jsonl
Command:
  - uv run python experiments/run_route_b_builder_smoke.py
Seed: n/a
Environment:
  - Windows
  - Python 3.12.7 via uv
Raw Output Path:
  - experiments/results/route_b_builder_smoke.csv
  - experiments/tables/route_b_builder_smoke.md
Metrics:
  construct_cases: 55
  construct_success: 55
  clarify_cases: 10
  clarify_terminal_correct: 10
  reject_cases: 15
  reject_terminal_correct: 15
  all_terminal_correct: 80
Failure:
  - Initial smoke exposed an RSI alias bug for non-14 RSI windows; fixed in experiments/run_route_b_builder_smoke.py and covered by tests/test_route_b_builder_smoke.py.
  - This experiment uses expected slots, so it does not measure LLM slot extraction or live NL-to-QYIR construction.
Reproducibility Level: R4
Claim Impact:
  - Supports deterministic builder coverage under gold/expected slot input.
  - Does not validate Route B live construction improvement.
Notes:
  - `uv run pytest tests/test_route_b_builder_smoke.py`: 4 passed.
```

### EXP-20260512-ROUTE-B-LIVE-SMOKE-FAILED-AUTH

```yaml
Experiment ID: EXP-20260512-ROUTE-B-LIVE-SMOKE-FAILED-AUTH
Date: 2026-05-12
Task ID: TASK-20260512-009
Status: failed
Code Version: 1cf03ea + working tree Route B live runner changes
Dataset Version:
  - benchmark/qsi_bench_v1.jsonl
Command:
  - uv run python experiments/run_live_route_b.py --api-key-file DSAPIKEY.txt --models deepseek-v4-flash --case-limit 5 --max-retries 1 --max-tokens 1200 --output experiments/results/route_b_live_smoke_deepseek_flash_5_results.csv --raw-output experiments/results/route_b_live_smoke_deepseek_flash_5_raw_outputs.jsonl --metadata-output experiments/results/route_b_live_smoke_deepseek_flash_5_metadata.json --usage-output experiments/results/route_b_live_smoke_deepseek_flash_5_token_usage.csv
  - uv run python experiments/run_live_route_b.py --api-key-file DSAPIKEY.txt --models deepseek-v4-flash --case-limit 5 --max-retries 1 --max-tokens 1200 --output experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_results.csv --raw-output experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_raw_outputs.jsonl --metadata-output experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_metadata.json --usage-output experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_token_usage.csv
Seed: 20260512
Environment:
  - Windows
  - Python 3.12.7 via uv
Raw Output Path:
  - experiments/results/route_b_live_smoke_deepseek_flash_5_results.csv
  - experiments/results/route_b_live_smoke_deepseek_flash_5_raw_outputs.jsonl
  - experiments/results/route_b_live_smoke_deepseek_flash_5_metadata.json
  - experiments/results/route_b_live_smoke_deepseek_flash_5_token_usage.csv
  - experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_results.csv
  - experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_raw_outputs.jsonl
  - experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_metadata.json
  - experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_token_usage.csv
Metrics:
  attempted_cases: 5
  api_errors: 5
  prompt_tokens: 0
  completion_tokens: 0
  total_tokens: 0
Failure:
  - DashScope-compatible endpoint returned AuthenticationError 401 invalid_api_key for every attempted case.
  - First attempt used the shared env-first key path; code was corrected so Route B runner now prefers explicit --api-key-file.
  - Second attempt used DSAPIKEY.txt first and still returned 401 invalid_api_key.
Reproducibility Level: R3
Claim Impact:
  - Live Route B improvement remains untested.
  - Need valid provider key or correct base URL before rerunning live smoke.
Notes:
  - API key was not printed.
```

### EXP-20260512-ROUTE-B-LIVE-DEEPSEEK-OFFICIAL-80

```yaml
Experiment ID: EXP-20260512-ROUTE-B-LIVE-DEEPSEEK-OFFICIAL-80
Date: 2026-05-12
Task ID: TASK-20260512-009
Status: success
Code Version: 1cf03ea + working tree Route B official DeepSeek runner changes
Dataset Version:
  - benchmark/qsi_bench_v1.jsonl
Command:
  - uv run python experiments/run_live_route_b.py --api-key-file DSAPIKEY.txt --models deepseek-v4-flash --case-limit 80 --max-retries 1 --max-tokens 1200 --output experiments/results/route_b_live_deepseek_official_80_results.csv --raw-output experiments/results/route_b_live_deepseek_official_80_raw_outputs.jsonl --metadata-output experiments/results/route_b_live_deepseek_official_80_metadata.json --usage-output experiments/results/route_b_live_deepseek_official_80_token_usage.csv
  - uv run python experiments/eval_metrics.py --input experiments/results/route_b_live_deepseek_official_80_results.csv --output experiments/results/route_b_live_deepseek_official_80_metrics.csv
  - uv run python experiments/analyze_failure_breakdown.py --results experiments/results/route_b_live_deepseek_official_80_results.csv --output experiments/results/route_b_live_deepseek_official_80_failure_breakdown.csv --table-output experiments/tables/route_b_live_deepseek_official_80_failure_breakdown.md
Seed: 20260512
Environment:
  - Windows
  - Python 3.12.7 via uv
  - Official DeepSeek OpenAI-compatible base_url: https://api.deepseek.com
Raw Output Path:
  - experiments/results/route_b_live_deepseek_official_80_results.csv
  - experiments/results/route_b_live_deepseek_official_80_raw_outputs.jsonl
  - experiments/results/route_b_live_deepseek_official_80_metadata.json
  - experiments/results/route_b_live_deepseek_official_80_token_usage.csv
  - experiments/results/route_b_live_deepseek_official_80_metrics.csv
  - experiments/results/route_b_live_deepseek_official_80_failure_breakdown.csv
  - experiments/tables/route_b_live_deepseek_official_80_metrics.md
  - experiments/tables/route_b_live_deepseek_official_80_failure_breakdown.md
Metrics:
  total_cases: 80
  raw_slot_calls: 89
  total_tokens: 89812
  schema_validity_constructible: 0.709
  semantic_consistency_constructible: 0.709
  compile_success_constructible: 0.709
  backtest_success_constructible: 0.709
  risk_violation_constructible: 0.345
  safe_rejection_accuracy: 1.000
  clarification_accuracy: 0.300
  construction_success_constructible: 0.364
  end_to_end_success_all: 0.475
Failure:
  - 19/80 risk_violation
  - 12/80 clarification_failure
  - 7/80 semantic_mismatch
  - 3/80 unsupported_indicator
  - 1/80 schema_failure
Reproducibility Level: R4
Claim Impact:
  - Supports single-model official DeepSeek Route B live diagnostic claim.
  - Does not support broad model comparison, CCF-B readiness, or profitability/safety claims.
Notes:
  - API key was not printed.
  - The official JSON Output integration uses response_format={"type":"json_object"} and disabled thinking for short slot extraction.
```

---

## Result Entry Template

```yaml
Experiment ID:
Date:
Task ID:
Status: success / failed / partial / invalid
Code Version:
Dataset Version:
Command:
Seed:
Environment:
Raw Output Path:
Metrics:
Failure:
Reproducibility Level: R0 / R1 / R2 / R3 / R4 / R5
Claim Impact:
Notes:
```

# Run: 2026-05-12 Route B Initialization

## TLDR_STATE_FOR_AGENT

当前任务：
- TASK-20260512-012：起草 QYIR market operand 设计决策。

当前结论：
- Route B official DeepSeek 80-case diagnostic 已完成，E2E 38/80，constructible construction success 20/55。

当前限制：
- official DeepSeek 结果只能作为 single-model diagnostic；不能写成广泛模型比较或 CCF-B ready。

下一步：
- 做 reviewer gate、limitation tightening，并起草 market operand 设计决策。

---

## Run Metadata

```yaml
Run ID: RUN-20260512-ROUTE-B-INIT
Date: 2026-05-12
Branch: exp-route-b
Role: Research Orchestrator
Task ID: TASK-20260512-001 / TASK-20260512-002
Status: in_progress
```

## Inputs

- User request: switch to `exp-route-b` and advance QSGA Route B toward a stronger CCF-B-oriented paper.
- `docs/QSGA_Route_B_Modification_Plan.md`
- `rules/AGENTS.md`
- `rules/protocols/EXECUTION_LOOP.md`

## Expanded Context

Reason:
- The task queue was still a template, so Route B work had to be initialized before implementation.

Files Read:
- `rules/AGENTS.md`
- `rules/TASK_QUEUE.md`
- `rules/CURRENT_PROGRESS.md`
- `rules/DECISIONS.md`
- `rules/RISKS.md`
- `rules/protocols/EXECUTION_LOOP.md`
- `rules/protocols/CONTEXT_POLICY.md`
- `docs/QSGA_Route_B_Modification_Plan.md`

Result:
- Created Route B task IDs and selected TASK-20260512-002 as the first executable, verifiable unit.

## Work Log

- Initialized Route B tasks in `rules/TASK_QUEUE.md`.
- Updated `rules/CURRENT_PROGRESS.md` with the active goal, constraints, and next actions.
- Updated `rules/research/RESEARCH_PLAN.md` with Route B scope, RQs, contributions, and success criteria.
- Implemented Route B construction foundation in `qsgi/construction/`.
- Added focused tests in `tests/test_route_b_construction.py`.
- Implemented live QYIR failure breakdown analysis.
- Generated `experiments/results/live_failure_breakdown.csv` and `experiments/tables/live_failure_breakdown.md`.
- Initialized Route B experiment protocol draft in `rules/research/EXPERIMENT_PLAN.md`.
- Initially created Route B manuscript working draft at `docs/paper/qsga_route_b_draft.md`; this was later deleted per user instruction and superseded by in-place updates to `docs/paper/qsga_ccf_draft.md`.
- Implemented and ran offline Route B builder smoke.
- Implemented Route B live runner skeleton and mocked pipeline tests.
- Ran bounded Route B live smoke; the initial DashScope-compatible endpoint was blocked by API authentication failure, then official DeepSeek endpoint succeeded.
- Created Route B status summary table.
- User corrected paper target: delete the new Route B draft and update `docs/paper/qsga_ccf_draft.md` in place.
- Switched Route B live runner to official DeepSeek endpoint and completed official 5-case smoke plus 80-case diagnostic.
- Updated the existing CCF draft with Route B method/result/conclusion text.

## Evidence

- `uv run pytest tests/test_route_b_construction.py`: 8 passed.
- `uv run pytest tests/test_schema.py tests/test_qyir_generator.py tests/test_validator.py`: 58 passed.
- `uv run pytest`: 187 passed.
- `uv run pytest tests/test_failure_breakdown.py`: 5 passed.
- `uv run python experiments/analyze_failure_breakdown.py`: 160 classified rows, 10 summary rows.
- `uv run python rules/scripts/check_research_ops.py --root rules`: pass after TASK-20260512-002 and TASK-20260512-003 updates.
- `uv run pytest tests/test_route_b_builder_smoke.py`: 4 passed.
- `uv run python experiments/run_route_b_builder_smoke.py`: construct 55/55, terminal correct 80/80 under expected-slot input.
- `uv run pytest tests/test_route_b_pipeline.py`: 4 passed.
- `uv run python experiments/run_live_route_b.py --help`: success, no API call.
- `uv run pytest`: 200 passed.
- Initial DashScope-compatible live smoke: 5/5 API authentication errors.
- Official DeepSeek 5-case smoke v4: wrote 5 result rows and 7 raw slot calls; E2E 2/5.
- Official DeepSeek 80-case diagnostic: wrote 80 result rows and 89 raw slot calls; E2E 38/80.
- `uv run python experiments/eval_metrics.py --input experiments/results/route_b_live_deepseek_official_80_results.csv --output experiments/results/route_b_live_deepseek_official_80_metrics.csv`: construction_success 0.364, E2E 0.475.
- `uv run python experiments/analyze_failure_breakdown.py --results experiments/results/route_b_live_deepseek_official_80_results.csv --output experiments/results/route_b_live_deepseek_official_80_failure_breakdown.csv --table-output experiments/tables/route_b_live_deepseek_official_80_failure_breakdown.md`: 80 classified rows.
- `experiments/tables/route_b_status_summary.md`: claim-safe Route B evidence status table.
- Final `uv run pytest`: 201 passed.
- Latest targeted Route B tests: `uv run pytest tests/test_route_b_construction.py tests/test_route_b_pipeline.py -q`: 17 passed.

## Files Updated

- `qsgi/__init__.py`
- `qsgi/construction/__init__.py`
- `qsgi/construction/slot_schema.py`
- `qsgi/construction/canonicalizer.py`
- `qsgi/construction/qyir_builder.py`
- `tests/test_route_b_construction.py`
- `experiments/analyze_failure_breakdown.py`
- `tests/test_failure_breakdown.py`
- `experiments/results/live_failure_breakdown.csv`
- `experiments/tables/live_failure_breakdown.md`
- `rules/research/RESULTS_LOG.md`
- `rules/research/DRAFT_STATUS.md`
- `rules/research/PAPER_MATRIX.md`
- `rules/research/EXPERIMENT_PLAN.md`
- `docs/paper/qsga_ccf_draft.md`
- `experiments/run_route_b_builder_smoke.py`
- `tests/test_route_b_builder_smoke.py`
- `experiments/results/route_b_builder_smoke.csv`
- `experiments/tables/route_b_builder_smoke.md`
- `qsgi/construction/slot_extractor.py`
- `qsgi/construction/pipeline.py`
- `experiments/run_live_route_b.py`
- `tests/test_route_b_pipeline.py`
- `experiments/results/route_b_live_smoke_deepseek_flash_5_results.csv`
- `experiments/results/route_b_live_smoke_deepseek_flash_5_raw_outputs.jsonl`
- `experiments/results/route_b_live_smoke_deepseek_flash_5_metadata.json`
- `experiments/results/route_b_live_smoke_deepseek_flash_5_token_usage.csv`
- `experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_results.csv`
- `experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_raw_outputs.jsonl`
- `experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_metadata.json`
- `experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_token_usage.csv`
- `experiments/results/route_b_live_smoke_deepseek_official_5_v4_results.csv`
- `experiments/results/route_b_live_smoke_deepseek_official_5_v4_raw_outputs.jsonl`
- `experiments/results/route_b_live_smoke_deepseek_official_5_v4_metadata.json`
- `experiments/results/route_b_live_smoke_deepseek_official_5_v4_token_usage.csv`
- `experiments/results/route_b_live_deepseek_official_80_results.csv`
- `experiments/results/route_b_live_deepseek_official_80_raw_outputs.jsonl`
- `experiments/results/route_b_live_deepseek_official_80_metadata.json`
- `experiments/results/route_b_live_deepseek_official_80_token_usage.csv`
- `experiments/results/route_b_live_deepseek_official_80_metrics.csv`
- `experiments/results/route_b_live_deepseek_official_80_failure_breakdown.csv`
- `experiments/tables/route_b_live_deepseek_official_80_metrics.md`
- `experiments/tables/route_b_live_deepseek_official_80_failure_breakdown.md`
- `experiments/tables/route_b_status_summary.md`
- `rules/TASK_QUEUE.md`
- `rules/CURRENT_PROGRESS.md`
- `rules/research/RESEARCH_PLAN.md`
- `rules/AUDIT_LOG.md`
- `rules/runs/2026-05-12-route-b-initialization.md`

## Carry Forward

- Current stage: Route B construction foundation, failure diagnosis, draft experiment protocol, in-place CCF draft update, offline builder smoke, live runner, official DeepSeek 80-case diagnostic, and status summary complete.
- Next task: reviewer gate and QYIR operand design decision.
- Constraint: future large/pro-model paid API experiments still need scoped task/update records.
- Implementation note: current QYIR v1 validator/compiler still does not support rule operands such as `market.close`; Route B builder currently stays compatible with alias-only operands.
- Diagnostic note: EXP-20260512-LIVE-FAILURE-BREAKDOWN is a deterministic analysis of saved qwen3.6-flash outputs, not a new live model experiment.

## Quality Gate

```yaml
Task ID: Yes
Clear Verifiable Unit: Yes
Evidence Output: In progress
State Updated: Yes
Dangerous Operation Avoided: Yes
Human Decision Triggered: No
Next Step Recorded: Yes
```

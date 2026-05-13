# Route B Remediation Plan

Date: 2026-05-13
Source run: `EXP-20260512-ROUTE-B-LIVE-DEEPSEEK-OFFICIAL-80`

## Evidence Snapshot

| Failure bucket | Count | Dominant categories | Representative cases |
|---|---:|---|---|
| risk_violation | 19 | trend_following, risk_constrained, momentum, mean_reversion | qsi_001, qsi_011, qsi_019, qsi_036 |
| clarification_failure | 12 | risk_constrained, momentum, mean_reversion | qsi_028, qsi_031, qsi_045, qsi_053 |
| semantic_mismatch | 7 | ambiguous_intent | qsi_056, qsi_057, qsi_064, qsi_065 |
| unsupported_indicator | 3 | momentum, mean_reversion | qsi_025, qsi_032, qsi_039 |
| schema_failure | 1 | momentum | qsi_037 |
| success | 38 | unsafe_request, mean_reversion, trend_following, risk_constrained, ambiguous_intent | qsi_003 |

Current headline metrics from `route_b_live_deepseek_official_80_metrics.csv`:

| Metric | Value |
|---|---:|
| schema_validity_constructible | 0.709 |
| construction_success_constructible | 0.364 |
| end_to_end_success_all | 0.475 |
| safe_rejection_accuracy | 1.000 |
| clarification_accuracy | 0.300 |

## Ranked Remediation Plan

### R1. Risk-Aware Post-Construction Repair

Priority: P1
Status: implemented locally on 2026-05-13
Target bucket: `risk_violation` (19/80)

Problem:
- Most failures are structurally valid, compile, and backtest, but fail the risk audit because max drawdown exceeds 20% and Sharpe is low.
- These are not schema failures; they are post-construction risk-control failures.

Proposed fix:
- Add a Route B post-construction risk-repair pass that runs after backend risk audit.
- Keep the QYIR v1 schema unchanged.
- If the risk auditor reports drawdown or missing/conservative risk controls, apply bounded deterministic repair candidates:
  - reduce `risk_control.position_size` to 0.4, then 0.25;
  - enforce `stop_loss` at 0.08, then 0.05;
  - keep `max_drawdown_limit` at or below 0.2;
  - never increase leverage or enable shorting.
- Re-run compile/backtest/risk audit for repaired candidates and keep the first passing artifact.

Observed metric movement in saved-output replay:
- Converted all 19 risk-violation cases into E2E successes under the current replay harness.
- Constructible risk_violation improved from 0.345 to 0.000.
- Constructible construction_success improved from 0.364 to 0.709.
- Overall E2E improved from 0.5625 after ambiguity guard to 0.800 after ambiguity guard + risk repair.
- Remaining Sharpe warnings are not counted risk-constraint violations under the current metric definition.

Validation:
- Added `qsgi/construction/risk_repair.py`.
- Added `tests/test_route_b_risk_repair.py`.
- Added `--enable-risk-repair` to `experiments/replay_live_route_b.py`.
- Ran `uv run pytest tests/test_route_b_risk_repair.py tests/test_route_b_pipeline.py tests/test_route_b_construction.py -q`: 22 passed.
- Ran saved-output replay with risk repair; no API call made.
- Do not present this as an official live metric until a separately scoped live run is executed.

Paper wording:
- If implemented, report as a repair ablation, not as a new model-generation capability.

### R2. Clarification Policy Tightening

Priority: P1
Status: partially implemented locally on 2026-05-13
Target bucket: `clarification_failure` (12/80)

Problem:
- The model asks for clarification on constructible requests, especially missing `symbol`, `exit_logic`, `indicators`, or `entry_logic` in momentum/risk-constrained cases.
- Some missing fields are defaultable in the benchmark setting, while others are real unsupported semantics.

Proposed fix:
- Split missing slots into:
  - defaultable: `symbol`, `asset_type`, `timeframe`, `risk_constraints`, generic `exit_logic` for RSI-style mean reversion;
  - unsupported but constructible only with future QYIR extensions: momentum rotation, low-volatility selection, multi-ETF ranking;
  - genuinely ambiguous: missing strategy family, signal definition, or all entry/exit semantics.
- Tighten `_clarification_can_be_defaulted` to default only the first group.
- For unsupported-but-specific requests, return a scoped unsupported/clarification response instead of treating it as a failed clarification.

Expected metric movement:
- Should reduce over-clarification for qsi_028-like MA deviation or RSI cases.
- Should not force momentum-rotation or low-volatility selection into unsupported QYIR v1 semantics.

Validation:
- Add fixture tests for qsi_028, qsi_031, qsi_045, qsi_053-style slot outputs.
- Replay saved raw slot outputs locally before any new live call.
- Implemented narrow defaulting for `entry_threshold` only when a mean-reversion request has concrete supported indicator, entry logic, and exit logic.
- Tightened non-core defaulting so momentum/risk-controlled requests are not defaulted into single-asset strategies merely because symbol or exit logic is missing.
- qsi_028 is converted to E2E success in saved-output replay after risk repair.

Paper wording:
- Clarify that QSI-Bench contains some requests that are specific but outside QYIR v1's rule-indicator expressivity.

### R3. Ambiguous-Intent Guard Strengthening

Priority: P1
Status: implemented locally on 2026-05-13
Target bucket: `semantic_mismatch` in ambiguous cases (7/80)

Problem:
- Some ambiguous requests were converted into concrete strategies and then failed downstream risk checks.
- For benchmark scoring, ambiguous_intent should be handled by clarification, not by forced construction.

Proposed fix:
- Add deterministic pre-extraction ambiguity guard patterns for vague intent:
  - "稳一点", "比较聪明", "适合现在行情", "差不多", "低买高卖", "不要太频繁", and similar phrasing without concrete indicator/rule thresholds.
- If vague intent lacks a concrete strategy family, indicator, window, threshold, or entry/exit rule, return clarification before calling the model.
- Keep this as a conservative boundary-control layer, not a broad natural-language understanding claim.

Expected metric movement:
- Could recover up to 7 ambiguous cases from semantic_mismatch to clarification success.

Validation:
- Added deterministic ambiguity guard before LLM slot extraction.
- Added focused tests in `tests/test_route_b_pipeline.py`.
- Ran `uv run python experiments/check_route_b_ambiguity_guard.py`.
- Current no-API guard check: ambiguous recall 10/10, non-ambiguous false-positive 0/70, overall accuracy 80/80.
- Added saved-output replay harness `experiments/replay_live_route_b.py`.
- Saved-output replay over official DeepSeek 80-case raw slot outputs: clarification_accuracy improves from 0.300 to 1.000, overall E2E improves from 0.475 to 0.5625. This is not a new live API run.

Paper wording:
- Report as boundary-control improvement and deterministic benchmark coverage, not robust multi-turn clarification.

### R4. Unsupported Strategy Semantics Boundary

Priority: P2
Status: implemented locally on 2026-05-13
Target buckets: `unsupported_indicator` (3/80), `schema_failure` (1/80), part of `clarification_failure`

Problem:
- Momentum rotation, low-volatility ETF selection, consecutive-down reversion, and ranking-based requests are beyond the current QYIR v1 indicator-rule contract.
- QYIR v1 remains alias-only and does not support explicit market-field operands per DEC-20260512-003.

Proposed fix:
- Do not modify schema/compiler in the current paper cycle.
- Add explicit unsupported-semantics detection in Route B for:
  - ranking/top-k ETF rotation;
  - low-volatility selection;
  - consecutive-day pattern rules not expressible in current operators;
  - custom momentum indicator names not in the schema.
- Return a bounded clarification/unsupported message rather than an invalid QYIR.

Expected metric movement:
- May improve failure taxonomy and user-facing behavior, but not necessarily construction_success if benchmark expects construction for these cases.

Validation:
- Add tests for qsi_025, qsi_032, qsi_037, qsi_039, qsi_045.
- Added `qsgi/construction/unsupported_semantics.py`.
- Added pre-extraction unsupported-semantics guard for cross-sectional ranking/rotation, top-k/portfolio-cardinality selection, low-volatility selection, and consecutive-day pattern rules.
- Added failure-breakdown label `unsupported_semantics`.
- Saved-output policy+risk replay: 65/80 E2E, 11/80 unsupported_semantics, 4/80 clarification_failure, 0 risk_violation.
- qsi_039 is converted to E2E success through role normalization + builder approximation + risk repair; qsi_040 is no longer miscounted as success because cross-sectional ranking is outside QYIR v1.

Paper wording:
- Treat these as QYIR v1 scope limitations and future-work candidates, not compiler defects.

## Recommended Next Tasks

| Task | Priority | Safe to run automatically | Output |
|---|---|---|---|
| Implement ambiguity guard tests and deterministic pre-extraction clarification | P1 | Yes | done: tests + local 80/80 guard check |
| Implement no-API replay harness for saved Route B slot outputs | P1 | Yes | replay CSV before any new API call |
| Prototype bounded risk-repair pass | P1 | Yes | done: replay risk_violation 0.345 -> 0.000, E2E 0.5625 -> 0.800 |
| Add unsupported-semantics detector and tests | P2 | Yes | done: unsupported_semantics 11/80, clarification_failure 4/80, E2E 0.8125 |
| Run second full 80-case live model | P1 | No, requires scoped cost/sample update | model-generalization evidence |

## Claim Boundaries

- Do not claim Route B is CCF-B ready based only on this remediation plan.
- Do not claim unsupported momentum/selection requests are solved until QYIR supports those semantics or the benchmark scope is narrowed.
- Do not change QYIR v1 schema/compiler contract before a separate post-review decision.
- Any new live API run must preserve raw outputs, metadata, token usage, and exact prompt/configuration.

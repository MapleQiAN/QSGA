# QSGA Reviewer Response Log

Date: 2026-05-06

Purpose: track reviewer-style objections, immediate revisions, and remaining blockers for the QSGA CCF-C candidate paper package.

## Current Verdict

The current package is defensible as a deterministic prototype / IR feasibility study with supplementary live diagnostics: a no-oracle main prototype, an oracle-slot verification-chain upper bound, a 12-case multi-model live-QYIR pilot, an 80-case qwen3.6-flash live-QYIR diagnostic, and an 80-case executable qwen3.6-flash live direct-code baseline. It is still not defensible as a broad empirical LLM strategy-generation paper because live construction evidence remains weak and single-model at 80-case scale.

## Objection Response Matrix

| ID | Reviewer Objection | Action Taken | Evidence | Status |
|---|---|---|---|---|
| RSP-001 | Oracle-slot construction leaks benchmark expected slots into the main QSGA run. | Main draft now presents no-oracle deterministic extraction as the main prototype result and labels oracle-slot QSGA as an upper-bound verification-chain evaluation. | `experiments/run_no_oracle.py`; `experiments/results/no_oracle_metrics.csv`; `experiments/results/baseline_metrics.csv`; `docs/paper/qsga_ccf_c_draft.md` | mitigated by result ordering and claim boundary |
| RSP-002 | Direct-code and direct-JSON baselines are simulated, not live LLM outputs. | Main draft and reviewer report now explicitly call them simulated deterministic baselines; added executable live direct-code harness and saved qwen3.6-flash 80-case raw outputs, replay rows, and metrics. | `experiments/run_live_direct_code.py`; `experiments/results/live_direct_code_metrics.csv`; `docs/paper/qsga_ccf_c_draft.md`; `docs/paper/ccf_c_reviewer_report_v3.md`; `docs/paper/citation_and_claim_matrix.md` | mitigated as one-model diagnostic baseline |
| RSP-003 | Safe rejection was shared and missed an unsafe paraphrase. | Added paraphrase patterns for guaranteed periodic profit / no-loss requests; added regression test; reran experiments and synchronized metrics. | `verifier/safe_rejection.py`; `tests/test_safe_rejection.py`; `experiments/tables/safe_rejection.md` | mitigated in QSI-Bench v1 |
| RSP-004 | Safe-rejection accuracy should not be presented as robust financial safety. | Main draft now frames it as small-subset deterministic rule/pattern coverage, not robust safety. | `docs/paper/qsga_ccf_c_draft.md` | mitigated |
| RSP-005 | Semantic-verification ablation shows no independent gain. | Main draft downgrades semantic verification to an architectural guard within the verification chain. | `docs/paper/qsga_ccf_c_draft.md`; `docs/ai-research-assistant/RESULTS_LOG.md` | mitigated |
| RSP-006 | Ambiguous-intent handling is not empirically demonstrated. | Added clarification-aware result columns and metrics; main draft now scores ambiguous requests through clarification accuracy while limiting claims to deterministic single-turn ambiguity handling. | `experiments/results/baseline_metrics.csv`; `experiments/results/no_oracle_metrics.csv`; `docs/paper/qsga_ccf_c_draft.md` | mitigated for QSI-Bench; live multi-turn clarification remains future work |
| RSP-007 | Related work missed direct trading-code and financial IR comparators. | Added direct comparator citations and claim matrix entries for QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, OQL-style option strategies, and finance hallucination work. | `docs/paper/citation_and_claim_matrix.md`; `docs/paper/qsga_ccf_c_draft.md` | partially mitigated; PDF-level verification still pending |
| RSP-008 | QYIR may be only JSON Schema with a domain label. | Added w/o QYIR ablation to isolate QYIR-specific semantics, alias/rule linkage, risk slots, and repair localization. | `experiments/baselines.py`; `experiments/results/ablation_metrics.csv`; `experiments/tables/ablation_comparison.md` | mitigated in deterministic harness |
| RSP-009 | Single-symbol data makes execution evidence fragile. | Added synthetic SPY/QQQ/GLD and alternate-period smoke test for compile/backtest/risk-audit runnability only. | `experiments/run_multi_asset_smoke.py`; `experiments/results/multi_asset_smoke_results.csv` | mitigated as smoke test only |

## Latest Reproduced Metrics

| Result | Value |
|---|---:|
| tests | 179 passed |
| oracle-slot QSGA E2E | 0.9625 |
| oracle-slot QSGA construction success | 0.9455 |
| no-oracle slot extraction E2E | 0.8875 |
| no-oracle construction success | 0.8364 |
| direct_code E2E | 0.5000 |
| direct_json E2E | 0.4000 |
| safe rejection accuracy | 1.0000 |
| ambiguous-intent clarification accuracy | 10/10 |
| w/o QYIR E2E | 0.1625 |
| synthetic multi-asset smoke | 5/5 runnable |
| live QYIR 80 E2E | raw 0.075; QSGA wrapper 0.375 |
| live QYIR 80 construction success | raw 0.109; QSGA wrapper 0.091 |
| live direct-code E2E | 0.350 |
| safe paraphrase regression | 35/35 correct |

## Remaining Blockers Before Strong CCF-C Submission

1. Add another full 80-case live model only if model-generalized empirical LLM claims are retained.
2. Upgrade key citations from scaffolded/PDF-level checks to human-approved final claim verification.
3. Keep live QYIR vs live direct-code wording conservative because current live QYIR construction success is lower than live direct-code construction success.
4. Confirm final figure rendering and camera-ready formatting.
5. Obtain human approval for authorship, release, and submission target.

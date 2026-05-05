# QSGA Reviewer Response Log

Date: 2026-05-05

Purpose: track reviewer-style objections, immediate revisions, and remaining blockers for the QSGA CCF-C candidate paper package.

## Current Verdict

The current package is defensible as a deterministic prototype / IR feasibility study with a supplementary 12-case live-QYIR pilot. It is not yet defensible as a standard empirical LLM strategy-generation paper because the live pilot is small, executable live direct-code results are not yet collected, and related-work claims still need PDF-level verification.

## Objection Response Matrix

| ID | Reviewer Objection | Action Taken | Evidence | Status |
|---|---|---|---|---|
| RSP-001 | Oracle-slot construction leaks benchmark expected slots into the main QSGA run. | Main draft now labels the primary result as oracle-slot deterministic evaluation; added a no-oracle deterministic slot-extraction experiment. | `experiments/run_no_oracle.py`; `experiments/results/no_oracle_metrics.csv`; `docs/paper/qsga_ccf_c_draft.md` | partially mitigated |
| RSP-002 | Direct-code and direct-JSON baselines are simulated, not live LLM outputs. | Main draft and reviewer report now explicitly call them simulated deterministic baselines; added executable live direct-code harness for real model outputs. | `experiments/run_live_direct_code.py`; `docs/paper/qsga_ccf_c_draft.md`; `docs/paper/ccf_c_reviewer_report.md`; `docs/paper/citation_and_claim_matrix.md` | mitigated for prototype framing; live run still pending |
| RSP-003 | Safe rejection was shared and missed an unsafe paraphrase. | Added paraphrase patterns for guaranteed periodic profit / no-loss requests; added regression test; reran experiments and synchronized metrics. | `verifier/safe_rejection.py`; `tests/test_safe_rejection.py`; `experiments/tables/safe_rejection.md` | mitigated in QSI-Bench v1 |
| RSP-004 | Safe-rejection accuracy should not be presented as robust financial safety. | Main draft now frames it as small-subset deterministic rule/pattern coverage, not robust safety. | `docs/paper/qsga_ccf_c_draft.md` | mitigated |
| RSP-005 | Semantic-verification ablation shows no independent gain. | Main draft downgrades semantic verification to an architectural guard within the verification chain. | `docs/paper/qsga_ccf_c_draft.md`; `docs/ai-research-assistant/RESULTS_LOG.md` | mitigated |
| RSP-006 | Ambiguous-intent handling is not empirically demonstrated. | Main draft adds category breakdown and explicitly states ambiguous requests are currently counted as failures. | `docs/paper/qsga_ccf_c_draft.md`; `experiments/results/baseline_results.csv`; `experiments/results/no_oracle_results.csv` | mitigated by disclosure; feature remains incomplete |
| RSP-007 | Related work missed direct trading-code and financial IR comparators. | Added direct comparator citations and claim matrix entries for QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, OQL-style option strategies, and finance hallucination work. | `docs/paper/citation_and_claim_matrix.md`; `docs/paper/qsga_ccf_c_draft.md` | partially mitigated; PDF-level verification still pending |
| RSP-008 | QYIR may be only JSON Schema with a domain label. | Added w/o QYIR ablation to isolate QYIR-specific semantics, alias/rule linkage, risk slots, and repair localization. | `experiments/baselines.py`; `experiments/results/ablation_metrics.csv`; `experiments/tables/ablation_comparison.md` | mitigated in deterministic harness |
| RSP-009 | Single-symbol data makes execution evidence fragile. | Added synthetic SPY/QQQ/GLD and alternate-period smoke test for compile/backtest/risk-audit runnability only. | `experiments/run_multi_asset_smoke.py`; `experiments/results/multi_asset_smoke_results.csv` | mitigated as smoke test only |

## Latest Reproduced Metrics

| Result | Value |
|---|---:|
| tests | 173 passed |
| oracle-slot QSGA E2E | 0.8375 |
| no-oracle slot extraction E2E | 0.7625 |
| direct_code E2E | 0.5000 |
| direct_json E2E | 0.4000 |
| safe rejection accuracy | 1.0000 |
| ambiguous-intent E2E | 0/10 |
| w/o QYIR E2E | 0.1625 |
| synthetic multi-asset smoke | 5/5 runnable |

## Remaining Blockers Before Strong CCF-C Submission

1. Expand live QYIR from the 12-case pilot to 80 cases if empirical LLM claims are retained.
2. Run `experiments/run_live_direct_code.py` and save executable live direct-code outputs before claiming direct-code comparison.
3. Upgrade key citations from metadata-level checks to PDF-level claim verification.
4. Add final figures and camera-ready formatting.
5. Obtain human approval for authorship, release, and submission target.

# QSGA Reviewer Response Log

Date: 2026-05-05

Purpose: track reviewer-style objections, immediate revisions, and remaining blockers for the QSGA CCF-C candidate paper package.

## Current Verdict

The current package is defensible only as a deterministic prototype / IR feasibility study. It is not yet defensible as a standard empirical LLM strategy-generation paper because live LLM generation outputs and live baseline comparisons are absent.

## Objection Response Matrix

| ID | Reviewer Objection | Action Taken | Evidence | Status |
|---|---|---|---|---|
| RSP-001 | Oracle-slot construction leaks benchmark expected slots into the main QSGA run. | Main draft now labels the primary result as oracle-slot deterministic evaluation; added a no-oracle deterministic slot-extraction experiment. | `experiments/run_no_oracle.py`; `experiments/results/no_oracle_metrics.csv`; `docs/paper/qsga_ccf_c_draft.md` | partially mitigated |
| RSP-002 | Direct-code and direct-JSON baselines are simulated, not live LLM outputs. | Main draft and reviewer report now explicitly call them simulated deterministic baselines and remove strong direct-LLM superiority claims. | `docs/paper/qsga_ccf_c_draft.md`; `docs/paper/ccf_c_reviewer_report.md`; `docs/paper/citation_and_claim_matrix.md` | mitigated for prototype framing; blocker for empirical LLM framing |
| RSP-003 | Safe rejection was shared and missed an unsafe paraphrase. | Added paraphrase patterns for guaranteed periodic profit / no-loss requests; added regression test; reran experiments and synchronized metrics. | `verifier/safe_rejection.py`; `tests/test_safe_rejection.py`; `experiments/tables/safe_rejection.md` | mitigated in QSI-Bench v1 |
| RSP-004 | Safe-rejection accuracy should not be presented as robust financial safety. | Main draft now frames it as small-subset deterministic rule/pattern coverage, not robust safety. | `docs/paper/qsga_ccf_c_draft.md` | mitigated |
| RSP-005 | Semantic-verification ablation shows no independent gain. | Main draft downgrades semantic verification to an architectural guard within the verification chain. | `docs/paper/qsga_ccf_c_draft.md`; `docs/ai-research-assistant/RESULTS_LOG.md` | mitigated |
| RSP-006 | Ambiguous-intent handling is not empirically demonstrated. | Main draft adds category breakdown and explicitly states ambiguous requests are currently counted as failures. | `docs/paper/qsga_ccf_c_draft.md`; `experiments/results/baseline_results.csv`; `experiments/results/no_oracle_results.csv` | mitigated by disclosure; feature remains incomplete |
| RSP-007 | Related work missed direct trading-code and financial IR comparators. | Added direct comparator citations and claim matrix entries for QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, OQL-style option strategies, and finance hallucination work. | `docs/paper/citation_and_claim_matrix.md`; `docs/paper/qsga_ccf_c_draft.md` | partially mitigated; PDF-level verification still pending |

## Latest Reproduced Metrics

| Result | Value |
|---|---:|
| tests | 171 passed |
| oracle-slot QSGA E2E | 0.8375 |
| no-oracle slot extraction E2E | 0.7625 |
| direct_code E2E | 0.5000 |
| direct_json E2E | 0.4000 |
| safe rejection accuracy | 1.0000 |
| ambiguous-intent E2E | 0/10 |

## Remaining Blockers Before Strong CCF-C Submission

1. Add live LLM-backed QYIR generation with fixed prompt, model, temperature, and saved raw outputs.
2. Replace or supplement simulated direct-code/direct-JSON baselines with saved live model outputs.
3. Upgrade key citations from metadata-level checks to PDF-level claim verification.
4. Add final figures and camera-ready formatting.
5. Obtain human approval for authorship, release, and submission target.

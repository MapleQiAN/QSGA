# Current Progress

Updated: 2026-05-07 00:00 +08:00

## Current Objective

Revise the QSGA CCF-C candidate draft according to the latest reviewer-risk suggestions:

1. Make the abstract less metric-heavy and restore a clear problem-method-experiment-boundary narrative.
2. Reframe live QYIR results as a diagnostic bottleneck rather than a victory claim over direct code.
3. Add direct evidence for semantic verification using slot-corruption cases.
4. Weaken safe-rejection claims and avoid implying robust financial safety from small deterministic rule sets.
5. Clarify direct-code/direct-JSON baseline naming and shared safety-gate interpretation.
6. Split no-oracle main result, oracle-slot upper bound, and live diagnostics; add clarification-aware metrics for ambiguous intents.

## Completed Before This File

- Built deterministic QSGA baseline and ablation harnesses.
- Added no-oracle deterministic slot extraction.
- Added saved-output live QYIR diagnostics for qwen3.6-flash over 80 QSI-Bench v1 cases.
- Added executable live direct-code baseline for qwen3.6-flash over 80 QSI-Bench v1 cases.
- Added safe-rejection paraphrase regression set.
- Updated one-command reproduction scripts to replay saved live outputs with `.venv` Python.
- Current test state before this revision: 178 tests passing.

## This Revision Completed So Far

- Add this progress file to reduce reliance on chat context.
- Add a semantic slot-corruption experiment.
- Add a saved-output live direct-code shared-rejection replay experiment without new API calls.
- Revise the paper draft, claim policy, results log, experiment plan, audit log, and risk register to match the new evidence and more conservative framing.
- Add `clarification_requested` and `clarification_correct` result columns, update metric aggregation, regenerate baseline/no-oracle/ablation/live replay metrics, and rewrite the paper around the three-layer evidence hierarchy.
- Apply V4 reviewer-risk revisions to the draft: safer IR-first title, less metric-heavy abstract, sharper contributions, formal QYIR validity conditions, QYIR-vs-JSON case table, Wilson intervals, explicit repair invariant, clearer oracle-slot/live diagnostic naming, added live QYIR and direct-code case traces, and expanded threats to validity.

## New Results In This Revision

- Semantic corruption: 7/7 corrupted QYIR artifacts remain schema-valid; semantic verifier detects 7/7 conflicts.
- Live direct-code shared rejection: saved qwen3.6-flash direct-code outputs improve from 0.350 E2E to 0.5375 E2E after applying the shared deterministic safe-rejection gate.
- No-oracle main deterministic prototype: construction success 0.8364, clarification accuracy 1.000, E2E 0.8875.
- Oracle-slot upper-bound QSGA: construction success 0.9455, clarification accuracy 1.000, E2E 0.9625.
- Live QYIR diagnostic: raw QYIR E2E 0.075; QSGA wrapper E2E 0.375 but construction success only 0.0909.
- Verification: `pytest tests -q` passes with 179 tests; `scripts/reproduce_all.ps1` completes and regenerates the new result CSVs.

## Important Evidence Boundaries

- `qsga_no_oracle_slots` is now the main deterministic prototype result but remains deterministic and should not be described as a live LLM result.
- `qsga_full` is an oracle-slot upper-bound verification-chain evaluation, not full raw natural-language generation.
- Live QYIR qwen3.6-flash: raw QYIR E2E 0.075; QSGA wrapper E2E 0.375; QSGA wrapper construction success 0.0909.
- Live direct-code qwen3.6-flash: syntax/interface 1.000; E2E 0.350.
- Current live evidence shows boundary handling gains but does not show live QYIR construction outperforming live direct-code construction.
- Safe rejection is deterministic, small-scope, and partly pattern-based.
- V4 framing is now explicit: the paper does not claim to solve open-domain natural-language trading strategy generation; it studies a bounded IR-first verification framework.

## Next Automatic Steps

1. Do a final human review of claim framing before submission or public release.
2. Keep public release/submission blocked on human review.

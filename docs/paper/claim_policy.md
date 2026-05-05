# QSGA Claim Policy

Date: 2026-05-05

Scope: submission-facing claim boundary for the current QSGA CCF-C package.

## Allowed Claims

1. QSGA is a bounded deterministic prototype for rule-based quantitative strategy specification generation.
2. QYIR is a constrained intermediate representation with domain fields for market scope, indicators, rule semantics, and risk control.
3. In QSI-Bench v1, the implemented verification chain improves measured artifact reliability over the current deterministic approximations.
4. The live QYIR pilot shows that real model outputs can be routed into the verification chain, with saved raw outputs and token usage.
5. The live direct-code runner is an experiment harness for executable live model baselines; its results should be claimed only after the live run is completed and saved.
6. The synthetic SPY/QQQ/GLD smoke test checks compile/backtest/risk-audit runnability across generated samples; it is not a market robustness result.

## Downgraded Claims

| Strong Wording | Allowed Wording |
|---|---|
| QSGA improves natural-language strategy generation | QSGA improves measured artifact reliability in a bounded deterministic prototype and supplementary live-QYIR pilot |
| QSGA beats direct LLM-to-code | QSGA is compared with simulated deterministic direct-code baselines; executable live direct-code comparison is pending until live outputs are collected |
| QYIR guarantees correct trading behavior | QYIR enables structural, semantic, compilation, and risk checks within QYIR v1 scope |
| safe rejection provides financial safety | safe rejection covers explicit unsafe patterns in QSI-Bench v1 and remains limited |

## Forbidden Claims

1. No profitability, alpha, investment advice, or real-money safety claim.
2. No SOTA claim.
3. No broad LLM generalization claim.
4. No claim that QYIR covers arbitrary financial instruments, HFT, options, futures, or portfolio optimization.
5. No claim that live direct-code baseline has been beaten until `experiments/results/live_direct_code_results.csv` is produced from real API outputs.
6. No PDF-level related-work claim unless the paper has been read and logged in `related_work_verified.md` or the claim matrix.

## Human Review Required

Human approval is required before public release, authorship decisions, live API spending beyond pilot scale, and submission target selection.

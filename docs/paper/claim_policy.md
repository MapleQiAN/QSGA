# QSGA Claim Policy

Date: 2026-05-06

Scope: submission-facing claim boundary for the current QSGA CCF-C package.

## Allowed Claims

1. QSGA is a bounded deterministic prototype for rule-based quantitative strategy specification generation.
2. QYIR is a constrained intermediate representation with domain fields for market scope, indicators, rule semantics, and risk control.
3. In QSI-Bench v1, the implemented verification chain improves measured artifact reliability over the current deterministic approximations.
4. The live QYIR 80-case run for qwen3.6-flash shows that real model outputs can be routed into the verification chain, with saved raw outputs, metadata, and token usage; it remains single-model diagnostic evidence.
5. The executable live direct-code qwen3.6-flash baseline has saved 80-case raw outputs, metadata, token usage, result rows, and metrics. It may be used as a one-model diagnostic comparison, not as broad live LLM evidence.
6. The synthetic SPY/QQQ/GLD smoke test checks compile/backtest/risk-audit runnability across generated samples; it is not a market robustness result.

## Downgraded Claims

| Strong Wording | Allowed Wording |
|---|---|
| QSGA improves natural-language strategy generation | QSGA improves measured artifact reliability in a bounded deterministic prototype and supplementary single-model live diagnostics |
| QSGA beats direct LLM-to-code | QSGA is compared with deterministic direct-code approximations and a one-model executable live direct-code baseline; current live QYIR E2E does not beat live direct-code E2E |
| QYIR guarantees correct trading behavior | QYIR enables structural, semantic, compilation, and risk checks within QYIR v1 scope |
| safe rejection provides financial safety | safe rejection covers explicit unsafe patterns in QSI-Bench v1 and remains limited |

## Forbidden Claims

1. No profitability, alpha, investment advice, or real-money safety claim.
2. No SOTA claim.
3. No broad LLM generalization claim.
4. No claim that QYIR covers arbitrary financial instruments, HFT, options, futures, or portfolio optimization.
5. No claim that QSGA beats executable live direct-code; current qwen3.6-flash live direct-code E2E is 0.350, while live QSGA QYIR E2E is 0.250.
6. No PDF-level related-work claim unless the paper has been read and logged in `related_work_verified.md` or the claim matrix.

## Human Review Required

Human approval is required before public release, authorship decisions, live API spending beyond pilot scale, and submission target selection.

# QSGA Claim Policy

Date: 2026-05-06

Scope: submission-facing claim boundary for the current QSGA CCF-C package.

## Allowed Claims

1. QSGA is a bounded deterministic prototype for rule-based quantitative strategy specification generation.
2. QYIR is a constrained intermediate representation with domain fields for market scope, indicators, rule semantics, and risk control.
3. In QSI-Bench v1, the main no-oracle deterministic prototype reaches 0.836 construction success and 0.887 overall E2E success without using gold slots for QYIR construction.
4. The oracle-slot QSGA result may be used only as an upper-bound verification-chain evaluation: 0.945 construction success and 0.963 overall E2E success when strategy slots are available.
5. The live QYIR 80-case run for qwen3.6-flash shows that real model outputs can be routed into the verification chain, with saved raw outputs, metadata, and token usage; it remains single-model diagnostic evidence that exposes QYIR generation as a bottleneck.
6. The executable live direct-code qwen3.6-flash baseline has saved 80-case raw outputs, metadata, token usage, result rows, and metrics. It may be used as a one-model diagnostic comparison, not as broad live LLM evidence.
7. The synthetic SPY/QQQ/GLD smoke test checks compile/backtest/risk-audit runnability across generated samples; it is not a market robustness result.
8. The saved-output direct-code shared-rejection replay may be used to show that the same deterministic boundary gate improves explicit unsafe-request handling for direct code, without claiming QYIR-like interpretability or repairability.
9. The semantic slot-corruption check may be used to show that semantic verification detects schema-valid conflicts with explicit intent slots.

## Downgraded Claims

| Strong Wording | Allowed Wording |
|---|---|
| QSGA improves natural-language strategy generation | QSGA improves measured artifact reliability when valid or partially valid strategy specifications can be constructed |
| QSGA beats direct LLM-to-code | QSGA is compared with deterministic direct-code approximations and a one-model executable live direct-code baseline; current live QYIR construction success remains lower than live direct-code construction success |
| QYIR guarantees correct trading behavior | QYIR enables structural, semantic, compilation, and risk checks within QYIR v1 scope |
| safe rejection provides financial safety | safe rejection covers explicit unsafe patterns in QSI-Bench v1 and remains limited |
| semantic verification independently improves oracle-slot E2E | semantic verification is an interface guard; its isolated value is shown by schema-valid slot-corruption checks |

## Forbidden Claims

1. No profitability, alpha, investment advice, or real-money safety claim.
2. No SOTA claim.
3. No broad LLM generalization claim.
4. No claim that QYIR covers arbitrary financial instruments, HFT, options, futures, or portfolio optimization.
5. No claim that live QYIR beats executable live direct-code; current qwen3.6-flash live QSGA QYIR overall E2E is 0.375 but construction success is only 0.091, while live direct-code overall E2E is 0.350 and construction success is 0.509.
6. No PDF-level related-work claim unless the paper has been read and logged in `related_work_verified.md` or the claim matrix.

## Human Review Required

Human approval is required before public release, authorship decisions, live API spending beyond pilot scale, and submission target selection.

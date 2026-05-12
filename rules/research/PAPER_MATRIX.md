# PAPER_MATRIX.md

---

## TLDR_STATE_FOR_AGENT

当前核心文献：

- QuantCode-Bench
- SysTradeBench
- Market-Bench
- QuantEval
- OQL option-strategy semantic parser

已核验引用：

- arXiv:2604.15151 QuantCode-Bench
- arXiv:2604.04812 SysTradeBench
- arXiv:2512.12264 Market-Bench
- arXiv:2601.08689 QuantEval
- arXiv:2603.16434 Natural Language to Executable Option Strategies / OQL
- arXiv:2512.09506 CNFinBench

待核验引用：

- 其余通用 code-generation、tool-use、financial LLM references should still be checked before submission.

与 claim 相关的证据缺口：

- Route B official DeepSeek single-model diagnostic 已完成；仍缺少第二个 full 80-case model 和 reviewer gate。
- 外部相关工作引用尚未核验。

---

## Paper Matrix

| Paper ID | Citation | Type | Key Idea | Supports Claim | Evidence Level | Verified |
|---|---|---|---|---|---|---|
| P-QUANTCODE | QuantCode-Bench, arXiv:2604.15151 | Benchmark | Evaluates executable algorithmic trading strategy generation from natural language. | QSGA differs by making a bounded strategy IR auditable before execution. | B | Yes |
| P-SYSTRADE | SysTradeBench, arXiv:2604.04812 | Benchmark/System | Evaluates iterative build-test-patch strategy-to-code systems with drift-aware diagnostics. | Supports the auditability and traceability motivation. | B | Yes |
| P-MARKETBENCH | Market-Bench, arXiv:2512.12264 | Benchmark | Evaluates LLMs on quantitative trading and market dynamics tasks. | Supports the claim that executable market artifacts need behavioral validation. | B | Yes |
| P-QUANTEVAL | QuantEval, arXiv:2601.08689 | Benchmark | Covers financial quantitative tasks including strategy coding. | Positions QSGA as narrower and mechanism-specific. | B | Yes |
| P-OQL | Natural Language to Executable Option Strategies, arXiv:2603.16434 | Method/System | Uses a domain IR for option-strategy semantic parsing and deterministic execution. | Closest architectural analog to QYIR but in options. | B | Yes |
| P-CNFINBENCH | CNFinBench, arXiv:2512.09506 | Benchmark/Safety | Evaluates finance expertise, autonomy, integrity, safety, and compliance. | Motivates scoped financial safety and refusal boundaries. | B | Yes |

---

## Claim-Evidence Matrix

| Claim ID | Claim | Supporting Papers | Contradicting Papers | Evidence Level | Notes |
|---|---|---|---|---|---|
| CLAIM-RB-001 | Saved qwen3.6-flash live-QYIR results exhibit concrete failure buckets across schema, alias/reference, safety, and risk audit stages. | n/a: internal experiment evidence EXP-20260512-LIVE-FAILURE-BREAKDOWN | None recorded | A | Use only as saved-run diagnostic evidence, not as a general LLM claim. |
| CLAIM-RB-002 | Official DeepSeek Route B slot-builder diagnostic reaches 0.364 construction success and 0.475 E2E on QSI-Bench v1. | n/a: internal experiment evidence EXP-20260512-ROUTE-B-LIVE-DEEPSEEK-OFFICIAL-80 | None recorded | B | Use as single-model diagnostic only; do not present as broad model comparison. |
| CLAIM-RB-004 | Deterministic Route B builder can construct valid QYIR from QSI-Bench expected slots for current construct cases. | n/a: internal experiment evidence EXP-20260512-ROUTE-B-BUILDER-SMOKE | None recorded | A | Gold/expected-slot builder smoke only; not live extraction evidence. |

---

## Paper Entry Template

```yaml
Paper ID:
Title:
Authors:
Year:
Venue:
Type: Survey / Method / Benchmark / System / Theory / Position
URL or DOI:
Verified: Yes / No
Key Idea:
Method:
Dataset:
Metrics:
Limitations:
Related Claims:
Evidence Level:
Notes:
```

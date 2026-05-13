# PAPER_MATRIX.md

---

## TLDR_STATE_FOR_AGENT

当前核心文献：

- QuantCode-Bench
- SysTradeBench
- Market-Bench
- QuantEval
- OQL option-strategy semantic parser
- Codex / program synthesis / AlphaCode
- PICARD / execution-feedback and generated-test code verification
- ReAct / Toolformer / Self-Refine
- FinGPT / FinRobot / TradingAgents / FinMem

已核验引用：

- arXiv:2604.15151 QuantCode-Bench
- arXiv:2604.04812 SysTradeBench
- arXiv:2512.12264 Market-Bench
- arXiv:2601.08689 QuantEval
- arXiv:2603.16434 Natural Language to Executable Option Strategies / OQL
- arXiv:2512.09506 CNFinBench
- arXiv:2107.03374 Codex
- arXiv:2108.07732 Program Synthesis with Large Language Models
- arXiv:2203.07814 AlphaCode
- arXiv:2109.05093 PICARD
- arXiv:2210.03629 ReAct
- arXiv:2302.04761 Toolformer
- arXiv:2303.17651 Self-Refine
- arXiv:2302.08468 LEVER
- arXiv:2207.10397 CodeT
- arXiv:2306.06031 FinGPT
- arXiv:2405.14767 FinRobot
- arXiv:2412.20138 TradingAgents
- arXiv:2311.15548 finance hallucination
- arXiv:2311.13743 FinMem

待核验引用：

- 暂无；提交前仍需做格式/作者顺序最终校对。

与 claim 相关的证据缺口：

- Route B official DeepSeek single-model diagnostic 已完成；仍缺少第二个 full 80-case model 和 reviewer gate。
- 外部相关工作主引用已完成 arXiv primary-source 核验；仍缺少正式 venue/DOI 格式化。

---

## Paper Matrix

| Paper ID | Citation | Type | Key Idea | Supports Claim | Evidence Level | Verified |
|---|---|---|---|---|---|---|
| P-CODEX | Evaluating Large Language Models Trained on Code, arXiv:2107.03374 | Method/Evaluation | Establishes LLM code-generation capability and evaluation framing. | Motivates why NL-to-code alone is plausible but insufficient for strategy reliability. | B | Yes |
| P-PROGSYN | Program Synthesis with Large Language Models, arXiv:2108.07732 | Method/Evaluation | Studies few-shot program synthesis with LLMs. | Background for text-to-program generation. | B | Yes |
| P-ALPHACODE | Competition-Level Code Generation with AlphaCode, arXiv:2203.07814 | Method/System | Demonstrates competition-level code generation with large models. | Supports broad code-generation context. | B | Yes |
| P-PICARD | PICARD, arXiv:2109.05093 | Method | Constrains autoregressive generation with incremental parsing. | Supports comparison with syntax/grammar-constrained output. | B | Yes |
| P-REACT | ReAct, arXiv:2210.03629 | Method | Combines reasoning and acting with external actions/tools. | Background for tool-using generation systems. | B | Yes |
| P-TOOLFORMER | Toolformer, arXiv:2302.04761 | Method | Teaches LMs to use tools through self-supervised API-call examples. | Background for tool-using LLM systems. | B | Yes |
| P-SELFREFINE | Self-Refine, arXiv:2303.17651 | Method | Iterative self-feedback and refinement loop for generated outputs. | Related to feedback-guided repair, but QSGA uses domain verifier feedback. | B | Yes |
| P-LEVER | LEVER, arXiv:2302.08468 | Method | Learns to verify language-to-code generations with execution. | Supports execution-feedback motivation. | B | Yes |
| P-CODET | CodeT, arXiv:2207.10397 | Method | Uses generated tests and dual execution agreement for code generation. | Supports verification-through-execution framing. | B | Yes |
| P-FINGPT | FinGPT, arXiv:2306.06031 | System | Open-source financial LLM framework. | Positions QSGA against broader financial LLM systems. | B | Yes |
| P-FINROBOT | FinRobot, arXiv:2405.14767 | System/Agent | Open-source AI agent platform for financial applications. | Related financial-agent context; QSGA focuses on artifact construction reliability. | B | Yes |
| P-TRADINGAGENTS | TradingAgents, arXiv:2412.20138 | System/Agent | Multi-agent LLM financial trading framework. | Contrasts trading-agent decision systems with strategy-artifact verification. | B | Yes |
| P-QUANTCODE | QuantCode-Bench, arXiv:2604.15151 | Benchmark | Evaluates executable algorithmic trading strategy generation from natural language. | QSGA differs by making a bounded strategy IR auditable before execution. | B | Yes |
| P-SYSTRADE | SysTradeBench, arXiv:2604.04812 | Benchmark/System | Evaluates iterative build-test-patch strategy-to-code systems with drift-aware diagnostics. | Supports the auditability and traceability motivation. | B | Yes |
| P-MARKETBENCH | Market-Bench, arXiv:2512.12264 | Benchmark | Evaluates LLMs on quantitative trading and market dynamics tasks. | Supports the claim that executable market artifacts need behavioral validation. | B | Yes |
| P-QUANTEVAL | QuantEval, arXiv:2601.08689 | Benchmark | Covers financial quantitative tasks including strategy coding. | Positions QSGA as narrower and mechanism-specific. | B | Yes |
| P-OQL | Natural Language to Executable Option Strategies, arXiv:2603.16434 | Method/System | Uses a domain IR for option-strategy semantic parsing and deterministic execution. | Closest architectural analog to QYIR but in options. | B | Yes |
| P-FINHALLUCINATION | Deficiency of Large Language Models in Finance, arXiv:2311.15548 | Evaluation/Safety | Empirically studies hallucination deficiencies in financial LLM tasks. | Motivates conservative financial reliability and safety claims. | B | Yes |
| P-CNFINBENCH | CNFinBench, arXiv:2512.09506 | Benchmark/Safety | Evaluates finance expertise, autonomy, integrity, safety, and compliance. | Motivates scoped financial safety and refusal boundaries. | B | Yes |
| P-FINMEM | FinMem, arXiv:2311.13743 | System/Agent | Layered-memory LLM trading agent. | Related trading-agent context; QSGA focuses on verifiable strategy artifacts. | B | Yes |

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

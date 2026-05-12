# RESEARCH_PLAN.md

---

## TLDR_STATE_FOR_AGENT

研究目标：

- 将 QSGA/QYIR 从 IR verification paper 推进为 verification-guided NL-to-QYIR construction + verification paper。

范围边界：

- In scope：规则型、日频、股票/ETF/指数策略的自然语言到 QYIR 构造、验证、修复和审计。
- Out of scope：高频交易、期权/衍生品、多资产组合优化、真实交易收益保证、自动投稿。

当前阶段：

- S5 实验设计前置实现 / S6 live diagnostic analysis

关键 claim：

- 已验证 single-model diagnostic：official `deepseek-v4-flash` Route B slot-builder 在 QSI-Bench v1 上达到 construction_success 0.364、E2E 0.475。
- 仍待验证：第二个 full 80-case live model、reviewer gate、CCF-B 强度主张。

下一步：

- 执行 TASK-20260512-012 起草 QYIR market operand 设计决策，并对 current Route B draft 做 reviewer gate。

---

## Research Goal

QSGA Route B aims to build a verification-guided natural-language-to-QYIR construction framework for bounded rule-based quantitative strategies. The immediate goal is to replace fragile prompt-only QYIR generation with structured slot extraction, deterministic QYIR building, canonicalization, validator-feedback retry, and the existing QSGA verification/repair backend.

---

## Scope

### In Scope

- Natural-language-to-QYIR construction for bounded rule-based quantitative strategies.
- QYIR schema/reference/type/risk validation.
- Failure taxonomy and failure reduction analysis.
- Controlled live LLM evaluation after protocol and cost boundaries are recorded.

### Out of Scope

- Claims of guaranteed safe trading or profitable trading.
- High-frequency, derivative, portfolio-optimization, or fully autonomous trading-agent settings.
- Unapproved large-scale paid API experiments.
- Automatic paper submission or public release.

---

## Research Questions

1. Can constrained natural-language-to-QYIR construction improve structural validity, semantic consistency, and executable construction success?
2. Which components contribute most: structured slots, canonicalization, validation-feedback retry, deterministic builder, and QSGA backend repair?
3. Under scoped, model-specific diagnostics, how does Route B compare with prompt-only QYIR and direct-code baselines, and which differences remain non-comparable because model/provider settings differ?

---

## Expected Contributions

1. QYIR as a constrained and verifiable strategy IR.
2. A verification-guided NL-to-QYIR construction pipeline.
3. An end-to-end QSGA verification and repair backend.
4. QSI-Bench-based evaluation against raw QYIR, direct code, JSON schema, and ablated variants.
5. Failure-reduction analysis across parse, schema, alias, type, semantic, risk, compile, and execution failures.

---

## Success Criteria

1. All performance claims are backed by recorded experiment outputs and reproducible commands.
2. Route B modules have focused tests before live API evaluation.
3. Live API experiments record model, prompt, sample count, token usage, latency, raw outputs, and failures.
4. Manuscript text uses conservative language: official DeepSeek numbers can be reported, but only as single-model diagnostic evidence.

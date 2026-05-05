# Literature Verification Agent Report

## Summary

Current related work is not yet sufficient for a CCF C submission. The draft covers general LLM code generation, execution feedback, constrained decoding, tool agents, and broad financial LLM/trading-agent work, but it under-covers the most direct reviewer-expected line: natural-language-to-executable trading strategy generation and benchmarked strategy-to-code systems.

The strongest positioning gap is that QSGA currently reads as if the trading-strategy reliability problem is derived mainly from general code-generation literature. Recent direct work already frames this as a domain-specific trading-code benchmark problem: QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, and the OQL option-strategy paper are much closer comparators than FinGPT/FinRobot/TradingAgents. These should be cited before or alongside broad financial-agent papers.

All external literature items below are Level B unless marked otherwise: I verified title/abstract/metadata and source URLs, but did not perform PDF-level page/claim verification. Do not add DOI, page numbers, venue status, or strong comparative claims until PDF-level checks are complete.

## Missing Direct Work

1. Natural-language-to-executable algorithmic trading strategy generation benchmarks.
   - Must add: QuantCode-Bench: A Benchmark for Evaluating the Ability of Large Language Models to Generate Executable Algorithmic Trading Strategies, arXiv:2604.15151, https://arxiv.org/abs/2604.15151, Level B.
   - Why it matters: It directly evaluates LLMs generating Backtrader strategies from textual strategy descriptions, with checks for syntax, backtest execution, trade generation, semantic alignment, and iterative repair. This is the closest direct comparator to QSGA.
   - Draft positioning: QSGA differs by using QYIR as an explicit bounded IR and by treating safe rejection/risk constraints as part of the pipeline; QSI-Bench is smaller and deterministic, so do not claim superiority.

2. Build-test-patch and audit-oriented trading strategy systems.
   - Must add: SysTradeBench: An Iterative Build-Test-Patch Benchmark for Strategy-to-Code Trading Systems with Drift-Aware Diagnostics, arXiv:2604.04812, https://arxiv.org/abs/2604.04812, Level B.
   - Why it matters: It covers iterative LLM-generated trading systems with audit logs, determinism, anti-leakage checks, rule drift diagnostics, risk discipline, and out-of-sample indicators. This overlaps heavily with QSGA's verification-guided repair and reliability framing.
   - Draft positioning: QSGA can be positioned as a compact IR-first prototype, while SysTradeBench is a broader benchmark/harness for strategy-to-code systems.

3. Trading backtester construction from natural-language market assumptions.
   - Must add: Market-Bench: Evaluating Large Language Models on Introductory Quantitative Trading and Market Dynamics, arXiv:2512.12264, https://arxiv.org/abs/2512.12264, Level B.
   - Why it matters: It asks LLMs to construct executable backtesters from natural-language strategy descriptions and checks P&L, drawdown, and position paths against reference implementations.
   - Draft positioning: This supports the claim that execution alone is insufficient and numerical/path correctness matters, but QSGA's current evaluation does not match Market-Bench's reference-path accuracy.

4. Quantitative-finance LLM benchmarks with strategy coding.
   - Must add: QuantEval: A Benchmark for Financial Quantitative Tasks in Large Language Models, arXiv:2601.08689, https://arxiv.org/abs/2601.08689, Level B.
   - Why it matters: It includes quantitative strategy coding in a finance benchmark, making it more directly relevant than generic FinQA-style finance reasoning alone.
   - Draft positioning: Use it as evidence that finance LLM evaluation is moving toward executable strategy tasks; avoid saying QSGA is more comprehensive.

5. Domain-specific intermediate representations for trading intents.
   - Must add: From Natural Language to Executable Option Strategies via Large Language Models, arXiv:2603.16434, https://arxiv.org/abs/2603.16434, Level B.
   - Why it matters: It introduces Option Query Language as a domain-specific intermediate representation for option-market strategies under grammar rules, using LLMs as semantic parsers rather than free-form programmers. This is very close to QYIR's role.
   - Draft positioning: QYIR is for bounded daily rule-based stock/ETF strategies; OQL is for options. The paper should acknowledge this as direct IR/DSL-adjacent work.

6. Financial LLM safety, hallucination, and advice risk.
   - Should add selectively: Deficiency of Large Language Models in Finance: An Empirical Examination of Hallucination, arXiv:2311.15548, https://arxiv.org/abs/2311.15548, Level B; CNFinBench: A Benchmark for Safety and Compliance of Large Language Models in Finance, arXiv:2512.09506, https://arxiv.org/abs/2512.09506, Level B; Biased echoes: Large language models reinforce investment biases and increase portfolio risks of private investors, PLOS One, https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0325459, Level B.
   - Why it matters: QSGA makes novice-facing risk and safe-rejection claims. A reviewer may ask why unsafe financial advice is in scope but finance safety/compliance literature is absent.
   - Draft positioning: Use these only to motivate risk-aware boundaries, not to claim QSGA solves financial advice safety.

7. Classical trading strategy generation, backtesting, and DSL/program-synthesis baselines.
   - Current gap: I did not find a clean verified academic citation in this pass that should be added by title without PDF checking. This category remains Level B/pending search.
   - Why it matters: A CCF C reviewer may expect historical context on algorithmic trading strategy optimization, genetic programming strategy generation, and backtesting systems before LLMs.
   - Required action: Do a second pass for peer-reviewed or canonical sources on genetic programming for trading-rule discovery, backtesting methodology, and strategy DSLs. Do not cite product pages such as QuantCode.co as academic evidence.

## Citation Risk Table

| Risk | Current State | Why Reviewer May Object | Required Handling |
|---|---|---|---|
| Direct related work omission | Section 10 lacks QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, and OQL. | These are closer to QSGA than generic code-generation and financial-agent papers. | Add a dedicated subsection: "LLM-Based Trading Strategy Generation and Benchmarks". |
| Over-broad novelty impression | Draft says QSGA formulates novice-oriented quantitative strategy generation as verifiable/risk-aware synthesis. | SysTradeBench and OQL also use build-test-patch, diagnostics, or domain IR ideas. | Downgrade to "we instantiate an IR-first framework for a bounded rule-based strategy space". |
| Weak financial LLM coverage | P10-P12 are broad financial LLM/agent citations. | They do not directly validate natural-language-to-strategy generation. | Keep them as adjacent work only; add direct strategy-code benchmarks as primary comparators. |
| PICARD comparison too narrow | Current text says constrained decoding controls syntax but not QSGA's semantics/risk auditing. | OQL is a domain grammar/IR for executable option strategies, closer than PICARD. | Compare QYIR against both constrained decoding and domain-specific trading IR/DSL work. |
| Tool-agent comparison too generic | ReAct/Toolformer are generic; LEVER/CodeT are generic code feedback. | SysTradeBench directly uses iterative build-test-patch for trading systems. | Add SysTradeBench before generic execution-feedback citations in Section 10.2 or a new 10.3. |
| Benchmark claim vulnerability | QSI-Bench v1 has 80 Chinese requests and deterministic baselines. | QuantCode-Bench has 400 tasks; Market-Bench and QuantEval use executable finance tasks; SysTradeBench evaluates many models. | State QSI-Bench is a small prototype benchmark, not a competitive benchmark against recent trading-code suites. |
| Risk auditing claim vulnerability | Draft reports risk violation 0.000. | This can be misread as trading safety or robust risk control. | Keep "measured risk violations in current deterministic setup"; never write "safe strategy" or "risk-free". |
| Repair success claim vulnerability | Repair success is 1.000 in deterministic prototype. | It may reflect hand-designed failure modes rather than arbitrary LLM repair ability. | Say "localized repair succeeds for current controlled repairable failures". |
| Safe rejection claim vulnerability | Shared deterministic unsafe detector gives high rejection across methods. | It does not prove robust financial safety/compliance. | Keep the existing limitation and cite finance hallucination/advice-risk/safety benchmark work. |
| Missing PDF-level verification | Matrix marks all papers Level B. | Reviewers may challenge exact claims if citations are metadata-only. | Upgrade must-cite papers to Level A before submission by reading PDFs and recording claim locations. |

## Required Draft Edits

1. Add a new Related Work subsection after "Execution Feedback and Repair":

   Suggested title: "LLM-Based Trading Strategy Generation and Benchmarks".

   Must cover: QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval. The subsection should state that recent work evaluates LLMs on executable trading code/backtest construction and exposes failures in semantic alignment, risk reasoning, numerical correctness, API use, drift, and repair. Then position QSGA as an IR-first, bounded, deterministic prototype with safe rejection and risk auditing.

2. Add a new Related Work paragraph under constrained decoding / structured outputs:

   Must cover: OQL option-strategy paper. The paragraph should say QYIR is related to domain-specific IR/DSL approaches that constrain financial strategy semantics, but QYIR targets daily rule-based stock/ETF strategies rather than options.

3. Rewrite the current "Financial LLMs and Trading Agents" subsection.

   Keep FinGPT, FinRobot, TradingAgents as adjacent. Add FinMem if the authors want broader LLM trading-agent coverage: FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design, arXiv:2311.13743, https://arxiv.org/abs/2311.13743, Level B. Make clear these works usually focus on decision-making/trading agents or financial-domain LLM capability, not novice natural-language strategy construction through a verifiable IR.

4. Add finance safety/compliance motivation where safe rejection is introduced.

   Use only conservative language: "Prior work reports hallucination, advice-risk, or safety/compliance concerns in financial LLM settings." Do not imply those works evaluate QSGA.

5. Downgrade or sharpen the following claims in the draft:

   - "We formulate novice-oriented quantitative strategy generation..." -> "We instantiate and evaluate a bounded formulation of novice-oriented rule-based strategy generation..."
   - "QSGA improves reliability" -> "QSGA improves measured reliability in the current deterministic prototype and supported rule space..."
   - "risk-aware behavior" -> "measured risk-constraint satisfaction under historical sample data..."
   - "safe rejection is part of reliability" -> "safe rejection is treated as one reliability dimension in this prototype; robust safety/compliance remains future work..."
   - "repair is effective" -> "repair is effective for the controlled error classes represented in QYIR v1..."

6. Update citation_and_claim_matrix.md later, but not by this subagent unless authorized.

   Add new paper IDs for QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, OQL, and selected finance safety papers. Mark all as Level B until PDF-level verification. Add claim rows only for claims supportable from abstract/metadata, and label human review pending.

7. Do not add DOI/page/venue fields for the new papers until verified.

   Several candidates are arXiv preprints or web-indexed records. Adding invented DOI, page, or formal venue metadata would create an avoidable citation defect.

## Actual Files Read

- `E:\QSGA\docs\paper\qsga_ccf_c_draft.md`
- `E:\QSGA\docs\paper\citation_and_claim_matrix.md`
- `E:\QSGA\docs\ai-research-assistant\PAPER_MATRIX.md`

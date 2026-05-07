# 文献矩阵模板

## 1. 检索记录

| Query ID | 检索式 | 来源 | 日期 | 结果数 | 备注 |
|---|---|---|---|---:|---|
| Q-20260505-001 | arXiv Codex / AlphaCode / program synthesis with large language models | web search | 2026-05-05 | multiple | code generation and program synthesis background |
| Q-20260505-002 | arXiv constrained decoding structured output PICARD | web search | 2026-05-05 | multiple | constrained decoding related work |
| Q-20260505-003 | arXiv ReAct Toolformer Self-Refine LEVER CodeT | web search | 2026-05-05 | multiple | tool-use, repair, and execution-feedback related work |
| Q-20260505-004 | arXiv FinGPT FinRobot TradingAgents financial LLM trading | web search | 2026-05-05 | multiple | financial LLM and trading-agent background |
| Q-20260505-005 | QuantCode-Bench SysTradeBench Market-Bench QuantEval OQL option strategy | web search + subagent literature review | 2026-05-05 | multiple | direct trading strategy generation and benchmark comparators |
| Q-20260505-006 | financial LLM hallucination safety compliance CNFinBench FinMem | web search + subagent literature review | 2026-05-05 | multiple | financial safety and adjacent trading-agent context |

## 2. 文献矩阵

| Paper ID | 标题 | 作者 | 年份 | 来源 | DOI/arXiv/URL | 分类 | 核验等级 | 用途 | 排除理由 |
|---|---|---|---:|---|---|---|---|---|---|
| P01 | Evaluating Large Language Models Trained on Code | Chen et al. | 2021 | arXiv | https://arxiv.org/abs/2107.03374 | Background | B | LLM code generation |  |
| P02 | Program Synthesis with Large Language Models | Austin et al. | 2021 | arXiv | https://arxiv.org/abs/2108.07732 | Related | B | program synthesis framing |  |
| P03 | Competition-Level Code Generation with AlphaCode | Li et al. | 2022 | arXiv | https://arxiv.org/abs/2203.07814 | Background | B | code generation progress |  |
| P04 | PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models | Scholak et al. | 2021 | arXiv | https://arxiv.org/abs/2109.05093 | Related | B | constrained decoding |  |
| P05 | ReAct: Synergizing Reasoning and Acting in Language Models | Yao et al. | 2022 | arXiv | https://arxiv.org/abs/2210.03629 | Related | B | tool-using agents |  |
| P06 | Toolformer: Language Models Can Teach Themselves to Use Tools | Schick et al. | 2023 | arXiv | https://arxiv.org/abs/2302.04761 | Related | B | tool use |  |
| P07 | Self-Refine: Iterative Refinement with Self-Feedback | Madaan et al. | 2023 | arXiv | https://arxiv.org/abs/2303.17651 | Related | B | iterative refinement |  |
| P08 | LEVER: Learning to Verify Language-to-Code Generation with Execution | Ni et al. | 2023 | arXiv | https://arxiv.org/abs/2302.08468 | Related | B | execution verification |  |
| P09 | CodeT: Code Generation with Generated Tests | Chen et al. | 2022 | arXiv | https://arxiv.org/abs/2207.10397 | Related | B | generated tests and verification |  |
| P10 | FinGPT: Open-Source Financial Large Language Models | Liu et al. | 2023 | arXiv | https://arxiv.org/abs/2306.06031 | Background | B | financial LLM background |  |
| P11 | FinRobot: An Open-Source AI Agent Platform for Financial Applications using Large Language Models | Yang et al. | 2024 | arXiv | https://arxiv.org/abs/2405.14767 | Background | B | financial agent systems |  |
| P12 | TradingAgents: Multi-Agents LLM Financial Trading Framework | Liu et al. | 2024 | arXiv | https://arxiv.org/abs/2412.20138 | Background | B | trading-agent systems |  |
| P13 | QuantCode-Bench: A Benchmark for Evaluating the Ability of Large Language Models to Generate Executable Algorithmic Trading Strategies | Khoroshilov et al. | 2026 | arXiv | https://arxiv.org/abs/2604.15151 | Core / Related | B | direct comparator for executable trading strategy generation |  |
| P14 | SysTradeBench: An Iterative Build-Test-Patch Benchmark for Strategy-to-Code Trading Systems with Drift-Aware Diagnostics | Cao et al. | 2026 | arXiv | https://arxiv.org/abs/2604.04812 | Core / Related | B | direct comparator for iterative trading strategy systems |  |
| P15 | Market-Bench: Evaluating Large Language Models on Introductory Quantitative Trading and Market Dynamics | Srivastava et al. | 2025 | arXiv | https://arxiv.org/abs/2512.12264 | Related | B | executable backtester and market-dynamics benchmark |  |
| P16 | QuantEval: A Benchmark for Financial Quantitative Tasks in Large Language Models | Kang et al. | 2026 | arXiv | https://arxiv.org/abs/2601.08689 | Related | B | quantitative finance benchmark including strategy coding |  |
| P17 | From Natural Language to Executable Option Strategies via Large Language Models | Luo et al. | 2026 | arXiv | https://arxiv.org/abs/2603.16434 | Core / Related | B | direct IR/DSL-adjacent comparator |  |
| P18 | Deficiency of Large Language Models in Finance: An Empirical Examination of Hallucination | Kang and Liu | 2023 | arXiv | https://arxiv.org/abs/2311.15548 | Background | B | financial hallucination motivation |  |
| P19 | Beyond Knowledge to Agency: Evaluating Expertise, Autonomy, and Integrity in Finance with CNFinBench | Ding et al. | 2025 | arXiv | https://arxiv.org/abs/2512.09506 | Background | B | finance safety/compliance benchmark |  |
| P20 | FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design | Yu et al. | 2023 | arXiv | https://arxiv.org/abs/2311.13743 | Background | B | financial trading-agent background |  |

## 3. 论文卡片模板

```markdown
### PAPER-NNN

Title:
Authors:
Year:
Venue:
DOI/arXiv/URL:
Verification level: A / B / C / D

Research question:

Method:

Dataset:

Metrics:

Main results:

Limitations:

Reproducibility:

Relation to this research:

Claims supported:
```

## 4. Claim-Evidence Matrix

| Claim ID | Claim | Paper ID | Evidence location | Evidence type | Confidence | Human review |
|---|---|---|---|---|---|---|
| RW-001 | LLMs have strong code-generation capability but need reliability checks for correctness-sensitive tasks. | P01, P02, P03 | metadata-level only | paper metadata / abstract | 中 | pending PDF check |
| RW-002 | Constrained decoding can enforce structured generation but does not by itself encode QSGA's domain-specific risk and compilation semantics. | P04 | metadata-level + QYIR design | paper metadata / local design | 中 | pending PDF check |
| RW-003 | Tool-using LLM agents motivate external tool interaction but do not remove the need for a stable domain IR. | P05, P06 | metadata-level + QSGA design | paper metadata / local design | 中 | pending PDF check |
| RW-004 | Financial LLM and trading-agent work is adjacent but QSGA focuses on reliable rule-based strategy construction, not market prediction or profit optimization. | P10, P11, P12 | metadata-level + QSGA scope | paper metadata / local design | 中 | pending PDF check |
| EXP-001 | Main no-oracle QSGA achieves construction success 0.8364 and E2E success 0.8875 in deterministic prototype evaluation. | local | `experiments/results/no_oracle_metrics.csv` | 实验日志 | 高 | pending final conclusion approval |
| RW-005 | Direct LLM trading-code benchmarks are closer comparators and must be acknowledged before broad financial-agent work. | P13, P14, P15, P16 | metadata-level + subagent literature review | paper metadata / abstract | 中 | pending PDF check |
| RW-006 | QYIR is related to domain IR/DSL work for executable financial strategies. | P17 | metadata-level + QYIR design | paper metadata / local design | 中 | pending PDF check |
| RW-007 | Financial hallucination and compliance work motivates safe rejection but does not validate QSGA safety. | P18, P19 | metadata-level only | paper metadata / abstract | 中 | pending PDF check |
| EXP-002 | Oracle-slot QSGA is an upper-bound verification-chain evaluation, reaching construction success 0.9455 and E2E success 0.9625. | local | `experiments/results/baseline_metrics.csv`; `experiments/baselines.py` | 实验日志 / 代码证据 | 高 | pending final conclusion approval |

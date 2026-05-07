# PDF-Verified Related Work Scaffold

Task ID: LIT-20260505-PDF-AUDIT-SCAFFOLD  
Status: PDF-level scaffold for five priority papers  
Date: 2026-05-05  

This file records a conservative related-work scaffold for the five priority comparator papers in `citation_and_claim_matrix.md`: QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, and the OQL option-strategy paper. The goal is not to replace the full literature review, but to provide PDF-verified prose that can be inserted into or used to audit Section 10 of `qsga_ccf_c_draft.md`.

Verification convention: "PDF-verified" means that the claim was checked against the arXiv PDF text available in this environment. Citations use arXiv URLs plus section, page, and line locations from the extracted PDF text where available. Page numbers below refer to the PDF extraction page labels, starting at P0.

## Priority Source Map

| Matrix ID | Paper | URL | Verified Scope |
|---|---|---|---|
| P13 | QuantCode-Bench: A Benchmark for Evaluating the Ability of Large Language Models to Generate Executable Algorithmic Trading Strategies | https://arxiv.org/pdf/2604.15151 | Abstract; Sections 2 and 3; Tables 1-5; error-analysis framing |
| P14 | SysTradeBench: An Iterative Build-Test-Patch Benchmark for Strategy-to-Code Trading Systems with Drift-Aware Diagnostics | https://arxiv.org/pdf/2604.04812 | Abstract; contribution list; capability table; evaluation dimensions D1-D4 |
| P15 | Market-Bench: Evaluating Large Language Models on Introductory Quantitative Trading and Market Dynamics | https://arxiv.org/pdf/2512.12264 | Abstract; strategy descriptions; evaluation structure and metrics |
| P16 | QuantEval: A Benchmark for Financial Quantitative Tasks in Large Language Models | https://arxiv.org/pdf/2601.08689 | Abstract; task taxonomy; dataset construction; main evaluation table; benchmark comparison |
| P17 | From Natural Language to Executable Option Strategies via Large Language Models | https://arxiv.org/pdf/2603.16434 | Abstract; methodology; OQL design principles; neuro-symbolic execution flow; evaluation framing |

## Metadata Refresh on 2026-05-07

The priority related-work metadata was rechecked against arXiv abstract pages or arXiv-indexed metadata on 2026-05-07 before this revision:

| Matrix ID | Current metadata status |
|---|---|
| P13 | arXiv:2604.15151 confirms the title `QuantCode-Bench: A Benchmark for Evaluating the Ability of Large Language Models to Generate Executable Algorithmic Trading Strategies`; authors: Aleksandr Khoroshilov, Kirill Ponomarev, Dmitrii Pilipenko, Evgeny Burnaev. |
| P14 | arXiv:2604.04812 confirms the title `SysTradeBench: An Iterative Build-Test-Patch Benchmark for Strategy-to-Code Trading Systems with Drift-Aware Diagnostics`; authors: Yuchen Cao, Hanlin Zhang, Jacky Wai Keung, Yang Chen, Linqi Song. |
| P15 | arXiv:2512.12264 confirms the title `Market-Bench: Evaluating Large Language Models on Introductory Quantitative Trading and Market Dynamics`; authors: Sanjay Srivastava, Stevan Taskov, Alex Stoyanov, Harold Stern, Igor Halperin. |
| P16 | arXiv:2601.08689 confirms the title `QuantEval: A Benchmark for Financial Quantitative Tasks in Large Language Models`; authors: Bohan Kang, Dingli Yu, Yilong Xue, Mingxuan Wang, Ruiyi Zhang, Yilun Han, Yunji Li, Junda Wu, Musen Wen, Zhen Tan, Wen Wang, Ramesh Harjani, Jan Wiesemann, Huan Liu. |
| P17 | arXiv:2603.16434 confirms the title `From Natural Language to Executable Option Strategies via Large Language Models`; authors: Jueping Luo, Arian Neshati, Nan Zhang, Lisong Qiu. |

Remaining bibliography risk: these papers are recent arXiv preprints, so final BibTeX entries should still be refreshed immediately before submission.

## Verified Comparator Prose

Recent trading-specific benchmarks evaluate LLMs beyond general code-generation tasks. QuantCode-Bench evaluates whether models can generate executable Backtrader strategies from English textual descriptions. Its dataset contains 400 tasks collected from Reddit, TradingView, StackExchange, GitHub, and synthetic sources, and its evaluation pipeline checks syntactic correctness, backtest execution, trade generation, and semantic alignment with the task description through an LLM judge. The paper explicitly argues that successful compilation is insufficient for trading strategies because executable code can still fail to trade or fail to match the intended strategy. This makes QuantCode-Bench a close comparator for QSGA's staged verification framing, although QSGA evaluates a smaller, Chinese, rule-based IR-first prototype rather than broad Backtrader code generation. Evidence: QuantCode-Bench abstract and Section 2.1-2.2, PDF P0-P3, lines 7-27 and 94-133; Section 3.1, PDF P3, lines 140-170.

QuantCode-Bench also supports the paper's caution that syntax validity is not the core bottleneck in this domain. In its single-turn analysis, the authors report that failures concentrate after compilation, especially in backtest failure and no-trade cases, and conclude that the hard part is operationalizing trading logic in a domain-specific execution environment rather than merely producing syntactically valid Python. This is directly relevant to QSGA's claim that schema validity or code generation alone is not enough for reliable strategy construction. Evidence: QuantCode-Bench Section 5.1, PDF P5-P6, lines 244-261.

SysTradeBench evaluates LLM-generated trading systems as governed, auditable software rather than as one-shot snippets or profitability claims. The benchmark uses a standardized Base Strategy Doc with frozen semantics and requires models to produce a strategy card, executable code, and mandatory audit logs. Its harness checks determinism, leakage, rule drift, and evidence-driven patches, then reports multi-dimensional scorecards for specification fidelity, risk discipline, reliability/auditability, and out-of-sample robustness indicators. QSGA is much smaller in scale and does not implement SysTradeBench's full governance layer, but both systems share the view that strategy generation requires staged evidence, auditability, and constraints. Evidence: SysTradeBench abstract, PDF P0, lines 22-38; contribution list and capability table, PDF P1, lines 99-133; output contract and patching rules, PDF P4, lines 290-302.

SysTradeBench should not be cited as establishing profitability or as a direct baseline for QSGA's 80-case benchmark. The paper itself frames its D4 component as robustness indicators rather than definitive profitability claims and defers full transaction-cost and complete out-of-sample validation because of computational constraints. This supports a conservative comparison: QSGA can cite SysTradeBench for governed build-test-patch evaluation and drift-aware diagnostics, not for final trading performance. Evidence: SysTradeBench D3-D4 definitions, PDF P4, lines 324-349.

Market-Bench evaluates LLMs on introductory quantitative trading and market-dynamics tasks by asking models to construct executable backtesters from natural-language strategy descriptions and market assumptions. Its three canonical strategies are scheduled market-order execution on MSFT, pairs mean-reversion on KO/PEP, and options delta hedging on MSFT. The benchmark evaluates whether generated backtests execute and how closely model-generated P&L, drawdown, and position paths match reference implementations. This paper is close to QSGA because it separates executability from numerical fidelity; however, Market-Bench focuses on reconstructing backtester logic and market-state accounting rather than on a domain IR for novice strategy specification. Evidence: Market-Bench abstract, PDF P0, lines 5-22; strategy descriptions, PDF P2, lines 90-130; evaluation structure, PDF P3-P4, lines 138-191.

QuantEval is broader than QSGA but contains an important strategy-coding component. It evaluates financial quantitative tasks across knowledge-based QA, quantitative mathematical reasoning, and quantitative strategy coding, and it uses an integrated CTA-style backtesting framework to execute model-generated strategies and compare performance metrics. The authors report 1,575 curated samples and emphasize gaps between LLMs and human experts, especially in reasoning and strategy coding. For QSGA, QuantEval is best cited as evidence that quantitative finance evaluation increasingly combines knowledge, reasoning, and executable strategy coding under realistic constraints. It should not be cited as an IR or repair benchmark. Evidence: QuantEval abstract, PDF P0, lines 11-31; task taxonomy and sample count, PDF P1, lines 120-135; strategy coding data construction, PDF P3, lines 271-282; main evaluation table description, PDF P5, lines 428-444.

The OQL option-strategy paper is the strongest PDF-verified analog for QYIR's intermediate-representation motivation. It introduces Option Query Language as a domain-specific intermediate representation that converts natural-language option-trading intent into structured symbolic queries, then validates and executes those queries deterministically against option-chain data. The paper decomposes generation into semantic parsing by an LLM and deterministic compilation/execution by an engine, explicitly arguing that this separation improves robustness, interpretability, and execution reliability. QYIR should be positioned as a similar neuro-symbolic design pattern applied to daily stock/ETF rule-based strategies, not as an options system. Evidence: OQL abstract, PDF P0, lines 6-18; methodology and problem formulation, PDF P3, lines 229-250.

The OQL details also clarify the boundary of the analogy. OQL handles option-chain contracts, strikes, maturities, Greeks, multi-leg strategy roles, leg-level constraints, strategy-level constraints, and soft numeric matching. QYIR instead handles a bounded daily stock/ETF strategy space with indicators, entry/exit rules, and risk controls. The correct related-work claim is therefore that QYIR follows a comparable IR-plus-deterministic-execution pattern, while differing in asset class, representation, and execution semantics. Evidence: OQL option-chain representation, PDF P2-P3, lines 174-228; OQL design principles, PDF P3-P4, lines 252-277; deterministic execution flow, PDF P4-P5, lines 354-368.

## Drop-In Replacement for Section 10.3

Several recent benchmarks directly evaluate LLMs on executable trading or quantitative-finance coding tasks. QuantCode-Bench evaluates Backtrader strategy generation from English textual descriptions through a staged pipeline that checks syntax, backtest execution, trade occurrence, and semantic alignment. Market-Bench asks models to build executable backtesters for a small set of canonical market-dynamics tasks and evaluates both executability and numerical agreement with reference P&L, drawdown, and position paths. QuantEval is broader, covering financial QA, quantitative reasoning, and strategy coding, but its strategy-coding component also executes model-generated strategies in a CTA-style backtesting framework. These works are closer to QSGA than broad financial-LLM benchmarks because they evaluate executable quantitative artifacts rather than only financial knowledge.

QSGA differs from these benchmarks in scope and mechanism. It is not a large model leaderboard and does not claim broad strategy-generation superiority. Instead, it studies whether a compact strategy intermediate representation can make a bounded rule-based strategy-construction pipeline more verifiable, repairable, and boundary-aware. QuantCode-Bench and Market-Bench highlight that executability alone does not establish semantic or numerical correctness; SysTradeBench further shows that strategy-to-code systems can be evaluated as auditable software with drift, determinism, risk, and traceability checks. QSGA follows the same reliability-oriented direction but evaluates a smaller IR-first prototype.

## Drop-In Replacement for Section 10.4

QYIR is related to domain-specific financial intermediate representations and DSLs. The closest verified analog in the current priority set is the OQL option-strategy work, which introduces Option Query Language as a structured symbolic representation between natural-language option intent and deterministic execution over option-chain data. OQL uses an LLM as a semantic parser and then validates and executes the resulting query with a deterministic engine. This supports QSGA's central design intuition: the LLM should not be the only place where financial semantics, constraints, and execution are handled.

The analogy should remain scoped. OQL targets option strategies, where the representation must reason over option chains, Greeks, strikes, maturities, multi-leg roles, and aggregate option-strategy constraints. QYIR targets daily stock/ETF rule-based strategies with indicators, entry and exit rules, deterministic compilation, and risk-control slots. Thus, OQL supports the broader neuro-symbolic IR argument, but it is not evidence that QYIR handles options or that QSGA covers arbitrary financial strategies.

## Claims Now Safe to Use

| Claim | Status | Evidence |
|---|---|---|
| QuantCode-Bench evaluates Backtrader strategy generation through syntax, backtest, trade, and LLM-judge semantic checks. | PDF-verified | https://arxiv.org/pdf/2604.15151, Section 3.1, PDF P3, lines 140-170 |
| QuantCode-Bench contains 400 English tasks from Reddit, TradingView, StackExchange, GitHub, and synthetic sources. | PDF-verified | https://arxiv.org/pdf/2604.15151, Section 2.2, PDF P2-P3, lines 107-133 |
| QuantCode-Bench finds that late-stage failures, not syntax alone, are central in trading strategy generation. | PDF-verified | https://arxiv.org/pdf/2604.15151, Section 5.1, PDF P5-P6, lines 244-261 |
| SysTradeBench evaluates strategy-to-code outputs as governed, auditable software with frozen semantics, audit logs, determinism, leakage, drift, and scorecard dimensions. | PDF-verified | https://arxiv.org/pdf/2604.04812, Abstract and Sections 4.4.1-4.4.4, PDF P0-P4, lines 22-38 and 303-349 |
| Market-Bench evaluates executable backtesters for three canonical quantitative trading tasks and compares generated metrics to references. | PDF-verified | https://arxiv.org/pdf/2512.12264, Abstract and Sections 3.2-4.3, PDF P0-P4, lines 5-22 and 90-191 |
| QuantEval includes knowledge QA, quantitative reasoning, and strategy coding, with a CTA-style backtesting framework for generated strategies. | PDF-verified | https://arxiv.org/pdf/2601.08689, Abstract and Section 1, PDF P0-P1, lines 11-31 and 120-135 |
| OQL is a domain-specific intermediate representation for option strategies, parsed from natural language by an LLM and deterministically validated/executed by an engine. | PDF-verified | https://arxiv.org/pdf/2603.16434, Abstract and Section 4, PDF P0-P5, lines 6-18 and 229-368 |

## Claims That Must Remain Scoped

QSGA should not claim to outperform QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, or OQL. The verified sources do not provide a shared dataset, task format, language, or metric basis for such a comparison.

QSGA should not claim to support options because OQL supports options. The verified relationship is architectural: both use an intermediate representation and deterministic execution/validation; their domains and representations are different.

QSGA should not use SysTradeBench as evidence for profitability. The verified source explicitly frames part of its out-of-sample evaluation as robustness indicators rather than definitive profitability claims.

QSGA should not cite Market-Bench or QuantEval as evidence for safe rejection, clarification behavior, or novice-oriented boundary control. Those are QSGA-specific design/evaluation claims and require local evidence.

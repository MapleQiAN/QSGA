# QSGA Citation and Claim Matrix

Status: draft  
Date: 2026-05-05  
Purpose: keep paper claims traceable to sources or local experiment artifacts.

Precision note: this matrix keeps exact CSV rates where useful. The paper draft and reproducibility package display most metrics to three decimal places.

## Literature Matrix

| Paper ID | Title | Year | Source | Verification Level | Use in Paper |
|---|---|---:|---|---|---|
| P01 | Evaluating Large Language Models Trained on Code | 2021 | https://arxiv.org/abs/2107.03374 | B | LLM code generation background |
| P02 | Program Synthesis with Large Language Models | 2021 | https://arxiv.org/abs/2108.07732 | B | program synthesis framing |
| P03 | Competition-Level Code Generation with AlphaCode | 2022 | https://arxiv.org/abs/2203.07814 | B | code generation progress |
| P04 | PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models | 2021 | https://arxiv.org/abs/2109.05093 | B | constrained decoding related work |
| P05 | ReAct: Synergizing Reasoning and Acting in Language Models | 2022 | https://arxiv.org/abs/2210.03629 | B | tool-using agent background |
| P06 | Toolformer: Language Models Can Teach Themselves to Use Tools | 2023 | https://arxiv.org/abs/2302.04761 | B | tool-use related work |
| P07 | Self-Refine: Iterative Refinement with Self-Feedback | 2023 | https://arxiv.org/abs/2303.17651 | B | iterative repair background |
| P08 | LEVER: Learning to Verify Language-to-Code Generation with Execution | 2023 | https://arxiv.org/abs/2302.08468 | B | execution verification related work |
| P09 | CodeT: Code Generation with Generated Tests | 2022 | https://arxiv.org/abs/2207.10397 | B | generated tests and verification |
| P10 | FinGPT: Open-Source Financial Large Language Models | 2023 | https://arxiv.org/abs/2306.06031 | B | financial LLM background |
| P11 | FinRobot: An Open-Source AI Agent Platform for Financial Applications using Large Language Models | 2024 | https://arxiv.org/abs/2405.14767 | B | financial agent background |
| P12 | TradingAgents: Multi-Agents LLM Financial Trading Framework | 2024 | https://arxiv.org/abs/2412.20138 | B | trading-agent background |
| P13 | QuantCode-Bench: A Benchmark for Evaluating the Ability of Large Language Models to Generate Executable Algorithmic Trading Strategies | 2026 | https://arxiv.org/abs/2604.15151 | A for audited comparator claims | direct trading strategy generation benchmark |
| P14 | SysTradeBench: An Iterative Build-Test-Patch Benchmark for Strategy-to-Code Trading Systems with Drift-Aware Diagnostics | 2026 | https://arxiv.org/abs/2604.04812 | A for audited governance/auditability claims | trading strategy build-test-patch benchmark |
| P15 | Market-Bench: Evaluating Large Language Models on Introductory Quantitative Trading and Market Dynamics | 2025 | https://arxiv.org/abs/2512.12264 | A for audited executable-backtester claims | executable backtester and market-dynamics benchmark |
| P16 | QuantEval: A Benchmark for Financial Quantitative Tasks in Large Language Models | 2026 | https://arxiv.org/abs/2601.08689 | A for audited benchmark/task-taxonomy claims | quantitative finance and strategy-coding benchmark |
| P17 | From Natural Language to Executable Option Strategies via Large Language Models | 2026 | https://arxiv.org/abs/2603.16434 | A for audited OQL/IR analogy claims | domain IR/DSL for option strategies |
| P18 | Deficiency of Large Language Models in Finance: An Empirical Examination of Hallucination | 2023 | https://arxiv.org/abs/2311.15548 | B | financial hallucination and safety motivation |
| P19 | Beyond Knowledge to Agency: Evaluating Expertise, Autonomy, and Integrity in Finance with CNFinBench | 2025 | https://arxiv.org/abs/2512.09506 | B | finance safety/compliance benchmark |
| P20 | FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design | 2023 | https://arxiv.org/abs/2311.13743 | B | financial trading-agent background |

Verification note: these entries are verified at metadata/link level only. Before submission, key related-work citations should be upgraded to Level A by checking PDFs and claim locations.

## Claim-Evidence Matrix

| Claim ID | Claim | Evidence | Strength | Status |
|---|---|---|---|---|
| C01 | QSGA studies reliable generation in a bounded rule-based strategy space, not arbitrary financial intent. | `docs/QYIR_v1_Spec.md`; QYIR supported-scope table | Strong | verified local |
| C02 | QSI-Bench v1 contains 80 samples across six categories. | `benchmark/qsi_bench_v1.jsonl`; `benchmark/annotation_guideline.md` | Strong | verified local |
| C03 | Oracle-slot full QSGA reaches E2E Success 0.8375 in the deterministic prototype. | `experiments/results/baseline_metrics.csv`; reproduced on 2026-05-05 | Strong but scoped | verified local |
| C04 | Oracle-slot full QSGA reduces counted risk-constraint violations to 0.000 under the current risk-auditor definition. | `experiments/results/baseline_metrics.csv`; `experiments/tables/main_comparison.md` | Strong but scoped | verified local |
| C05 | Removing risk audit increases risk violation to 0.508 and lowers E2E Success to 0.5125. | `experiments/results/ablation_metrics.csv` | Strong | verified local |
| C06 | Removing repair lowers E2E Success to 0.375. | `experiments/results/ablation_metrics.csv` | Strong | verified local |
| C07 | Removing safe rejection lowers safe rejection accuracy to 0.000. | `experiments/results/ablation_metrics.csv` | Strong | verified local |
| C08 | Main 80-case experiments are deterministic and the small live pilot does not prove online LLM generalization. | `experiments/baselines.py` module docstring; `experiments/results/live_llm_metrics.csv` | Strong | verified local |
| C09 | Constrained decoding controls output structure, but QSGA focuses on strategy semantics, compilation, risk auditing, and repair. | P04 plus QYIR design | Medium | needs PDF-level citation check |
| C10 | Tool-using agents motivate but do not replace explicit domain IR. | P05, P06 plus QSGA architecture | Medium | needs PDF-level citation check |
| C11 | Direct trading-code benchmarks are closer comparators than broad financial LLM papers. | P13, P14, P15, P16 | Medium | needs PDF-level citation check |
| C12 | QYIR is related to domain-specific financial IR/DSL approaches, especially OQL-style option-strategy representations. | P17 plus QYIR design | Medium | needs PDF-level citation check |
| C13 | Current benchmark results do not measure raw natural-language slot extraction because QYIR candidates are constructed from expected slots. | `experiments/baselines.py`; `subagent_experiment_audit.md`; `subagent_adversarial_review.md` | Strong | verified local |
| C14 | Ambiguous-intent handling is not empirically demonstrated as clarification success in current CSVs. | `experiments/results/baseline_results.csv`; category breakdown | Strong | verified local |
| C15 | A deterministic no-oracle slot extractor reaches E2E Success 0.7625, below oracle-slot QSGA but above simulated baselines in the current harness. | `experiments/results/no_oracle_metrics.csv`; `experiments/run_no_oracle.py` | Strong but scoped | verified local |
| C16 | In a 3-model 12-case live LLM pilot, live_qsga_qyir improves measured E2E over live_raw_qyir for qwen3.6-flash, deepseek-v4-flash, and kimi-k2.6. | `experiments/results/live_llm_metrics.csv`; `experiments/results/live_llm_raw_outputs.jsonl` | Weak to medium; pilot only | verified local |
| C17 | The live pilot is not sufficient to claim broad live LLM generalization because the sample is small and absolute E2E remains low. | `experiments/results/live_llm_metrics.csv`; `docs/ai-research-assistant/RESULTS_LOG.md` | Strong | verified local |
| C18 | Removing QYIR lowers E2E Success to 0.1625 in the deterministic ablation harness. | `experiments/results/ablation_metrics.csv`; `experiments/tables/ablation_comparison.md` | Strong but scoped | verified local |
| C19 | A synthetic SPY/QQQ/GLD smoke check reaches 5/5 compile, backtest, and risk-audit runnability, but does not support profitability or market-robustness claims. | `experiments/results/multi_asset_smoke_results.csv`; `experiments/run_multi_asset_smoke.py` | Strong but smoke-only | verified local |
| C20 | The executable live direct-code qwen3.6-flash baseline reaches 1.000 syntax/interface success but only 0.350 E2E Success on 80 QSI-Bench cases. | `experiments/results/live_direct_code_results.csv`; `experiments/results/live_direct_code_metrics.csv`; `experiments/results/live_direct_code_raw_outputs.jsonl` | Medium; one model and one prompt | verified local |
| C21 | Priority related-work comparators P13-P17 have PDF-level audit scaffolds. | `docs/paper/related_work_verified.md`; `docs/paper/citation_audit_backlog.md` | Strong for audited claims | verified PDF scaffold |
| C22 | A 35-case safe-rejection paraphrase regression set reaches 1.000 accuracy and 0.000 unsafe-acceptance rate, but remains a small deterministic pattern-coverage test. | `benchmark/unsafe_paraphrase_bench.jsonl`; `experiments/results/safe_paraphrase_metrics.csv` | Strong but narrow | verified local |

## Forbidden or Downgraded Claims

| Claim | Decision |
|---|---|
| QSGA guarantees profitable strategies. | Forbidden |
| QSGA is safe for real-money trading. | Forbidden |
| QSGA achieves SOTA. | Forbidden |
| QSGA fully understands vague financial intent. | Forbidden |
| QSGA has been broadly validated on live LLM outputs. | Forbidden; current evidence is only a small live QYIR pilot |
| QYIR improves semantic verification independently in current ablation. | Downgrade: current ablation does not show independent gain |
| Current baselines prove superiority over direct LLM-to-code. | Forbidden; live pilot covers QYIR prompting, not executable live-code generation |
| The 0.000 risk-violation result means financial safety. | Forbidden; it only means zero counted violations under current harness |

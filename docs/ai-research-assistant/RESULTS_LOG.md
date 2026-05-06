# 实验结果日志模板

## 1. 运行记录

| Run ID | Experiment ID | Commit | Seed | Config | Dataset version | Status | Result path | Log path |
|---|---|---|---:|---|---|---|---|---|
| RUN-20260505-001 | EXP-20260505-001 | working tree clean before edits | n/a | deterministic baseline harness | QSI-Bench v1 + `spy_sample.csv` | completed | `experiments/results/baseline_metrics.csv` | `docs/ai-research-assistant/runs/2026-05-05-qsga-paper-run.md` |
| RUN-20260505-002 | EXP-20260505-002 | working tree clean before edits | n/a | deterministic ablation harness | QSI-Bench v1 + `spy_sample.csv` | completed | `experiments/results/ablation_metrics.csv` | `docs/ai-research-assistant/runs/2026-05-05-qsga-paper-run.md` |
| RUN-20260505-003 | EXP-20260505-004 | working tree with paper/code additions | n/a | deterministic no-oracle slot extractor | QSI-Bench v1 + `spy_sample.csv` | completed | `experiments/results/no_oracle_metrics.csv` | `experiments/results/no_oracle_results.csv` |
| RUN-20260505-004 | EXP-20260505-003 | working tree with live LLM runner | 20260505 | live LLM pilot: qwen3.6-flash, deepseek-v4-flash, kimi-k2.6; temperature 0; max_retries 0 | QSI-Bench v1 12-case stratified subset + `spy_sample.csv` | completed pilot | `experiments/results/live_llm_metrics.csv` | `experiments/results/live_llm_raw_outputs.jsonl`; `experiments/results/live_llm_run_metadata.json`; `experiments/results/live_llm_token_usage.csv` |
| RUN-20260506-001 | EXP-20260506-001 | working tree with live QYIR 80 outputs | 20260505 | qwen3.6-flash; temperature 0; fixed QYIR prompts; saved-output replayable run | QSI-Bench v1 80 cases + `spy_sample.csv` | completed | `experiments/results/live_qyir_80_metrics.csv` | `experiments/results/live_qyir_80_raw_outputs.jsonl`; `experiments/results/live_qyir_80_metadata.json`; `experiments/results/live_qyir_80_token_usage.csv` |
| RUN-20260505-005 | EXP-20260505-006 | working tree with `wo_qyir` ablation | n/a | deterministic ablation harness with `wo_qyir` | QSI-Bench v1 + `spy_sample.csv` | completed | `experiments/results/ablation_metrics.csv` | `experiments/results/ablation_results.csv` |
| RUN-20260505-006 | EXP-20260505-007 | working tree with smoke runner | n/a | synthetic SPY/QQQ/GLD smoke | generated OHLCV samples | completed smoke | `experiments/results/multi_asset_smoke_results.csv` | `experiments/run_multi_asset_smoke.py` |
| RUN-20260505-007 | EXP-20260505-008 | working tree with live direct-code runner | 20260505 | qwen3.6-flash; temperature 0; max_tokens 900; fixed `generate_signals(df)` prompt | QSI-Bench v1 80 cases + `spy_sample.csv` | completed | `experiments/results/live_direct_code_metrics.csv` | `experiments/results/live_direct_code_raw_outputs.jsonl`; `experiments/results/live_direct_code_metadata.json`; `experiments/results/live_direct_code_token_usage.csv` |
| RUN-20260505-008 | EXP-20260505-009 | working tree with safe paraphrase bench | n/a | deterministic safe-rejection paraphrase regression | `benchmark/unsafe_paraphrase_bench.jsonl` | completed | `experiments/results/safe_paraphrase_metrics.csv` | `experiments/results/safe_paraphrase_results.csv` |

## 2. 结果解释

| Conclusion ID | Hypothesis | Evidence | Statistical result | Counter-evidence | Limitation | Recommended wording |
|---|---|---|---|---|---|---|
| CONC-20260505-001 | Full QSGA improves end-to-end reliability over deterministic baselines | `baseline_metrics.csv`: QSGA E2E 0.8375 vs direct_code 0.500 and direct_json 0.400 | descriptive rates only; no CI/significance | deterministic harness, no live LLM | small benchmark and single data source | 中：Full QSGA improves E2E success in the deterministic prototype evaluation. |
| CONC-20260505-002 | Risk auditing is necessary for risk-aware claims | `ablation_metrics.csv`: wo_risk_audit risk violation 0.508 vs full 0.000 | descriptive rates only | repair rules are deterministic | historical/sample risk only | 中：Risk auditing eliminates measured risk violations in QSI-Bench v1 under current prototype conditions. |
| CONC-20260505-003 | Repair contributes to E2E success | `ablation_metrics.csv`: wo_repair E2E 0.375 vs full 0.8375 | descriptive rates only | repairable failures are controlled | may not generalize to arbitrary LLM errors | 中：Localized repair improves controlled prototype reliability. |
| CONC-20260505-004 | Safe rejection is part of reliability | `ablation_metrics.csv`: wo_safe_rejection safe rejection accuracy 0.000 vs full 1.000 | descriptive rates only | detector is partly keyword-based | subtle unsafe requests not tested | 中：Safe rejection prevents unsafe acceptance in the benchmark's explicit unsafe-request subset. |
| CONC-20260505-005 | Semantic verifier should not be claimed as independently improving metrics | `ablation_metrics.csv`: wo_semantic_verification equals full | no difference | n/a | deterministic expected-slot construction overlaps semantic checks | 弱：Semantic verification is an architectural guard, not independently demonstrated as a metric gain in this setup. |
| CONC-20260505-006 | Current QSGA result is oracle-slot verification-chain validation, not raw NL generation | `experiments/baselines.py`: `build_qyir_from_record(record)` uses `expected_slots`; subagent audits | descriptive code evidence | none | blocks strong end-to-end claims | 强：The current experiment validates downstream verification after expected slots are available. |
| CONC-20260505-007 | Ambiguous intent clarification is not empirically demonstrated | category breakdown: ambiguous_intent 0/10 E2E for `qsga_full` | descriptive rates only | intended framework supports clarification | no clarification metric exists | 强：Ambiguous cases are failures in current E2E evaluation. |
| CONC-20260505-008 | Deterministic no-oracle slot extraction partially mitigates oracle leakage | `no_oracle_metrics.csv`: E2E 0.7625, semantic consistency 0.708 | descriptive rates only | still deterministic, not live LLM | ambiguous 0/10 remains | 中：No-oracle extractor supports a stronger prototype claim, but not live LLM generalization. |
| CONC-20260505-009 | Live QSGA wrapper improves measured E2E over raw live QYIR generation, but remains weak in absolute terms | `live_qyir_80_metrics.csv`: qwen3.6-flash QSGA QYIR 0.250 vs raw QYIR 0.075; `live_direct_code_metrics.csv`: live direct-code 0.350 | descriptive rates only, n=80 for one model | live direct-code E2E is higher; non-unsafe live QYIR generation remains fragile | single full live model and one prompt family | 弱到中：The QSGA wrapper improves over raw QYIR prompting mainly through safe rejection, but current live evidence does not show superiority over executable direct-code. |
| CONC-20260505-010 | Live pilot confirms unsafe-request gate effect on real model runs | `live_llm_metrics.csv`: live_qsga_qyir safe_rejection_accuracy 1.000 for all three pilot models; live_raw_qyir 0.000 | descriptive rates only, unsafe subset has 2 cases in pilot | detector is deterministic and keyword-heavy | subtle unsafe requests not tested | 中：In the live pilot subset, the QSGA safe-rejection gate prevents the raw models from attempting unsafe requests. |
| CONC-20260505-011 | QYIR adds value beyond surface structured output in the current deterministic harness | `ablation_metrics.csv`: `wo_qyir` E2E 0.1625 vs `qsga_full` 0.8375 | descriptive rates only | `wo_qyir` is an approximation, not a live model | fairness of the ablation remains a reviewer-sensitive point | 中：The `wo_qyir` ablation supports the role of QYIR-specific alias, rule, risk-slot, and repair semantics in the implemented prototype. |
| CONC-20260505-012 | Synthetic symbol/period smoke test supports runnability, not market robustness | `multi_asset_smoke_results.csv`: 5/5 compile/backtest/risk-audit runnable | smoke counts only | synthetic data, single QYIR case | no profitability or robustness claim | 弱：The pipeline remains runnable across several synthetic symbol/period settings. |
| CONC-20260505-013 | Executable live direct-code outputs can parse and expose the required interface but remain unreliable end to end | `live_direct_code_metrics.csv`: syntax 1.000, interface 1.000, E2E 0.350; `live_direct_code_results.csv` | descriptive rates only, one model | only qwen3.6-flash and one prompt | not a broad model comparison | 中：The executable live direct-code baseline shows that surface code validity is insufficient for semantic, risk, and unsafe-intent reliability. |
| CONC-20260505-014 | Safe-rejection paraphrase coverage is improved on a small deterministic regression set | `safe_paraphrase_metrics.csv`: accuracy 1.000, false-positive rate 0.000, unsafe-acceptance rate 0.000 | descriptive rates only, n=35 | keyword/pattern rules remain brittle | not robust financial safety | 弱：The paraphrase set provides regression coverage for explicit unsafe and boundary-safe phrasings. |

## 3. 失败实验

| Failure ID | Run ID | 失败类型 | 日志位置 | 影响 | 下一步 |
|---|---|---|---|---|---|
| FAIL-20260505-001 | RUN-20260505-001 | live LLM evidence absent | `experiments/baselines.py` | limits claim strength | decide DEC-20260505-001 |
| FAIL-20260505-002 | RUN-20260505-002 | semantic-verifier ablation no independent gain | `experiments/results/ablation_metrics.csv` | requires claim downgrade | mitigated in paper draft |
| FAIL-20260505-003 | RUN-20260505-001 | oracle-slot construction | `experiments/baselines.py` | invalidates strong raw NL generation claim | mitigated by draft downgrade; no-oracle experiment still needed |
| FAIL-20260505-004 | RUN-20260505-001 | simulated baselines | `experiments/baselines.py` | weakens comparative claims | mitigated by baseline wording; live baseline still needed |
| FAIL-20260505-005 | RUN-20260505-001 | ambiguous cases not clarified | `experiments/results/baseline_results.csv` | weakens boundary-control claim | add clarification metric or keep limitation |
| FAIL-20260505-006 | RUN-20260505-004 | qwen3.6-plus too slow/token-heavy for 20-case batch in current run | timed-out 20-case command; no complete output files written | cannot include qwen3.6-plus in batch metrics without more time/budget | keep qwen3.6-plus as one-case probe or run a separate capped batch |
| FAIL-20260505-007 | RUN-20260505-004 | live pilot absolute E2E remains low and risk violations remain | `experiments/results/live_llm_metrics.csv` | prevents strong live LLM generalization claims | frame as pilot evidence; improve prompts/repair or run larger benchmark later |
| FAIL-20260506-001 | RUN-20260506-001 | 80-case live QYIR absolute E2E remains low | `experiments/results/live_qyir_80_metrics.csv` | prevents broad live QYIR reliability claims | frame as diagnostic evidence and keep single-model limitation explicit |
| FAIL-20260505-008 | RUN-20260505-007 | live direct-code runtime failures and invalid/no-trade signals | `experiments/results/live_direct_code_results.csv` | direct-code E2E 0.350 despite syntax/interface 1.000 | use as baseline evidence; do not overclaim |
| FAIL-20260505-009 | RUN-20260505-007 | direct-code backtester warning on generated outputs | live run stdout contained pandas casting and equity overflow warnings | generated code can create unstable position series; metrics remain descriptive | document as baseline fragility; consider stricter execution sandbox later |

## 4. 强结论检查

任何写入摘要、贡献点或结论的表述必须满足：

1. 对应 `Conclusion ID` 存在。
2. 证据来自实验日志或 A 级文献。
3. 统计分析已完成。
4. 人类已审核。

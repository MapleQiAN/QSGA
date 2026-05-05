# 实验结果日志模板

## 1. 运行记录

| Run ID | Experiment ID | Commit | Seed | Config | Dataset version | Status | Result path | Log path |
|---|---|---|---:|---|---|---|---|---|
| RUN-20260505-001 | EXP-20260505-001 | working tree clean before edits | n/a | deterministic baseline harness | QSI-Bench v1 + `spy_sample.csv` | completed | `experiments/results/baseline_metrics.csv` | `docs/ai-research-assistant/runs/2026-05-05-qsga-paper-run.md` |
| RUN-20260505-002 | EXP-20260505-002 | working tree clean before edits | n/a | deterministic ablation harness | QSI-Bench v1 + `spy_sample.csv` | completed | `experiments/results/ablation_metrics.csv` | `docs/ai-research-assistant/runs/2026-05-05-qsga-paper-run.md` |
| RUN-20260505-003 | EXP-20260505-004 | working tree with paper/code additions | n/a | deterministic no-oracle slot extractor | QSI-Bench v1 + `spy_sample.csv` | completed | `experiments/results/no_oracle_metrics.csv` | `experiments/results/no_oracle_results.csv` |

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

## 3. 失败实验

| Failure ID | Run ID | 失败类型 | 日志位置 | 影响 | 下一步 |
|---|---|---|---|---|---|
| FAIL-20260505-001 | RUN-20260505-001 | live LLM evidence absent | `experiments/baselines.py` | limits claim strength | decide DEC-20260505-001 |
| FAIL-20260505-002 | RUN-20260505-002 | semantic-verifier ablation no independent gain | `experiments/results/ablation_metrics.csv` | requires claim downgrade | mitigated in paper draft |
| FAIL-20260505-003 | RUN-20260505-001 | oracle-slot construction | `experiments/baselines.py` | invalidates strong raw NL generation claim | mitigated by draft downgrade; no-oracle experiment still needed |
| FAIL-20260505-004 | RUN-20260505-001 | simulated baselines | `experiments/baselines.py` | weakens comparative claims | mitigated by baseline wording; live baseline still needed |
| FAIL-20260505-005 | RUN-20260505-001 | ambiguous cases not clarified | `experiments/results/baseline_results.csv` | weakens boundary-control claim | add clarification metric or keep limitation |

## 4. 强结论检查

任何写入摘要、贡献点或结论的表述必须满足：

1. 对应 `Conclusion ID` 存在。
2. 证据来自实验日志或 A 级文献。
3. 统计分析已完成。
4. 人类已审核。

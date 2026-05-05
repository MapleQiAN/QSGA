# 论文草稿状态模板

## 1. 章节状态

| 章节 | 状态 | 引用检查 | 证据检查 | 人审状态 | 备注 |
|---|---|---|---|---|---|
| Abstract | draft | pending Level A | checked local claims | required | deterministic scope included |
| Introduction | draft | pending Level A | checked local claims | required | four contributions retained |
| Related Work | draft | P13-P17 Level A scaffold; others Level B | priority comparator claims checked | required | `related_work_verified.md` added |
| Method | draft | n/a | checked against QYIR spec/code | required | QYIR/QSGA sections complete |
| Experiments | draft | n/a | checked against experiment scripts | required | deterministic main experiments, live QYIR pilot, executable live direct-code baseline |
| Results | draft | n/a | reproduced metrics | required | descriptive rates only; live direct-code covers one model |
| Limitations | draft | n/a | checked | required | deterministic prototype and small-live-pilot limitations included |
| Ethics Statement | draft | n/a | checked | required | no investment advice claim |
| Appendix | draft | n/a | checked | optional | artifact map and reproducibility package |

## 2. CCF C 审稿状态

| 项目 | 状态 | 备注 |
|---|---|---|
| CCF C Reviewer Report | done | `docs/paper/ccf_c_reviewer_report.md` |
| Recommendation | Borderline as IR/prototype with live pilot; Weak Reject if framed as broad empirical LLM benchmark | oracle-slot and small-live-pilot risks remain |
| P0/P1 风险已登记 | done | `RISKS.md`, `DECISIONS.md` |
| 一票否决项检查 | open | public release/submission requires human approval |
| Claim Strength Audit | done | `docs/paper/citation_and_claim_matrix.md` and reviewer report |

## 3. Claim 状态

| Claim ID | 章节 | 表述 | 证据 | 强度 | 状态 |
|---|---|---|---|---|---|
| C01 | Abstract/Conclusion | QSGA improves E2E success in deterministic prototype | `baseline_metrics.csv` | 中 | draft |
| C02 | Results | Risk audit reduces measured risk violations | `ablation_metrics.csv` | 中 | draft |
| C03 | Results | Repair improves controlled prototype reliability | `ablation_metrics.csv` | 中 | draft |
| C04 | Results | Safe rejection prevents explicit unsafe-request acceptance | `ablation_metrics.csv` | 中 | draft |
| C05 | Limitations | Current results do not prove live LLM generalization | `experiments/baselines.py` | 强 | draft |
| C06 | Experiments/Limitations | Current QSGA evaluation is oracle-slot deterministic validation | `experiments/baselines.py` | 强 | draft |
| C07 | Results/Limitations | Ambiguous cases are not currently measured as clarification success | `baseline_results.csv` category breakdown | 强 | draft |
| C08 | Results | No-oracle deterministic slot extraction reaches 0.7625 E2E | `no_oracle_metrics.csv` | 中 | draft |
| C09 | Results/Limitations | Live QSGA wrapper improves E2E over raw live QYIR prompting in a 3-model 12-case pilot, but absolute success remains limited | `live_llm_metrics.csv` | 弱到中 | draft |
| C10 | Results | w/o QYIR reaches 0.1625 E2E, supporting QYIR-specific representation value in the deterministic harness | `ablation_metrics.csv` | 中 | draft |
| C11 | Results | Synthetic SPY/QQQ/GLD smoke reaches 5/5 runnability without market robustness claims | `multi_asset_smoke_results.csv` | 弱 | draft |
| C12 | Results/Limitations | Executable live direct-code qwen3.6-flash reaches 1.000 syntax/interface but 0.350 E2E | `live_direct_code_metrics.csv` | 中 | draft |
| C13 | Related Work | P13-P17 direct comparators support scoped positioning of QSGA | `related_work_verified.md` | 中 | draft |

## 4. 禁止进入终稿的内容

1. 无证据 claim。
2. 未核验引用。
3. 未人审强结论。
4. 未处理伦理风险。
5. 未记录失败实验。
6. 伪装成真实审稿意见的模拟 reviewer 输出。
7. 未处理 CCF C Reviewer Agent 的 P0/P1 拒稿风险。

# 论文草稿状态模板

## 1. 章节状态

| 章节 | 状态 | 引用检查 | 证据检查 | 人审状态 | 备注 |
|---|---|---|---|---|---|
| Abstract | draft | pending Level A | checked local claims | required | deterministic scope included |
| Introduction | draft | pending Level A | checked local claims | required | four contributions retained |
| Related Work | draft | Level B | pending PDF claim check | required | metadata/link-level only |
| Method | draft | n/a | checked against QYIR spec/code | required | QYIR/QSGA sections complete |
| Experiments | draft | n/a | checked against experiment scripts | required | live LLM limitation explicit |
| Results | draft | n/a | reproduced metrics | required | descriptive rates only |
| Limitations | draft | n/a | checked | required | deterministic prototype limitation included |
| Ethics Statement | draft | n/a | checked | required | no investment advice claim |
| Appendix | draft | n/a | checked | optional | artifact map and reproducibility package |

## 2. CCF C 审稿状态

| 项目 | 状态 | 备注 |
|---|---|---|
| CCF C Reviewer Report | done | `docs/paper/ccf_c_reviewer_report.md` |
| Recommendation | Weak Reject-level / Borderline as prototype | oracle-slot and simulated-baseline P1 risks remain |
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

## 4. 禁止进入终稿的内容

1. 无证据 claim。
2. 未核验引用。
3. 未人审强结论。
4. 未处理伦理风险。
5. 未记录失败实验。
6. 伪装成真实审稿意见的模拟 reviewer 输出。
7. 未处理 CCF C Reviewer Agent 的 P0/P1 拒稿风险。

# 论文草稿状态模板

## 1. 章节状态

| 章节 | 状态 | 引用检查 | 证据检查 | 人审状态 | 备注 |
|---|---|---|---|---|---|
| Abstract | revised after V5 | pending Level A | checked local claims | required | QYIR-centered problem statement; reports oracle 0.963, no-oracle 0.887, live construction 0.091 |
| Introduction | revised after V5 | pending Level A | checked local claims | required | RQ split into IR verification and live LLM bottleneck diagnosis; contribution claims lowered |
| Related Work | draft | P13-P17 Level A scaffold plus 2026-05-07 arXiv metadata refresh; others Level B | priority comparator claims checked | required | `related_work_verified.md` updated; final BibTeX refresh still required |
| Method | revised after V5 | n/a | checked against QYIR spec/code | required | added QYIR grammar, validity conjunction, operand type system, compilation semantics, semantic-slot algorithm, repair invariants |
| Experiments | revised after V5 + route-A polish | n/a | checked against experiment scripts | required | added claim matrix and explicit proof obligations for oracle/no-oracle/live/direct-code experiments |
| Results | revised after V5 + route-A polish | n/a | reproduced metrics | required | added no-oracle slot diagnostics; sharpened direct-code low-friction vs QYIR post-construction verifiability comparison |
| Limitations | revised after V5 + route-A polish | n/a | checked | required | reframed threats as scoped research boundaries; QSI-Bench described as controlled failure-mode benchmark |
| Discussion/Conclusion | revised after V5 + route-A polish | n/a | checked | required | added scope-boundary discussion and direct-code/QYIR friction-verifiability tradeoff |
| Ethics Statement | draft | n/a | checked | required | no investment advice claim |
| Appendix | draft | n/a | checked | optional | artifact map and reproducibility package |

## 2. CCF C 审稿状态

| 项目 | 状态 | 备注 |
|---|---|---|
| CCF C Reviewer Report | V5 applied | `docs/paper/ccf_c_reviewer_report_v5.md` |
| Recommendation | Borderline only as QYIR/QSGA IR verification-system paper; Weak Reject if framed as broad empirical LLM benchmark | live construction 0.091 and slot-level no-oracle weaknesses are treated as bottleneck evidence |
| P0/P1 风险已登记 | done | `RISKS.md`, `DECISIONS.md` |
| 一票否决项检查 | open | public release/submission requires human approval |
| Claim Strength Audit | done | `docs/paper/citation_and_claim_matrix.md` and reviewer report |

## 3. Claim 状态

| Claim ID | 章节 | 表述 | 证据 | 强度 | 状态 |
|---|---|---|---|---|---|
| C01 | Abstract/Conclusion | QSGA improves reliability when valid or partially valid strategy specifications can be constructed | `baseline_metrics.csv`; `no_oracle_metrics.csv` | 中 | draft |
| C02 | Results | Risk audit reduces measured risk violations | `ablation_metrics.csv` | 中 | draft |
| C03 | Results | Repair improves controlled prototype reliability | `ablation_metrics.csv` | 中 | draft |
| C04 | Results | Explicit unsafe-intent rejection prevents explicit unsafe-request acceptance | `ablation_metrics.csv` | 中 | draft |
| C05 | Limitations | Current results do not prove live LLM generalization | `experiments/baselines.py` | 强 | draft |
| C06 | Experiments/Limitations | Oracle-slot QSGA is an upper-bound verification-chain validation, not raw NL generation | `experiments/baselines.py` | 强 | draft |
| C07 | Results/Limitations | Ambiguous cases are measured through clarification accuracy, but only with deterministic single-turn rules | `baseline_metrics.csv`; `no_oracle_metrics.csv` | 中 | draft |
| C08 | Results | No-oracle deterministic slot extraction reaches 0.8875 E2E and 0.8364 construction success | `no_oracle_metrics.csv` | 中 | draft |
| C09 | Results/Limitations | Live QSGA wrapper improves E2E over raw live QYIR prompting, but construction success remains 0.0909 and live QYIR generation is the bottleneck | `live_qyir_80_metrics.csv`; `live_direct_code_metrics.csv` | 弱到中 | draft |
| C10 | Results | w/o QYIR reaches 0.1625 E2E, supporting QYIR-specific representation value in the deterministic harness | `ablation_metrics.csv` | 中 | draft |
| C11 | Results | Synthetic SPY/QQQ/GLD smoke reaches 5/5 runnability without market robustness claims | `multi_asset_smoke_results.csv` | 弱 | draft |
| C12 | Results/Limitations | Executable live direct-code qwen3.6-flash reaches 1.000 syntax/interface but 0.350 E2E | `live_direct_code_replay_results.csv` | 中 | draft |
| C13 | Related Work | P13-P17 direct comparators support scoped positioning of QSGA | `related_work_verified.md` | 中 | draft |
| C14 | Results | Semantic verifier detects schema-valid explicit intent-slot corruptions in 7/7 corruption cases | `semantic_corruption_metrics.csv` | 中 | draft |
| C15 | Results/Limitations | Shared explicit unsafe-intent replay improves saved live direct-code E2E to 0.5375 mainly through unsafe handling | `live_direct_code_shared_rejection_metrics.csv` | 中 | draft |
| C16 | Results | Major proportions now include Wilson 95% confidence intervals to expose small-sample uncertainty | `qsga_ccf_c_draft.md` Section 8.4 | 中 | revised after V4 |
| C17 | Abstract/Discussion/Conclusion | QYIR improves auditability, failure localization, compilation control, and risk-aware repair for bounded strategy specifications, while robust NL-to-QYIR generation remains open | `ccf_c_reviewer_report_v5.md`; `baseline_metrics.csv`; `no_oracle_metrics.csv`; `live_qyir_80_metrics.csv` | 中 | revised after V5 |
| C18 | Results/Limitations | Slot-level no-oracle diagnostics show the extractor mainly captures indicator and risk-control cues, while fine-grained entry/exit extraction remains weak | `no_oracle_slot_diagnostics.csv`; `no_oracle_slot_diagnostics.md`; `run_slot_diagnostics.py` | 中 | revised after V5 |
| C19 | Results/Discussion | Direct code has lower entry friction but weaker controllability; QYIR has higher construction difficulty but stronger post-construction verifiability | `live_direct_code_metrics.csv`; `live_qyir_80_metrics.csv`; `claim_policy.md` | 中 | revised after route-A polish |
| C20 | Experiments/Claim Matrix | Each experiment has an explicit supported/not-claimed boundary | `citation_and_claim_matrix.md`; `qsga_ccf_c_draft.md` Section 8.1 | 强 | revised after route-A polish |

## 4. 禁止进入终稿的内容

1. 无证据 claim。
2. 未核验引用。
3. 未人审强结论。
4. 未处理伦理风险。
5. 未记录失败实验。
6. 伪装成真实审稿意见的模拟 reviewer 输出。
7. 未处理 CCF C Reviewer Agent 或 V5 reviewer-risk report 的 P0/P1 拒稿风险。

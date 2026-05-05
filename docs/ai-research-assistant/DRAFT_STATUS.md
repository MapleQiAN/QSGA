# 论文草稿状态模板

## 1. 章节状态

| 章节 | 状态 | 引用检查 | 证据检查 | 人审状态 | 备注 |
|---|---|---|---|---|---|
| Abstract | todo | pending | pending | required |  |
| Introduction | todo | pending | pending | required |  |
| Related Work | todo | pending | pending | required |  |
| Method | todo | pending | pending | required |  |
| Experiments | todo | pending | pending | required |  |
| Results | todo | pending | pending | required |  |
| Limitations | todo | pending | pending | required |  |
| Ethics Statement | todo | pending | pending | required |  |
| Appendix | todo | pending | pending | optional |  |

## 2. CCF C 审稿状态

| 项目 | 状态 | 备注 |
|---|---|---|
| CCF C Reviewer Report | pending | 必须按 `CCF_C_REVIEWER_AGENT.md` 输出 |
| Recommendation | pending | Accept-level / Weak Accept-level / Borderline / Weak Reject-level / Reject-level |
| P0/P1 风险已登记 | pending | 写入 `RISKS.md` 或 `DECISIONS.md` |
| 一票否决项检查 | pending | 不得有未解决项 |
| Claim Strength Audit | pending | 摘要、贡献点、结论必须覆盖 |

## 3. Claim 状态

| Claim ID | 章节 | 表述 | 证据 | 强度 | 状态 |
|---|---|---|---|---|---|
|  |  |  |  | 强 / 中 / 弱 / 不足 | draft |

## 4. 禁止进入终稿的内容

1. 无证据 claim。
2. 未核验引用。
3. 未人审强结论。
4. 未处理伦理风险。
5. 未记录失败实验。
6. 伪装成真实审稿意见的模拟 reviewer 输出。
7. 未处理 CCF C Reviewer Agent 的 P0/P1 拒稿风险。

# AGENTS.md

版本：v3.0

本文件是 AI Agent 的主规范。每轮必须优先读取本文件，但不得因此忽略 `TASK_QUEUE.md` 和 `protocols/EXECUTION_LOOP.md`。

---

## TLDR_STATE_FOR_AGENT

当前规则核心：

1. 每轮必须按 `protocols/EXECUTION_LOOP.md` 执行。
2. 每轮必须从 `TASK_QUEUE.md` 选择任务，不允许凭感觉自由发挥。
3. 优先选择最高优先级、非阻塞、低风险、可验证任务。
4. 遇到人类决策点，写入 `DECISIONS.md`，然后切换到其它非阻塞任务。
5. 禁止伪造数据、引用、实验结果、强结论。
6. 禁止每轮无脑读取所有文档，必须遵守 `protocols/CONTEXT_POLICY.md`。
7. 单窗口环境允许 Orchestrator 串行模拟多 Agent，但必须保留角色边界和交接记录。

当前默认入口：

- 读 `TASK_QUEUE.md` 的 Active Tasks
- 读 `CURRENT_PROGRESS.md` 的摘要和 Next Actions
- 读 `DECISIONS.md` 的 PendingReview / waiting_human
- 读 `RISKS.md` 的 Critical / High active
- 选择一个任务执行
- 更新任务、进度、风险、审计日志

---

## 1. 默认读取策略

每轮默认只读取：

1. `AGENTS.md` 的 `TLDR_STATE_FOR_AGENT` 和相关规则。
2. `TASK_QUEUE.md` 的 `TLDR_STATE_FOR_AGENT`、Active Tasks、Blocked Tasks。
3. `CURRENT_PROGRESS.md` 的 `TLDR_STATE_FOR_AGENT`、当前阶段、Next Actions。
4. `DECISIONS.md` 的 `PendingReview` 和 `waiting_human` 部分。
5. `RISKS.md` 的 Critical / High active 部分。
6. `protocols/EXECUTION_LOOP.md` 的执行算法。
7. `protocols/CONTEXT_POLICY.md` 的读取限制。

按需读取：

- 做实验时：`research/EXPERIMENT_PLAN.md`、`research/RESULTS_LOG.md` 的相关实验。
- 写论文时：`research/DRAFT_STATUS.md`、`research/PAPER_MATRIX.md` 的相关 claim。
- 审稿模拟时：`protocols/REVIEWER_GATE.md`、`protocols/QUALITY_GUARDRAILS.md`。
- 多角色协作时：`protocols/MULTI_AGENT_PROTOCOL.md`。
- 阶段规划时：`protocols/SOP.md`。
- QSGA 项目时：`profiles/QSGA_PROFILE.md`。
- 关键操作前：追加 `AUDIT_LOG.md`，不默认读取全文。

禁止：

- 每轮读取全部实验日志。
- 每轮读取全部论文草稿。
- 每轮读取全部历史 runs。
- 每轮读取全部文献矩阵。
- 通过“我需要完整上下文”为理由吞掉整个仓库。

---

## 2. 科研真实性红线

以下行为禁止，无论任何理由：

1. 编造实验结果。
2. 编造引用、DOI、作者、年份、会议。
3. 把未验证结论写成已验证结论。
4. 把失败实验包装成成功实验。
5. 选择性隐藏负面结果。
6. 使用无法追溯来源的数据支撑强结论。
7. 删除或覆盖原始实验日志。
8. 未经人类确认，自动投稿、公开发布、声明成果。
9. 未经人类确认，修改核心研究问题、核心实验协议、论文主张。
10. 使用强词，如“首次”“SOTA”“证明”“显著优于”，但没有 A 级或强 B 级证据。

---

## 3. 任务队列优先原则

Agent 每轮必须从 `TASK_QUEUE.md` 选择任务。

任务选择优先级：

1. `blocked_human` 之外的任务。
2. Priority 为 P0 或 P1。
3. `Safe to Run Automatically: Yes`。
4. 依赖已经满足。
5. 能产生可验证证据。
6. 预计成本较低或中等。
7. 对当前阶段推进价值最高。

禁止：

- 跳过任务队列直接自拟大任务。
- 在没有任务 ID 的情况下修改核心文档。
- 为了显得忙而反复润色同一段文字。
- 把一个巨大目标伪装成一个小任务。

如果发现任务队列为空，Agent 必须先创建候选任务，并按 P0/P1/P2 排序，而不是开始自由发挥。

---

## 4. 异步优先原则

能自行决定的问题直接推进，记录依据，不问用户。

可以自行决定：

- 文档整理、格式统一、代码风格统一。
- 非核心变量命名。
- 普通 bug 修复。
- 补充日志、注释、测试。
- 整理实验记录。
- 对未验证结论降级表述。
- 把明显不合规内容移到待验证区。
- 为任务队列补充低风险候选任务。
- 为长文档补充 `TLDR_STATE_FOR_AGENT` 摘要。

必须写入 `DECISIONS.md` 等待人类确认：

- 是否改变研究方向。
- 是否修改核心 claim。
- 是否新增或删除关键 baseline。
- 是否冻结实验协议。
- 是否投稿。
- 是否公开代码、数据、模型、结果。
- 是否使用付费 API 或第三方账号。
- 是否引入有伦理、隐私、版权风险的数据。
- 是否接受失败结果并调整论文叙事。
- 是否署名、致谢、声明贡献。
- 是否批量运行高成本实验。

遇到需要人类确认的问题：

1. 写入 `DECISIONS.md`。
2. 给出选项、AI 推荐、风险、默认假设。
3. 把当前任务状态改为 `blocked_human`。
4. 返回 `TASK_QUEUE.md` 领取其它非阻塞任务。
5. 不要原地等待。

---

## 5. 多 Agent 与 Orchestrator 规则

复杂科研任务必须进行角色拆分和任务解耦。

如果环境支持并行 Agent：

- Orchestrator 负责分发任务、收集交接、处理冲突。
- 子 Agent 只修改自己负责的文件或片段。
- 冲突写入 `RISKS.md` 或 `DECISIONS.md`。

如果环境不支持真实并行：

- 由 Orchestrator 串行模拟多个 Agent。
- 每个角色必须独立输出任务报告。
- 不得把多个角色的判断混成一个不可追踪的“综合感觉”。
- 每次角色切换必须记录输入、输出、证据和限制。

推荐角色：

- Research Orchestrator
- Literature Scout
- Paper Reader
- Citation Verifier
- Experiment Designer
- Execution Agent
- Statistics Agent
- Writer Agent
- Reviewer Agent
- Archivist Agent

---

## 6. 自动推进规则

当用户要求“持续推进”“自动化”“自己往下做”“连续工作”时：

1. 读取 `TASK_QUEUE.md`。
2. 选择最高优先级、非阻塞、低风险、可验证任务。
3. 执行一个最小可验证单元。
4. 写入或更新运行记录。
5. 更新任务状态。
6. 更新 `CURRENT_PROGRESS.md`。
7. 如有新风险，写入 `RISKS.md`。
8. 如有新证据，写入 `research/PAPER_MATRIX.md` 或 `research/RESULTS_LOG.md`。
9. 如有未验证内容，写入 `research/DRAFT_STATUS.md` 的 Unverified Claims。
10. 如遇人审点，写入 `DECISIONS.md`，然后继续其它任务。
11. 不自动执行危险操作。

---

## 7. 危险操作清单

以下操作必须请求人类确认，执行前停止当前分支：

- 删除实验数据、原始日志、数据库或结果目录。
- 覆盖论文主稿。
- 修改 frozen 实验协议。
- 修改最终结论强度。
- 自动投稿、公开仓库、上传数据集。
- 付费调用 API。
- 批量运行高成本实验。
- 使用含隐私、敏感、版权不明的数据。
- 改变项目许可证。
- 改动署名、致谢、贡献声明。

---

## 8. 证据等级

所有论文 claim 必须标注证据等级：

| 等级 | 含义 | 可进论文正文 |
|---|---|---|
| A | 已通过实验验证，有命令、日志、代码版本、数据版本、seed | 可以 |
| B | 有实现和局部验证，但实验规模有限 | 谨慎 |
| C | 有理论或工程理由，但实验不足 | 不可作为核心结论 |
| D | 观察、假设、直觉 | 只能写为 limitation 或 future work |
| X | 无证据支撑 | 禁止 |

强结论只能来自 A 或强 B 证据。

---

## 9. 实验记录最低要求

每个实验必须记录：

- 实验 ID、日期、研究问题。
- 代码版本或 commit。
- 数据集名称、版本、来源、许可证。
- 环境和依赖。
- 配置文件、随机种子、运行命令。
- 原始输出位置、指标结果。
- 失败情况。
- 可复现等级 R0 到 R5。
- 对论文 claim 的影响。

---

## 10. 审计日志要求

以下操作必须写入 `AUDIT_LOG.md`：

- 检索、精读、实验设计、实验运行。
- 结果解释、论文强主张。
- 人类审核和审批。
- 公开或发布尝试。
- 工具调用失败和重试。
- 核心文档的大范围修改。
- 任务队列重排或批量状态变更。

---

## 11. 每轮收尾格式

每轮结束前必须输出并写入运行记录：

```text
完成：
- [具体事项]

验证：
- [有证据支撑的结论]

未验证：
- [需要后续确认的内容]

新增风险：
- [风险描述，没有则写无]

需要人类确认：
- [决策事项，没有则写无]

任务队列更新：
- [任务 ID 和状态变化]

下一步：
- [可立即推进的任务 ID]
```

# Execution Loop

本文件定义每轮 Agent 的执行算法。目标是让 Agent 像自动驾驶系统一样推进科研任务，而不是像灵感型写手一样随机发挥。

---

## TLDR_STATE_FOR_AGENT

每轮必须执行：

1. Load Minimal Context
2. Parse Current State
3. Select Task From `TASK_QUEUE.md`
4. Check Safety and Dependencies
5. Execute One Verifiable Unit
6. Update Evidence and Project State
7. Run Quality Gate
8. Produce Handoff Summary
9. Compress Context for Next Run

禁止：

- 没有任务 ID 就大范围修改。
- 遇到人类决策点就停止整个项目。
- 只润色文字但不产出证据。
- 把多个巨大任务塞进一轮。
- 未更新任务队列就结束。

---

## 1. Load Minimal Context

默认读取：

1. `AGENTS.md` 的摘要区和自动推进规则。
2. `TASK_QUEUE.md` 的摘要区、Active Tasks、Blocked Tasks。
3. `CURRENT_PROGRESS.md` 的摘要区、当前阶段、Next Actions。
4. `DECISIONS.md` 的 PendingReview / waiting_human。
5. `RISKS.md` 的 Critical / High active。
6. `protocols/CONTEXT_POLICY.md`。
7. 本文件。

按任务需要读取其它文档，不得扩大为全仓库阅读。

---

## 2. Parse Current State

Agent 必须先明确：

```text
Current Stage:
Available Tasks:
Blocked Tasks:
Critical Risks:
Human Decisions Pending:
Evidence Gaps:
Last Known Next Actions:
```

如果缺少当前阶段，则从 `CURRENT_PROGRESS.md` 推断；如果仍无法推断，则创建 P0 任务：明确当前阶段与研究目标。

---

## 3. Select Task From TASK_QUEUE.md

选择任务算法：

```text
候选任务 = Active Tasks 中 Status 为 todo / in_progress / revision_needed 的任务
过滤掉：
  - blocked_human
  - blocked_dependency
  - Safe to Run Automatically: No 且未获人类授权
  - Risk Level 为 Critical 且无人类授权
排序：
  - Priority: P0 > P1 > P2 > P3
  - 能产生证据 > 只能润色
  - 能解除依赖 > 单点优化
  - 低风险 > 高风险
  - 低成本 > 高成本
选择第一个任务作为本轮任务
```

如果没有可执行任务：

1. 创建新任务候选。
2. 或对 blocked task 的共同前置部分进行整理。
3. 或执行低风险维护任务，如补摘要、补 evidence map、核验引用。
4. 不得无任务 ID 开始工作。

---

## 4. Check Safety and Dependencies

执行前检查：

```text
Task ID:
Human Review Required:
Safe to Run Automatically:
Dependencies Satisfied:
Risk Level:
Dangerous Operation:
```

若触发危险操作：

1. 不执行危险部分。
2. 写入 `DECISIONS.md`。
3. 将任务状态改为 `blocked_human`。
4. 切换到其它非阻塞任务。

若只是依赖缺失：

1. 将任务状态改为 `blocked_dependency`。
2. 创建或激活依赖任务。
3. 切换到依赖任务或其它可执行任务。

---

## 5. Execute One Verifiable Unit

每轮只做一个最小可验证单元。

合格的最小单元示例：

- 核验 5 篇核心引用。
- 跑一个 baseline 的 smoke test。
- 修复一个实验脚本错误并记录命令。
- 为一个 claim 补证据等级。
- 完成一节论文的 claim 降级。
- 整理一个 failure case 表。
- 给一个长文档补 `TLDR_STATE_FOR_AGENT`。

不合格示例：

- “重写整篇论文”。
- “全面优化实验”。
- “把所有文献都看完”。
- “顺便重构整个代码库”。
- “感觉这个方法很强，所以加强表述”。

---

## 6. Update Evidence and Project State

执行后必须更新相关文件：

| 情况 | 更新文件 |
|---|---|
| 任务状态变化 | `TASK_QUEUE.md` |
| 当前阶段变化 | `CURRENT_PROGRESS.md` |
| 出现实验结果 | `research/RESULTS_LOG.md` |
| 出现文献证据 | `research/PAPER_MATRIX.md` |
| 出现论文 claim 变化 | `research/DRAFT_STATUS.md` |
| 出现风险 | `RISKS.md` |
| 出现人类决策点 | `DECISIONS.md` |
| 关键操作或失败重试 | `AUDIT_LOG.md` |
| 本轮运行摘要 | `runs/YYYY-MM-DD-topic.md` |

---

## 7. Run Quality Gate

本轮结束前进行质量门检查：

```text
是否有任务 ID：Yes / No
是否执行了一个明确任务：Yes / No
是否产生可验证输出：Yes / No
是否记录证据或限制：Yes / No
是否更新任务状态：Yes / No
是否触发人审：Yes / No
是否避免危险操作：Yes / No
是否留下下一步：Yes / No
```

若任何关键项为 No，必须补齐后再结束。

---

## 8. Produce Handoff Summary

每轮输出固定格式：

```text
## Handoff Summary

Run ID:
Task ID:
Role:
Status:

Completed:
Evidence:
Files Updated:
Risks:
Human Decisions Needed:
Blocked Items:
Next Recommended Task:
Context to Carry Forward:
```

`Context to Carry Forward` 必须短，优先给下一轮 Agent 使用，不写流水账。

---

## 9. Compress Context for Next Run

每轮结束必须保证至少一个状态文件被更新：

- `TASK_QUEUE.md` 的任务状态和 Last Result。
- `CURRENT_PROGRESS.md` 的 TLDR 摘要。
- 对应研究文档的 TLDR 摘要。
- `runs/YYYY-MM-DD-topic.md` 的交接摘要。

压缩原则：

1. 结论优先。
2. 证据链接优先。
3. 未验证内容单独标注。
4. 不复制大段原文。
5. 不把历史过程写成小说。

---

## 10. 异常处理

### 10.1 工具失败

若工具失败：

1. 记录错误到 `AUDIT_LOG.md`。
2. 判断是否可重试。
3. 最多重试合理次数。
4. 仍失败则把任务状态改为 `blocked_dependency` 或 `revision_needed`。
5. 切换到其它任务。

### 10.2 发现前文错误

若发现前文存在错误：

1. 不静默覆盖。
2. 在相关文件写明修正原因。
3. 若影响核心 claim，写入 `DECISIONS.md` 或 `RISKS.md`。
4. 更新任务队列。

### 10.3 结果不符合预期

实验失败或结果变差时：

1. 记录失败结果。
2. 不包装成成功。
3. 分析失败原因。
4. 判断是否需要改变实验设计。
5. 若需要，写入 `DECISIONS.md`。
6. 若不需要，创建 failure analysis 任务。

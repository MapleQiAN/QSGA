# TASK_QUEUE.md

本文件是 Research Ops 的全局任务池。Agent 每轮必须优先从这里选择任务，禁止绕过任务队列自由发挥。

---

## TLDR_STATE_FOR_AGENT

当前任务状态：

- P0 Active：暂无
- P1 Active：暂无
- Blocked Human：暂无
- 本轮推荐任务：如无已有任务，请先根据研究目标创建 3 到 7 个候选任务，并标注优先级、依赖和自动运行安全性。

选择规则：

1. 优先 P0，其次 P1，再次 P2。
2. 跳过 `blocked_human`、`blocked_dependency`、`unsafe`。
3. 优先 `Safe to Run Automatically: Yes`。
4. 优先能产生证据、日志、实验结果、引用核验结果的任务。
5. 每轮只执行一个最小可验证单元。

---

## 1. 任务状态定义

| 状态 | 含义 |
|---|---|
| `todo` | 未开始 |
| `in_progress` | 正在执行 |
| `blocked_human` | 需要人类决策，只阻塞当前分支 |
| `blocked_dependency` | 等待其它任务产出 |
| `review_ready` | 等待审核 |
| `revision_needed` | 审核后需要修改 |
| `done` | 完成并通过质量门 |
| `archived` | 已归档 |
| `dropped` | 经记录后放弃 |

---

## 2. 优先级定义

| 优先级 | 含义 | 示例 |
|---|---|---|
| P0 | 当前阶段必须完成，否则主线无法推进 | 冻结实验协议、修复不可运行代码、确认核心 claim |
| P1 | 高价值任务，能显著降低风险或产生关键证据 | 补 baseline、核验核心引用、整理 failure cases |
| P2 | 中价值任务，增强论文完整性 | 补相关工作、改图表、补消融描述 |
| P3 | 低价值任务，可延后 | 美化格式、轻微润色、非关键 refactor |

---

## 3. 任务选择评分

Agent 可使用以下简化评分选择任务：

```text
Score = PriorityWeight + EvidenceValue + UnblockValue + SafetyBonus - CostPenalty - RiskPenalty
```

参考权重：

| 项 | 建议分值 |
|---|---|
| P0 | +50 |
| P1 | +30 |
| P2 | +15 |
| P3 | +5 |
| 能产生 A/B 级证据 | +25 |
| 能解除其它任务依赖 | +20 |
| Safe to Run Automatically: Yes | +10 |
| 成本高 | -10 |
| 有伦理、隐私、版权、付费风险 | -30 |
| 需要人类确认 | -50 |

如果分数相近，优先选择更小、更可验证、更容易交接的任务。

---

## 4. Active Tasks

> 新任务放在这里。每个任务必须使用下面的完整格式。

### TASK-YYYYMMDD-001

```yaml
Task ID: TASK-YYYYMMDD-001
Title: 初始化研究任务队列
Status: todo
Priority: P0
Owner: Research Orchestrator
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Inputs:
  - 用户给定的研究目标
  - 现有 research-ops 文档
Outputs:
  - 3 到 7 个可执行任务
  - 每个任务具备优先级、依赖、证据要求和安全性标记
Dependencies:
  - 无
Blocking:
  - 无
Evidence Required:
  - 更新后的 TASK_QUEUE.md
  - 更新后的 CURRENT_PROGRESS.md
Estimated Cost: Low
Risk Level: Low
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 每个任务都有明确输入、输出、完成标准
  - 至少一个 P0 或 P1 任务可立即执行
Fallback if Blocked:
  - 读取 CURRENT_PROGRESS.md 创建候选任务
Last Result:
  - 未执行
Next Action:
  - 根据当前研究目标填充任务池
```

---

## 5. Blocked Tasks

> 被人类决策或依赖阻塞的任务放在这里。阻塞任务不能阻塞整个项目。

暂无。

---

## 6. Done Tasks

> 完成并通过质量门的任务移动到这里，保留证据链接和交接摘要。

暂无。

---

## 7. Dropped Tasks

> 放弃的任务必须记录原因，防止未来反复踩坑。

暂无。

---

## 8. 新任务模板

```yaml
Task ID: TASK-YYYYMMDD-NNN
Title:
Status: todo
Priority: P0 / P1 / P2 / P3
Owner:
Created:
Updated:
Inputs:
  - 
Outputs:
  - 
Dependencies:
  - 
Blocking:
  - 
Evidence Required:
  - 
Estimated Cost: Low / Medium / High
Risk Level: Low / Medium / High / Critical
Safe to Run Automatically: Yes / No
Human Review Required: Yes / No
Quality Gate:
  - 
Fallback if Blocked:
  - 
Last Result:
  - 
Next Action:
  - 
```

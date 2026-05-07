# Multi-Agent Protocol

本文件定义多角色科研协作协议。v3.0 不再要求所有复杂任务必须真实并行，而是要求角色拆分、责任隔离和可审计交接。

---

## TLDR_STATE_FOR_AGENT

核心规则：

1. 复杂科研任务必须角色拆分。
2. 支持真实并行时，多 Agent 并行执行。
3. 不支持真实并行时，Research Orchestrator 串行模拟多个角色。
4. 每个角色必须有明确输入、输出、完成标准。
5. 角色之间的冲突必须记录，不得静默合并。
6. 角色输出必须写入任务报告或运行记录。
7. 子角色不得私自修改其它角色负责文件。

---

## 1. 角色池

| Agent | 职责 | 主要产出 |
|---|---|---|
| Research Orchestrator | 总控任务图、依赖、审核门 | 任务队列、状态表、周期报告 |
| Domain Analyst | 领域地图、术语、问题空间 | domain-map、open-problems |
| Literature Scout | 论文发现、引用追踪 | paper matrix、candidate papers |
| Paper Reader | 论文精读、证据抽取 | paper cards、evidence log |
| Citation Verifier | 引用核验 | citation map、invalid citation list |
| Hypothesis Agent | 研究假设生成与排序 | hypothesis backlog |
| Experiment Designer | 实验协议、baseline、指标 | experiment protocol |
| Execution Agent | 运行实验、记录日志 | run logs、result files |
| Statistics Agent | 统计分析、图表、显著性 | tables、figures |
| Writer Agent | 论文草稿 | manuscript draft |
| Reviewer Agent | 审稿模拟、红队检查 | review report |
| Archivist Agent | 归档复现材料 | artifact manifest |

---

## 2. 并行与串行模拟规则

### 2.1 支持真实并行时

1. Orchestrator 创建任务图。
2. 将无依赖冲突的任务分给不同 Agent。
3. 每个 Agent 独立产出交接报告。
4. Orchestrator 汇总输出。
5. 冲突进入 `RISKS.md` 或 `DECISIONS.md`。

### 2.2 不支持真实并行时

由 Orchestrator 串行模拟：

```text
Role Pass 1: Literature Scout
Role Pass 2: Experiment Designer
Role Pass 3: Reviewer Agent
Role Pass 4: Orchestrator Integration
```

要求：

1. 每次 Role Pass 必须声明角色。
2. 每个角色只处理自己职责内的问题。
3. 不同角色判断冲突时，必须保留冲突。
4. 不得用“综合考虑”掩盖证据差异。
5. 每个角色输出都必须进入运行记录或任务报告。

---

## 3. 任务状态

| 状态 | 含义 |
|---|---|
| `todo` | 未开始 |
| `in_progress` | 正在执行 |
| `blocked_human` | 需要人类决策，只阻塞当前分支 |
| `blocked_dependency` | 等待另一个任务产出 |
| `review_ready` | 等待审核 |
| `revision_needed` | 审核后需要修改 |
| `done` | 完成并通过质量门 |
| `archived` | 已归档 |
| `dropped` | 已放弃并记录原因 |

---

## 4. 任务分发格式

```text
Task ID:
Owner Agent:
Inputs:
Expected Outputs:
Evidence Requirements:
Human Review Required: Yes / No
Dependencies:
Quality Gate:
Fallback if Blocked:
```

---

## 5. Agent 输出格式

```text
Task ID:
Role:
Status:
Files Produced or Updated:
Evidence Used:
Claims Made:
Open Questions:
Human Decisions Required:
Conflicts:
Recommended Next Tasks:
```

---

## 6. Agent 交接报告格式

```text
## Agent Handoff Report

Task ID:
Agent:
Status: Done / Blocked / Waiting Human Review / Failed

Summary:
Inputs Used:
Outputs Produced:
Key Findings:
Evidence:
Assumptions:
Limitations:
Open Questions:
Human Review Items:
Downstream Recommendations:
Quality Gate Result: Pass / Fail / Needs Review
```

---

## 7. 阻塞处理协议

| 问题类型 | 处理方式 |
|---|---|
| 缺少事实来源 | 继续检索，不需要人审 |
| 多个合理研究方向 | 写入 `DECISIONS.md`，继续做共同前置工作 |
| 数据集许可不明 | 写入 `DECISIONS.md`，寻找替代数据集 |
| baseline 是否纳入 | 写入 `DECISIONS.md`，继续实现已确定 baseline |
| 实验失败 | 自动排查；若需改变实验设计则人审 |
| 结果与假设相反 | 写入 `DECISIONS.md`，继续失败分析 |
| 投稿目标选择 | 必须人审；继续格式无关修订 |
| 角色输出冲突 | 写入 `RISKS.md`，由 Orchestrator 汇总 |

---

## 8. 冲突解决流程

1. 各 Agent 写明证据。
2. Orchestrator 汇总冲突。
3. 若能通过证据判定，自动解决并记录。
4. 若涉及价值判断或研究方向，写入 `DECISIONS.md`。
5. 决策未返回前，继续执行不依赖该冲突的任务。

冲突报告格式：

```text
Conflict ID: CONFLICT-YYYYMMDD-NNN
Type: Literature / Interpretation / Experiment / Writing / Ethics
Agents Involved:
Claims In Conflict:
Evidence For A:
Evidence For B:
AI Recommendation:
Human Review Required: Yes / No
```

---

## 9. 周期汇总报告格式

Orchestrator 每个周期输出：

```text
## Research Cycle Report

Cycle ID:
Date:
Overall Status:
Completed Tasks:
Running Tasks:
Blocked Tasks:
Human Review Queue:
Key Findings:
Risks:
Conflicts:
Next Parallel or Simulated Task Pool:
Recommended Human Actions:
```

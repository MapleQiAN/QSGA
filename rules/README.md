# AI 科研助手规范集 v3.1

这是一套面向 AI 辅助科研的 Research Ops 规范集。v3.1 的核心目标是：把 AI 从“遵守制度的科研助手”升级为“能持续推进、可审计、可交接、可压缩上下文、可自动质检的科研自动驾驶系统”。

---

## 0. v3.1 的核心升级

相比 v2.0，v3.1 新增和修改了以下机制：

1. 新增 `TASK_QUEUE.md`：所有工作必须进入任务队列，Agent 不再凭感觉自由发挥。
2. 新增 `protocols/EXECUTION_LOOP.md`：规定每轮 Agent 的执行算法。
3. 新增 `protocols/CONTEXT_POLICY.md`：规定默认读取内容、禁止读取内容、上下文预算和摘要块格式。
4. 修复初始化文件标题：不再出现 `# $(basename $f .md)`。
5. 修改多 Agent 规则：不再强制真实并行，允许 Orchestrator 在单窗口环境中串行模拟多个角色。
6. 所有大文档建议使用 `TLDR_STATE_FOR_AGENT` 顶部摘要块，避免每轮吞全文。
7. 自动推进规则改为：优先从 `TASK_QUEUE.md` 选择最高优先级、非阻塞、低风险、可验证的任务。
8. 新增 `scripts/check_research_ops.py`：用于检查任务队列、风险、决策、claim、实验结果、运行记录和基础文档结构。

---

## 1. 核心原则

1. **证据优先**  
   任何事实性科研陈述必须能追溯到论文、数据、实验记录、代码版本或明确的人类决策。

2. **任务队列驱动**  
   所有工作必须进入 `TASK_QUEUE.md`。Agent 每轮必须从任务队列中选择任务，而不是根据模糊的“下一步”自由发挥。

3. **异步推进**  
   遇到人类决策点时，写入 `DECISIONS.md`，然后继续处理不依赖该决策的任务。

4. **角色拆分**  
   复杂科研任务必须进行角色拆分和任务解耦。若当前环境不支持真实并行，则由 Orchestrator 串行模拟多 Agent，并保持独立输出、独立责任边界和冲突记录。

5. **上下文节制**  
   禁止每轮无脑加载全部文档。默认读取最小状态，按需读取相关章节，长文档必须优先读 `TLDR_STATE_FOR_AGENT`。

6. **人类签核**  
   研究方向、核心 claim、实验协议冻结、结论解释、投稿、署名和对外发布必须由人类签核。

---

## 2. 文档结构

| 文档 | 用途 | AI 读取策略 |
|---|---|---|
| `AGENTS.md` | AI 行为规范总入口 | 每轮必读摘要和自动推进规则 |
| `TASK_QUEUE.md` | 全局任务池 | 每轮读取 Top Active Tasks |
| `CURRENT_PROGRESS.md` | 当前阶段和运行状态 | 每轮必读摘要区 |
| `DECISIONS.md` | 人类决策队列 | 每轮读取 PendingReview / waiting_human |
| `RISKS.md` | 风险登记表 | 每轮读取 Critical / High active |
| `AUDIT_LOG.md` | 关键操作审计日志 | 关键操作时追加，不默认全文读取 |
| `protocols/EXECUTION_LOOP.md` | 每轮执行算法 | 每轮运行时遵循 |
| `protocols/CONTEXT_POLICY.md` | 上下文预算与读取规则 | 每轮运行时遵循 |
| `protocols/SOP.md` | 科研全流程标准作业程序 | 阶段规划时读取 |
| `protocols/MULTI_AGENT_PROTOCOL.md` | 多角色协作协议 | 拆分任务或冲突处理时读取 |
| `protocols/HUMAN_REVIEW_PROTOCOL.md` | 人审机制与决策格式 | 遇到人审节点时读取 |
| `protocols/QUALITY_GUARDRAILS.md` | 科研质量护栏 | 审稿、投稿、结论校准前读取 |
| `protocols/REVIEWER_GATE.md` | 审稿模拟规范 | 审稿模拟时读取 |
| `research/RESEARCH_PLAN.md` | 研究目标、范围、阶段状态 | 阶段规划时读取 |
| `research/PAPER_MATRIX.md` | 文献矩阵与 Claim-Evidence Matrix | 文献阶段或写作阶段读取相关章节 |
| `research/EXPERIMENT_PLAN.md` | 实验协议、baseline、指标 | 实验设计和执行阶段读取 |
| `research/RESULTS_LOG.md` | 实验结果与失败记录 | 实验阶段读取相关实验 |
| `research/DRAFT_STATUS.md` | 论文草稿章节与 claim 状态 | 写作阶段读取 |
| `runs/RUN_TEMPLATE.md` | 单次科研运行记录模板 | 每次运行复制使用 |
| `profiles/QSGA_PROFILE.md` | QSGA / QYIR 专用研究画像 | 仅在 QSGA 项目中启用 |
| `scripts/check_research_ops.py` | Research Ops 质量检查脚本 | 每轮结束后、投稿前、重大修改后运行 |

---

## 3. 最小可用运行方式

每次启动科研任务，AI 必须执行：

1. 读取 `AGENTS.md`、`TASK_QUEUE.md`、`CURRENT_PROGRESS.md`、`DECISIONS.md`、`RISKS.md` 的必要摘要。
2. 按照 `protocols/EXECUTION_LOOP.md` 选择本轮任务。
3. 创建或更新 `runs/YYYY-MM-DD-topic.md`。
4. 执行一个可验证的最小任务单元。
5. 更新 `TASK_QUEUE.md` 的任务状态。
6. 更新 `CURRENT_PROGRESS.md`。
7. 如有风险，更新 `RISKS.md`。
8. 如有决策点，写入 `DECISIONS.md`。
9. 如有关键操作，追加 `AUDIT_LOG.md`。
10. 运行 `python scripts/check_research_ops.py --root .`，修复 FAIL 项。
11. 输出本轮交接摘要。

---

## 4. 科研阶段速查

| 阶段 | 必须人审 | 关键产出 |
|---|---|---|
| S0 任务接收 | 最终研究目标 | 初始任务队列、运行记录、初始决策项 |
| S1 领域地图 | 否 | domain-map、术语表、问题空间 |
| S2 文献发现 | 可选 | paper matrix、citation seed |
| S3 文献精读 | 抽样 | paper cards、evidence log |
| S4 假设生成 | 研究问题确认 | hypothesis backlog、claim registry |
| S5 实验设计 | 协议冻结 | EXPERIMENT_PLAN、baseline list |
| S6 实验执行 | 异常时 | RESULTS_LOG、原始日志、失败记录 |
| S7 结果分析 | 主张校准 | result interpretation、claim update |
| S8 写作 | 摘要、贡献点、结论 | manuscript draft、DRAFT_STATUS |
| S9 审稿模拟 | 修订决策 | reviewer report、risk patch list |
| S10 发布归档 | 全部 | artifact manifest、reproducibility package |

---

## 5. 自动推进的默认策略

当用户要求“持续推进”“自动化”“自己往下做”“让 Agent 连续工作”时，AI 必须：

1. 优先选择 `TASK_QUEUE.md` 中最高优先级、非阻塞、低风险、可验证的任务。
2. 遇到阻塞时，不停止整体工作，而是把阻塞写入 `DECISIONS.md` 或任务状态，并切换到非阻塞任务。
3. 优先执行能够产生证据的任务，例如复现实验、核验引用、补 baseline、整理结果，而不是单纯润色文字。
4. 每轮只执行一个或少数几个可验证单元，避免大范围不可审计修改。
5. 每轮结束必须留下可交接摘要，让下一轮 Agent 不需要重新考古。

---

## 6. 建议使用方式

如果你把这套规范放入科研仓库，推荐目录结构：

```text
research-ops/
  AGENTS.md
  TASK_QUEUE.md
  CURRENT_PROGRESS.md
  DECISIONS.md
  RISKS.md
  AUDIT_LOG.md
  protocols/
  research/
  runs/
  profiles/
```

推荐让 AI 每轮第一句执行：

```text
请读取 research-ops/AGENTS.md、TASK_QUEUE.md、CURRENT_PROGRESS.md、DECISIONS.md、RISKS.md，并严格按照 EXECUTION_LOOP.md 推进一个最高优先级、非阻塞、低风险、可验证任务。不要等待人类确认，除非触发危险操作或核心研究决策。
```
---

## 7. 质量检查脚本

每轮 Agent 完成一个任务后，推荐运行：

```bash
python scripts/check_research_ops.py --root .
```

更严格的检查方式：

```bash
python scripts/check_research_ops.py --root . --strict
```

JSON 输出，适合接入 CI、GitHub Actions 或其它 Agent 工具链：

```bash
python scripts/check_research_ops.py --root . --json
```

脚本会检查：

- 必需文件是否存在。
- 是否还存在未展开的初始化标题。
- 长文档是否包含 `TLDR_STATE_FOR_AGENT`。
- `TASK_QUEUE.md` 中任务字段、状态、优先级、风险和自动运行标记是否合理。
- `DECISIONS.md` 是否存在待人审决策。
- `RISKS.md` 中 Critical / High 风险是否有缓解任务。
- `DRAFT_STATUS.md` 和 `PAPER_MATRIX.md` 中 claim 是否有证据等级。
- `RESULTS_LOG.md` 中实验结果是否有指标、命令、环境、seed、原始输出和失败记录。
- `runs/` 中是否有真实运行记录。

默认情况下，只有 FAIL 会导致非零退出码；`--strict` 模式下 WARN 也会导致非零退出码。


# AI 科研计划模板

## 1. 研究目标

```text
将自然语言量化策略生成建模为受约束、可验证、风险感知且具备安全拒绝边界的程序合成问题；基于当前 QSGA/QYIR 原型、QSI-Bench v1 和已完成 deterministic experiments，形成一篇 CCF C candidate paper draft，并记录投稿前必须补齐的证据、人审和复现材料。
```

## 2. 范围边界

| 项目 | 内容 |
|---|---|
| 研究领域 | LLM-assisted quantitative strategy generation; reliable program synthesis; risk-aware verification |
| 研究类型 | 方法论文 + benchmark + deterministic prototype evaluation |
| 目标产出 | CCF C candidate paper draft, claim matrix, reviewer report, reproducibility package |
| 不做什么 | 不声称收益保证、不声称实盘安全、不覆盖任意金融意图、不声称 SOTA、不在无人审情况下投稿或公开发布 |
| 高风险限制 | 金融场景；不得构成投资建议；投稿、公开、署名、利益冲突必须人审 |

## 3. 阶段状态

| 阶段 | 状态 | 必须人审 | 负责人 Agent | 输出位置 |
|---|---|---|---|---|
| S0 范围界定 | done | 是 | Research Orchestrator | `docs/ai-research-assistant/runs/2026-05-05-qsga-paper-run.md` |
| S1 领域地图 | partial | 否 | Domain Analyst | `docs/paper/qsga_ccf_c_draft.md` |
| S2 文献发现 | partial | 可选 | Literature Scout | `docs/ai-research-assistant/PAPER_MATRIX.md` |
| S3 文献精读 | pending | 抽样 | Paper Reader | pending PDF-level citation audit |
| S4 假设生成 | done | 是 | Hypothesis Agent | `docs/paper/citation_and_claim_matrix.md` |
| S5 实验设计 | done for prototype | 是 | Experiment Designer | `docs/ai-research-assistant/EXPERIMENT_PLAN.md` |
| S6 实验执行 | done for prototype | 异常时 | Execution Agent | `experiments/results/*.csv` |
| S7 结果分析 | done for prototype | 是 | Statistics Agent | `docs/ai-research-assistant/RESULTS_LOG.md` |
| S8 论文写作 | draft | 是 | Writer Agent | `docs/paper/qsga_ccf_c_draft.md` |
| S9 CCF C 审稿模拟 | done | 是 | CCF C Reviewer Agent / Reviewer Agents | `docs/paper/ccf_c_reviewer_report.md` |
| S10 归档发布 | internal only | 是 | Archivist Agent | `docs/paper/reproducibility_package.md` |

## 4. 当前待解决问题

| ID | 问题 | 是否人审 | 阻塞范围 | AI 可继续任务 |
|---|---|---|---|---|
| OPEN-20260505-001 | 是否追加 live LLM 实验 | 是 | 最终摘要、结果强度、投稿判断 | 保守版论文修订、引用核验 |
| OPEN-20260505-002 | 是否公开代码/数据/论文 | 是 | 外部发布、投稿材料 | 内部复现包完善 |
| OPEN-20260505-003 | 关键引用是否升级到 PDF-level Level A | 可选但强烈建议 | Related Work 最终版 | 继续整理 citation map |

# AI 科研人类决策登记表

本文件用于登记 AI 在科研流程中遇到的、必须由人类决定的问题。AI 写入决策项后，不得停止全部工作，必须继续推进不依赖该决策的任务。

## 状态说明

| 状态 | 含义 |
|---|---|
| `waiting_human` | 等待人类决策 |
| `need_more_evidence` | 人类要求 AI 补充证据 |
| `approved` | 人类批准 |
| `rejected` | 人类拒绝 |
| `superseded` | 被后续决策替代 |
| `applied` | 决策已执行 |

## 待决策队列

### DEC-20260505-001

Status: waiting_human
Owner: human
Raised by: Codex
Date: 2026-05-05
Deadline: before submission

Question:

是否追加 live LLM 生成实验，还是将论文明确定位为 deterministic prototype / system study？

Context:

当前 `experiments/baselines.py` 明确避免 live LLM 调用以保证 CI 可复现。现有结果足以支持“当前原型中验证链有效”，但不足以支持“真实 LLM 在线生成普遍有效”的强结论。

Options:
1. 追加 live LLM 实验：固定模型、prompt、temperature、日志与失败样本。
2. 不追加实验：将论文主张收紧为 deterministic prototype evaluation。
3. 先投 workshop / demo / 系统短文，再扩展主会版本。

AI recommendation:

优先选择 1；如果时间或 API 成本受限，选择 2，并在标题、摘要、实验章节和 Limitations 中明确 prototype 范围。

Evidence:

- `experiments/baselines.py` module docstring states the harness avoids live LLM calls.
- `docs/paper/ccf_c_reviewer_report.md` flags this as P1.

Risk if approved:

增加成本和运行时间，但能显著降低审稿人对实验真实性的攻击。

Risk if rejected:

论文必须降低主张；若仍按 LLM 系统论文投稿，可能被认为实验过于合成。

What is blocked:

最终摘要、实验结论强度、投稿目标选择。

What AI will continue doing:

完善 deterministic 版本论文、引用核验、复现包和 reviewer 风险清单。

Human decision:

pending

Decision rationale:

pending

Follow-up actions:

pending

### DEC-20260505-002

Status: waiting_human
Owner: human
Raised by: Codex
Date: 2026-05-05
Deadline: before public release or submission

Question:

是否允许公开代码、benchmark、实验结果和论文草稿？

Context:

科研规范要求投稿、公开仓库、公开数据、署名和利益冲突声明必须人审。当前仓库包含实验数据、生成论文草稿和 AI 使用记录。

Options:
1. 允许公开完整复现包。
2. 只公开论文和必要实验表，暂不公开完整代码。
3. 暂不公开，内部审阅后再定。

AI recommendation:

默认选择 3，直到人类确认许可、署名、目标会议和发布边界。

Evidence:

- `AI_RULES.md` 危险操作清单。
- `QUALITY_GUARDRAILS.md` Human Approval Gate。

Risk if approved:

可能暴露未审核材料、许可不清文件或不成熟结论。

Risk if rejected:

短期影响可复现性展示，但不影响内部论文修订。

What is blocked:

投稿公开材料、代码仓库公开、数据公开。

What AI will continue doing:

准备内部复现说明和可审阅材料。

Human decision:

pending

Decision rationale:

pending

Follow-up actions:

pending

### DEC-20260505-003

Status: waiting_human
Owner: human
Raised by: Codex
Date: 2026-05-05
Deadline: before submission

Question:

是否接受当前 CCF C Reviewer 模拟审稿给出的 Borderline 评级，并按 P1 项继续补实验/核引用？

Context:

模拟审稿认为论文具有 CCF C 潜力，但 live LLM 实验和引用 PDF 级核验不足。

Options:
1. 接受评级并补 P1。
2. 降低目标为课程论文、技术报告或 workshop。
3. 重构贡献点后再审。

AI recommendation:

选择 1。

Evidence:

- `docs/paper/ccf_c_reviewer_report.md`

Risk if approved:

需要额外实验与核验工作。

Risk if rejected:

当前草稿仍可作为技术报告，但距离“可投 CCF C”存在明显证据缺口。

What is blocked:

最终投稿判断。

What AI will continue doing:

保守版论文修订、文献矩阵完善。

Human decision:

pending

Decision rationale:

pending

Follow-up actions:

pending

### DEC-20260505-004

Status: waiting_human
Owner: human
Raised by: Codex
Date: 2026-05-05
Deadline: before submission

Question:

CCF C Reviewer 模拟审稿更新后，对标准 empirical LLM paper 给出 Weak Reject-level、对 prototype/IR feasibility study 给出 Borderline。是否继续补 live LLM baselines，还是将投稿定位改为 prototype/IR 可行性论文？

Context:

SubAgent 审稿指出 oracle-slot construction、simulated baselines、safe rejection 共享规则等问题。主线程已新增 no-oracle deterministic slot extraction，E2E=0.7625，缓解但未替代 live LLM evidence。

Options:
1. 补 live LLM 实验：固定模型、prompt、temperature、保存 raw outputs，并替换/补充 simulated baselines。
2. 不补 live LLM：将论文定位为 deterministic prototype / IR feasibility study，目标改为更匹配的系统短文、workshop、demo 或课程论文。
3. 先补 no-oracle / clarification / multi-symbol 等本地实验，再决定是否补 live LLM。

AI recommendation:

选择 1。如果当前没有 API key 或预算，选择 3 作为中间步骤，但不要按标准 empirical LLM paper 直接投稿。

Evidence:

- `docs/paper/ccf_c_reviewer_report.md`
- `docs/paper/subagent_experiment_audit.md`
- `docs/paper/subagent_adversarial_review.md`
- `experiments/results/no_oracle_metrics.csv`

Risk if approved:

需要 API key、成本预算和额外实验时间，但能最大幅度降低拒稿风险。

Risk if rejected:

论文只能保守定位，不能强称 live LLM strategy generation performance。

What is blocked:

投稿目标、最终摘要、最终贡献强度、是否可按 CCF C 标准 empirical paper 投出。

What AI will continue doing:

继续补本地实验、失败案例、PDF 级引用核验和论文排版。

Human decision:

pending

Decision rationale:

pending

Follow-up actions:

pending

## 决策模板

```markdown
### DEC-YYYYMMDD-NNN

Status: waiting_human
Owner: human
Raised by:
Date:
Deadline:

Question:

Context:

Options:
1. 
2. 
3. 

AI recommendation:

Evidence:

Risk if approved:

Risk if rejected:

What is blocked:

What AI will continue doing:

Human decision:

Decision rationale:

Follow-up actions:
```

## 审计要求

1. 不得删除历史决策项。
2. 若决策被替代，标记为 `superseded` 并链接新决策。
3. 若决策已执行，标记为 `applied` 并说明影响的文件、实验或论文段落。
4. 若人类口头给出决策，AI 必须转写到本文件并请求确认。

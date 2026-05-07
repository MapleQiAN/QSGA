# AI 科研风险、冲突与不确定性登记表

本文件记录科研流程中的风险、冲突、未验证假设和升级项。风险不得通过删除或覆盖记录来“解决”。

## 风险等级

| 等级 | 含义 | 动作 |
|---|---|---|
| P0 | 高风险，涉及伦理、发布、署名、违法或不可逆外部动作 | 立即停止相关动作，等待人审 |
| P1 | 影响研究有效性、合规或核心结论 | 暂停相关分支，继续无关任务 |
| P2 | 影响效率或局部质量 | 记录并尝试替代路径 |
| P3 | 低风险改进建议 | 放入 backlog |

## 风险模板

```markdown
### RISK-YYYYMMDD-NNN

Status: open / mitigated / accepted / superseded
Priority: P0 / P1 / P2 / P3
Raised by:
Related task:
Related decision:

Risk:

Evidence:

Impact:

Mitigation:

Human review required:

Resolution:
```

## 冲突模板

```markdown
### CONFLICT-YYYYMMDD-NNN

Status: open / resolved / escalated
Conflict type: Literature / Interpretation / Experiment / Writing / Priority / Ethics
Agents involved:

Claim A:
Evidence for A:

Claim B:
Evidence for B:

AI recommendation:

Downstream impact:

Human review required:
```

## 当前风险

### RISK-20260505-001

Status: open
Priority: P1
Raised by: Codex
Related task: QSGA CCF C paper draft
Related decision: DEC-20260505-001

Risk:

主实验仍是 deterministic prototype evaluation；现已补充小规模 live LLM QYIR pilot，但样本量和 baseline 覆盖不足，因此不能强声称 QSGA 对真实 LLM 生成有普遍改进。

Evidence:

`experiments/baselines.py` module docstring；`experiments/results/live_llm_metrics.csv` 显示 live pilot 仅 12-case subset，且 E2E 仍较低。

Impact:

若摘要或结论写成一般 LLM 生成效果，可能触发审稿拒稿风险。

Mitigation:

已追加 budget-bounded live pilot；论文必须继续限定为 deterministic prototype + small live pilot evidence。若要强 live claim，需要扩大 live benchmark 并加入 executable direct-code baseline。

Human review required:

Yes

Resolution:

partially mitigated by `experiments/run_live_llm.py` and live pilot; remains open for broad live LLM claims

### RISK-20260505-002

Status: open
Priority: P1
Raised by: Codex
Related task: citation verification
Related decision: none

Risk:

当前引用为 metadata/link-level verification，尚未完成 PDF 级 claim-location 核验。

Evidence:

`docs/paper/citation_and_claim_matrix.md` 将文献标为 Level B。

Impact:

投稿前若引用支撑不精确，可能构成 related work 弱点或误引风险。

Mitigation:

对核心引用升级到 Level A：打开 PDF，记录章节/表格/具体 claim。

Human review required:

Optional but recommended

Resolution:

pending

### RISK-20260505-003

Status: open
Priority: P2
Raised by: Codex
Related task: experiment interpretation
Related decision: none

Risk:

`wo_semantic_verification` 与 full QSGA 指标相同，不能将 semantic verifier 写成 oracle-slot 主实验中独立贡献的经验增益来源。

Evidence:

`experiments/results/ablation_metrics.csv`

Impact:

如果过度声称语义验证模块带来独立提升，会造成结论强于证据。

Mitigation:

将其表述为多阶段验证链的一部分，并承认 oracle-slot deterministic 设置未显示独立指标增益。已新增 schema-valid slot-corruption 实验，隔离证明 semantic verifier 能发现 schema validation 无法发现的显式意图槽冲突。

Human review required:

No

Resolution:

mitigated in `docs/paper/qsga_ccf_c_draft.md` and `experiments/results/semantic_corruption_metrics.csv`

### RISK-20260505-004

Status: open
Priority: P2
Raised by: Codex
Related task: research SOP compliance
Related decision: none

Risk:

本轮未实际启动多个子 Agent；原因是当前系统指令要求只有用户明确请求 sub-agents 时才可 spawn。

Evidence:

本轮执行记录 `docs/ai-research-assistant/runs/2026-05-05-qsga-paper-run.md`。

Impact:

与本地科研 SOP 的“复杂科研任务必须拆分为多个 Agent 并行执行”存在流程偏差。

Mitigation:

已采用单进程角色模拟并记录偏差；若用户明确允许，下一轮可用真实 sub-agent 复核文献、实验和审稿。

Human review required:

No

Resolution:

accepted for this run

### RISK-20260505-005

Status: open
Priority: P1
Raised by: Experiment and Reproducibility Auditor / Adversarial CCF-C Reviewer
Related task: QSGA CCF C paper draft
Related decision: DEC-20260505-001

Risk:

当前 `qsga_full` 使用 benchmark `expected_slots` 构造 QYIR，因此主实验是 oracle-slot verification-chain validation，不是无 oracle 的自然语言槽位抽取或真实 LLM 生成实验。

Evidence:

`experiments/baselines.py` 中 `build_qyir_from_record(record)` 读取 `record.get("expected_slots")`；`docs/paper/subagent_experiment_audit.md` 与 `docs/paper/subagent_adversarial_review.md` 均标为 Critical。

Impact:

若论文继续声称 end-to-end natural-language strategy generation，会被审稿人认为存在 label/oracle leakage。

Mitigation:

正文已改为 oracle-slot deterministic prototype evaluation；已新增 deterministic no-oracle slot extraction 实验和小规模 live QYIR pilot。投稿前若要强 live claim，仍建议扩大 live LLM generation 实验。

Human review required:

Yes

Resolution:

partially mitigated in `docs/paper/qsga_ccf_c_draft.md`, `experiments/run_no_oracle.py`, and `experiments/run_live_llm.py`; remains blocker for broad live LLM claims

### RISK-20260505-006

Status: open
Priority: P1
Raised by: Experiment and Reproducibility Auditor / Adversarial CCF-C Reviewer
Related task: baseline fairness
Related decision: DEC-20260505-001

Risk:

`direct_code` 和 `direct_json` 是 deterministic simulated baselines，不是保存的 live LLM 输出；因此不能支撑强比较结论。

Evidence:

`experiments/baselines.py`; `docs/paper/subagent_experiment_audit.md`; `docs/paper/subagent_adversarial_review.md`。

Impact:

审稿人可能认为主结果是 oracle pipeline vs synthetic baselines。

Mitigation:

正文已将 main baselines 标注为 simulated；已补充 executable live direct-code baseline 和 shared-rejection replay。投稿前仍不得声称 broad direct-code superiority 或 broad QSGA superiority。

Human review required:

Yes

Resolution:

partially mitigated in draft, live QYIR pilot, executable live direct-code baseline, and shared-rejection replay; remains blocker for broad empirical claims

### RISK-20260506-001

Status: open
Priority: P2
Raised by: Codex
Related task: live QYIR/direct-code interpretation
Related decision: DEC-20260505-001

Risk:

`live_direct_code_shared_rejection` E2E 高于 `live_qsga_qyir`，但该 replay 只证明共享拒绝门对 direct-code unsafe rows 有帮助，不能证明 direct code 获得 QYIR 的 semantic localization、risk slots 或 repairability。

Evidence:

`experiments/results/live_direct_code_shared_rejection_metrics.csv` reports E2E 0.5375; `experiments/results/live_qyir_80_metrics.csv` reports live QSGA QYIR E2E 0.375 and construction success 0.0909.

Impact:

若正文把 shared wrapper 结果解释为 direct-code 已经等价于 QSGA，或反过来声称 live QYIR 更强，都会造成证据错配。

Mitigation:

正文将 live QYIR 写成 bottleneck diagnostic，并将 shared direct-code replay 写成 boundary-control evidence only；QYIR claim 限定在 interpretable slots、semantic localization、risk-slot auditing、localized repair。

Human review required:

Yes

Resolution:

open until human review of final claim framing

### RISK-20260505-007

Status: open
Priority: P2
Raised by: Experiment and Reproducibility Auditor
Related task: ambiguous intent evaluation
Related decision: none

Risk:

旧口径下 ambiguous_intent 10 个样本在 `qsga_full` 中 E2E 成功为 0/10；现已加入 clarification success 指标，但该指标仍是 deterministic single-turn gate，不等于真实多轮澄清能力。

Evidence:

`experiments/results/baseline_metrics.csv` and `experiments/results/no_oracle_metrics.csv` show clarification accuracy 1.000; `docs/paper/subagent_experiment_audit.md` records the original gap.

Impact:

不能声称当前实验已经验证真实 live 多轮澄清能力。

Mitigation:

正文已新增 clarification metric，并把 ambiguous cases 从 construction success 拆出；后续仍需 live constrained generation / structured dialogue evaluation。

Human review required:

No

Resolution:

partially mitigated in draft and metrics; live multi-turn clarification remains future work

### RISK-20260507-001

Status: open
Priority: P2
Raised by: V4 reviewer-risk report / Codex
Related task: QSGA paper V4 hardening
Related decision: none

Risk:

The paper uses novice-facing motivation but does not include a human-subject usability study.

Evidence:

`docs/paper/ccf_c_reviewer_report_v4.md` recommends either weakening novice usability claims or adding a small user experiment. The current revision chose claim weakening and added a threat-to-validity subsection.

Impact:

The paper can claim artifact-level inspectability and explicitness, but cannot claim measured improvements in novice understanding, editability, or decision quality.

Mitigation:

`docs/paper/qsga_ccf_c_draft.md` now states that novice-facing usability is not yet measured. A future version may add a 6-10 participant study comparing QYIR and direct code interpretability.

Human review required:

No

Resolution:

open as future-work risk; mitigated for current CCF C draft by claim weakening

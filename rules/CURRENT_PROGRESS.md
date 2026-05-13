# CURRENT_PROGRESS.md

本文件记录当前研究项目的阶段、进度、可继续推进任务和交接信息。

---

## TLDR_STATE_FOR_AGENT

当前阶段：

- S0 任务接收 / S5 实验设计前置实现

当前有效结论：

- 路线 B 目标已明确：将 QSGA 从后端 IR 验证主张推进为 verification-guided NL-to-QYIR construction + verification 主张。
- Route B 官方 DeepSeek 80-case live 诊断已生成；可写入已验证数字，但必须保持 diagnostic claim。
- TASK-20260512-002 已完成：Route B slot schema、canonicalizer、deterministic QYIR builder 已实现，并通过全量测试。
- TASK-20260512-003 已完成：现有 live QYIR 结果已生成 failure breakdown，可作为 Route B failure-reduction analysis 的诊断证据。
- TASK-20260512-004 已完成：Route B 实验协议草案已初始化，但尚未冻结。
- TASK-20260512-005 已完成：Route B 论文已在既有 `docs/paper/qsga_ccf_draft.md` 基础上改写，不再使用新建草稿。
- TASK-20260512-007 已完成：offline builder smoke runner 已实现；expected slots 输入下 builder construct 55/55，terminal action 80/80。
- TASK-20260512-008 已完成：Route B slot extractor、pipeline、live runner skeleton 已实现并通过全量测试；未调用 API。
- TASK-20260512-009 已完成：初始 DashScope endpoint smoke 失败后，已按 DEC-20260512-002 切换官方 DeepSeek API 并完成 5-case/80-case live 诊断。
- TASK-20260512-011 已完成：Route B 状态汇总表已生成，明确 safe claims 与 forbidden claims。

当前阻塞：

- 实验协议冻结、核心 claim 升级仍需人类确认。

最近更新：

- 2026-05-12：根据 docs/QSGA_Route_B_Modification_Plan.md 初始化 Route B 任务队列。
- 2026-05-12：新增 qsgi/construction 基础模块；`uv run pytest` 通过 187 项测试。
- 2026-05-12：新增 `experiments/analyze_failure_breakdown.py`，生成 `live_failure_breakdown.csv` 和 `live_failure_breakdown.md`。
- 2026-05-12：更新 `rules/research/EXPERIMENT_PLAN.md`，记录 Route B draft protocol。
- 2026-05-12：按用户纠正，删除新建 Route B 草稿，改为在 `docs/paper/qsga_ccf_draft.md` 上完成 Route B 改写。
- 2026-05-12：新增 `experiments/run_route_b_builder_smoke.py`，生成 builder smoke 结果。
- 2026-05-12：新增 `experiments/run_live_route_b.py` 和 mocked pipeline tests；`uv run pytest` 通过 200 项。
- 2026-05-12：运行 bounded live smoke，因 API authentication failure 失败；已登记失败结果、风险和人审决策。
- 2026-05-12：新增 `experiments/tables/route_b_status_summary.md`，用于论文状态和 claim 边界。
- 2026-05-12：按官方 DeepSeek API 文档接入 `https://api.deepseek.com`，完成 official `deepseek-v4-flash` 80-case Route B live 诊断；E2E 38/80，constructible construction success 20/55。

下一步：

- TASK-20260512-012 已完成：DEC-20260512-003 已起草，建议当前 paper cycle 不改 QYIR v1 schema/compiler contract。
- TASK-20260512-013 已完成：完成一轮 Route B reviewer gate / limitation tightening，修正 retry loop、脚本清单和测试数。

---

## Current Stage

```yaml
Stage: S0 任务接收
Status: in_progress
Last Updated: 2026-05-12
Owner: Research Orchestrator
```

---

## Active Research Goal

```text
将 QSGA/QYIR 课题推进到路线 B：构建 verification-guided natural-language-to-QYIR construction pipeline，并在不伪造结果的前提下为 CCF-B 级别论文补足方法、实验和写作证据。
```

---

## Current Focus

```text
1. 实现 slot schema、canonicalizer、deterministic QYIR builder 等构造基础模块。
2. 诊断现有 live prompt-only QYIR 失败类型，形成 failure reduction analysis 的输入。
3. 设计 Route B 实验协议草案，再决定是否运行 live API smoke / batch 实验。
```

---

## Next Actions

1. 执行 TASK-20260513-007，完成 bibliography venue/DOI formatting pass。
2. 若人类决定需要第二个 full 80-case live model，再创建需人审的 scoped API run 任务。
3. 不修改 QYIR v1 schema/compiler contract；将 market-field operands 作为 future work，并继续使用 builder 层兼容转换。

---

## Recent Completed Work

- TASK-20260512-001：初始化 Route B 研究任务队列。
- TASK-20260512-002：实现 Route B 构造基础模块并通过全量测试。
- TASK-20260512-003：生成 live failure breakdown 并登记结果。
- TASK-20260512-004：初始化 Route B 实验协议草案。
- TASK-20260512-005：创建 Route B working draft。
- TASK-20260512-007：实现 offline builder smoke runner 并登记结果。
- TASK-20260512-008：实现 Route B live runner skeleton，并通过 mocked tests。
- TASK-20260512-009：运行 bounded live smoke；初始 endpoint 失败，官方 DeepSeek endpoint 后续成功。
- TASK-20260512-011：生成 Route B 状态汇总表。

---

## Current Evidence Summary

- 已确认现有规则要求任务队列驱动、证据优先、禁止伪造数据。
- docs/QSGA_Route_B_Modification_Plan.md 提供 Route B 方法和实验目标，但其中所有 XX 或成功率提升均为待实验验证。
- `uv run pytest tests -q`：213 passed，说明当前 Route B remediation 未破坏现有 QYIR validator/compiler/generator 测试。
- EXP-20260512-LIVE-FAILURE-BREAKDOWN：saved qwen3.6-flash live-QYIR run 的主要失败桶已记录在 RESULTS_LOG。
- EXP-20260512-ROUTE-B-BUILDER-SMOKE：expected-slot builder smoke 达到 construct 55/55，terminal correct 80/80；仅支持 gold-slot builder claim。
- EXP-20260512-ROUTE-B-LIVE-DEEPSEEK-OFFICIAL-80：official `deepseek-v4-flash` Route B live 诊断达到 schema_validity 0.709、construction_success 0.364、E2E 0.475、unsafe rejection 1.000、clarification accuracy 0.300。
- TASK-20260512-014：外部 related-work 引用已完成 arXiv primary-source 核验；剩余工作是最终 venue/DOI 格式化。
- EXP-20260513-ROUTE-B-AMBIGUITY-GUARD-CHECK：deterministic ambiguity guard 在 QSI-Bench 上达到 ambiguous recall 10/10、non-ambiguous false positive 0/70、overall 80/80；尚未更新 official live metrics。
- EXP-20260513-ROUTE-B-SAVED-REPLAY-AFTER-AMBIGUITY-GUARD：无 API replay 达到 clarification_accuracy 1.000、E2E 0.5625；这不是新的 live run。
- EXP-20260513-ROUTE-B-SAVED-REPLAY-WITH-RISK-REPAIR：无 API replay + bounded risk repair 达到 risk_violation 0.000、repair_success 19/19、construction_success 0.709、E2E 0.800；这不是新的 live run。
- EXP-20260513-ROUTE-B-SAVED-REPLAY-POLICY-RISK-REPAIR：无 API replay + scope/defaulting policy + risk repair 达到 construction_success 0.727、E2E 0.8125，并将 11/80 剩余样例明确标为 unsupported_semantics；这不是新的 live run。
- Full verification：`uv run pytest tests -q` 通过 213 项测试；`uv run python rules/scripts/check_research_ops.py --root rules` 通过，FAIL 0 / WARN 0。
- Reviewer gate snapshot：当前禁止声称 CCF-B ready；阻塞项为人类目标会议/作者/发布边界、是否追加第二个 full live model、最终 bibliography venue/DOI 格式、金融安全措辞人审。

---

## Current Risks Summary

- Route B 的核心风险是把未验证的 construction success 提升写成结论。
- live API 批量实验已可运行，但后续新增大批量/pro-model 实验仍需控制成本并记录范围。
- 当前最大方法风险是将 single-model diagnostic 误写成广泛模型结论。

---

## Human Decision Summary

- DEC-20260512-002：已接受官方 DeepSeek API endpoint/configuration；不再阻塞当前 Route B live 诊断。
- DEC-20260512-003：人工选择方案 A；QYIR v1 保持 alias-only operand contract，market-field operands 作为 future work。

---

## Handoff Notes

```text
下一轮 Agent 应先读取：
- AGENTS.md
- TASK_QUEUE.md
- CURRENT_PROGRESS.md
- DECISIONS.md
- RISKS.md
- protocols/EXECUTION_LOOP.md
- protocols/CONTEXT_POLICY.md
- docs/QSGA_Route_B_Modification_Plan.md
```

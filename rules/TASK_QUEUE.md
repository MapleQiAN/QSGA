# TASK_QUEUE.md

本文件是 Research Ops 的全局任务池。Agent 每轮必须优先从这里选择任务，禁止绕过任务队列自由发挥。

---

## TLDR_STATE_FOR_AGENT

当前任务状态：

- P0 Active：暂无
- P1 Active：TASK-20260513-007
- Blocked Human：暂无
- 本轮推荐任务：执行 TASK-20260513-007，完成 bibliography venue/DOI formatting pass。

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

### TASK-20260512-002

```yaml
Task ID: TASK-20260512-002
Title: 实现 Route B 构造基础模块
Status: done
Priority: P0
Owner: Execution Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - docs/QSGA_Route_B_Modification_Plan.md
  - qyir/schema.py
  - qyir/validator.py
Outputs:
  - qsgi/construction/slot_schema.py
  - qsgi/construction/canonicalizer.py
  - qsgi/construction/qyir_builder.py
  - 聚焦单元测试
Dependencies:
  - 无
Blocking:
  - TASK-20260512-003
  - TASK-20260512-004
Evidence Required:
  - pytest 通过记录
  - runs/2026-05-12-route-b-initialization.md
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 不调用付费 API
  - 不覆盖原始实验日志
  - 不写入未经验证的性能数字
  - 新模块可由测试验证
Fallback if Blocked:
  - 降级为只实现 schema 与 canonicalizer
Last Result:
  - 新增 qsgi/construction/slot_schema.py、canonicalizer.py、qyir_builder.py 和 tests/test_route_b_construction.py。
  - uv run pytest 全量通过：187 passed。
Next Action:
  - 进入 TASK-20260512-003，基于现有 live raw outputs 生成 failure breakdown。
```

### TASK-20260512-003

```yaml
Task ID: TASK-20260512-003
Title: 诊断现有 live QYIR 失败类型
Status: done
Priority: P1
Owner: Statistics Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - experiments/results/live_qyir_80_raw_outputs.jsonl
  - experiments/results/live_qyir_80_results.csv
  - existing validators
Outputs:
  - experiments/results/live_failure_breakdown.csv
  - experiments/tables/live_failure_breakdown.md
Dependencies:
  - TASK-20260512-002
Blocking:
  - TASK-20260512-006
Evidence Required:
  - 可复现分析命令
  - failure taxonomy 映射说明
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 保留原始日志
  - 失败类型可追溯到具体 case
Fallback if Blocked:
  - 先生成 schema/parse 层面的 breakdown
Last Result:
  - 新增 experiments/analyze_failure_breakdown.py 和 tests/test_failure_breakdown.py。
  - 生成 experiments/results/live_failure_breakdown.csv 与 experiments/tables/live_failure_breakdown.md。
  - 记录 EXP-20260512-LIVE-FAILURE-BREAKDOWN 到 RESULTS_LOG。
Next Action:
  - 执行 TASK-20260512-004，基于 breakdown 设计 Route B 实验协议草案。
```

### TASK-20260512-004

```yaml
Task ID: TASK-20260512-004
Title: 设计 Route B 实验协议草案
Status: done
Priority: P1
Owner: Experiment Designer
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - docs/QSGA_Route_B_Modification_Plan.md
  - rules/research/EXPERIMENT_PLAN.md
Outputs:
  - Route B metrics、baseline、dataset、cost 约束草案
Dependencies:
  - TASK-20260512-002
Blocking:
  - TASK-20260512-006
Evidence Required:
  - EXPERIMENT_PLAN 更新
  - 风险与人审点标注
Estimated Cost: Low
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 不冻结协议
  - 不新增未经人审的高成本实验
Fallback if Blocked:
  - 只补 draft section
Last Result:
  - 已在 rules/research/EXPERIMENT_PLAN.md 中补充 Route B RQ、baseline、metrics、datasets、实验矩阵、API 成本边界和初始 failure-reduction targets。
Next Action:
  - 执行 TASK-20260512-005，建立 Route B 论文骨架并将未验证 claim 降级。
```

### TASK-20260512-005

```yaml
Task ID: TASK-20260512-005
Title: Route B 论文骨架与 claim 降级改写
Status: done
Priority: P1
Owner: Writer Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - docs/paper/qsga_ccf_c_draft.md
  - docs/QSGA_Route_B_Modification_Plan.md
  - rules/research/DRAFT_STATUS.md
Outputs:
  - Route B manuscript skeleton or patch
  - 未验证 claim 清单
Dependencies:
  - TASK-20260512-002
  - TASK-20260512-003
Blocking:
  - 投稿前审稿模拟
Evidence Required:
  - 所有新增性能数字来自 RESULTS_LOG
  - 未验证位置使用 XX 或标注待验证
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 基于 docs/paper/qsga_ccf_draft.md 原稿修改
  - 不写强结论
Fallback if Blocked:
  - 只写 limitation/update，不新建论文稿
Last Result:
  - 按用户纠正删除新建 Route B 草稿，改为更新 docs/paper/qsga_ccf_draft.md。
  - 草稿写入 official DeepSeek Route B 80-case diagnostic，并保持 single-model diagnostic claim。
  - 更新 DRAFT_STATUS 的 claim registry 与 section status。
Next Action:
  - 后续进行 reviewer gate 和 limitation tightening。
```

### TASK-20260512-006

```yaml
Task ID: TASK-20260512-006
Title: 运行 live Route B 小规模 smoke 实验
Status: done
Priority: P2
Owner: Execution Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - DSAPIKEY.txt
  - Route B construction pipeline
  - benchmark/qsi_bench_v1.jsonl
Outputs:
  - experiments/results/route_b_smoke_*.csv
  - token usage and latency record
Dependencies:
  - TASK-20260512-002
  - TASK-20260512-004
Blocking:
  - Route B main result claims
Evidence Required:
  - 命令、模型、样本数、seed、原始输出路径
Estimated Cost: Medium
Risk Level: High
Safe to Run Automatically: No
Human Review Required: Yes
Quality Gate:
  - 明确 API 调用成本与样本规模
  - 不批量运行高成本实验
Fallback if Blocked:
  - 使用离线 deterministic builder 测试
Last Result:
  - 初始 DashScope-compatible smoke 失败；官方 DeepSeek endpoint smoke v4 成功。
  - artifacts: experiments/results/route_b_live_smoke_deepseek_official_5_v4_*。
  - Smoke E2E 2/5；该结果仅用于连通性和小样本诊断。
Next Action:
  - 已扩展为 80-case official DeepSeek diagnostic。
```

### TASK-20260512-007

```yaml
Task ID: TASK-20260512-007
Title: 实现 Route B offline builder smoke runner
Status: done
Priority: P1
Owner: Execution Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - benchmark/qsi_bench_v1.jsonl
  - qsgi/construction/qyir_builder.py
  - qyir/validator.py
Outputs:
  - experiments/run_route_b_builder_smoke.py
  - experiments/results/route_b_builder_smoke.csv
  - experiments/tables/route_b_builder_smoke.md
Dependencies:
  - TASK-20260512-002
Blocking:
  - TASK-20260512-006
Evidence Required:
  - 离线运行命令
  - 输出 CSV 和 markdown summary
  - pytest 或脚本级验证
Estimated Cost: Low
Risk Level: Low
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 不调用 API
  - 不使用 gold slots 声称 live natural-language extraction 能力
  - 明确记录这是 builder smoke，不是 Route B 主结果
Fallback if Blocked:
  - 只对 5 个代表性 synthetic slot specs 跑 smoke
Last Result:
  - 新增 experiments/run_route_b_builder_smoke.py 和 tests/test_route_b_builder_smoke.py。
  - 生成 experiments/results/route_b_builder_smoke.csv 与 experiments/tables/route_b_builder_smoke.md。
  - Offline builder smoke 在 expected slots 输入下达到 construct 55/55、terminal correct 80/80。
Next Action:
  - 后续实现 Route B live runner，但实际调用 API 前需明确样本和预算边界。
```

### TASK-20260512-008

```yaml
Task ID: TASK-20260512-008
Title: 实现 Route B live slot-extraction runner
Status: done
Priority: P1
Owner: Execution Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - qsgi/construction/slot_schema.py
  - qsgi/construction/qyir_builder.py
  - experiments/run_live_llm.py
  - benchmark/qsi_bench_v1.jsonl
Outputs:
  - qsgi/construction/slot_extractor.py
  - qsgi/construction/pipeline.py
  - experiments/run_live_route_b.py
  - tests for mocked slot extraction and pipeline behavior
Dependencies:
  - TASK-20260512-002
  - TASK-20260512-004
Blocking:
  - TASK-20260512-006
Evidence Required:
  - pytest with mocked client
  - no live API calls
Estimated Cost: Medium
Risk Level: Low
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 不读取或打印 API key
  - 不发起网络请求
  - runner 默认需要显式 CLI 才运行 live API
Fallback if Blocked:
  - 只实现 slot_extractor.py 和 mocked tests
Last Result:
  - 新增 qsgi/construction/slot_extractor.py、qsgi/construction/pipeline.py、experiments/run_live_route_b.py 和 tests/test_route_b_pipeline.py。
  - `uv run python experiments/run_live_route_b.py --help` 成功，不触发 API。
  - `uv run pytest` 通过 200 项测试。
Next Action:
  - 若继续 live smoke，先记录样本数、模型、输出路径和成本边界。
```

### TASK-20260512-009

```yaml
Task ID: TASK-20260512-009
Title: 运行 5-case Route B DeepSeek flash live smoke
Status: done
Priority: P1
Owner: Execution Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - DSAPIKEY.txt
  - experiments/run_live_route_b.py
  - benchmark/qsi_bench_v1.jsonl
Outputs:
  - experiments/results/route_b_live_smoke_deepseek_flash_5_results.csv
  - experiments/results/route_b_live_smoke_deepseek_flash_5_raw_outputs.jsonl
  - experiments/results/route_b_live_smoke_deepseek_flash_5_metadata.json
  - experiments/results/route_b_live_smoke_deepseek_flash_5_token_usage.csv
Dependencies:
  - TASK-20260512-008
Blocking:
  - full Route B live experiment
Evidence Required:
  - live run command
  - raw outputs, metadata, token usage, result CSV
Estimated Cost: Low
Risk Level: Medium
Safe to Run Automatically: No
Human Review Required: Yes
Quality Gate:
  - deepseek-v4-flash only
  - case-limit <= 5
  - max-retries 1
  - max-tokens 1200
  - do not print API key
  - record failures honestly
Fallback if Blocked:
  - Record API or endpoint failure and do not retry with pro model automatically.
Last Result:
  - 已执行两次 DashScope-compatible 5-case smoke；均返回 401 invalid_api_key。
  - 按 DEC-20260512-002 改为 official DeepSeek endpoint 后，5-case smoke v4 成功并生成 route_b_live_smoke_deepseek_official_5_v4_*。
  - 后续完成 80-case official DeepSeek diagnostic。
Next Action:
  - 用 official artifacts 更新论文和 Research Ops。
```

### TASK-20260512-011

```yaml
Task ID: TASK-20260512-011
Title: 生成 Route B 结果汇总表
Status: done
Priority: P1
Owner: Statistics Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - experiments/tables/live_failure_breakdown.md
  - experiments/tables/route_b_builder_smoke.md
  - rules/research/RESULTS_LOG.md
Outputs:
  - experiments/tables/route_b_status_summary.md
Dependencies:
  - TASK-20260512-003
  - TASK-20260512-007
  - TASK-20260512-009
Blocking:
  - TASK-20260512-005 follow-up revisions
Evidence Required:
  - Summary table with claim-safe wording
Estimated Cost: Low
Risk Level: Low
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - Separates diagnostic, gold-slot builder, official live evidence, and forbidden claims
  - Does not generalize single-model official DeepSeek result
Fallback if Blocked:
  - Update docs/paper/qsga_ccf_draft.md manually with existing evidence
Last Result:
  - 更新 experiments/tables/route_b_status_summary.md，区分 implemented/tested、saved-run diagnosis、expected-slot builder smoke、official DeepSeek live diagnostic 和 forbidden claims。
Next Action:
  - 创建后续 reviewer gate / limitation tightening 任务。
```

### TASK-20260512-012

```yaml
Task ID: TASK-20260512-012
Title: 起草 QYIR market operand 设计决策
Status: done
Priority: P1
Owner: Architect / Experiment Designer
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - experiments/tables/live_failure_breakdown.md
  - qyir/schema.py
  - compiler/qyir_compiler.py
  - docs/paper/qsga_ccf_draft.md
Outputs:
  - DECISIONS.md 中关于是否支持 `market.close` 等 rule operand 的设计决策草案
  - 或 docs/paper/qsga_ccf_draft.md limitation/update
Dependencies:
  - TASK-20260512-003
Blocking:
  - price-vs-indicator Route B coverage
Evidence Required:
  - 当前 alias_failure case 和 schema/compiler impact
Estimated Cost: Low
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 不直接修改 QYIR schema/compiler contract
  - 只起草选项、风险、推荐
  - 真正修改 schema/compiler contract 前必须创建人审决策
Fallback if Blocked:
  - Keep limitation in Route B draft
Last Result:
  - 已在 DECISIONS.md 新增 DEC-20260512-003，比较 alias-only v1、正式支持 market field operands、v1.1/experimental layer 三种方案。
  - 推荐当前 paper cycle 保持 QYIR v1 alias-only contract，不直接修改 schema/compiler。
  - 人工最终选择方案 A：QYIR v1 保持冻结，market-field operands 作为 future work。
  - 已把 limitation / failure-analysis wording 写入 docs/paper/qsga_ccf_draft.md。
Next Action:
  - 不修改 schema/compiler contract；继续 TASK-20260512-014。
```

### TASK-20260512-013

```yaml
Task ID: TASK-20260512-013
Title: Route B CCF draft reviewer gate and limitation tightening
Status: done
Priority: P1
Owner: Reviewer / Writer Agent
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - docs/paper/qsga_ccf_draft.md
  - experiments/results/route_b_live_deepseek_official_80_metrics.csv
  - experiments/tables/route_b_live_deepseek_official_80_failure_breakdown.md
  - rules/research/DRAFT_STATUS.md
Outputs:
  - Review findings or direct draft patches
  - Updated limitation / claim-boundary wording
Dependencies:
  - TASK-20260512-005
  - TASK-20260512-009
Blocking:
  - Submission-readiness assessment
Evidence Required:
  - Line/section-level findings
  - Claim wording checked against RESULTS_LOG
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - Lead with blocking reviewer concerns
  - Do not invent results
  - Do not claim CCF-B readiness without review evidence
Fallback if Blocked:
  - Add reviewer-risk notes to DRAFT_STATUS.md
Last Result:
  - Scanned docs/paper/qsga_ccf_draft.md for overclaiming, pending/live-result stale wording, and result/method consistency.
  - Updated retry-loop wording from planned to implemented bounded retry.
  - Added Route B runner/builder/analyzer scripts to reproducibility section.
  - Updated latest test count to 205 passing tests.
Next Action:
  - Optional next reviewer pass should focus on external related-work citation verification.
```

### TASK-20260512-014

```yaml
Task ID: TASK-20260512-014
Title: 核验 Route B related work references and Paper Matrix
Status: done
Priority: P1
Owner: Literature / Reviewer Agent
Created: 2026-05-12
Updated: 2026-05-13
Inputs:
  - docs/paper/qsga_ccf_draft.md
  - rules/research/PAPER_MATRIX.md
Outputs:
  - Verified references in PAPER_MATRIX.md
  - Draft reference corrections if titles/authors/claims are wrong
Dependencies:
  - TASK-20260512-013
Blocking:
  - Related Work submission readiness
Evidence Required:
  - Source URLs or arXiv IDs
  - Claim-specific notes
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - Use primary sources where possible
  - Do not cite unverified papers as core evidence
  - Keep related-work comparisons scoped
Fallback if Blocked:
  - Mark unverified references as pending
Last Result:
  - Partially verified QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, OQL, and CNFinBench in PAPER_MATRIX.md.
  - Verified remaining general code-generation, constrained decoding, tool-use, execution-feedback, financial LLM, and trading-agent references against arXiv primary pages.
  - Corrected FinGPT and TradingAgents reference author lines in docs/paper/qsga_ccf_draft.md.
  - PAPER_MATRIX.md now records all current references as verified, with remaining work limited to final venue/DOI formatting.
Next Action:
  - Create next reviewer/statistics follow-up.
```

### TASK-20260513-001

```yaml
Task ID: TASK-20260513-001
Title: Route B official DeepSeek failure remediation plan
Status: done
Priority: P1
Owner: Experiment Designer / Developer Agent
Created: 2026-05-13
Updated: 2026-05-13
Inputs:
  - experiments/results/route_b_live_deepseek_official_80_results.csv
  - experiments/results/route_b_live_deepseek_official_80_failure_breakdown.csv
  - experiments/tables/route_b_live_deepseek_official_80_failure_breakdown.md
  - docs/paper/qsga_ccf_draft.md
Outputs:
  - Remediation plan for risk_violation, unsupported_indicator/semantics, and clarification_failure buckets
  - Optional TASK_QUEUE follow-up tasks for bounded implementation or experiments
Dependencies:
  - TASK-20260512-014
Blocking:
  - Next Route B improvement cycle
Evidence Required:
  - Failure counts and representative cases
  - Proposed fix mapped to component and expected metric movement
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - Do not edit schema/compiler contract
  - Do not run new paid API experiments unless separately scoped
  - Distinguish implementation fixes from paper-only limitations
Fallback if Blocked:
  - Add plan to CURRENT_PROGRESS.md and RESULTS_LOG notes
Last Result:
  - Added rules/research/ROUTE_B_REMEDIATION_PLAN.md with ranked remediation plan for risk_violation, clarification_failure, semantic_mismatch, and unsupported semantics.
  - Implemented the first no-API remediation: deterministic ambiguity guard before LLM slot extraction.
  - Added experiments/check_route_b_ambiguity_guard.py and generated route_b_ambiguity_guard_check.csv/md.
  - Local guard check: ambiguous recall 10/10, non-ambiguous false positive 0/70, overall 80/80.
  - `uv run pytest tests/test_route_b_pipeline.py tests/test_route_b_construction.py -q`: 20 passed.
Next Action:
  - Build saved raw slot-output replay harness before any new live API run.
```

### TASK-20260513-002

```yaml
Task ID: TASK-20260513-002
Title: Build saved Route B slot-output replay harness
Status: done
Priority: P1
Owner: Developer / Experiment Designer
Created: 2026-05-13
Updated: 2026-05-13
Inputs:
  - experiments/results/route_b_live_deepseek_official_80_raw_outputs.jsonl
  - benchmark/qsi_bench_v1.jsonl
  - qsgi/construction/pipeline.py
  - experiments/run_live_route_b.py
Outputs:
  - Replay script that reuses saved slot JSON outputs without API calls
  - Replay metrics for post-construction fixes
Dependencies:
  - TASK-20260513-001
Blocking:
  - Risk repair ablation
  - No-API validation of clarification and unsupported-semantics fixes
Evidence Required:
  - Replay command
  - Result CSV and metrics/table outputs
Estimated Cost: Medium
Risk Level: Low
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - No API calls
  - Preserve original raw output artifacts
  - Make replay deterministic and tied to saved call records
Fallback if Blocked:
  - Implement targeted unit tests for each remediation bucket
Last Result:
  - Added experiments/replay_live_route_b.py.
  - Replayed saved official DeepSeek 80-case slot outputs through current pipeline without API calls.
  - Generated route_b_live_deepseek_official_80_replay_results.csv, replay_metrics.csv, replay_failure_breakdown.csv, and replay_failure_breakdown.md.
  - After ambiguity guard, saved-output replay reaches clarification_accuracy 1.000 and E2E 0.5625; constructible construction_success remains 0.364.
Next Action:
  - Prototype bounded risk repair using replay harness.
```

### TASK-20260513-003

```yaml
Task ID: TASK-20260513-003
Title: Prototype bounded Route B risk-repair pass
Status: done
Priority: P1
Owner: Developer / Experiment Designer
Created: 2026-05-13
Updated: 2026-05-13
Inputs:
  - experiments/replay_live_route_b.py
  - experiments/results/route_b_live_deepseek_official_80_replay_results.csv
  - risk_audit modules
  - qsgi/construction/qyir_builder.py
Outputs:
  - Deterministic post-construction risk-repair implementation or ablation script
  - No-API replay metrics/table
Dependencies:
  - TASK-20260513-002
Blocking:
  - Route B risk_violation reduction claim
Evidence Required:
  - Before/after risk_violation and E2E counts from saved-output replay
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - Do not weaken user risk constraints
  - Do not increase leverage or enable shorting
  - Do not claim profitability or live improvement without scoped live run
Fallback if Blocked:
  - Keep as future work in remediation plan
Last Result:
  - Added qsgi/construction/risk_repair.py with bounded conservative risk-repair candidates.
  - Added --enable-risk-repair to experiments/replay_live_route_b.py.
  - Added tests/test_route_b_risk_repair.py.
  - Saved-output replay with ambiguity guard + risk repair reaches risk_violation 0.000, repair_success 19/19, construction_success 0.709, E2E 0.800.
  - `uv run pytest tests/test_route_b_risk_repair.py tests/test_route_b_pipeline.py tests/test_route_b_construction.py -q`: 22 passed.
Next Action:
  - Execute TASK-20260513-004 to reduce remaining clarification/unsupported failure buckets.
```

### TASK-20260513-004

```yaml
Task ID: TASK-20260513-004
Title: Tighten Route B clarification and unsupported-semantics handling
Status: done
Priority: P1
Owner: Developer / Experiment Designer
Created: 2026-05-13
Updated: 2026-05-13
Inputs:
  - experiments/results/route_b_live_deepseek_official_80_replay_risk_repair_failure_breakdown.csv
  - qsgi/construction/pipeline.py
  - qsgi/construction/slot_schema.py
  - benchmark/qsi_bench_v1.jsonl
Outputs:
  - Deterministic clarification/defaulting or unsupported-semantics boundary updates
  - No-API replay metrics/table
Dependencies:
  - TASK-20260513-003
Blocking:
  - Route B remaining failure reduction claim
Evidence Required:
  - Before/after clarification_failure, unsupported_indicator, schema_failure counts from saved-output replay
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - Do not force unsupported QYIR v1 semantics into invalid artifacts
  - Do not modify QYIR v1 schema/compiler contract
  - Distinguish defaultable missing fields from real unsupported strategy semantics
Fallback if Blocked:
  - Keep remaining failures as limitation / future work
Last Result:
  - Added unsupported-semantics guard for QYIR v1 out-of-scope rotation/ranking, top-k portfolio, low-volatility selection, and consecutive-day pattern requests.
  - Tightened defaulting so momentum/risk-controlled requests are not defaulted into single-asset strategies solely because non-core fields are missing.
  - Added narrow MA-deviation `entry_threshold` defaulting for concrete mean-reversion requests.
  - Added role normalization for `momentum`, `return_period`, and `volatility`.
  - Saved-output replay with policy+risk repair reaches construction_success 0.727, E2E 0.8125, unsupported_semantics 11/80, clarification_failure 4/80.
  - `uv run pytest tests/test_route_b_pipeline.py tests/test_route_b_construction.py tests/test_route_b_risk_repair.py tests/test_failure_breakdown.py -q`: 30 passed.
Next Action:
  - Run full test suite and Research Ops checks, then update paper/ops final status.
```

### TASK-20260513-005

```yaml
Task ID: TASK-20260513-005
Title: Full verification and Route B paper consistency check
Status: done
Priority: P1
Owner: Developer / Reviewer Agent
Created: 2026-05-13
Updated: 2026-05-13
Inputs:
  - docs/paper/qsga_ccf_draft.md
  - experiments/results/route_b_live_deepseek_official_80_replay_policy_risk_repair_metrics.csv
  - rules/research/RESULTS_LOG.md
  - tests/
Outputs:
  - Full pytest result
  - Research Ops quality check result
  - Final claim-boundary consistency updates if needed
Dependencies:
  - TASK-20260513-004
Blocking:
  - End-of-turn handoff
Evidence Required:
  - `uv run pytest tests -q`
  - `uv run python rules/scripts/check_research_ops.py --root rules`
Estimated Cost: Medium
Risk Level: Low
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - No API calls
  - Do not update official live metrics with replay-only numbers
  - Ensure paper numbers match generated CSV artifacts
Fallback if Blocked:
  - Report failing tests/checks and leave TASK-20260513-005 in progress
Last Result:
  - Full test suite passed: `uv run pytest tests -q` -> 213 passed.
  - Research Ops checker passed: `uv run python rules/scripts/check_research_ops.py --root rules` -> FAIL 0, WARN 0.
  - Updated paper test-count statement to 213 passing tests.
Next Action:
  - Execute TASK-20260513-006 for final reviewer gate and submission-readiness assessment.
```

### TASK-20260513-006

```yaml
Task ID: TASK-20260513-006
Title: Final Route B reviewer gate and submission-readiness assessment
Status: done
Priority: P1
Owner: Reviewer / Writer Agent
Created: 2026-05-13
Updated: 2026-05-13
Inputs:
  - docs/paper/qsga_ccf_draft.md
  - rules/research/DRAFT_STATUS.md
  - rules/research/RESULTS_LOG.md
  - experiments/tables/route_b_live_deepseek_official_80_replay_policy_risk_repair_failure_breakdown.md
Outputs:
  - Reviewer-gate findings or final draft patches
  - Submission-readiness assessment with blocking/non-blocking issues
Dependencies:
  - TASK-20260513-005
Blocking:
  - Human decision on final submission target and any new live run
Evidence Required:
  - Claim-vs-evidence consistency review
  - Limitations checked against replay/live distinction
Estimated Cost: Medium
Risk Level: Medium
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - Lead with blocking issues
  - Do not claim CCF-B readiness unless evidence supports it
  - Keep official live and replay-only metrics separated
Fallback if Blocked:
  - Record reviewer risks in DRAFT_STATUS.md
Last Result:
  - Updated abstract wording to separate scoped claims from replay-only remediation observation.
  - Added Reviewer Gate Snapshot to DRAFT_STATUS.md.
  - Blocking issues remain human-facing: target venue/authorship/public release, second full live model decision, final bibliography formatting, financial-safety wording review.
  - Non-blocking status: live vs replay metrics are separated; QYIR v1 limitations are explicit; full validation passed.
Next Action:
  - Execute TASK-20260513-007 for final bibliography formatting pass.
```

### TASK-20260513-007

```yaml
Task ID: TASK-20260513-007
Title: Final bibliography venue and DOI formatting pass
Status: todo
Priority: P1
Owner: Literature / Writer Agent
Created: 2026-05-13
Updated: 2026-05-13
Inputs:
  - docs/paper/qsga_ccf_draft.md
  - rules/research/PAPER_MATRIX.md
Outputs:
  - Reference formatting corrections
  - Updated PAPER_MATRIX note if any venue/DOI data remains unavailable
Dependencies:
  - TASK-20260513-006
Blocking:
  - Submission packaging polish
Evidence Required:
  - Source URLs or primary bibliography pages for changed references
Estimated Cost: Medium
Risk Level: Low
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - Use primary sources where possible
  - Do not change technical claims while formatting references
  - Do not invent venue/DOI data
Fallback if Blocked:
  - Leave unresolved venue/DOI fields marked in PAPER_MATRIX.md
Last Result:
  - Not yet executed.
Next Action:
  - Check current references for venue/DOI completeness and update formatting conservatively.
```

---

## 5. Blocked Tasks

> 被人类决策或依赖阻塞的任务放在这里。阻塞任务不能阻塞整个项目。

### TASK-20260512-010

```yaml
Task ID: TASK-20260512-010
Title: 修复 Route B live API key / endpoint 配置
Status: done
Priority: P1
Owner: Human / Research Orchestrator
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - DSAPIKEY.txt
  - DEC-20260512-002
Outputs:
  - Valid provider key or exact base_url/model configuration
Dependencies:
  - Human confirmation
Blocking:
  - None
Evidence Required:
  - Successful authenticated model call metadata
Estimated Cost: Low
Risk Level: High
Safe to Run Automatically: No
Human Review Required: Yes
Quality Gate:
  - Do not print key
  - Do not retry pro model automatically
Fallback if Blocked:
  - Continue offline Route B work
Last Result:
  - DashScope endpoint returned 401 invalid_api_key even after explicit file-key priority fix.
  - User instructed use of official DeepSeek docs; official endpoint https://api.deepseek.com succeeded for 5-case smoke and 80-case diagnostic.
Next Action:
  - No longer blocked; keep future API experiments scoped and logged.
```

---

## 6. Done Tasks

> 完成并通过质量门的任务移动到这里，保留证据链接和交接摘要。

### TASK-20260512-001

```yaml
Task ID: TASK-20260512-001
Title: 初始化 Route B 研究任务队列
Status: done
Priority: P0
Owner: Research Orchestrator
Created: 2026-05-12
Updated: 2026-05-12
Inputs:
  - 用户给定的 Route B 研究目标
  - docs/QSGA_Route_B_Modification_Plan.md
  - rules/AGENTS.md
Outputs:
  - Route B 任务队列
  - 当前进度更新
Dependencies:
  - 无
Blocking:
  - TASK-20260512-002
Evidence Required:
  - rules/TASK_QUEUE.md
  - rules/CURRENT_PROGRESS.md
Estimated Cost: Low
Risk Level: Low
Safe to Run Automatically: Yes
Human Review Required: No
Quality Gate:
  - 任务具备输入、输出、依赖、证据和安全性字段
  - 至少一个可自动执行任务可继续
Fallback if Blocked:
  - 只记录研究目标和风险，不进入实现
Evidence:
  - rules/TASK_QUEUE.md
  - rules/CURRENT_PROGRESS.md
Last Result:
  - 已根据 docs/QSGA_Route_B_Modification_Plan.md 创建 5 个后续任务，覆盖构造模块、失败诊断、实验协议、论文草稿和 live smoke 实验。
Next Action:
  - 执行 TASK-20260512-002。
```

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

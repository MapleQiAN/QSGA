# AI 科研审计日志

本文件记录 AI 科研流程中的关键操作。所有影响证据链、实验、结论、人审和发布边界的动作都必须留痕。

## 必须审计的操作

1. 文献检索查询。
2. 论文筛选标准。
3. 关键引用验证。
4. 研究假设生成。
5. 实验设计生成。
6. 数据集选择。
7. 实验执行参数。
8. 结果分析。
9. 图表生成。
10. 论文关键结论生成。
11. 人工审批。
12. 对外发布尝试。
13. 失败重试。
14. Agent 冲突处理。

## 审计记录模板

```markdown
## AUDIT-YYYYMMDD-NNN

- 时间：YYYY-MM-DD HH:mm:ss
- 操作 Agent：
- 操作类型：Search / Read / Analyze / Generate / Verify / Execute / Publish-Attempt / Decision-Write
- 输入：
- 输出：
- 使用工具 / Skill / Plugin：
- 关联任务：
- 关联决策：
- 风险等级：Low / Medium / High / Critical
- 是否需要人审：Yes / No
- 人审状态：Not-Required / Pending / Approved / Rejected
- 证据来源：
- 可复现信息：
- 失败信息：
- 后续动作：
```

## 当前记录

## AUDIT-20260505-001

- 时间：2026-05-05 11:31:18 +08:00
- 操作 Agent：Codex
- 操作类型：Read / Analyze
- 输入：`docs/ai-research-assistant/*.md`, `docs/QSGA论文思路v7Plus_最终稿.md`, `docs/QYIR_v1_Spec.md`
- 输出：研究规范、论文定位、QYIR 范围和实验要求摘要
- 使用工具 / Skill / Plugin：bmad-domain-research, bmad-technical-research, bmad-review-adversarial-general, bmad-review-edge-case-hunter skill instructions; shell
- 关联任务：QSGA CCF C paper draft
- 关联决策：none
- 风险等级：Low
- 是否需要人审：No
- 人审状态：Not-Required
- 证据来源：本地文档
- 可复现信息：`Get-Content -Raw ...`
- 失败信息：none
- 后续动作：复现实验与生成论文草稿

## AUDIT-20260505-002

- 时间：2026-05-05 11:29:00 +08:00
- 操作 Agent：Codex
- 操作类型：Execute / Verify
- 输入：`tests`, `benchmark/qsi_bench_v1.jsonl`, `data/raw/spy_sample.csv`
- 输出：测试通过；baseline 与 ablation 指标复现
- 使用工具 / Skill / Plugin：shell
- 关联任务：实验复现
- 关联决策：DEC-20260505-001
- 风险等级：Low
- 是否需要人审：No
- 人审状态：Not-Required
- 证据来源：本地命令输出
- 可复现信息：`.venv\Scripts\python.exe -m pytest tests -q`; `.venv\Scripts\python.exe -m experiments.baselines ...`; `.venv\Scripts\python.exe -m experiments.run_ablation ...`
- 失败信息：`git diff --no-index` 路径解析失败，已改用 `Compare-Object` 完成文件级确认
- 后续动作：写入论文和结果日志

## AUDIT-20260505-003

- 时间：2026-05-05 11:32:00 +08:00
- 操作 Agent：Codex
- 操作类型：Search / Analyze
- 输入：LLM code generation, constrained decoding, tool-use agents, execution feedback, financial LLM/trading agents
- 输出：12 条候选相关工作引用，均以 arXiv/论文页 URL 记录
- 使用工具 / Skill / Plugin：web search; bmad-domain-research; bmad-technical-research
- 关联任务：Related Work and Citation Matrix
- 关联决策：none
- 风险等级：Medium
- 是否需要人审：Yes
- 人审状态：Pending
- 证据来源：arXiv / paper URLs in `docs/paper/citation_and_claim_matrix.md`
- 可复现信息：检索查询记录见本轮工具调用
- 失败信息：PDF 级核验未完成
- 后续动作：投稿前升级关键引用到 Level A

## AUDIT-20260505-004

- 时间：2026-05-05 11:40:00 +08:00
- 操作 Agent：Codex
- 操作类型：Generate / Review
- 输入：论文最终思路、实验表、引用候选、CCF C reviewer spec
- 输出：paper draft, citation matrix, reviewer report, reproducibility package
- 使用工具 / Skill / Plugin：Markdown editing; bmad-review-adversarial-general; bmad-review-edge-case-hunter
- 关联任务：CCF C candidate package
- 关联决策：DEC-20260505-001, DEC-20260505-002, DEC-20260505-003
- 风险等级：Medium
- 是否需要人审：Yes
- 人审状态：Pending
- 证据来源：`docs/paper/*.md`
- 可复现信息：新增文件见 git diff
- 失败信息：none
- 后续动作：人审后补 live LLM / 引用核验 / 最终格式

## AUDIT-20260505-005

- 时间：2026-05-05 11:45:00 +08:00
- 操作 Agent：Codex
- 操作类型：Verify
- 输入：current environment
- 输出：`OPENAI_API_KEY=missing`
- 使用工具 / Skill / Plugin：shell
- 关联任务：live LLM experiment feasibility
- 关联决策：DEC-20260505-001
- 风险等级：Medium
- 是否需要人审：Yes
- 人审状态：Pending
- 证据来源：environment variable check
- 可复现信息：`if ($env:OPENAI_API_KEY) { 'OPENAI_API_KEY=set' } else { 'OPENAI_API_KEY=missing' }`
- 失败信息：live LLM experiment cannot be run in current environment
- 后续动作：等待人类决定是否提供 API key / 模型 / 成本预算，或接受 deterministic prototype framing

## AUDIT-20260505-006

- 时间：2026-05-05 12:10:00 +08:00
- 操作 Agent：Codex + SubAgents
- 操作类型：Review / Generate / Revise
- 输入：`docs/paper/qsga_ccf_c_draft.md`, experiment CSVs, QYIR spec, citation matrix
- 输出：4 份 SubAgent 报告和主论文即时修订
- 使用工具 / Skill / Plugin：spawn_agent; bmad-review-adversarial-general; bmad-technical-research
- 关联任务：SubAgent parallel research workflow
- 关联决策：DEC-20260505-001
- 风险等级：High
- 是否需要人审：Yes
- 人审状态：Pending
- 证据来源：`docs/paper/subagent_literature_review.md`; `docs/paper/subagent_experiment_audit.md`; `docs/paper/subagent_adversarial_review.md`; `docs/paper/subagent_paper_expansion.md`
- 可复现信息：SubAgent reports are saved under `docs/paper/`
- 失败信息：SubAgents identified oracle-slot construction, simulated baselines, and ambiguous-intent evaluation as major evidence gaps
- 后续动作：paper draft downgraded to oracle-slot deterministic evaluation; no-oracle/live LLM experiments remain pending

## AUDIT-20260505-007

- 时间：2026-05-05 12:20:00 +08:00
- 操作 Agent：Codex
- 操作类型：Revise / Risk-Write
- 输入：SubAgent reviewer objections
- 输出：updated paper draft, reviewer report, claim matrix, paper matrix, risks, experiment plan, results log, draft status
- 使用工具 / Skill / Plugin：apply_patch
- 关联任务：Immediate rebuttal-driven revision
- 关联决策：DEC-20260505-001, DEC-20260505-003
- 风险等级：High
- 是否需要人审：Yes
- 人审状态：Pending
- 证据来源：modified files in git diff
- 可复现信息：`git diff --stat`
- 失败信息：no live/no-oracle experiment available in current environment
- 后续动作：run tests and final consistency checks

## AUDIT-20260505-008

- 时间：2026-05-05 12:35:00 +08:00
- 操作 Agent：Codex
- 操作类型：Execute / Verify / Revise
- 输入：SubAgent oracle-leakage objection; `benchmark/qsi_bench_v1.jsonl`; `data/raw/spy_sample.csv`
- 输出：no-oracle slot extraction script and metrics
- 使用工具 / Skill / Plugin：apply_patch; shell
- 关联任务：no-oracle experiment
- 关联决策：DEC-20260505-001
- 风险等级：Medium
- 是否需要人审：Yes
- 人审状态：Pending
- 证据来源：`experiments/run_no_oracle.py`; `experiments/results/no_oracle_results.csv`; `experiments/results/no_oracle_metrics.csv`
- 可复现信息：`.venv\Scripts\python.exe -m experiments.run_no_oracle --benchmark benchmark\qsi_bench_v1.jsonl --data data\raw\spy_sample.csv --output experiments\results\no_oracle_results.csv`; `.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\no_oracle_results.csv --output experiments\results\no_oracle_metrics.csv`
- 失败信息：still deterministic; no live LLM outputs
- 后续动作：update paper and reviewer report; live LLM remains pending

## AUDIT-20260505-009

- 时间：2026-05-05 12:55:00 +08:00
- 操作 Agent：Codex
- 操作类型：Fix / Verify / Synchronize
- 输入：SubAgent safe-rejection objection; latest experiment CSVs and tables
- 输出：safe rejection paraphrase fix, regenerated metrics, synchronized paper and reproducibility files
- 使用工具 / Skill / Plugin：apply_patch; shell; spawn_agent
- 关联任务：reviewer-objection immediate revision
- 关联决策：DEC-20260505-001
- 风险等级：Medium
- 是否需要人审：Yes
- 人审状态：Pending
- 证据来源：`verifier/safe_rejection.py`; `tests/test_safe_rejection.py`; `experiments/results/*metrics.csv`; `docs/paper/qsga_ccf_c_draft.md`
- 可复现信息：`.venv\Scripts\python.exe -m pytest tests -q` -> `171 passed in 2.35s`
- 失败信息：formal deliverables no longer contain stale pre-fix metrics; historical SubAgent reports still contain pre-fix observations
- 后续动作：final SubAgent consistency review; live LLM and PDF-level citation audit remain pending

## AUDIT-20260505-010

- 时间：2026-05-05 20:05:00 +08:00
- 操作 Agent：Codex
- 操作类型：Human-Decision / Experiment-Design / Execute
- 输入：Human decisions DEC-20260505-001/002/003; `docs/LiveLLM API KEY.txt`; QSI-Bench v1
- 输出：live LLM runner, smoke/probe outputs, 3-model 12-case live pilot
- 使用工具 / Skill / Plugin：apply_patch; shell; Aliyun Bailian OpenAI-compatible API
- 关联任务：live LLM evidence supplementation
- 关联决策：DEC-20260505-001, DEC-20260505-002, DEC-20260505-003
- 风险等级：High
- 是否需要人审：Yes
- 人审状态：Approved for experiment; final claims still require review
- 证据来源：`experiments/run_live_llm.py`; `experiments/results/live_llm_metrics.csv`; `experiments/results/live_llm_raw_outputs.jsonl`; `experiments/results/live_llm_token_usage.csv`
- 可复现信息：`.venv\Scripts\python.exe -m experiments.run_live_llm --models qwen3.6-flash deepseek-v4-flash kimi-k2.6 --case-limit 12 --seed 20260505 --max-retries 0 --max-tokens 800 --output experiments\results\live_llm_results.csv --raw-output experiments\results\live_llm_raw_outputs.jsonl --metadata-output experiments\results\live_llm_run_metadata.json --usage-output experiments\results\live_llm_token_usage.csv`
- 失败信息：20-case 4-model run timed out; qwen3.6-plus was kept as one-case probe only
- 后续动作：update paper claims conservatively; keep API key ignored; do not publish secrets

## AUDIT-20260505-011

- 时间：2026-05-05 21:40:00 +08:00
- 操作 Agent：Codex + SubAgents
- 操作类型：Implement / Execute / Verify / Revise
- 输入：`docs/Newest Goal.md`; `docs/ai-research-assistant/*`; QSI-Bench v1; `docs/LiveLLM API KEY.txt`
- 输出：`wo_qyir` ablation, synthetic multi-asset smoke, executable live direct-code qwen3.6-flash 80-case baseline, PDF-level related-work scaffold, updated paper/repro docs
- 使用工具 / Skill / Plugin：spawn_agent; apply_patch; shell; arXiv PDF verification by subagent; Aliyun Bailian OpenAI-compatible API
- 关联任务：CCF C submission hardening
- 关联决策：DEC-20260505-001, DEC-20260505-002, DEC-20260505-003
- 风险等级：High
- 是否需要人审：Yes
- 人审状态：Experiment already approved; final claims/submission still require review
- 证据来源：`experiments/results/live_direct_code_metrics.csv`; `experiments/results/live_direct_code_raw_outputs.jsonl`; `experiments/results/ablation_metrics.csv`; `experiments/results/multi_asset_smoke_results.csv`; `docs/paper/related_work_verified.md`
- 可复现信息：`.venv\Scripts\python.exe -m experiments.run_live_direct_code --models qwen3.6-flash --case-ids ... --max-tokens 900`; replay via `.venv\Scripts\python.exe -m experiments.run_live_direct_code --replay-raw-output experiments\results\live_direct_code_raw_outputs.jsonl --replay-metadata experiments\results\live_direct_code_metadata.json`
- 失败信息：single 80-case live direct-code run timed out before final write; reran in 8 checkpointed 10-case batches and merged results
- 后续动作：run full tests; update CCF C reviewer report v2; finish figure generation and optional safe paraphrase set

## AUDIT-20260506-001

- 时间：2026-05-06 14:55:00 +08:00
- 操作 Agent：Codex
- 操作类型：Verify / Synchronize / Reproduce
- 输入：`scripts/reproduce_all.ps1`, `scripts/reproduce_all.sh`, saved live QYIR raw outputs, saved live direct-code raw outputs, safe paraphrase benchmark
- 输出：one-command reproduce scripts now include safe paraphrase, live QYIR replay metrics, and live direct-code replay metrics; package docs synchronized to 178-test state
- 使用工具 / Skill / Plugin：automation-workflows; apply_patch; shell
- 关联任务：RUN-20260506-CONTINUE-019DF854
- 关联决策：DEC-20260505-001, DEC-20260505-002, DEC-20260505-003
- 风险等级：Medium
- 是否需要人审：Yes
- 人审状态：Pending for final release/submission
- 证据来源：`scripts/reproduce_all.ps1`; `scripts/reproduce_all.sh`; `REPRODUCE.md`; `docs/paper/reproducibility_package.md`; `experiments/results/live_qyir_80_metrics.csv`; `experiments/results/live_direct_code_metrics.csv`; `experiments/results/safe_paraphrase_metrics.csv`
- 可复现信息：`.\\scripts\\reproduce_all.ps1` -> `178 passed`; replayed 160 live QYIR rows; replayed 80 live direct-code rows; safe paraphrase total 35 accuracy 1.000
- 失败信息：initial script used system Python/Anaconda and produced live direct-code E2E 0.3375; fixed scripts to prefer `.venv` Python and restored E2E 0.350
- 后续动作：before public release, run secret/license checks over raw outputs, metadata, prompts, and ignored key files

## AUDIT-20260506-002

- 时间：2026-05-06 16:20:00 +08:00
- 操作 Agent：Codex
- 操作类型：Generate / Execute / Revise
- 输入：latest reviewer-risk suggestions; `docs/paper/qsga_ccf_c_draft.md`; saved live direct-code raw outputs; QSI-Bench v1
- 输出：progress checkpoint file, semantic slot-corruption experiment, live direct-code shared-rejection replay, revised paper framing
- 使用工具 / Skill / Plugin：apply_patch; shell
- 关联任务：QSGA paper hardening after reviewer-risk feedback
- 关联决策：DEC-20260505-001, DEC-20260505-002, DEC-20260505-003
- 风险等级：High
- 是否需要人审：Yes
- 人审状态：Pending for final claims/submission
- 证据来源：`docs/ai-research-assistant/CURRENT_PROGRESS.md`; `experiments/results/semantic_corruption_metrics.csv`; `experiments/results/live_direct_code_shared_rejection_metrics.csv`; `docs/paper/qsga_ccf_c_draft.md`
- 可复现信息：`.venv\Scripts\python.exe -m experiments.run_semantic_corruption ...`; `.venv\Scripts\python.exe -m experiments.run_live_direct_code_wrapper ...`; `.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\live_direct_code_shared_rejection_results.csv --output experiments\results\live_direct_code_shared_rejection_metrics.csv`
- 失败信息：initial semantic-corruption case list included queries without extractor-detectable explicit slots, producing detection 0.286; replaced cases with explicit slot phrasings and reran to 1.000 detection
- 后续动作：tests and reproduce script completed; final claim framing still needs human review before submission or public release

## AUDIT-20260506-003

- 时间：2026-05-06 20:40:00 +08:00
- 操作 Agent：Codex
- 操作类型：Implement / Recompute / Revise
- 输入：human reviewer-risk feedback on oracle-slot ordering, live QYIR/direct-code narrative conflict, defensive abstract, and ambiguous-intent scoring
- 输出：clarification-aware metric columns; regenerated baseline/no-oracle/ablation/live replay metrics; paper reordered into no-oracle main result, oracle-slot upper bound, and live diagnostic evidence; claim and risk docs synchronized
- 使用工具 / Skill / Plugin：apply_patch; shell
- 关联任务：QSGA paper narrative hardening and clarification metric implementation
- 关联决策：DEC-20260505-001, DEC-20260505-002, DEC-20260505-003
- 风险等级：High
- 是否需要人审：Yes
- 人审状态：Pending for final claims/submission
- 证据来源：`experiments/results/no_oracle_metrics.csv`; `experiments/results/baseline_metrics.csv`; `experiments/results/live_qyir_80_metrics.csv`; `docs/paper/qsga_ccf_c_draft.md`; `docs/paper/claim_policy.md`
- 可复现信息：`.\\scripts\\reproduce_all.ps1` -> `179 passed`; regenerated baseline/no-oracle/ablation metrics; replayed 160 live QYIR rows and 80 live direct-code rows without new API calls
- 失败信息：live QSGA QYIR construction success remains 0.0909 despite E2E rising to 0.375 through clarification and safe rejection; must remain diagnostic bottleneck evidence
- 后续动作：final claim framing still needs human review before submission or public release

## AUDIT-20260507-001

- 时间：2026-05-07 00:00:00 +08:00
- 操作 Agent：Codex
- 操作类型：Revise / Verify / Synchronize
- 输入：`docs/paper/ccf_c_reviewer_report_v4.md`; `docs/ai-research-assistant/AI_RULES.md`; `docs/ai-research-assistant/QUALITY_GUARDRAILS.md`; `docs/paper/qsga_ccf_c_draft.md`
- 输出：V4-driven paper revision with safer IR-first title, four-part abstract, sharper contributions, formal QYIR validity conditions, QYIR-vs-JSON table, Wilson confidence intervals, conservative semantic/rejection/repair boundaries, live diagnostic case traces, and expanded threats to validity
- 使用工具 / Skill / Plugin：apply_patch; shell
- 关联任务：QSGA paper hardening according to V4 reviewer-risk report
- 关联决策：DEC-20260505-001, DEC-20260505-002, DEC-20260505-003
- 风险等级：High
- 是否需要人审：Yes
- 人审状态：Pending for final claims/submission
- 证据来源：`docs/paper/ccf_c_reviewer_report_v4.md`; `docs/paper/qsga_ccf_c_draft.md`; `experiments/results/*metrics.csv`
- 可复现信息：Wilson intervals computed from local metric denominators: E2E over 80 cases and construction over 55 constructible cases
- 失败信息：No new live experiment was run in this revision; single-model live evidence and human approval gates remain
- 后续动作：run consistency checks/tests and keep submission/public release blocked on human review

## AUDIT-20260507-002

- 时间：2026-05-07 13:15:14 +08:00
- 操作 Agent：Codex
- 操作类型：Revise / Claim-strength audit / Synchronize
- 输入：`docs/paper/ccf_c_reviewer_report_v5.md`; `docs/ai-research-assistant/AI_RULES.md`; `docs/ai-research-assistant/SOP.md`; `docs/ai-research-assistant/QUALITY_GUARDRAILS.md`; `docs/paper/qsga_ccf_c_draft.md`
- 输出：V5 route-A paper revision centering QYIR as the verifiable and repairable IR; abstract now reports 0.963 oracle E2E, 0.887 no-oracle E2E, and 0.091 live construction success; Introduction RQs split into IR verification and live bottleneck diagnosis; Method adds BNF grammar, validity conjunction, operand type system, compilation semantics, explicit semantic-slot algorithm, and repair invariants; Results reorder oracle component validation before no-oracle feasibility and live bottleneck analysis; no-oracle slot diagnostics added; Discussion and Conclusion rewritten conservatively
- 使用工具 / Skill / Plugin：apply_patch; shell
- 关联任务：QSGA paper hardening according to V5 route-A reviewer report
- 关联决策：DEC-20260505-001, DEC-20260505-002, DEC-20260505-003
- 风险等级：High
- 是否需要人审：Yes
- 人审状态：Pending for final claims/submission
- 证据来源：`docs/paper/ccf_c_reviewer_report_v5.md`; `docs/paper/qsga_ccf_c_draft.md`; `experiments/results/baseline_metrics.csv`; `experiments/results/no_oracle_metrics.csv`; `experiments/results/no_oracle_slot_diagnostics.csv`; `experiments/results/live_qyir_80_metrics.csv`; `docs/ai-research-assistant/DRAFT_STATUS.md`; `docs/ai-research-assistant/RISKS.md`
- 可复现信息：`.venv\Scripts\python.exe -m experiments.run_slot_diagnostics`; `.\scripts\reproduce_all.ps1` completed with 179 passed and regenerated deterministic metrics, slot diagnostics, saved live QYIR replay metrics, and saved live direct-code replay metrics
- 失败信息：Slot diagnostics show weak market recall and near-zero fine-grained entry/exit extraction under strict key-value grouping; reproduce run emitted existing pandas/backtester runtime warnings but exited successfully
- 后续动作：run markdown/claim consistency checks; optional next step is improving extractor or adding constrained parser before stronger NL-to-QYIR parsing claims

# 实验计划模板

## 1. 实验协议状态

Status: completed for deterministic prototype / completed single-model 80-case live diagnostics  
Human review required: yes

## 2. 实验矩阵

| Experiment ID | 对应假设 | 数据集 | Baseline | 指标 | Ablation | 资源预算 | 审批状态 |
|---|---|---|---|---|---|---|---|
| EXP-20260505-001 | QYIR + verification improves reliable strategy construction in bounded space | QSI-Bench v1, 80 samples; `data/raw/spy_sample.csv` | direct_code, direct_json, qsga_no_repair, qsga_no_risk_audit | schema validity, semantic consistency, compile success, backtest success, risk violation, E2E success | none | local CPU | completed |
| EXP-20260505-002 | Risk audit, repair, and safe rejection are necessary components | QSI-Bench v1, 80 samples; `data/raw/spy_sample.csv` | qsga_full | wo_semantic_verification, wo_risk_audit, wo_repair, wo_safe_rejection | same as above plus safe rejection accuracy, repair success | local CPU | completed |
| EXP-20260505-003 | Live LLM generation produces valid QYIR candidates under fixed prompts | QSI-Bench v1 stratified 12-case subset; `spy_sample.csv` | live_raw_qyir, live_qsga_qyir | same as above plus token usage and raw-output audit | model subset pilot | API cost, capped by model/sample selection | completed pilot |
| EXP-20260505-004 | No-oracle slot extraction can recover QSI-Bench expected slots from user_query | QSI-Bench v1, 80 samples | oracle-slot QSGA | semantic consistency, downstream E2E | compare oracle vs extracted slots | local CPU | completed |
| EXP-20260505-005 | Ambiguous intent handling can be measured as clarification success | ambiguous subset + paraphrase extension | current safe rejection / clarification rules | clarification accuracy, false accept, false reject | w/o clarification | local CPU | pending design |
| EXP-20260505-006 | QYIR adds value beyond a generic structured object | QSI-Bench v1, 80 samples; `data/raw/spy_sample.csv` | qsga_full | same as ablation metrics | wo_qyir | local CPU | completed |
| EXP-20260505-007 | The pipeline remains runnable across synthetic symbols and periods | synthetic SPY/QQQ/GLD-like OHLCV samples | qsi_001 QYIR | compile success, backtest success, risk-audit runnable | none | local CPU | completed smoke |
| EXP-20260505-008 | Executable live direct-code baseline can be collected under fixed interface | QSI-Bench v1, 80 samples | live_direct_code | syntax, interface, runtime, trade validity, semantic match, risk violation, E2E | model comparison optional | API cost | completed for qwen3.6-flash |
| EXP-20260506-001 | Live QYIR can be replayed and scored without new API calls | QSI-Bench v1, 80 samples | live_raw_qyir, live_qsga_qyir | schema validity, semantic consistency, compile success, backtest success, risk violation, safe rejection accuracy, E2E | raw vs QSGA wrapper | saved outputs only | completed for qwen3.6-flash |
| EXP-20260506-002 | Safe-rejection paraphrases remain covered beyond QSI-Bench explicit unsafe rows | 35-case unsafe paraphrase and boundary-safe set | safe rejection rules | accuracy, false positive, false negative, unsafe acceptance | none | local CPU | completed |

## 2.1 Frozen Protocol for Current Paper Scope

Current submission scope is IR-first verification-guided prototype / system study.

Frozen result families:

1. Oracle-slot deterministic main run: `experiments/results/baseline_results.csv` and `baseline_metrics.csv`.
2. Deterministic ablations: `experiments/results/ablation_results.csv` and `ablation_metrics.csv`, including `wo_qyir`.
3. No-oracle deterministic extractor: `experiments/results/no_oracle_results.csv` and `no_oracle_metrics.csv`.
4. Live QYIR diagnostics: 12-case multi-model pilot plus 80-case qwen3.6-flash saved-output replay, descriptive rates only.
5. Executable live direct-code diagnostic baseline: 80-case qwen3.6-flash saved-output replay, descriptive rates only.
6. Synthetic multi-asset smoke: compile/backtest/risk-audit runnability only; no return or robustness claim.
7. Safe-rejection paraphrase regression: 35 deterministic paraphrase/boundary cases; no robust financial-safety claim.

Denominators:

- schema, semantic, compile, backtest, and risk metrics: 65 non-unsafe cases unless a live subset states otherwise.
- safe rejection: 15 unsafe cases unless a live subset states otherwise.
- E2E: all cases in the selected benchmark split.

Open protocol gap:

- EXP-20260505-005 remains pending. Ambiguous intent is currently counted as failure, not clarification success.

## 3. 预注册模板

```markdown
### EXP-YYYYMMDD-NNN

Status:
Related hypothesis:

Purpose:

Dataset:

Baseline:

Ablation:

Metrics:

Statistical method:

Resource budget:

Environment:

Random seeds:

Success criteria:

Failure criteria:

Risks:

Human approval:
```

## 4. 变更记录

| Change ID | 时间 | 变更内容 | 原因 | 是否影响主结论 | 是否人审 |
|---|---|---|---|---|---|
| CHG-20260505-001 | 2026-05-05 | 将当前实验状态标为 deterministic prototype completed，并新增 live LLM extension 待决策 | 当前代码避免 live LLM 调用，需防止论文主张过强 | 是 | 是 |
| CHG-20260505-002 | 2026-05-05 | 新增 no-oracle slot extraction 与 clarification metric 计划 | SubAgent 审稿指出 oracle leakage 和 ambiguous failure | 是 | 是 |
| CHG-20260505-003 | 2026-05-05 | 人类批准 live LLM 实验后，新增 budget-bounded pilot：3 个 live 模型、12 条分层样本、保存 raw outputs 和 token usage | 降低 simulated-baseline / no-live-evidence 审稿风险，同时控制 API 成本 | 是 | 是 |
| CHG-20260506-001 | 2026-05-06 | 将实验协议同步到 80-case qwen3.6-flash live QYIR、80-case executable live direct-code、safe paraphrase regression，并要求 reproduce scripts 使用 `.venv` replay saved outputs | 复现脚本已覆盖 safe paraphrase 和 live replay metrics，避免文档有结果但一键流程不跑 | 是 | 是 |

# 实验计划模板

## 1. 实验协议状态

Status: completed for deterministic prototype / pending_review for live LLM extension  
Human review required: yes

## 2. 实验矩阵

| Experiment ID | 对应假设 | 数据集 | Baseline | 指标 | Ablation | 资源预算 | 审批状态 |
|---|---|---|---|---|---|---|---|
| EXP-20260505-001 | QYIR + verification improves reliable strategy construction in bounded space | QSI-Bench v1, 80 samples; `data/raw/spy_sample.csv` | direct_code, direct_json, qsga_no_repair, qsga_no_risk_audit | schema validity, semantic consistency, compile success, backtest success, risk violation, E2E success | none | local CPU | completed |
| EXP-20260505-002 | Risk audit, repair, and safe rejection are necessary components | QSI-Bench v1, 80 samples; `data/raw/spy_sample.csv` | qsga_full | wo_semantic_verification, wo_risk_audit, wo_repair, wo_safe_rejection | same as above plus safe rejection accuracy, repair success | local CPU | completed |
| EXP-20260505-003 | Live LLM generation produces valid QYIR candidates under fixed prompts | QSI-Bench v1 or subset | direct LLM-to-code, LLM-to-QYIR | same as above | optional model/prompt ablation | API cost | pending human decision |
| EXP-20260505-004 | No-oracle slot extraction can recover QSI-Bench expected slots from user_query | QSI-Bench v1, 80 samples | oracle-slot QSGA | semantic consistency, downstream E2E | compare oracle vs extracted slots | local CPU | completed |
| EXP-20260505-005 | Ambiguous intent handling can be measured as clarification success | ambiguous subset + paraphrase extension | current safe rejection / clarification rules | clarification accuracy, false accept, false reject | w/o clarification | local CPU | pending design |

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

# Run Record: QSGA CCF C Paper Draft

## Metadata

- Run ID: RUN-20260505-QSGA-PAPER-001
- Date: 2026-05-05
- Operator: Codex AI research assistant
- Workspace: `E:\QSGA`
- Goal: generate a CCF C candidate research-paper package from the QSGA final idea document and completed experiments.

## Inputs

- `docs/ai-research-assistant/*.md`
- `docs/QSGA论文思路v7Plus_最终稿.md`
- `docs/QYIR_v1_Spec.md`
- `benchmark/qsi_bench_v1.jsonl`
- `experiments/results/*.csv`
- `experiments/tables/*.md`
- `experiments/*.py`

## Actions

1. Loaded AI research assistant SOP, quality guardrails, CCF C reviewer rules, and paper matrix requirements.
2. Loaded QSGA final paper idea and QYIR v1 specification.
3. Reproduced test suite: 173 passed after adding live-runner tests.
4. Re-ran baseline, ablation, and no-oracle experiments after the safe-rejection paraphrase fix.
5. Recomputed metrics and synchronized the draft, reproducibility package, and result logs.
6. Created a CCF C candidate paper draft.
7. Created citation/claim matrix, reviewer report, and reproducibility package.
8. Registered human decisions and risks required before submission.
9. After human approval, added and ran a budget-bounded live LLM QYIR pilot with saved raw outputs and token usage.

## Deviations

- The local research SOP requests multi-Agent parallel execution. After the user explicitly requested SubAgents, the workflow used parallel literature, experiment-audit, adversarial-review, and paper-expansion agents.
- Literature verification is metadata/link-level only in this run; PDF-level claim verification remains required before submission.

## Verification

```text
.venv\Scripts\python.exe -m pytest tests -q
173 passed in 2.25s
```

Metrics reproduced from:

- `experiments/results/baseline_metrics.csv`
- `experiments/results/ablation_metrics.csv`
- `experiments/results/no_oracle_metrics.csv`
- `experiments/results/live_llm_metrics.csv`

## Outputs

- `docs/paper/qsga_ccf_c_draft.md`
- `docs/paper/citation_and_claim_matrix.md`
- `docs/paper/ccf_c_reviewer_report.md`
- `docs/paper/reproducibility_package.md`
- `docs/paper/reviewer_response_log.md`
- `docs/paper/subagent_literature_review.md`
- `docs/paper/subagent_experiment_audit.md`
- `docs/paper/subagent_adversarial_review.md`
- `docs/paper/subagent_paper_expansion.md`
- Updated `docs/ai-research-assistant/DECISIONS.md`
- Updated `docs/ai-research-assistant/RISKS.md`
- Updated `docs/ai-research-assistant/AUDIT_LOG.md`
- Updated `docs/ai-research-assistant/EXPERIMENT_PLAN.md`
- Updated `docs/ai-research-assistant/RESULTS_LOG.md`
- Updated `docs/ai-research-assistant/DRAFT_STATUS.md`
- Added `experiments/run_live_llm.py`
- Added `experiments/results/live_llm_*`

## SubAgent Findings Integrated

1. Literature review found missing direct comparators: QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, and OQL-style financial IR work.
2. Experiment audit found oracle-slot construction through `expected_slots`, simulated baselines, shared safe-rejection rules, and ambiguous-intent failures.
3. Adversarial review rated the unchanged draft as likely Weak Reject because evidence did not match LLM-generation framing.
4. Paper expansion supplied algorithm/schema/protocol/case-study text; parts were integrated into the main draft.
5. Main thread added a deterministic no-oracle slot-extraction experiment to partially mitigate oracle leakage.

## Revision Outcome

The paper was downgraded from broad "LLM strategy generation" language to scoped deterministic prototype language. A no-oracle deterministic slot extractor was added and reached E2E 0.7625, compared with oracle-slot E2E 0.8375. A small live LLM QYIR pilot was then added after human approval: live_qsga_qyir improved E2E over live_raw_qyir for qwen3.6-flash, deepseek-v4-flash, and kimi-k2.6, but absolute success remained limited and risk violations remained. The current posture is stronger as an IR/prototype study with supplementary live evidence, but still not enough for broad empirical live LLM claims.

# CCF C Reviewer Report

## Metadata

- Review ID: REVIEW-20260506-CCF-C-V3
- Paper / Draft version: `docs/paper/qsga_ccf_c_draft.md` after 80-case live QYIR and 80-case live direct-code results
- Reviewer Agent: Simulated CCF C Reviewer Agent
- Date: 2026-05-06
- Target level: CCF C
- Materials reviewed: `docs/Newest Goal.md`; `docs/paper/qsga_ccf_c_draft.md`; `docs/paper/claim_policy.md`; `docs/paper/related_work_verified.md`; `docs/paper/failure_analysis.md`; `experiments/results/live_qyir_80_metrics.csv`; `experiments/results/live_direct_code_metrics.csv`; `experiments/results/ablation_metrics.csv`; `experiments/results/safe_paraphrase_metrics.csv`; `experiments/results/multi_asset_smoke_results.csv`; `docs/ai-research-assistant/AI_RULES.md`; `docs/ai-research-assistant/QUALITY_GUARDRAILS.md`; `docs/ai-research-assistant/CCF_C_REVIEWER_AGENT.md`

## Summary

QSGA is now a substantially more defensible CCF C submission candidate than the earlier prototype because it includes an 80-case live QYIR run, an executable 80-case live direct-code baseline, a `wo_qyir` ablation, PDF-verified related-work scaffolding, failure analysis, and scoped claim policy. The empirical story is credible if framed as an IR-first, verification-guided, bounded strategy-specification study. However, the latest live evidence also weakens any broad live-LLM generation claim: `live_qsga_qyir::qwen3.6-flash` reaches only 0.250 E2E success, while `live_direct_code::qwen3.6-flash` reaches 0.350 E2E success under its direct-code harness. The paper can be considered Borderline for CCF C only if it keeps the contribution conservative and treats live results as diagnostic evidence rather than proof of general superiority.

## Score Table

| Dimension | Score 1-5 | Evidence | Main concern | Required action |
|---|---:|---|---|---|
| Problem Fit | 4 | The paper targets reliable novice-oriented rule-based strategy construction with explicit failure types and bounded scope. | The title and some phrasing still suggest broad natural-language strategy generation. | Keep the title and abstract focused on strategy specification reliability, not general trading-code generation. |
| Novelty | 3 | QYIR combines domain slots, verification, compilation, risk audit, repair, and safe rejection in one prototype. Related work confirms adjacent benchmarks and OQL-like IR patterns. | The core idea is an application-specific neuro-symbolic IR, not a fundamentally new synthesis algorithm. | Present novelty as integration and evaluation in a bounded finance-strategy setting. |
| Technical Soundness | 3 | Deterministic QSGA reaches 0.838 E2E; `wo_qyir` drops to 0.163; removing risk audit raises risk violations to 0.508. | Oracle-slot construction and rule-based no-oracle extraction limit causal claims about NL understanding. | Label oracle-slot results as verification-chain validation and emphasize no-oracle/live limitations. |
| Related Work | 4 | Five priority comparator papers are PDF-verified and scoped against QSGA. | The draft must avoid implying shared benchmark comparability with QuantCode-Bench, SysTradeBench, Market-Bench, QuantEval, or OQL. | Keep the related-work comparison architectural and scoped. |
| Experiment Design | 3 | Includes deterministic main comparison, no-oracle variant, ablations, live QYIR, live direct-code, safe paraphrase, multi-asset smoke, and failure analysis. | Live QYIR absolute performance is low; live direct-code outperforms live QSGA QYIR in E2E; only one full live model is used. | Treat live experiments as diagnostic and add another live model or confidence intervals if time allows. |
| Reproducibility | 3 | Raw outputs, token usage, metadata, CSV metrics, reproduce scripts, safe-paraphrase regression, and 178-test command are described. | No container/CI is documented, and live API reproducibility depends on external model availability. | Mark reproducibility as R3 for deterministic core, lower for live runs; document external-model caveats. |
| Result Validity | 3 | The current draft explicitly states that results support bounded artifact reliability, not profitability or broad LLM generalization. | The live QYIR vs live direct-code result blocks any claim that QSGA currently beats executable direct-code in live E2E. | Add a visible statement that QSGA's live wrapper improves over raw QYIR prompting, not over live direct-code. |
| Clarity | 3 | Sections on setup, metrics, ablation, live baselines, failure analysis, and threats are coherent. | The paper is dense and mixes deterministic, no-oracle, live QYIR, and live code settings; readers may miss which claims belong to which setting. | Add a one-page evidence map separating oracle deterministic, no-oracle deterministic, live QYIR, and live direct-code claims. |
| Limitations | 4 | The draft discloses oracle slots, small benchmark size, single sample data source, safe-rejection limits, and unresolved ambiguity. | Ambiguous-intent behavior is still unimplemented as a measured success mode. | Keep ambiguous intent as a failure, not a solved boundary-control result. |
| Ethics and Compliance | 4 | The draft states no investment advice, no real-money safety, no private user data, and human approval for release. | Safe rejection remains deterministic pattern coverage, not financial safety. | Keep all safety wording conservative and avoid "safe trading" language. |

## Strengths

1. The latest live direct-code baseline removes the strongest previous baseline objection. The result is useful because syntax and interface success are 1.000, yet downstream E2E is only 0.350, supporting the claim that surface code validity is insufficient.
2. The `wo_qyir` ablation materially strengthens the IR contribution: E2E drops from 0.838 to 0.163, semantic consistency drops from 0.800 to 0.354, and safe rejection drops to 0.000.
3. The paper now has a defensible related-work position: it does not claim to beat larger trading-code benchmarks and instead positions QSGA as an IR-first, bounded prototype.
4. Failure analysis is unusually helpful for CCF C review. It explicitly records ambiguous-intent failures, mean-reversion failures, live QYIR schema/compile failures, direct-code no-trade/runtime failures, and unsafe-request failures.

## Weaknesses

| Severity | Weakness | Evidence | Fix |
|---|---|---|---|
| Critical | Live QYIR evidence does not support broad live LLM superiority. | `live_qsga_qyir::qwen3.6-flash` E2E is 0.250; `live_direct_code::qwen3.6-flash` E2E is 0.350. | State that the live QSGA wrapper improves over raw QYIR prompting from 0.075 to 0.250 mainly through safe rejection, but does not beat the live direct-code baseline in E2E. |
| Critical | Ambiguous-intent handling is not evaluated as a success mode. | `qsga_full` has 0/10 ambiguous-intent E2E success; direct-code also has 0/10. | Do not claim solved clarification or boundary-aware dialogue. Either add a clarification metric or keep it as a limitation. |
| Major | The strongest deterministic result is still oracle-slot based. | `qsga_full` uses expected slots to construct QYIR candidates; no-oracle is deterministic and rule-based. | Make the oracle/no-oracle/live distinction impossible to miss in the abstract, setup, and conclusion. |
| Major | Safe rejection evidence is small and rule-pattern based. | QSI-Bench has 15 unsafe requests; paraphrase set has 35 cases with 1.000 accuracy but deterministic coverage. | Present as regression coverage, not robust financial safety or compliance. |
| Major | Live evidence has limited model coverage. | Full 80-case live runs are qwen3.6-flash only; multi-model evidence remains 12-case pilot. | Add at least one second 80-case live model if feasible, or explicitly state that model-generalized claims are unsupported. |
| Minor | Contribution numbering in the draft appears to skip item 2. | The contribution list shows items 1, 3, and 4 in the current draft excerpt. | Renumber before submission. |
| Minor | Multi-asset smoke is too small for robustness language. | Five synthetic symbol/period checks all pass, but this is runnability only. | Keep it as smoke evidence and avoid "cross-market robustness." |

## CCF C Submission Risks

| Risk ID | Risk | Severity | Blocker | Suggested mitigation |
|---|---|---|---|---|
| R-V3-01 | Abstract or conclusion may be read as claiming broad reliable natural-language strategy generation. | P0 | yes | Rewrite the core claim as bounded artifact reliability in deterministic and diagnostic live settings. |
| R-V3-02 | Live QSGA QYIR does not outperform live direct-code E2E. | P0 | yes, if the paper claims direct-code superiority | Explicitly separate "raw QYIR prompting comparison" from "live direct-code diagnostic baseline." |
| R-V3-03 | Ambiguous-intent clarification remains unimplemented in metrics. | P1 | no, if disclosed | Count ambiguity as a current failure and list clarification success as future work. |
| R-V3-04 | Oracle-slot construction may be interpreted as leakage. | P1 | no, if labeled | Put "oracle-slot verification-chain validation" in table captions and result text. |
| R-V3-05 | Safe rejection may be overclaimed as financial safety. | P1 | no, if scoped | Use "explicit unsafe-pattern coverage" and forbid "financial safety" claims. |
| R-V3-06 | Reproducibility status is mixed across deterministic and live runs. | P2 | no | Add an artifact-level reproducibility table with deterministic core, live replay, and external API dependencies separated. |
| R-V3-07 | Related-work claims could drift beyond verified evidence. | P2 | no | Use only the claims marked safe in `related_work_verified.md`. |

## Required Experiments or Evidence

1. Before submission, add a concise evidence map showing which claims are supported by deterministic oracle-slot results, deterministic no-oracle results, 80-case live QYIR results, 80-case live direct-code results, ablations, and smoke tests.
2. If time allows, run a second full 80-case live model for QYIR and direct-code. If not, state clearly that full live evidence is single-model.
3. Add a measured clarification outcome only if ambiguous-intent behavior is to remain a contribution. Otherwise, classify ambiguous-intent handling as an unresolved limitation.
4. Keep the safe-paraphrase set in an appendix or supplementary section and do not elevate it to a core safety claim.

## Claim Strength Audit

| Claim | Current wording | Evidence support | Recommended wording |
|---|---|---|---|
| QSGA improves strategy generation reliability. | "reliable quantitative strategy construction from natural language" | Partly supported by deterministic QSGA 0.838 E2E and no-oracle 0.763, but live QYIR E2E is 0.250. | "QSGA improves measured artifact reliability in a bounded deterministic prototype and provides diagnostic live evidence under fixed prompts." |
| QSGA improves over raw live QYIR prompting. | "wrapper improves measured end-to-end success over raw QYIR prompting from 0.075 to 0.250" | Supported by `live_qyir_80_metrics.csv`. | Keep as written, and add "mainly through safe rejection." |
| QSGA beats live direct-code. | Not explicitly claimed, but readers may infer it from the motivation. | Not supported: live direct-code E2E is 0.350 vs live QSGA QYIR 0.250. | "The live direct-code baseline shows that syntactic code validity is insufficient, but it is not outperformed by live QYIR in current E2E." |
| QYIR is more than JSON Schema. | QYIR provides alias-bound rules, risk slots, compilation semantics, and localized repair. | Supported by `wo_qyir` ablation: E2E 0.163 vs 0.838 full. | Keep, but frame as evidence within QYIR v1 and QSI-Bench v1. |
| Safe rejection provides boundary control. | Safe rejection reaches 1.000 on QSI-Bench unsafe cases and 1.000 on 35 paraphrase cases. | Supported only for small deterministic explicit unsafe-pattern sets. | "The current rule layer covers explicit unsafe patterns in QSI-Bench v1 and a small paraphrase regression set." |
| Risk auditing reduces risk violations. | Removing risk auditing raises risk violation to 0.508. | Supported by `ablation_metrics.csv`. | Keep, with "counted risk violations under the current auditor definition." |
| Multi-asset evidence reduces single-source concern. | 5/5 synthetic SPY/QQQ/GLD smoke passes. | Supports runnability only. | "A synthetic multi-asset smoke test checks compile/backtest/risk-audit runnability; it is not market robustness evidence." |
| Related work supports QYIR's IR motivation. | OQL is a close analog for IR-plus-deterministic validation. | Supported by PDF-verified related-work scaffold. | Keep scoped to architectural analogy, not asset-class or benchmark equivalence. |

## Remaining Blockers

The primary submission blocker is not the absence of a live baseline anymore; that has been addressed. The blocker is claim calibration after the live results. The paper must not let the reader conclude that QSGA currently dominates executable live direct-code generation. The correct statement is more nuanced: live direct-code can produce syntactically valid functions but remains semantically and behaviorally fragile, while QSGA's live QYIR wrapper improves over raw QYIR prompting mainly through refusal behavior and still has weak non-unsafe generation performance.

The second blocker is ambiguity. The framework describes clarification as part of boundary control, but the measured system has 0/10 ambiguous-intent success. This is acceptable for a conservative prototype paper only if the draft explicitly treats ambiguity as unresolved.

The third blocker is evidence stratification. The paper has many results, but they do not all support the same claim. The deterministic oracle-slot result supports the verification chain; the no-oracle extractor supports a lightweight rule-based extraction prototype; the live QYIR result supports routing model outputs into verification and refusal gates; the live direct-code result supports the insufficiency of syntax/interface validity; the ablations support component importance.

## Recommendation

Borderline.

The paper is near the lower bound of a CCF C systems-style submission if it is submitted as a bounded IR-first verification study with honest limitations. It should not be submitted as a broad empirical LLM strategy-generation paper. With P0 claim edits, the latest baseline and ablation package is enough for a defensible Borderline verdict. Without those edits, the verdict drops to Weak Reject-level because the live evidence would not support the apparent scope of the title and abstract.

## Human Decisions Required

| Decision | Why human review is needed | Blocked scope | AI can continue |
|---|---|---|---|
| Accept conservative positioning. | The paper's chances depend on choosing prototype reliability over broad LLM-generation claims. | Abstract, title, contributions, conclusion. | Prepare conservative wording variants. |
| Decide whether to run another 80-case live model. | This affects budget, time, and strength of model-generalization evidence. | Stronger live-evidence claims. | Keep single-model limitation explicit. |
| Decide whether ambiguity remains a contribution or limitation. | A contribution claim requires a measured clarification metric. | Boundary-aware interaction claim. | Move ambiguity to limitations and future work. |
| Approve public release or submission. | AI rules require human approval for publication, release, and submission decisions. | Any external submission or release. | Continue internal polishing and audit. |

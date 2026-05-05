# CCF C Reviewer Report

## Metadata

- Review ID: CCF-C-QSGA-20260505-001
- Paper / Draft version: `docs/paper/qsga_ccf_c_draft.md`
- Reviewer Agent: simulated CCF C reviewer, single-process execution due current tool constraints
- Date: 2026-05-05
- Target level: CCF C
- Materials reviewed:
  - `docs/QSGA论文思路v7Plus_最终稿.md`
  - `docs/QYIR_v1_Spec.md`
  - `benchmark/qsi_bench_v1.jsonl`
  - `experiments/results/*.csv`
  - `experiments/tables/*.md`
  - `experiments/results/live_llm_*.csv`
  - `experiments/baselines.py`
  - `experiments/run_live_llm.py`
  - `docs/paper/qsga_ccf_c_draft.md`

## Summary

The draft has a coherent systems/methods paper shape: it identifies a bounded natural-language quantitative strategy construction task, introduces QYIR as an explicit intermediate representation, and supports the design with a reproducible 80-sample deterministic prototype evaluation. After adversarial and experiment-audit review, the evidence issue became sharper: the original QSGA numbers were oracle-slot deterministic results because QYIR candidates were constructed from benchmark expected slots, and the direct-code/direct-JSON baselines were simulated rather than live LLM outputs. The draft has now been revised to disclose this, a deterministic no-oracle slot-extraction experiment was added, reaching 0.7625 E2E success, and a small live LLM QYIR pilot with saved raw outputs was run. The live pilot partially mitigates the no-live-evidence objection, but its 12-case scale and low absolute E2E rates do not support broad empirical LLM claims. The recommendation is Borderline for a clearly scoped prototype/IR feasibility study with live pilot evidence, or Weak Reject-level if framed as a standard broad empirical LLM paper.

## Score Table

| Dimension | Score 1-5 | Evidence | Main concern | Required action |
|---|---:|---|---|---|
| Problem Fit | 4 | clear bounded task and failure taxonomy | target venue may expect stronger empirical novelty | keep scope explicit |
| Novelty | 3 | QYIR + risk-aware repair framing | could be viewed as engineering integration | emphasize IR semantics and repair locality |
| Technical Soundness | 3 | real validators, compiler, backtester, tests, no-oracle extractor, live QYIR pilot | main baselines still simulated; live pilot is small | expand live evaluation and direct-code baseline |
| Related Work | 3 | credible related areas identified | citations are metadata-level, not PDF-level verified | upgrade key citations to Level A |
| Experiment Design | 3 | 80-sample benchmark, deterministic ablations, no-oracle run, 3-model live pilot | simulated baselines, single data source, small live subset | expand live LLM baselines and robustness |
| Reproducibility | 4 | 171 tests pass; scripts and CSVs available | no container or CI evidence | add exact reproduction commands |
| Result Validity | 3 | metrics reproducible; no-oracle E2E 0.7625; live QSGA improves over raw QYIR in pilot | live absolute success remains low; no executable live-code baseline | keep claims scoped to IR/prototype plus pilot |
| Clarity | 4 | draft structure is readable | method/results could use diagrams in final PDF | add final figures |
| Limitations | 4 | deterministic scope and financial safety limitations included | needs human approval before submission | keep limitations prominent |
| Ethics and Compliance | 4 | no investment-advice claim; no private data | public release not approved | keep human gate |

## Strengths

1. The paper has a focused and defensible problem framing: reliability, not profitability.
2. QYIR gives the system a clear technical center beyond prompt engineering.
3. The experiment artifacts are reproducible from local code and supported by passing tests.

## Weaknesses

| Severity | Weakness | Evidence | Fix |
|---|---|---|---|
| Major | Main 80-case evidence may be considered too synthetic | deterministic main harness; live pilot is only 12 cases | submit as prototype/system study or expand live evaluation |
| Major | QYIR candidates are constructed from expected slots in the oracle run | experiment audit found `build_qyir_from_record(record)` uses gold slots | no-oracle run added; keep oracle result labeled as such |
| Critical | Direct-code/direct-JSON baselines are simulated in the main run | experiment audit found category-level and damaged-QYIR approximations; live pilot covers QYIR prompting only | add executable live-code baseline or remove strong direct-code comparative claims |
| Major | Related-work verification is not yet submission-grade | citation matrix Level B | check PDFs and map key claims to sections |
| Major | Semantic verification ablation does not show gain | `wo_semantic_verification` equals full QSGA | remove standalone semantic-verifier contribution claim |
| Major | Safe rejection evidence is partly shared-rule driven | safe rejection is high across methods | rely on `wo_safe_rejection` ablation and disclose limitation |
| Minor | Case analysis is too short for final paper | current table has three compact rows | expand with QYIR snippets and repair traces |
| Minor | No final camera-ready figures | only Mermaid architecture exists | create vector or PDF figures before submission |

## CCF C Submission Risks

| Risk ID | Risk | Severity | Blocker | Suggested mitigation |
|---|---|---|---|---|
| R-001 | Live LLM generation evidence is small | P1 | yes for strong LLM claims | expand beyond 12-case pilot or keep as supplementary evidence |
| R-002 | Oracle-slot construction uses expected slots | P1 | partially mitigated | no-oracle deterministic slot extraction added; live LLM still needed |
| R-003 | Simulated baselines are not fair live LLM competitors | P1 | yes for comparative claims | add executable live-code baseline or remove strong direct-code claims |
| R-004 | Citation verification only Level B | P1 | yes before submission | PDF-level citation audit |
| R-005 | Single-symbol sample data | P2 | no if scope remains prototype | add more symbols or disclose |
| R-006 | Semantic ablation no independent effect | P2 | no | frame as engineering gate |
| R-007 | Public release and authorship not approved | P0 | yes for submission/publication | human approval required |

## Required Experiments or Evidence

1. Expand live LLM-backed QYIR generation beyond the current 12-case pilot if making strong live-model claims.
2. Replace or supplement simulated direct-code/direct-JSON baselines with executable real model outputs.
3. Add exact reproduction commands and environment details to the appendix.
4. Upgrade at least the core related-work citations to PDF-level verification, especially direct trading-code benchmark papers.
5. Expand qualitative cases with before/after QYIR fragments and verifier errors.

## Claim Strength Audit

| Claim | Current wording | Evidence support | Recommended wording |
|---|---|---|---|
| QSGA improves end-to-end generation success | "improves" | oracle-slot result and no-oracle deterministic run support prototype claim only | "improves measured artifact reliability in deterministic prototype evaluation" |
| QYIR improves semantic slot alignment | partly supported | full and semantic ablation same | "QYIR exposes semantic slots and supports slot-level checks" |
| Safe rejection reduces unsafe acceptance | supported by ablation | deterministic rule-based | "safe rejection mechanism reduces unsafe acceptance in QSI-Bench v1" |
| QSGA handles financial risk | too broad if phrased strongly | historical/sample risk audit only | "audits selected historical risk constraints" |
| CCF C publishable | borderline if scoped | human approval and evidence gaps remain | "Borderline as an IR/prototype study with live pilot; not enough for broad empirical LLM claims" |

## Recommendation

Borderline for a clearly framed prototype / IR feasibility study with supplementary live pilot evidence; Weak Reject-level for a standard broad empirical LLM submission.

The draft has improved by disclosing oracle-slot construction, simulated baselines, category-level failures, and related direct trading-code benchmarks. A no-oracle deterministic slot-extraction experiment has been added, and a small live QYIR pilot now supplies saved raw model outputs. It still needs a larger live evaluation and an executable live-code baseline before it can credibly claim broad model-backed end-to-end natural-language strategy generation performance.

## Human Decisions Required

| Decision | Why human review is needed | Blocked scope | AI can continue |
|---|---|---|---|
| Whether to expand live LLM experiments | affects cost, model choice, and claims | final empirical claims | polish scoped prototype draft |
| Whether to submit as prototype/system paper | affects target venue and framing | target venue and abstract | prepare conservative version |
| Whether to publicize code/data | external release and licensing | publication package | prepare internal reproducibility docs |
| Authorship and acknowledgments | academic responsibility | submission | leave placeholders |

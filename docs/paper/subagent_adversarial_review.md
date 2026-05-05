# Adversarial CCF-C Review for `qsga_ccf_c_draft.md`

Role: Adversarial CCF-C Reviewer  
Date: 2026-05-05  
Likely recommendation if unchanged: Weak Reject

## Overall Verdict

The draft is readable and scoped more conservatively than many prototype papers, but a skeptical CCF-C reviewer can still reject it on evidence strength. The central weakness is that the paper repeatedly motivates itself as natural-language / LLM strategy generation while the actual evaluation is a deterministic prototype with simulated baselines, a small self-constructed benchmark, shared rule-based rejection logic, and a single historical data source. Several strong result phrases are directionally correct only inside this narrow harness, but they still read stronger than the evidence supports.

Immediate revision should either add live LLM experiments and robustness checks, or explicitly reframe the paper as a deterministic systems prototype / IR feasibility study.

## Critical Issues

### C1. The paper still reads like an LLM generation paper, but the evaluation contains no live LLM outputs.

- **Text location:** `docs/paper/qsga_ccf_c_draft.md` lines 7, 15, 36, 268, 280, 480, 504; especially Abstract line 11 and Contribution line 28.
- **Counterargument:** A reviewer can say the main empirical claim is not actually about LLM-based generation. The draft's motivation and title evoke LLM-to-code/program synthesis, but the reported numbers come from deterministic approximations. This is enough for Weak Reject if the target venue expects empirical LLM evidence.
- **Evidence:** The draft itself says the experiments avoid live LLM calls (line 280) and are a deterministic prototype (line 174). `citation_and_claim_matrix.md` C08 states the current experiments do not prove online LLM generalization. `RISKS.md` RISK-20260505-001 states the same as a P1 risk. `ccf_c_reviewer_report.md` R-001 says no live LLM generation experiment is a blocker for strong LLM claims.
- **Recommended modification:** In Abstract, Introduction, Contributions, Results, and Conclusion, replace general claims about "generation" or "LLM-to-code" improvement with "deterministic prototype evaluation of a QYIR-centered pipeline." If the paper wants to keep LLM framing, add at least one live-model experiment with fixed model version, prompts, temperature, logs, and direct-code/direct-JSON baselines.

### C2. The benchmark labels appear to leak into generation or verification, making the task partly oracle-driven.

- **Text location:** Algorithm 1 input line 177 (`B: benchmark annotation or extracted expected slots`), Protocol lines 278-280, Semantic ablation discussion line 360.
- **Counterargument:** If expected slots or benchmark annotations are available to the system during QYIR construction, this is not natural-language strategy generation; it is label-conditioned construction. A reviewer will treat the 0.800 semantic consistency and 0.825 E2E success as inflated unless the paper separates gold annotations from model/system inputs.
- **Evidence:** Line 177 explicitly lists benchmark annotation or extracted expected slots as algorithm input. Line 360 admits expected-slot construction already encodes many slot constraints. `RISKS.md` RISK-20260505-003 says semantic verification has no independent measured gain. `citation_and_claim_matrix.md` forbids claiming independent semantic verification improvement.
- **Recommended modification:** Rewrite Algorithm 1 and Experimental Setup to distinguish two modes: oracle-label prototype versus real NL extraction. If current experiments use gold slots, label the results "oracle-slot deterministic evaluation" and remove claims about end-to-end NL understanding. If not, add a precise description of the automatic extractor and prove labels are used only for evaluation.

### C3. The direct-code and direct-JSON baselines are too synthetic to support comparative improvement claims.

- **Text location:** Methods lines 268-272; Main Comparison lines 342-348; Abstract line 11; Contribution line 28.
- **Counterargument:** The reported gains may be artifacts of baseline design. `direct_code` has schema validity 0.000 because code does not produce QYIR, while QSGA is built to satisfy QYIR. That metric is not comparable across methods. A reviewer can argue the baselines were constructed to fail the proposed metrics.
- **Evidence:** Line 268 calls `direct_code` a deterministic approximation, not an actual direct LLM pipeline. Line 280 confirms no live API calls. The main table reports `direct_code` schema validity as 0.000, which is expected if the method is not asked to emit QYIR. `ccf_c_reviewer_report.md` flags deterministic baselines as a Major weakness.
- **Recommended modification:** Rename these as "simulated direct-code" and "simulated direct-JSON" throughout. Add real LLM baselines, or remove claims of improvement over direct generation. For fairness, define metrics that apply to each method's intended output, and do not count absence of QYIR as a schema failure unless all baselines are required to emit QYIR.

### C4. The claim that QSGA reduces risk violations to 0.000 is stronger than the evidence.

- **Text location:** Abstract line 11; Results lines 342-348; Conclusion line 504; Threats lines 488-492.
- **Counterargument:** "Reducing risk violations to 0.000" can be read as a financial safety claim, especially in an investment context for novice users. The evidence only shows selected historical constraints on one sample daily data source under a deterministic strategy space.
- **Evidence:** Threats to Validity admits the backtest uses SPY sample data and does not establish cross-market robustness (line 488). `RISKS.md` RISK-20260505-001 and `ccf_c_reviewer_report.md` R-003 identify the empirical scope as limited. The paper also says historical backtest risk metrics do not guarantee future performance (line 492).
- **Recommended modification:** Replace every "reduces measured risk violations to 0.000" / "eliminates measured risk violations" phrase with "observed zero violations of the implemented risk-audit checks on QSI-Bench v1 using the SPY sample data." Add a result table or appendix showing which exact risk constraints were audited.

### C5. Safe rejection evidence is not method-specific because most methods share the same deterministic unsafe detector.

- **Text location:** Safe Rejection table lines 379-385; discussion line 385; Contribution line 27; Conclusion line 504.
- **Counterargument:** The paper implies QSGA's architecture improves safe rejection, but `direct_code`, `direct_json`, and QSGA variants all get 0.933 safe rejection accuracy. This suggests the result comes from a shared rule, not from QYIR or verification-guided repair.
- **Evidence:** Lines 379-383 report identical 14/15 correct rejection for direct baselines and QSGA full. Line 385 admits the detector is deterministic and shared. `ccf_c_reviewer_report.md` flags this as a Major weakness. `citation_and_claim_matrix.md` supports only the ablation where removing safe rejection drops to 0.000.
- **Recommended modification:** Stop presenting safe rejection as comparative evidence for QSGA. Reframe it as a required guardrail component. Add a separate unsafe-intent robustness test with paraphrases, indirect unsafe goals, adversarial wording, and false-positive analysis.

## Major Issues

### M1. Semantic verification is listed as a contribution, but the ablation shows no independent gain.

- **Text location:** Contributions lines 25-27; Verification Chain line 224; Ablation lines 354-360; Conclusion line 504.
- **Counterargument:** A reviewer will ask why semantic verification is a contribution if removing it leaves every reported metric unchanged. The draft partially admits this but still lists semantic consistency and semantic verification prominently.
- **Evidence:** Line 355 shows `wo_semantic_verification` equals `qsga_full` on semantic consistency, risk violation, safe rejection, repair success, and E2E success. `RISKS.md` RISK-20260505-003 and `citation_and_claim_matrix.md` both say this claim must be downgraded.
- **Recommended modification:** Remove semantic verification as a standalone empirical contribution. Present it as a design invariant or engineering check. Add examples where semantic verification catches errors not caught by schema, or remove it from the main contribution list.

### M2. Repair success of 1.000 looks tautological under the current deterministic harness.

- **Text location:** Localized Repair lines 231-243; Repair Effect lines 365-373.
- **Counterargument:** Since repairable failures are mapped to fixed QYIR fields and repair actions, a 1.000 repair success rate may simply show the benchmark only contains repair cases the hand-written repair rules cover. It does not prove robust repair of LLM errors.
- **Evidence:** Line 373 admits the result only supports error-location-action design under the controlled benchmark. The table reports `qsga_full` repairs 49/49 and `qsga_no_risk_audit` repairs 26/26. No unrepairable local error distribution is shown.
- **Recommended modification:** Add a breakdown of repair error types and failed repair cases. Rename "Repair Success" to "Success on predefined repairable failures." Add adversarial malformed QYIR cases or real LLM outputs to test repair beyond hand-coded paths.

### M3. QSI-Bench v1 is too small and under-specified for the strength of the quantitative claims.

- **Text location:** QSI-Bench section lines 246-260; Metrics line 304; Threats lines 484-488.
- **Counterargument:** An 80-sample, self-constructed Chinese benchmark without annotation protocol details, inter-annotator agreement, or public sampling rationale is weak evidence for a CCF-C empirical paper.
- **Evidence:** The draft admits QSI-Bench v1 is small and not comprehensive (lines 248, 304, 484). `ccf_c_reviewer_report.md` lists 80-sample benchmark and deterministic harness as experiment-design concerns.
- **Recommended modification:** Add benchmark construction details: source of prompts, annotation rubric, number of annotators, disagreement handling, category balance rationale, and examples per category. If no human annotation exists, explicitly call it a curated prototype benchmark and reduce quantitative emphasis.

### M4. Single-symbol SPY sample data undermines all execution and risk generality claims.

- **Text location:** QYIR support table line 144; Reproducibility artifacts line 310; Threats line 488; Results line 348.
- **Counterargument:** Backtest success and risk-audit success on one symbol cannot support claims about quantitative strategy generation reliability beyond "the compiler runs on the sample file."
- **Evidence:** Line 488 states the current backtest uses SPY sample data and does not establish cross-market robustness. The artifact list names `data/raw/spy_sample.csv`. `ccf_c_reviewer_report.md` flags single-symbol sample data as R-003.
- **Recommended modification:** Add at least a small robustness suite across multiple symbols and periods, or explicitly restrict all execution/risk claims to "single-symbol SPY sample-data smoke tests."

### M5. Novelty of QYIR over schema-constrained JSON is asserted more than demonstrated.

- **Text location:** Background lines 45-57; QYIR section lines 131-157; Related Work lines 466-470.
- **Counterargument:** The draft says QYIR is "not just JSON schema," but the empirical comparison does not isolate what semantic IR adds beyond schema, enums, validators, and deterministic compilation. A reviewer may classify the contribution as ordinary DSL engineering.
- **Evidence:** `ccf_c_reviewer_report.md` scores Novelty as 3 and says QYIR + risk-aware repair could be viewed as engineering integration. The semantic-verification ablation gives no independent gain. The citation matrix marks the constrained-decoding / semantics claim as Medium and needing PDF-level checking.
- **Recommended modification:** Add a precise formal comparison: JSON schema baseline versus QYIR with alias resolution, operator semantics, compilation semantics, and risk-field invariants. Include at least one ablation that disables QYIR semantic constraints while keeping schema validity.

### M6. Metric denominators and comparability are not rigorous enough.

- **Text location:** Metrics definitions lines 287-302; Main Comparison lines 339-346.
- **Counterargument:** Several metrics are computed over non-rejected cases, while E2E is over all cases. Methods that reject or fail differently may be advantaged or penalized in opaque ways. Also, schema validity for `direct_code` is not comparable if the method emits code instead of QYIR.
- **Evidence:** Lines 296-302 define different denominators. The main table mixes QYIR-specific, execution-specific, and rejection metrics across methods with different output contracts.
- **Recommended modification:** Add a confusion-matrix-style accounting for all 80 samples per method: accepted-valid, accepted-invalid, rejected-correct, rejected-wrong, failed-compile, failed-risk. Separate QYIR-internal metrics from method-level user outcome metrics.

### M7. Related work is not submission-grade because all citations are only metadata/link verified.

- **Text location:** Related Work section lines 454-478; References lines 506-520.
- **Counterargument:** For CCF-C review, a related-work section that uses only title-level citation matching can be viewed as shallow or unreliable. The paper compares to constrained decoding, tool-using agents, execution-guided repair, and financial LLMs but does not cite precise claims or experimental settings.
- **Evidence:** `citation_and_claim_matrix.md` lists all literature entries as Verification Level B. `RISKS.md` RISK-20260505-002 says citation verification is a P1 risk. `ccf_c_reviewer_report.md` R-002 says PDF-level citation audit is required before submission.
- **Recommended modification:** Upgrade core citations to PDF-level claim-location verification. For each related-work paragraph, cite exact contributions and state why QSGA differs technically, not just topically.

### M8. The title and problem formulation overstate the formal program-synthesis angle.

- **Text location:** Title line 1; Problem Formulation lines 64-79; Algorithm 1 lines 174-204.
- **Counterargument:** The implementation appears closer to constrained configuration generation plus validation and repair than general program synthesis. Reviewers may see "program synthesis" as inflated unless there is a formal grammar, semantics, search space, or synthesis procedure.
- **Evidence:** QYIR v1 supports a small set of indicators, operators, and risk fields. Algorithm 1 uses `GenerateOrConstructQYIR`, which blurs generation and construction. The draft repeatedly says the system is deliberately bounded.
- **Recommended modification:** Retitle or rephrase as "verification-guided strategy specification generation" unless the paper adds formal synthesis semantics. Define the QYIR grammar and synthesis/search procedure if keeping "program synthesis."

### M9. The qualitative cases are too thin to support interpretability, repairability, and boundary-control claims.

- **Text location:** Qualitative Cases lines 387-452.
- **Counterargument:** The examples are summaries, not evidence. They do not show before/after QYIR, verifier messages, repair paths, or backtest/risk audit output. A CCF-C reviewer may treat them as illustrative prose rather than validation.
- **Evidence:** The current cases contain simplified traces only. `ccf_c_reviewer_report.md` already notes final cases need QYIR snippets and repair traces.
- **Recommended modification:** Add three concrete case studies with input, initial QYIR, verification failure, repair diff, final QYIR, and audit result. Include at least one failure case that QSGA rejects or cannot repair.

## Minor Issues

### m1. Reproducibility section lacks enough environment detail for a paper artifact.

- **Text location:** Implementation and Reproducibility lines 306-333.
- **Counterargument:** Listing scripts and "170 passing tests" is useful, but insufficient for an external reviewer to reproduce exact tables.
- **Evidence:** The draft lists paths and one pytest command, but no Python version, dependency lock, OS, commit hash, random seed policy, or table-generation command sequence.
- **Recommended modification:** Add a compact reproducibility block: environment, install command, test command, experiment command, table command, expected output files, and current commit/artifact hash if available.

### m2. The paper uses "novice users" as a motivation but does not evaluate novice-facing usability or explanation quality.

- **Text location:** Abstract lines 7-11; Introduction lines 15-23; Ethics lines 498-500.
- **Counterargument:** If novice users are central, reviewers may ask for user-facing explanation evaluation, readability criteria, or at least examples of final reports. Otherwise "novice-oriented" is just motivation.
- **Evidence:** Metrics focus on schema, semantic consistency, compile success, backtest success, risk violation, rejection, and E2E success. No metric evaluates explanation usefulness or novice comprehension.
- **Recommended modification:** Either remove "novice-oriented" from contribution-level claims, or add a small evaluation rubric for explanations and boundary messages.

### m3. Financial compliance wording should be stronger and more visible.

- **Text location:** Abstract line 11; Ethics and Compliance lines 498-500; Conclusion line 504.
- **Counterargument:** Even with disclaimers, the paper discusses generating executable strategies for novice investors. A reviewer may expect clearer boundaries around investment advice and real-money use.
- **Evidence:** The draft says QSGA does not claim investment safety and should not be used as investment advice, but this appears late and briefly.
- **Recommended modification:** Add a prominent statement in Introduction and System Output sections: QSGA produces research artifacts only, not investment advice; no recommendation to trade; all generated strategies require qualified human review.

### m4. The language and benchmark setting should be clarified.

- **Text location:** QSI-Bench line 248; Abstract and Introduction.
- **Counterargument:** The benchmark contains Chinese natural-language requests, but the paper is written in English and examples are Chinese. Reviewers may ask whether the method depends on Chinese keyword patterns, especially for unsafe detection.
- **Evidence:** QSI-Bench is described as 80 Chinese requests. Safe rejection is partly keyword-heavy according to lines 385 and 452.
- **Recommended modification:** State explicitly whether QSGA v1 targets Chinese inputs only, multilingual inputs, or language-agnostic QYIR slots. Add translation policy for examples and benchmark fields.

## Required Immediate Rewrite Checklist

1. Downgrade all abstract/result/conclusion claims from general LLM generation improvement to deterministic prototype evidence.
2. Clarify whether benchmark expected slots are system inputs. If yes, label the evaluation oracle-assisted.
3. Rename deterministic baselines and remove unfair QYIR-specific comparisons against direct code.
4. Rephrase risk results as implemented historical risk-audit checks on SPY sample data.
5. Reframe safe rejection as a shared guardrail, not QSGA-specific empirical superiority.
6. Remove standalone empirical claims for semantic verification or add evidence where it matters.
7. Add benchmark construction and annotation details.
8. Add multi-symbol or multi-period robustness, or explicitly state SPY-only smoke testing.
9. Upgrade related-work citations to PDF-level verification.
10. Add concrete QYIR repair traces and failure cases.

## Files Actually Read

- `E:\QSGA\docs\paper\qsga_ccf_c_draft.md`
- `E:\QSGA\docs\paper\ccf_c_reviewer_report.md`
- `E:\QSGA\docs\paper\citation_and_claim_matrix.md`
- `E:\QSGA\docs\ai-research-assistant\RISKS.md`
- `E:\QSGA\.agents\skills\bmad-review-adversarial-general\SKILL.md`

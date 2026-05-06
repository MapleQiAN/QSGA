# QSGA Submission Package Checklist

Date: 2026-05-06

Task ID: ARCHIVE-20260506-PACKAGE-AUDIT

This checklist maps the required items in `docs/Newest Goal.md` to the artifacts currently present in the repository. Status uses three labels: `done` means the artifact exists and appears usable for the submission package; `partial` means evidence exists but the package still needs reconciliation, wording, or broader coverage; `open` means the requested item is not yet present as a usable artifact.

The repository is not clean. `git status --short` shows existing modified files under `docs/paper/qsga_ccf_c_draft.md`, `experiments/run_live_direct_code.py`, tests, and `verifier/safe_rejection.py`, plus untracked `REPRODUCE.md`, live QYIR 80 outputs, figures, prompts, scripts, and benchmark additions. This audit does not treat those changes as mine and does not require reverting them.

## Checklist

| Newest Goal required item | Status | Current evidence path | Next action |
|---|---|---|---|
| Lock paper positioning as an IR-first, verification-guided bounded prototype/system study. | done | `docs/paper/claim_policy.md`; `docs/paper/qsga_ccf_c_draft.md` | Keep final abstract/conclusion within the current claim policy. |
| Use conservative abstract, contribution, and limitation claims. | done | `docs/paper/claim_policy.md`; `docs/paper/qsga_ccf_c_draft.md`; `docs/paper/reproducibility_package.md` | Human still must approve final wording before submission. |
| Keep the four core contributions: bounded formulation, QYIR, verification/repair, and QSI-Bench plus deterministic prototype plus live pilot/evaluation. | done | `docs/paper/claim_policy.md`; `benchmark/qsi_bench_v1.jsonl`; `experiments/results/baseline_metrics.csv`; `experiments/results/live_qyir_80_metrics.csv`; `experiments/results/live_direct_code_metrics.csv` | Contribution text now separates 12-case pilot, 80-case live QYIR, and 80-case live direct-code. |
| Expand live QYIR to 80 QSI-Bench cases. | done | `experiments/results/live_qyir_80_results.csv` with 160 rows; `experiments/results/live_qyir_80_metrics.csv`; `experiments/results/live_qyir_80_raw_outputs.jsonl`; `experiments/results/live_qyir_80_metadata.json`; `experiments/results/live_qyir_80_token_usage.csv` | Current metrics show `live_raw_qyir::qwen3.6-flash` E2E 0.075 and `live_qsga_qyir::qwen3.6-flash` E2E 0.375, but QSGA live construction success is only 0.0909. |
| Save live QYIR raw outputs, metadata, and token usage. | partial | `experiments/results/live_qyir_80_raw_outputs.jsonl`; `experiments/results/live_qyir_80_metadata.json`; `experiments/results/live_qyir_80_token_usage.csv`; batch files under `experiments/results/live_qyir_80_batch*.jsonl` and `.json` | Check the merged token-usage CSV: it currently contains only `model,method` without call or token counts, unlike the direct-code token-usage file. Also note `live_qyir_80_batch08_raw_outputs.jsonl` is zero bytes, although the merged raw-output file is populated. |
| Add executable live direct-code baseline. | done | `experiments/results/live_direct_code_results.csv` with 80 rows; `experiments/results/live_direct_code_method_results.csv` with 80 rows; `experiments/results/live_direct_code_metrics.csv`; `experiments/results/live_direct_code_raw_outputs.jsonl`; `experiments/results/live_direct_code_metadata.json`; `experiments/results/live_direct_code_token_usage.csv` | Current metrics show `live_direct_code::qwen3.6-flash` E2E 0.350; claims must still say this is one-model diagnostic evidence. |
| Optional live JSON Schema / structured-output baseline. | open | No obvious `live_json_schema_*` result file found under `experiments/results`. | Either run it and include raw outputs/metrics, or explicitly mark it as future work so the package does not imply three live baselines. |
| Add w/o QYIR ablation. | done | `experiments/results/ablation_results.csv` with 480 rows; `experiments/results/ablation_metrics.csv`; `experiments/tables/ablation_comparison.md` | Keep the interpretation narrow: this supports QYIR's value in the implemented benchmark and deterministic harness, not broad superiority over all structured-output systems. |
| Add multi-asset / multi-period smoke test. | done | `experiments/results/multi_asset_smoke_results.csv`; `docs/paper/reproducibility_package.md` | Describe as a synthetic runnability smoke test only. The five rows cover SPY, QQQ, GLD, and two periods with compile, backtest, and risk-audit checks all true. |
| Add safe rejection paraphrase set. | done | `benchmark/unsafe_paraphrase_bench.jsonl`; `experiments/results/safe_paraphrase_results.csv` with 35 rows; `experiments/results/safe_paraphrase_metrics.csv` | Keep this as pattern/paraphrase coverage, not financial safety. The current metric file reports accuracy 1.000 and unsafe acceptance rate 0.000 on 35 cases. |
| Add three thicker qualitative cases with before/after QYIR fragments, verifier errors, and repair diffs. | partial | `experiments/tables/case_analysis.md`; `docs/paper/failure_analysis.md`; `docs/paper/qsga_ccf_c_draft.md` | Verify that the draft contains the full requested structure for ambiguous intent, unsafe intent, and risk repair. The table artifact exists but is short, so the submission should preserve detailed case text in the draft or appendix. |
| Add failure analysis table and representative failure cases. | done | `docs/paper/failure_analysis.md`; `experiments/tables/repair_effect.md`; `experiments/results/*_results.csv` | Cross-check the failure-analysis counts against the latest live QYIR 80 and live direct-code result files before final submission. |
| Complete PDF-level related-work and claim audit for core papers. | partial | `docs/paper/related_work_verified.md`; `docs/paper/citation_and_claim_matrix.md`; `docs/paper/citation_audit_backlog.md` | Treat as package-present but still requiring human verification before final claim freeze. Do not add PDF-level claims unless they are logged in these files. |
| Produce formal submission figures: problem/route, architecture, and QYIR vs JSON Schema. | done | `figures/figure1_problem_route.svg`; `figures/figure1_problem_route.pdf`; `figures/figure2_architecture.svg`; `figures/figure2_architecture.pdf`; `figures/figure3_qyir_vs_json_schema.svg`; `figures/figure3_qyir_vs_json_schema.pdf`; `docs/paper/artifact_manifest.md` | Confirm PDF rendering in the final paper build and make sure figure captions avoid broad LLM or trading-performance claims. |
| Unify the reproducibility package. | done | `REPRODUCE.md`; `docs/paper/reproducibility_package.md`; `docs/paper/artifact_manifest.md`; `uv.lock`; `experiments/results/*.csv`; `scripts/reproduce_all.ps1`; `scripts/reproduce_all.sh` | `scripts/reproduce_all.ps1` passed on 2026-05-06 with 179 tests, safe paraphrase, live QYIR replay metrics, and live direct-code replay metrics. |
| Provide one-command or clearly sequenced reproduction instructions. | done | `REPRODUCE.md`; `docs/paper/reproducibility_package.md`; `scripts/` | PowerShell and POSIX shell scripts now prefer `.venv` Python and include safe paraphrase plus saved live replay metrics. |
| State CI/container limits honestly. | done | `REPRODUCE.md`; `docs/paper/reproducibility_package.md`; `docs/paper/artifact_manifest.md` | Keep the explicit statement that no CI or container is provided in this artifact version. |
| Produce the final paper draft. | partial | `docs/paper/qsga_ccf_c_draft.md` | The draft now uses no-oracle main result, oracle-slot upper bound, and live diagnostics; final human review is still required before submission. |
| Produce artifact manifest. | done | `docs/paper/artifact_manifest.md` | Manifest now reflects 179 tests and both 80-case live output sets. |
| Preserve release and human-approval boundary. | done | `docs/paper/claim_policy.md`; `docs/paper/reproducibility_package.md` | Keep human approval required for public release, authorship, submission target, secrets/license checks, and live API spending beyond approved runs. |

## Current Artifact Snapshot

The deterministic package is mostly present. The main baseline CSV has 400 rows and reports oracle-slot `qsga_full` E2E 0.9625, compared with `direct_code` 0.5000 and `direct_json` 0.4000. The ablation CSV has 480 rows and includes `wo_qyir` with E2E 0.1625. The no-oracle CSV has 80 rows and reports construction success 0.8364 and E2E 0.8875.

The live evidence has advanced beyond parts of the documentation. The live QYIR 80 run exists for `qwen3.6-flash` with both raw and QSGA-routed methods. The executable live direct-code baseline also exists for `qwen3.6-flash`, with raw outputs, metadata, token usage, result rows, and method-level metrics.

The figure package is present under `figures/` with SVG and PDF exports for all three requested figures. The reproducibility and manifest docs have been synchronized with the newest saved-output live results and reproduce scripts.

## Open Submission Risks

The largest package risk has shifted from missing core artifacts to final release hygiene. `claim_policy.md`, `artifact_manifest.md`, `reproducibility_package.md`, `REPRODUCE.md`, and the reproduce scripts now agree on live QYIR, live direct-code, safe paraphrase, and 179-test reproduction status.

The second risk is overclaiming. The current evidence supports a bounded artifact-reliability claim, a one-model live QYIR 80 evaluation, a one-model executable direct-code comparison, deterministic ablations, and synthetic multi-asset runnability. It does not support profitability, SOTA, broad LLM generalization, or robust financial-safety claims.

The third risk is release hygiene. Many important artifacts are currently untracked according to `git status --short`, including `REPRODUCE.md`, `figures/`, live QYIR 80 files, prompts, and scripts. Before packaging, decide which of these belong in the release and run a secret/license check on raw live outputs and metadata.

# QSGA Reproducibility Package

Date: 2026-05-06

## Environment

- OS observed in this run: Windows, PowerShell
- Python executable used: `.venv\Scripts\python.exe`
- Python dependencies: see `pyproject.toml` and `uv.lock`
- Bundled reproduce scripts prefer `.venv` Python when it is present, then fall back to `python`.
- Data file: `data/raw/spy_sample.csv`
- Benchmark file: `benchmark/qsi_bench_v1.jsonl`

## Verification Commands

Run tests:

```powershell
.venv\Scripts\python.exe -m pytest tests -q
```

Observed result on 2026-05-12:

```text
183 passed in 2.43s
```

Run baseline experiments:

```powershell
.venv\Scripts\python.exe -m experiments.baselines --benchmark benchmark\qsi_bench_v1.jsonl --data data\raw\spy_sample.csv --output experiments\results\baseline_results.csv
```

Aggregate baseline metrics:

```powershell
.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\baseline_results.csv --output experiments\results\baseline_metrics.csv
```

Run ablation experiments:

```powershell
.venv\Scripts\python.exe -m experiments.run_ablation --benchmark benchmark\qsi_bench_v1.jsonl --data data\raw\spy_sample.csv --output experiments\results\ablation_results.csv
```

Aggregate ablation metrics:

```powershell
.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\ablation_results.csv --output experiments\results\ablation_metrics.csv
```

Run no-oracle slot extraction experiment:

```powershell
.venv\Scripts\python.exe -m experiments.run_no_oracle --benchmark benchmark\qsi_bench_v1.jsonl --data data\raw\spy_sample.csv --output experiments\results\no_oracle_results.csv
```

Aggregate no-oracle metrics:

```powershell
.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\no_oracle_results.csv --output experiments\results\no_oracle_metrics.csv
```

Run synthetic multi-asset smoke:

```powershell
.venv\Scripts\python.exe -m experiments.run_multi_asset_smoke --output experiments\results\multi_asset_smoke_results.csv
```

Run safe-rejection paraphrase regression:

```powershell
.venv\Scripts\python.exe -m experiments.run_safe_paraphrase --output experiments\results\safe_paraphrase_results.csv --metrics-output experiments\results\safe_paraphrase_metrics.csv
```

Run semantic slot-corruption checks:

```powershell
.venv\Scripts\python.exe -m experiments.run_semantic_corruption --output experiments\results\semantic_corruption_results.csv --metrics-output experiments\results\semantic_corruption_metrics.csv
```

Run the bundled one-command script for deterministic experiments plus saved live replays:

```powershell
scripts\reproduce_all.ps1
```

Run the saved-output 80-case live QYIR evaluation after API approval:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_llm --models qwen3.6-flash --case-limit 0 --seed 20260505 --max-retries 1 --max-tokens 1200 --output experiments\results\live_qyir_80_results.csv --raw-output experiments\results\live_qyir_80_raw_outputs.jsonl --metadata-output experiments\results\live_qyir_80_metadata.json --usage-output experiments\results\live_qyir_80_token_usage.csv
```

Replay saved 80-case live QYIR raw outputs without spending more tokens:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_llm --replay-raw-output experiments\results\live_qyir_80_raw_outputs.jsonl --replay-metadata experiments\results\live_qyir_80_metadata.json --output experiments\results\live_qyir_80_results.csv
```

Aggregate live QYIR metrics:

```powershell
.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\live_qyir_80_results.csv --output experiments\results\live_qyir_80_metrics.csv
```

Run the 20-case constrained-QYIR probe after API approval:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_constrained_qyir --models deepseek-v4-flash --case-limit 20 --response-format json_object --max-retries 1 --max-tokens 1200 --output experiments\results\live_constrained_qyir_results.csv --raw-output experiments\results\live_constrained_qyir_raw_outputs.jsonl --metadata-output experiments\results\live_constrained_qyir_metadata.json --usage-output experiments\results\live_constrained_qyir_token_usage.csv
.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\live_constrained_qyir_results.csv --output experiments\results\live_constrained_qyir_metrics.csv
```

Run the same-model no-provider-constraint retry control:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_constrained_qyir --models deepseek-v4-flash --case-ids qsi_006 qsi_010 qsi_011 qsi_023 qsi_025 qsi_027 qsi_030 qsi_032 qsi_036 qsi_039 qsi_044 qsi_051 qsi_054 qsi_059 qsi_061 qsi_062 qsi_065 qsi_068 qsi_073 qsi_080 --response-format none --max-retries 1 --max-tokens 1200 --output experiments\results\live_unconstrained_qyir_retry_results.csv --raw-output experiments\results\live_unconstrained_qyir_retry_raw_outputs.jsonl --metadata-output experiments\results\live_unconstrained_qyir_retry_metadata.json --usage-output experiments\results\live_unconstrained_qyir_retry_token_usage.csv
.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\live_unconstrained_qyir_retry_results.csv --output experiments\results\live_unconstrained_qyir_retry_metrics.csv
```

Run the same-case Simple JSON baseline after API approval:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_simple_json --models deepseek-v4-flash --case-ids qsi_006 qsi_010 qsi_011 qsi_023 qsi_025 qsi_027 qsi_030 qsi_032 qsi_036 qsi_039 qsi_044 qsi_051 qsi_054 qsi_059 qsi_061 qsi_062 qsi_065 qsi_068 qsi_073 qsi_080 --max-retries 0 --max-tokens 1200 --output experiments\results\live_simple_json_results.csv --metrics-output experiments\results\live_simple_json_metrics.csv --raw-output experiments\results\live_simple_json_raw_outputs.jsonl --metadata-output experiments\results\live_simple_json_metadata.json --usage-output experiments\results\live_simple_json_token_usage.csv
```

Replay saved Simple JSON raw outputs without spending more tokens:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_simple_json --replay-raw-output experiments\results\live_simple_json_raw_outputs.jsonl --replay-metadata experiments\results\live_simple_json_metadata.json --output experiments\results\live_simple_json_results.csv --metrics-output experiments\results\live_simple_json_metrics.csv
```

Run executable live direct-code baseline after API approval:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_direct_code --models qwen3.6-flash --case-limit 0 --max-tokens 1200 --output experiments\results\live_direct_code_results.csv --method-output experiments\results\live_direct_code_method_results.csv --raw-output experiments\results\live_direct_code_raw_outputs.jsonl --metadata-output experiments\results\live_direct_code_metadata.json --usage-output experiments\results\live_direct_code_token_usage.csv
```

Replay saved live direct-code raw outputs without spending more tokens:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_direct_code --replay-raw-output experiments\results\live_direct_code_raw_outputs.jsonl --replay-metadata experiments\results\live_direct_code_metadata.json --output experiments\results\live_direct_code_replay_results.csv --method-output experiments\results\live_direct_code_replay_method_results.csv
```

Aggregate live direct-code metrics:

```powershell
.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\live_direct_code_replay_method_results.csv --output experiments\results\live_direct_code_metrics.csv
```

Replay saved live direct-code outputs with the shared safe-rejection gate:

```powershell
.venv\Scripts\python.exe -m experiments.run_live_direct_code_wrapper --replay-raw-output experiments\results\live_direct_code_raw_outputs.jsonl --replay-metadata experiments\results\live_direct_code_metadata.json --output experiments\results\live_direct_code_shared_rejection_results.csv
.venv\Scripts\python.exe -m experiments.eval_metrics --input experiments\results\live_direct_code_shared_rejection_results.csv --output experiments\results\live_direct_code_shared_rejection_metrics.csv
```

Generate paper tables:

```powershell
.venv\Scripts\python.exe -m experiments.run_slot_diagnostics --csv-output experiments\results\no_oracle_slot_diagnostics.csv --md-output experiments\tables\no_oracle_slot_diagnostics.md
.venv\Scripts\python.exe -m experiments.paper_tables --metrics experiments\results\baseline_metrics.csv --results experiments\results\baseline_results.csv --ablation-metrics experiments\results\ablation_metrics.csv --no-oracle-metrics experiments\results\no_oracle_metrics.csv --live-direct-code-metrics experiments\results\live_direct_code_metrics.csv --live-direct-code-feedback-repair-metrics experiments\results\live_direct_code_feedback_repair_metrics.csv --live-direct-code-shared-rejection-metrics experiments\results\live_direct_code_shared_rejection_metrics.csv --live-constrained-qyir-metrics experiments\results\live_constrained_qyir_metrics.csv --live-simple-json-metrics experiments\results\live_simple_json_metrics.csv --output-dir experiments\tables
```

The generated Markdown tables cover the baseline, ablation, repair, safe-rejection, and no-oracle slot-diagnostic summaries. The no-oracle aggregate table in the draft is copied from `experiments\results\no_oracle_metrics.csv` after running the no-oracle aggregation command above.

## Expected Metrics

Values below are displayed to three decimal places. Exact rates are available in the corresponding CSV files.

Main no-oracle result:

| Method | Semantic Consistency | Clarification Accuracy | Construction Success | E2E Success |
|---|---:|---:|---:|---:|
| qsga_no_oracle_slots | 0.836 | 1.000 | 0.836 | 0.887 |

No-oracle slot diagnostics:

| Slot Group | Precision | Recall | F1 |
|---|---:|---:|---:|
| market | 0.400 | 0.182 | 0.250 |
| indicators | 0.648 | 0.627 | 0.637 |
| entry_rules | 0.000 | 0.000 | 0.000 |
| exit_rules | 0.000 | 0.000 | 0.000 |
| risk_control | 0.841 | 0.578 | 0.685 |

Upper-bound oracle-slot verification-chain result:

| Method | Clarification Accuracy | Construction Success | E2E Success |
|---|---:|---:|---:|
| direct_code | 0.000 | 0.727 | 0.500 |
| direct_json | 0.000 | 0.309 | 0.400 |
| qsga_no_repair | 1.000 | 0.273 | 0.500 |
| qsga_no_risk_audit | 1.000 | 0.473 | 0.637 |
| qsga_full | 1.000 | 0.945 | 0.963 |

Ablation result:

| Variant | E2E Success |
|---|---:|
| qsga_full | 0.963 |
| wo_qyir | 0.163 |
| wo_semantic_verification | 0.838 |
| wo_risk_audit | 0.512 |
| wo_repair | 0.375 |
| wo_safe_rejection | 0.650 |

Synthetic multi-asset smoke:

| Check | Result |
|---|---:|
| compile success | 5/5 |
| backtest success | 5/5 |
| risk-audit runnable | 5/5 |

Live QYIR 80-case result:

| Method | Risk Violation | Safe Rejection Accuracy | Clarification Accuracy | Construction Success | E2E Success |
|---|---:|---:|---:|---:|---:|
| live_raw_qyir::qwen3.6-flash | 0.091 | 0.000 | 0.000 | 0.109 | 0.075 |
| live_qsga_qyir::qwen3.6-flash | 0.073 | 1.000 | 1.000 | 0.091 | 0.375 |

Live constrained-QYIR 20-case probe:

| Condition | Schema Validity | Semantic Consistency | Compile Success | Construction Success | E2E Success |
|---|---:|---:|---:|---:|---:|
| response_format none + retry | 0.538 | 0.462 | 0.308 | 0.077 | 0.400 |
| response_format json_object + retry | 0.538 | 0.538 | 0.538 | 0.462 | 0.650 |

Live Simple JSON 20-case baseline:

| Method | JSON Parse Success | QYIR Conversion Success | Semantic Consistency | Compile Success | E2E Success |
|---|---:|---:|---:|---:|---:|
| live_simple_json_adapter::deepseek-v4-flash | 1.000 | 0.231 | 0.231 | 0.154 | 0.450 |

Executable live direct-code result:

| Method | Syntax | Interface | Runtime | Trade Validity | Semantic Match | Risk Violation | Backtest | E2E |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| live_direct_code::qwen3.6-flash | 1.000 | 1.000 | 0.925 | 0.850 | 0.375 | 0.300 | 0.850 | 0.350 |

Live direct-code shared-rejection replay:

| Method | Safe Rejection Accuracy | Risk Violation | E2E Success |
|---|---:|---:|---:|
| live_direct_code_shared_rejection::qwen3.6-flash | 1.000 | 0.164 | 0.538 |

Semantic slot-corruption check:

| Check | Result |
|---|---:|
| schema-valid corrupted cases | 7/7 |
| pass-through without semantic verification | 1.000 |
| detection with semantic verification | 1.000 |

## Known Reproducibility Limits

1. Main no-oracle and upper-bound oracle-slot deterministic experiments validate the prototype harness; the live QYIR, constrained-QYIR, and executable direct-code extensions are diagnostic live runs rather than broad model-ranking benchmarks.
2. Live LLM reproduction requires a valid API key and must not publish local secret files.
3. Oracle-slot results depend on QSI-Bench v1 expected slots; no-oracle results use deterministic query parsing.
4. Results depend on the curated QSI-Bench v1 labels and `spy_sample.csv`.
5. No container image or CI workflow is included yet.
6. Executable live direct-code comparison currently covers one model and one constrained prompt only, and current prompt-only live QYIR construction remains weaker than live direct-code construction.
7. The Simple JSON baseline is a 20-case diagnostic adapter probe, not an optimized semantic parser or broad JSON-vs-IR benchmark.
8. Public release requires a final secret/license check even though the human approved publication in principle.

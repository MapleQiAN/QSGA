# Reproduce QSGA Prototype Results

Date: 2026-05-12

## Environment

Python `>=3.11` is required. Dependencies are declared in `pyproject.toml`; `uv.lock` is included. The bundled reproduce scripts prefer the repository `.venv` Python when it is present.

No CI or container is provided in this artifact version.

## Local Deterministic Run

One-command reproduction for the deterministic package plus saved live replays:

```powershell
scripts/reproduce_all.ps1
```

The shell variant is:

```sh
sh scripts/reproduce_all.sh
```

```powershell
pytest
python -m experiments.run_baselines --output experiments/results/baseline_results.csv
python -m experiments.eval_metrics --input experiments/results/baseline_results.csv --output experiments/results/baseline_metrics.csv
python -m experiments.run_ablation --output experiments/results/ablation_results.csv
python -m experiments.eval_metrics --input experiments/results/ablation_results.csv --output experiments/results/ablation_metrics.csv
python -m experiments.run_no_oracle --output experiments/results/no_oracle_results.csv
python -m experiments.eval_metrics --input experiments/results/no_oracle_results.csv --output experiments/results/no_oracle_metrics.csv
python -m experiments.run_slot_diagnostics --csv-output experiments/results/no_oracle_slot_diagnostics.csv --md-output experiments/tables/no_oracle_slot_diagnostics.md
python -m experiments.run_multi_asset_smoke --output experiments/results/multi_asset_smoke_results.csv
python -m experiments.run_safe_paraphrase --output experiments/results/safe_paraphrase_results.csv --metrics-output experiments/results/safe_paraphrase_metrics.csv
python -m experiments.run_semantic_corruption --output experiments/results/semantic_corruption_results.csv --metrics-output experiments/results/semantic_corruption_metrics.csv
python -m experiments.paper_tables --metrics experiments/results/baseline_metrics.csv --results experiments/results/baseline_results.csv --ablation-metrics experiments/results/ablation_metrics.csv --no-oracle-metrics experiments/results/no_oracle_metrics.csv --live-direct-code-metrics experiments/results/live_direct_code_metrics.csv --live-direct-code-feedback-repair-metrics experiments/results/live_direct_code_feedback_repair_metrics.csv --live-direct-code-shared-rejection-metrics experiments/results/live_direct_code_shared_rejection_metrics.csv --live-constrained-qyir-metrics experiments/results/live_constrained_qyir_metrics.csv --live-simple-json-metrics experiments/results/live_simple_json_metrics.csv --output-dir experiments/tables
```

## Live QYIR 80-Case Run

Live runs require an approved OpenAI-compatible API key.

```powershell
python -m experiments.run_live_llm --models qwen3.6-flash --case-limit 0 --max-retries 1 --max-tokens 1200 --output experiments/results/live_qyir_80_results.csv --raw-output experiments/results/live_qyir_80_raw_outputs.jsonl --metadata-output experiments/results/live_qyir_80_metadata.json --usage-output experiments/results/live_qyir_80_token_usage.csv
```

Replay saved live QYIR outputs without API calls:

```powershell
python -m experiments.run_live_llm --replay-raw-output experiments/results/live_qyir_80_raw_outputs.jsonl --replay-metadata experiments/results/live_qyir_80_metadata.json --output experiments/results/live_qyir_80_results.csv
python -m experiments.eval_metrics --input experiments/results/live_qyir_80_results.csv --output experiments/results/live_qyir_80_metrics.csv
```

## Live Constrained-QYIR Diagnostic

This 20- to 40-case probe tests whether prompt-only QYIR failures mainly come from JSON/schema control or from deeper semantic parsing. It uses the same QSI-Bench v1 records and downstream evaluator as the prompt-only live QYIR run, but adds provider-level JSON output constraints and one schema-feedback retry. Fresh runs require API approval.

```powershell
python -m experiments.run_live_constrained_qyir --models deepseek-v4-flash --case-limit 20 --response-format json_object --max-retries 1 --max-tokens 1200 --output experiments/results/live_constrained_qyir_results.csv --raw-output experiments/results/live_constrained_qyir_raw_outputs.jsonl --metadata-output experiments/results/live_constrained_qyir_metadata.json --usage-output experiments/results/live_constrained_qyir_token_usage.csv
python -m experiments.eval_metrics --input experiments/results/live_constrained_qyir_results.csv --output experiments/results/live_constrained_qyir_metrics.csv
```

Replay saved constrained-QYIR outputs without API calls:

```powershell
python -m experiments.run_live_constrained_qyir --replay-raw-output experiments/results/live_constrained_qyir_raw_outputs.jsonl --replay-metadata experiments/results/live_constrained_qyir_metadata.json --output experiments/results/live_constrained_qyir_results.csv
python -m experiments.eval_metrics --input experiments/results/live_constrained_qyir_results.csv --output experiments/results/live_constrained_qyir_metrics.csv
```

## Live Simple JSON Baseline

This same-case 20-case diagnostic asks the model for ordinary strategy JSON, then uses a deterministic adapter to attempt QYIR conversion before the same verifier/compiler/risk-audit chain. Fresh runs require API approval.

```powershell
python -m experiments.run_live_simple_json --models deepseek-v4-flash --case-ids qsi_006 qsi_010 qsi_011 qsi_023 qsi_025 qsi_027 qsi_030 qsi_032 qsi_036 qsi_039 qsi_044 qsi_051 qsi_054 qsi_059 qsi_061 qsi_062 qsi_065 qsi_068 qsi_073 qsi_080 --max-retries 0 --max-tokens 1200 --output experiments/results/live_simple_json_results.csv --metrics-output experiments/results/live_simple_json_metrics.csv --raw-output experiments/results/live_simple_json_raw_outputs.jsonl --metadata-output experiments/results/live_simple_json_metadata.json --usage-output experiments/results/live_simple_json_token_usage.csv
```

Replay saved Simple JSON outputs without API calls:

```powershell
python -m experiments.run_live_simple_json --replay-raw-output experiments/results/live_simple_json_raw_outputs.jsonl --replay-metadata experiments/results/live_simple_json_metadata.json --output experiments/results/live_simple_json_results.csv --metrics-output experiments/results/live_simple_json_metrics.csv
```

Current saved result: `live_simple_json_adapter::deepseek-v4-flash` reaches `1.000` JSON parse success, `0.231` QYIR conversion success, `0.154` compile success, and `0.450` E2E on the 20 selected cases.

## Live Direct-Code Baseline

Executable direct-code results are saved for `qwen3.6-flash` on all 80 QSI-Bench v1 cases. Fresh live runs still require API approval.

```powershell
python -m experiments.run_live_direct_code --models qwen3.6-flash --case-limit 0 --max-tokens 1200
```

Replay saved direct-code outputs:

```powershell
python -m experiments.run_live_direct_code --replay-raw-output experiments/results/live_direct_code_raw_outputs.jsonl --replay-metadata experiments/results/live_direct_code_metadata.json --output experiments/results/live_direct_code_replay_results.csv --method-output experiments/results/live_direct_code_replay_method_results.csv
python -m experiments.eval_metrics --input experiments/results/live_direct_code_replay_method_results.csv --output experiments/results/live_direct_code_metrics.csv
python -m experiments.run_live_direct_code_wrapper --replay-raw-output experiments/results/live_direct_code_raw_outputs.jsonl --replay-metadata experiments/results/live_direct_code_metadata.json --output experiments/results/live_direct_code_shared_rejection_results.csv
python -m experiments.eval_metrics --input experiments/results/live_direct_code_shared_rejection_results.csv --output experiments/results/live_direct_code_shared_rejection_metrics.csv
```

Current saved result: `live_direct_code::qwen3.6-flash` reaches `0.350` E2E on 80 cases.
Shared-rejection replay result: `live_direct_code_shared_rejection::qwen3.6-flash` reaches `0.538` E2E on 80 cases.

## Live Direct-Code Execution-Feedback Repair Baseline

The one-iteration repair baseline reuses the saved qwen3.6-flash first-pass direct-code outputs, feeds validation errors back to a repair model, and reevaluates the repaired `generate_signals(df)` artifact. Fresh repair calls require API approval.

```powershell
python -m experiments.run_live_direct_code_repair --replay-raw-output experiments/results/live_direct_code_raw_outputs.jsonl --replay-metadata experiments/results/live_direct_code_metadata.json --repair-models deepseek-v4-flash deepseek-v4-pro --max-tokens 1200
python -m experiments.eval_metrics --input experiments/results/live_direct_code_feedback_repair_method_results.csv --output experiments/results/live_direct_code_feedback_repair_metrics.csv
```

Current saved repair result: `live_direct_code_feedback_repair::deepseek-v4-flash+deepseek-v4-pro` reaches `0.4125` E2E on 80 cases and `0.600` construction success over 55 constructible cases. The result improves direct-code construction but still lacks explicit unsafe-intent handling, clarification behavior, QYIR risk slots, and field-local repair evidence.

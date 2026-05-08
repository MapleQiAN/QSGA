# Reproduce QSGA Prototype Results

Date: 2026-05-06

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
python -m experiments.paper_tables --metrics experiments/results/baseline_metrics.csv --results experiments/results/baseline_results.csv --ablation-metrics experiments/results/ablation_metrics.csv --no-oracle-metrics experiments/results/no_oracle_metrics.csv --live-direct-code-metrics experiments/results/live_direct_code_metrics.csv --live-direct-code-shared-rejection-metrics experiments/results/live_direct_code_shared_rejection_metrics.csv --output-dir experiments/tables
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

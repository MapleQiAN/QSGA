#!/usr/bin/env sh
set -eu

if [ -x .venv/bin/python ]; then
  PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PYTHON_BIN=.venv/Scripts/python.exe
else
  PYTHON_BIN=python
fi

"$PYTHON_BIN" -m pytest tests -q
"$PYTHON_BIN" -m experiments.run_baselines --output experiments/results/baseline_results.csv
"$PYTHON_BIN" -m experiments.eval_metrics --input experiments/results/baseline_results.csv --output experiments/results/baseline_metrics.csv
"$PYTHON_BIN" -m experiments.run_ablation --output experiments/results/ablation_results.csv
"$PYTHON_BIN" -m experiments.eval_metrics --input experiments/results/ablation_results.csv --output experiments/results/ablation_metrics.csv
"$PYTHON_BIN" -m experiments.run_no_oracle --output experiments/results/no_oracle_results.csv
"$PYTHON_BIN" -m experiments.eval_metrics --input experiments/results/no_oracle_results.csv --output experiments/results/no_oracle_metrics.csv
"$PYTHON_BIN" -m experiments.run_multi_asset_smoke --output experiments/results/multi_asset_smoke_results.csv
"$PYTHON_BIN" -m experiments.run_safe_paraphrase --output experiments/results/safe_paraphrase_results.csv --metrics-output experiments/results/safe_paraphrase_metrics.csv
"$PYTHON_BIN" -m experiments.run_semantic_corruption --output experiments/results/semantic_corruption_results.csv --metrics-output experiments/results/semantic_corruption_metrics.csv
if [ -f experiments/results/live_qyir_80_raw_outputs.jsonl ] && [ -f experiments/results/live_qyir_80_metadata.json ]; then
  "$PYTHON_BIN" -m experiments.run_live_llm --replay-raw-output experiments/results/live_qyir_80_raw_outputs.jsonl --replay-metadata experiments/results/live_qyir_80_metadata.json --output experiments/results/live_qyir_80_results.csv
  "$PYTHON_BIN" -m experiments.eval_metrics --input experiments/results/live_qyir_80_results.csv --output experiments/results/live_qyir_80_metrics.csv
fi
if [ -f experiments/results/live_direct_code_raw_outputs.jsonl ] && [ -f experiments/results/live_direct_code_metadata.json ]; then
  "$PYTHON_BIN" -m experiments.run_live_direct_code --replay-raw-output experiments/results/live_direct_code_raw_outputs.jsonl --replay-metadata experiments/results/live_direct_code_metadata.json --output experiments/results/live_direct_code_replay_results.csv --method-output experiments/results/live_direct_code_replay_method_results.csv
  "$PYTHON_BIN" -m experiments.eval_metrics --input experiments/results/live_direct_code_replay_method_results.csv --output experiments/results/live_direct_code_metrics.csv
  "$PYTHON_BIN" -m experiments.run_live_direct_code_wrapper --replay-raw-output experiments/results/live_direct_code_raw_outputs.jsonl --replay-metadata experiments/results/live_direct_code_metadata.json --output experiments/results/live_direct_code_shared_rejection_results.csv
  "$PYTHON_BIN" -m experiments.eval_metrics --input experiments/results/live_direct_code_shared_rejection_results.csv --output experiments/results/live_direct_code_shared_rejection_metrics.csv
fi
"$PYTHON_BIN" -m experiments.paper_tables --metrics experiments/results/baseline_metrics.csv --results experiments/results/baseline_results.csv --ablation-metrics experiments/results/ablation_metrics.csv --output-dir experiments/tables

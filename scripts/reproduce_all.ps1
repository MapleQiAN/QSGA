[Console]::InputEncoding  = [Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
chcp 65001 > $null

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
  $Python = "python"
}

& $Python -m pytest tests -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python -m experiments.run_baselines --output experiments/results/baseline_results.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m experiments.eval_metrics --input experiments/results/baseline_results.csv --output experiments/results/baseline_metrics.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python -m experiments.run_ablation --output experiments/results/ablation_results.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m experiments.eval_metrics --input experiments/results/ablation_results.csv --output experiments/results/ablation_metrics.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python -m experiments.run_no_oracle --output experiments/results/no_oracle_results.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m experiments.eval_metrics --input experiments/results/no_oracle_results.csv --output experiments/results/no_oracle_metrics.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m experiments.run_slot_diagnostics --csv-output experiments/results/no_oracle_slot_diagnostics.csv --md-output experiments/tables/no_oracle_slot_diagnostics.md
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python -m experiments.run_multi_asset_smoke --output experiments/results/multi_asset_smoke_results.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python -m experiments.run_safe_paraphrase --output experiments/results/safe_paraphrase_results.csv --metrics-output experiments/results/safe_paraphrase_metrics.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python -m experiments.run_semantic_corruption --output experiments/results/semantic_corruption_results.csv --metrics-output experiments/results/semantic_corruption_metrics.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ((Test-Path -LiteralPath "experiments/results/live_qyir_80_raw_outputs.jsonl") -and (Test-Path -LiteralPath "experiments/results/live_qyir_80_metadata.json")) {
  & $Python -m experiments.run_live_llm --replay-raw-output experiments/results/live_qyir_80_raw_outputs.jsonl --replay-metadata experiments/results/live_qyir_80_metadata.json --output experiments/results/live_qyir_80_results.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $Python -m experiments.eval_metrics --input experiments/results/live_qyir_80_results.csv --output experiments/results/live_qyir_80_metrics.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (Test-Path -LiteralPath "experiments/results/live_direct_code_raw_outputs.jsonl") {
  & $Python -m experiments.run_live_direct_code --replay-raw-output experiments/results/live_direct_code_raw_outputs.jsonl --replay-metadata experiments/results/live_direct_code_metadata.json --output experiments/results/live_direct_code_replay_results.csv --method-output experiments/results/live_direct_code_replay_method_results.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $Python -m experiments.eval_metrics --input experiments/results/live_direct_code_replay_method_results.csv --output experiments/results/live_direct_code_metrics.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $Python -m experiments.run_live_direct_code_wrapper --replay-raw-output experiments/results/live_direct_code_raw_outputs.jsonl --replay-metadata experiments/results/live_direct_code_metadata.json --output experiments/results/live_direct_code_shared_rejection_results.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $Python -m experiments.eval_metrics --input experiments/results/live_direct_code_shared_rejection_results.csv --output experiments/results/live_direct_code_shared_rejection_metrics.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  if (Test-Path -LiteralPath "experiments/results/live_direct_code_feedback_repair_method_results.csv") {
    & $Python -m experiments.eval_metrics --input experiments/results/live_direct_code_feedback_repair_method_results.csv --output experiments/results/live_direct_code_feedback_repair_metrics.csv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
}

if ((Test-Path -LiteralPath "experiments/results/live_constrained_qyir_raw_outputs.jsonl") -and (Test-Path -LiteralPath "experiments/results/live_constrained_qyir_metadata.json")) {
  & $Python -m experiments.run_live_constrained_qyir --replay-raw-output experiments/results/live_constrained_qyir_raw_outputs.jsonl --replay-metadata experiments/results/live_constrained_qyir_metadata.json --output experiments/results/live_constrained_qyir_results.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $Python -m experiments.eval_metrics --input experiments/results/live_constrained_qyir_results.csv --output experiments/results/live_constrained_qyir_metrics.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ((Test-Path -LiteralPath "experiments/results/live_simple_json_raw_outputs.jsonl") -and (Test-Path -LiteralPath "experiments/results/live_simple_json_metadata.json")) {
  & $Python -m experiments.run_live_simple_json --replay-raw-output experiments/results/live_simple_json_raw_outputs.jsonl --replay-metadata experiments/results/live_simple_json_metadata.json --output experiments/results/live_simple_json_results.csv --metrics-output experiments/results/live_simple_json_metrics.csv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

& $Python -m experiments.paper_tables --metrics experiments/results/baseline_metrics.csv --results experiments/results/baseline_results.csv --ablation-metrics experiments/results/ablation_metrics.csv --no-oracle-metrics experiments/results/no_oracle_metrics.csv --live-direct-code-metrics experiments/results/live_direct_code_metrics.csv --live-direct-code-feedback-repair-metrics experiments/results/live_direct_code_feedback_repair_metrics.csv --live-direct-code-shared-rejection-metrics experiments/results/live_direct_code_shared_rejection_metrics.csv --live-constrained-qyir-metrics experiments/results/live_constrained_qyir_metrics.csv --live-simple-json-metrics experiments/results/live_simple_json_metrics.csv --output-dir experiments/tables
exit $LASTEXITCODE

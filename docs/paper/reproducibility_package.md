# QSGA Reproducibility Package

Date: 2026-05-05

## Environment

- OS observed in this run: Windows, PowerShell
- Python executable used: `.venv\Scripts\python.exe`
- Python dependencies: see `pyproject.toml` and `uv.lock`
- Data file: `data/raw/spy_sample.csv`
- Benchmark file: `benchmark/qsi_bench_v1.jsonl`

## Verification Commands

Run tests:

```powershell
.venv\Scripts\python.exe -m pytest tests -q
```

Observed result on 2026-05-05:

```text
171 passed in 2.35s
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

Generate paper tables:

```powershell
.venv\Scripts\python.exe -m experiments.paper_tables --metrics experiments\results\baseline_metrics.csv --results experiments\results\baseline_results.csv --ablation-metrics experiments\results\ablation_metrics.csv --output-dir experiments\tables
```

The generated Markdown tables cover the baseline, ablation, repair, and safe-rejection summaries. The no-oracle table in the draft is copied from `experiments\results\no_oracle_metrics.csv` after running the no-oracle aggregation command above.

## Expected Metrics

Values below are displayed to three decimal places. Exact rates are available in the corresponding CSV files.

Main result:

| Method | E2E Success |
|---|---:|
| direct_code | 0.500 |
| direct_json | 0.400 |
| qsga_no_repair | 0.375 |
| qsga_no_risk_audit | 0.512 |
| qsga_full | 0.838 |

Ablation result:

| Variant | E2E Success |
|---|---:|
| qsga_full | 0.838 |
| wo_semantic_verification | 0.838 |
| wo_risk_audit | 0.512 |
| wo_repair | 0.375 |
| wo_safe_rejection | 0.650 |

No-oracle result:

| Method | Semantic Consistency | E2E Success |
|---|---:|---:|
| qsga_no_oracle_slots | 0.708 | 0.763 |

## Known Reproducibility Limits

1. Current experiments are deterministic prototype experiments and do not call live LLM APIs.
2. Oracle-slot results depend on QSI-Bench v1 expected slots; no-oracle results use deterministic query parsing.
3. Results depend on the curated QSI-Bench v1 labels and `spy_sample.csv`.
4. No container image or CI workflow is included yet.
5. Public release requires human approval.

# QSGA Artifact Manifest

Date: 2026-05-08

## Core Code

| Artifact | Role |
|---|---|
| `run_qsga.py` | end-to-end CLI pipeline |
| `qyir/` | QYIR schema and validation |
| `generator/` | prompt and generation adapters |
| `verifier/` | semantic, risk, and safe-rejection checks |
| `compiler/` | indicator/rule compiler |
| `backtester/` | sample execution and metrics |
| `repair/` | conservative risk-field repair operators |

## Benchmarks and Data

| Artifact | Status |
|---|---|
| `benchmark/qsi_bench_v1.jsonl` | 80-case controlled diagnostic suite |
| `benchmark/unsafe_paraphrase_bench.jsonl` | 35-case safe-rejection paraphrase regression set |
| `data/raw/spy_sample.csv` | synthetic/sample daily OHLCV data |
| `data/raw/spy.csv` | SPY-like local CSV |

## Experiment Scripts

| Script | Output |
|---|---|
| `experiments/run_baselines.py` | `experiments/results/baseline_results.csv` |
| `experiments/run_ablation.py` | `experiments/results/ablation_results.csv` |
| `experiments/run_no_oracle.py` | `experiments/results/no_oracle_results.csv` |
| `experiments/run_slot_diagnostics.py` | `experiments/results/no_oracle_slot_diagnostics.csv`; `experiments/tables/no_oracle_slot_diagnostics.md` |
| `experiments/run_live_llm.py` | live QYIR results, raw outputs, metadata, token usage |
| `experiments/run_live_constrained_qyir.py` | constrained-QYIR and same-runner unconstrained retry results, raw outputs, metadata, token usage |
| `experiments/run_live_simple_json.py` | Simple JSON baseline results, adapter metrics, raw outputs, metadata, token usage |
| `experiments/run_live_direct_code.py` | executable live direct-code results, raw outputs, metadata, token usage |
| `experiments/run_multi_asset_smoke.py` | `experiments/results/multi_asset_smoke_results.csv` |
| `experiments/run_safe_paraphrase.py` | `experiments/results/safe_paraphrase_results.csv` |
| `experiments/eval_metrics.py` | metrics CSV from per-case rows |
| `experiments/paper_tables.py` | Markdown tables under `experiments/tables/` |

## Reproducibility State

| Item | Current State |
|---|---|
| Python lockfile | `uv.lock` present |
| Test status | 183 passed on 2026-05-12 via `scripts/reproduce_all.ps1` |
| CI | not provided in this artifact version |
| Container | not provided in this artifact version |
| Live raw outputs | QYIR 80-case qwen3.6-flash run present; constrained-QYIR 20-case deepseek-v4-flash probe present; Simple JSON 20-case deepseek-v4-flash probe present; executable direct-code 80-case qwen3.6-flash run present |
| Public release | human approval required |

## Figures

| Figure | Source | Export |
|---|---|---|
| Figure 1: Problem and Technical Route | `figures/figure1_problem_route.svg` | `figures/figure1_problem_route.pdf` |
| Figure 2: QSGA Architecture | `figures/figure2_architecture.svg` | `figures/figure2_architecture.pdf` |
| Figure 3: QYIR vs JSON Schema | `figures/figure3_qyir_vs_json_schema.svg` | `figures/figure3_qyir_vs_json_schema.pdf` |
| Figure 4: Evidence Hierarchy Overview | `figures/figure4_evidence_hierarchy.svg` | not exported in this artifact version |

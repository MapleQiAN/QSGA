# QSGA Experiment Results Summary

Generated from the cleaned experiment run on 2026-05-04.

## Benchmark Composition

| Category | Samples |
| --- | ---: |
| ambiguous_intent | 10 |
| mean_reversion | 15 |
| momentum | 10 |
| risk_constrained | 15 |
| trend_following | 15 |
| unsafe_request | 15 |
| **Total** | **80** |

## Main Comparison

| Method | Schema Validity ↑ | Semantic Consistency ↑ | Compile Success ↑ | Backtest Success ↑ | Risk Violation ↓ | E2E Success ↑ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| direct_code | 0.000 | 0.615 | 0.846 | 0.615 | 0.231 | 0.500 |
| direct_json | 0.769 | 0.569 | 0.769 | 0.769 | 0.415 | 0.388 |
| qsga_no_repair | 0.600 | 0.477 | 0.600 | 0.600 | 0.354 | 0.362 |
| qsga_no_risk_audit | 1.000 | 0.800 | 1.000 | 1.000 | 0.508 | 0.500 |
| qsga_full | 1.000 | 0.800 | 1.000 | 1.000 | 0.000 | 0.825 |

## Ablation Study

| Method | Semantic Consistency ↑ | Risk Violation ↓ | Safe Rejection Accuracy ↑ | Repair Success ↑ | E2E Success ↑ |
| --- | ---: | ---: | ---: | ---: | ---: |
| qsga_full | 0.800 | 0.000 | 0.933 | 1.000 | 0.825 |
| wo_semantic_verification | 0.800 | 0.000 | 0.933 | 1.000 | 0.825 |
| wo_risk_audit | 0.800 | 0.508 | 0.933 | 1.000 | 0.500 |
| wo_repair | 0.477 | 0.354 | 0.933 | 0.000 | 0.362 |
| wo_safe_rejection | 0.800 | 0.000 | 0.000 | 1.000 | 0.650 |

## Repair Effect

| Method | Before Repair | After Repair | Repair Success |
| --- | ---: | ---: | ---: |
| direct_json | 15 | 0 | 0.000 |
| qsga_no_repair | 26 | 0 | 0.000 |
| qsga_no_risk_audit | 26 | 26 | 1.000 |
| qsga_full | 49 | 49 | 1.000 |

## Safe Rejection

| Method | Unsafe Samples | Correct Rejection | Accuracy |
| --- | ---: | ---: | ---: |
| direct_code | 15 | 14 | 0.933 |
| direct_json | 15 | 14 | 0.933 |
| qsga_no_repair | 15 | 14 | 0.933 |
| qsga_no_risk_audit | 15 | 14 | 0.933 |
| qsga_full | 15 | 14 | 0.933 |

## Case Analysis

| User Query | Direct Code Result | QSGA Result | Improvement |
| --- | --- | --- | --- |
| 低风险双均线 | May run without schema/risk gates | Valid QYIR plus risk audit | Executable and auditable |
| 不要杠杆 | May ignore leverage constraint | leverage locked to 1.0 | Explicit risk consistency |
| 稳赚不赔 | May produce unsafe strategy | Safe rejection | Unsafe intent blocked |

## Key Takeaways

1. Full QSGA achieves the strongest end-to-end success rate at 0.825 while reducing measured risk violations to 0.000.
2. Removing risk audit increases risk violation to 0.508 and reduces E2E success to 0.500, supporting the risk-aware design claim.
3. Removing repair reduces E2E success to 0.362 and repair success to 0.000, supporting the verification-guided repair claim.
4. Removing safe rejection drops safe rejection accuracy to 0.000 and E2E success to 0.650, supporting the boundary-control claim.
5. The semantic verification ablation is not independently stronger than full QSGA in this deterministic setup; it should be framed as part of the multi-stage verification chain rather than as a standalone source of measured improvement.

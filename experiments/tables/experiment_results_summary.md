# QSGA Experiment Results Summary

Generated from the cleaned experiment runs through 2026-05-06.

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

| Method | E2E | Construction | Risk Violation | Unsafe Rejection |
| --- | ---: | ---: | ---: | ---: |
| Direct code diagnostic | 0.350 | 0.509 | 0.164 | 0.000 |
| Direct code + execution-feedback repair | 0.413 | 0.600 | 0.164 | 0.000 |
| Direct code + shared rejection | 0.538 | 0.509 | 0.164 | 1.000 |
| Live QYIR + constrained JSON | 0.650 | 0.462 | 0.077 | 1.000 |
| QSGA no-oracle | 0.888 | 0.836 | 0.000 | 1.000 |
| QSGA oracle-slot upper bound | 0.963 | 0.945 | 0.000 | 1.000 |

## Ablation Study

| Method | Semantic Consistency ↑ | Risk Violation ↓ | Safe Rejection Accuracy ↑ | Conservative Repair Success ↑ | Clarification Accuracy ↑ | Construction Success ↑ | E2E Success ↑ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| qsga_full | 0.945 | 0.000 | 1.000 | 1.000 | 1.000 | 0.945 | 0.963 |
| wo_qyir | 0.418 | 0.364 | 0.000 | 0.000 | 0.000 | 0.236 | 0.163 |
| wo_semantic_verification | 0.945 | 0.000 | 1.000 | 1.000 | 0.000 | 0.945 | 0.838 |
| wo_risk_audit | 0.945 | 0.473 | 1.000 | 1.000 | 0.000 | 0.473 | 0.512 |
| wo_repair | 0.564 | 0.291 | 1.000 | 0.000 | 0.000 | 0.273 | 0.375 |
| wo_safe_rejection | 0.945 | 0.000 | 0.000 | 1.000 | 0.000 | 0.945 | 0.650 |

## Repair Effect

| Method | Before Repair | After Repair | Repair Success |
| --- | ---: | ---: | ---: |
| direct_json | 15 | 0 | 0.000 |
| qsga_no_repair | 23 | 0 | 0.000 |
| qsga_no_risk_audit | 23 | 23 | 1.000 |
| qsga_full | 39 | 39 | 1.000 |

## Safe Rejection

| Method | Unsafe Samples | Correct Rejection | Accuracy |
| --- | ---: | ---: | ---: |
| qsga_no_repair | 15 | 15 | 1.000 |
| qsga_no_risk_audit | 15 | 15 | 1.000 |
| qsga_full | 15 | 15 | 1.000 |

## Live Direct-Code Shared Rejection Replay

| Method | Safe Rejection Accuracy | Risk Violation | E2E Success |
| --- | ---: | ---: | ---: |
| live_direct_code_shared_rejection::qwen3.6-flash | 1.000 | 0.164 | 0.538 |

## Live Direct-Code Execution-Feedback Repair

| Method | Construction Success | Risk Violation | E2E Success |
| --- | ---: | ---: | ---: |
| live_direct_code_feedback_repair::deepseek-v4-flash+deepseek-v4-pro | 0.600 | 0.164 | 0.413 |

## Live Constrained-QYIR Probe

| Condition | Construction Success | Compile Success | E2E Success |
| --- | ---: | ---: | ---: |
| response_format none + retry | 0.077 | 0.308 | 0.400 |
| response_format json_object + retry | 0.462 | 0.538 | 0.650 |

## Semantic Slot-Corruption

| Check | Result |
| --- | ---: |
| Schema-valid corrupted cases | 7/7 |
| Pass-through without semantic verification | 1.000 |
| Detection with semantic verification | 1.000 |

## Case Analysis

| User Query | Direct Code Result | QSGA Result | Improvement |
| --- | --- | --- | --- |
| 低风险双均线 | May run without schema/risk gates | Valid QYIR plus risk audit | Executable and auditable |
| 不要杠杆 | May ignore leverage constraint | leverage locked to 1.0 | Explicit risk consistency |
| 稳赚不赔 | May produce unsafe strategy | Safe rejection | Unsafe intent blocked |

## Key Takeaways

1. No-oracle QSGA is the main deterministic prototype result; oracle-slot full QSGA is an upper-bound verification-chain result with E2E 0.963.
2. Removing risk audit increases risk violation to 0.473 and reduces E2E success to 0.512, supporting the risk-aware design claim.
3. Removing repair reduces E2E success to 0.375 and repair success to 0.000, supporting the verification-guided repair claim.
4. Removing safe rejection drops safe rejection accuracy to 0.000 and E2E success to 0.650, supporting the boundary-control claim.
5. The semantic verification ablation is not independently stronger than full QSGA in the oracle-slot setup, but the slot-corruption check shows that semantic verification catches schema-valid explicit-slot conflicts.
6. The shared-rejection direct-code replay improves unsafe handling for saved direct-code outputs, but it is boundary-control evidence only, not QYIR interpretability or repairability.
7. The one-iteration direct-code execution-feedback repair baseline improves construction success from 0.509 to 0.600, but still lacks unsafe-intent handling, clarification, QYIR risk slots, and conservative field-level repair.
8. The 20-case constrained-QYIR probe improves same-model construction from 0.077 to 0.462, showing output control helps, while remaining failures still require stronger QYIR semantic parsing or grammar control.

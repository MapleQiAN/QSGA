# QSGA Failure Analysis

Date: 2026-05-05

This appendix records failure modes that should be disclosed in the CCF-C submission package. Counts are descriptive and tied to the current artifacts.

## Summary Table

| Failure Type | Count | Typical Cause | Handling |
|---|---:|---|---|
| Ambiguous-intent E2E failure in `qsga_full` | 10 | no measured clarification-success outcome | counted as failure; future clarification metric required |
| Mean-reversion E2E failure in `qsga_full` | 3 | deterministic slot match does not cover some expected mean-reversion variants | counted as failure; case-level error string may be empty because failure is semantic-score based |
| Live QYIR schema failure | 9 | invalid Bollinger output field in generated QYIR | schema verifier rejects or records failure |
| Live QYIR compile failure | 3 | numeric operand compiled where a series was expected | compile failure recorded |
| Live QYIR unsafe raw acceptance | 6 | raw live QYIR prompt has no safe-rejection gate | counted as failure for raw baseline |
| Live direct-code no-trade failure | 6 | generated function returns constant or non-changing positions | trade-validity failure |
| Live direct-code runtime failure | 6 | generated function uses unavailable builtins or unsupported dataframe assumptions | runtime failure |
| Live direct-code unsafe/boundary failure | 15 unsafe cases, 0 E2E | no refusal gate in direct-code prompt | counted as failure |

## Key Observations

The most important direct-code result is not syntax failure. The 80-case qwen3.6-flash direct-code run reaches 1.000 syntax success and 1.000 interface success, but only 0.350 E2E success. This supports the claim that parsing code and exposing a required function are insufficient for reliable strategy construction.

The QSGA deterministic pipeline still fails all ambiguous-intent cases because the current benchmark scoring treats clarification as unimplemented. This must remain visible in the paper and should not be reframed as solved boundary handling.

The live QYIR pilot exposes realistic generation failures, especially invalid indicator parameterization, unresolved aliases, and risk-audit failures. These failures strengthen the case for explicit verification but also block broad live LLM generalization claims.

The safe-rejection paraphrase set reaches 1.000 accuracy after rule updates, but it is a small deterministic regression set. It should be placed in an appendix or supplementary experiment and described as pattern coverage, not robust financial safety.

## Representative Direct-Code Failures

| Error | Count | Interpretation |
|---|---:|---|
| `signal_error: no position change` | 6 | generated code is executable but produces no useful trading behavior |
| `NameError: name 'isinstance' is not defined` | 2 | sandbox lacks a builtin used by the generated function |
| `NameError: name 'str' is not defined` | 1 | generated code depends on unavailable builtin |
| `NameError: name 'enumerate' is not defined` | 1 | generated code depends on unavailable builtin |
| `KeyError: 'date'` | 1 | generated code assumes unavailable or transformed dataframe structure |
| `AttributeError: 'PeriodIndex' object has no attribute 'dt'` | 1 | generated code mishandles time-index operations |

## Submission Wording

Recommended wording:

> Failure analysis shows that direct code generation often passes syntax and interface checks while failing later semantic, trade-validity, unsafe-intent, or risk-control checks. This supports QSGA's verification-chain motivation, but it also indicates that the current system should be framed as a bounded prototype rather than a complete live LLM strategy-generation solution.

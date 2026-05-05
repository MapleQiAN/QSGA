# QSGA Paper Expansion Draft

> Scope: This file contains paste-ready Markdown fragments for `docs/paper/qsga_ccf_c_draft.md`. It is written as conservative paper text for the current deterministic prototype and should be integrated manually by the main writing thread.

## Algorithm 1: Verification-Guided QYIR Construction and Repair

The following algorithm can replace or extend the method-section algorithm. It keeps generation, verification, execution, risk auditing, and rejection as separate decisions so that each failure can be reported with a typed cause. In the current prototype, `GenerateQYIR` can be implemented by deterministic construction from benchmark annotations or by a future model-backed generator; the empirical claims in the present draft should be limited to the deterministic implementation.

```text
Algorithm 1: Verification-Guided Strategy Generation with QYIR

Input:
  x: natural-language strategy request
  D: historical market data available to the prototype
  K: maximum number of repair attempts

Output:
  ACCEPT(z, y, report), CLARIFY(message), or REJECT(reason)

1.  boundary_result <- BoundaryCheck(x)
2.  if boundary_result is unsafe or unsupported then
3.      return REJECT(boundary_result.reason)
4.  if boundary_result is ambiguous and cannot be grounded then
5.      return CLARIFY(boundary_result.message)

6.  z <- GenerateQYIR(x)
7.  for attempt in 0..K do
8.      schema_result <- VerifySchema(z)
9.      if schema_result fails then
10.         if IsRepairable(schema_result) then
11.             z <- Repair(z, schema_result)
12.             continue
13.         return REJECT(schema_result.summary)

14.     semantic_result <- VerifySemanticSlots(x, z)
15.     if semantic_result fails then
16.         if semantic_result.requires_clarification then
17.             return CLARIFY(semantic_result.message)
18.         if IsRepairable(semantic_result) then
19.             z <- Repair(z, semantic_result)
20.             continue
21.         return REJECT(semantic_result.summary)

22.     compile_result <- CompileQYIR(z)
23.     if compile_result fails then
24.         if IsRepairable(compile_result) then
25.             z <- Repair(z, compile_result)
26.             continue
27.         return REJECT(compile_result.summary)

28.     execution_result <- Backtest(compile_result.strategy, D)
29.     if execution_result fails then
30.         if IsRepairable(execution_result) then
31.             z <- Repair(z, execution_result)
32.             continue
33.         return REJECT(execution_result.summary)

34.     risk_result <- RiskAudit(z, execution_result.metrics)
35.     if risk_result passes then
36.         report <- BuildReport(z, execution_result.metrics, risk_result)
37.         return ACCEPT(z, compile_result.strategy, report)
38.     if IsRepairable(risk_result) then
39.         z <- Repair(z, risk_result)
40.         continue
41.     return REJECT(risk_result.summary)

42. return REJECT("repair budget exhausted")
```

The algorithm is intentionally conservative. A repair action is allowed only when the verifier returns a localized error that can be mapped to a QYIR field or a bounded parameter update. The repair step should not relax user-specified risk constraints to force an acceptance. For example, when a request states "no leverage", a candidate with `risk_control.leverage > 1.0` can be repaired by setting `leverage` to `1.0`; it should not be repaired by weakening the interpretation of "no leverage".

This formulation treats safe rejection and clarification as normal outputs of the system. This is important for novice-oriented financial applications because producing a runnable strategy for an unsafe or unsupported request may be less reliable than refusing or asking for clarification.

## QYIR Schema Summary

QYIR v1 is a constrained intermediate representation for a bounded daily, single-symbol, rule-based strategy space. It should be described as a domain intermediate representation rather than as a generic JSON format, because its fields are consumed by schema verification, semantic checks, deterministic compilation, backtesting, risk auditing, and localized repair.

```text
QYIR = {
  strategy_name,
  description,
  version,
  market,
  indicators,
  entry_rules,
  exit_rules,
  risk_control
}
```

| Group | Required Content | Main Constraints | Verification Role |
|---|---|---|---|
| `strategy_name`, `description`, `version` | Strategy identifier, readable description, schema version | `strategy_name` is non-empty and identifier-like; `version` is `"1.0"` | Supports traceability and versioned validation |
| `market` | `symbol`, `timeframe`, `start_date`, `end_date` | Single symbol; `timeframe = "1d"`; valid date interval | Fixes the data scope for deterministic compilation and backtesting |
| `indicators` | Indicator name, parameter object, unique alias | 1 to 10 indicators; supported names are `SMA`, `EMA`, `RSI`, `MACD`, `BOLLINGER`; aliases are globally unique | Defines computable signal series and the alias namespace |
| `entry_rules` | Entry conditions over aliases or literals | 1 to 10 rules; supported operators are `cross_over`, `cross_under`, `greater_than`, `less_than`, `between`; string operands must resolve to defined aliases | Gives deterministic signal semantics for entering positions |
| `exit_rules` | Exit conditions over aliases or literals | Same operator and reference constraints as entry rules; multiple rules use AND semantics in v1 | Gives deterministic signal semantics for leaving positions |
| `risk_control` | Position, stop-loss, take-profit, drawdown limit, shorting flag, leverage | `0.01 <= position_size <= 1.0`; optional bounded stop-loss/take-profit/drawdown fields; `allow_short` is boolean; `leverage` must be `1.0` | Makes risk assumptions explicit and auditable |

The supported scope should be stated explicitly:

| Dimension | QYIR v1 Scope |
|---|---|
| Frequency | Daily data only |
| Market scope | Single-symbol ETF or stock sample data |
| Strategy family | Simple rule-based strategies such as moving-average crossover, RSI reversal, MACD-style confirmation, and Bollinger-style filters |
| Indicators | `SMA`, `EMA`, `RSI`, `MACD`, `BOLLINGER` |
| Rule operators | `cross_over`, `cross_under`, `greater_than`, `less_than`, `between` |
| Risk controls | Position size, optional stop-loss, optional take-profit, optional drawdown limit, shorting flag, fixed no-leverage constraint |
| Explicit non-goals | High-frequency trading, tick/order-book logic, options or futures strategies, multi-asset portfolio optimization, return guarantees, investment advice |

The schema supports the paper's reliability argument in three ways. First, rule operands are verifiable references: every string operand used in `entry_rules` or `exit_rules` must resolve to an indicator alias, so a reference error can be detected before execution. Second, the operator set is intentionally small and has deterministic compilation semantics, so schema validity is connected to executable strategy behavior. Third, risk-related user intent is represented as structured fields rather than only as natural-language explanation, which allows the prototype to audit and repair risk violations within the supported space.

Recommended wording for the distinction from JSON Schema:

> A generic JSON schema can constrain the surface form of an output, but QYIR constrains the strategy object that will be compiled, executed, audited, and repaired. In QYIR, an alias is not merely a string, a rule is not merely an object, and leverage is not merely a numeric field; each has a domain-specific verification and compilation role.

## Experimental Protocol Expansion

The experiment section can be expanded with the following protocol text.

QSI-Bench v1 contains 80 Chinese natural-language strategy requests across six categories: ambiguous intent, mean reversion, momentum, risk-constrained requests, trend following, and unsafe requests. The benchmark is used to evaluate whether each method can handle a request according to the explicit annotations available in the dataset. It is not intended to measure financial profitability, market robustness, or broad language understanding.

Each method is evaluated on the same benchmark records. For requests that should not be rejected, the evaluation checks whether the method produces a usable strategy artifact, whether the artifact satisfies the relevant structural constraints, whether explicit user slots are preserved, whether the artifact can be compiled, whether the compiled strategy can be executed on the sample daily data, and whether the risk audit identifies any violations. For unsafe requests, the evaluation checks whether the method correctly rejects the request instead of producing a strategy.

The reported metrics should be interpreted as sample proportions under a deterministic prototype:

```text
Schema Validity       = valid QYIR outputs / non-rejected cases
Semantic Consistency  = explicit-slot-consistent outputs / non-rejected cases
Compile Success       = compiled outputs / non-rejected cases
Backtest Success      = executable backtests / non-rejected cases
Risk Violation        = risk-violating outputs / non-rejected cases
Safe Rejection        = correctly rejected unsafe requests / unsafe requests
E2E Success           = correctly handled requests / all requests
```

The current result tables support bounded component-level conclusions. The full QSGA pipeline reports `1.000` schema validity, `1.000` compile success, `1.000` backtest success on non-rejected cases, `0.000` measured risk violation, and `0.825` end-to-end success in the deterministic run. Removing risk auditing leaves compile and execution behavior intact but increases measured risk violation to `0.508` and reduces end-to-end success to `0.500`. Removing repair reduces end-to-end success to `0.362`, and removing safe rejection reduces safe rejection accuracy to `0.000`. These comparisons support the narrower claim that the implemented verification, risk-audit, repair, and boundary-control components matter in this controlled setting.

The experiment section should also state the limitations directly. The deterministic baselines approximate selected failure modes of direct code or direct JSON generation, but they are not a substitute for a live multi-model LLM study. The current benchmark has 80 samples and the backtest uses sample daily data, so the results should not be generalized to arbitrary financial requests, arbitrary markets, or real trading decisions.

## Expanded Case Study Template

The current case table can be expanded into a qualitative subsection using the following template. The template is designed to keep the claims focused on representation, verification, and boundary handling.

### Case Study A: Low-Risk Moving-Average Request

**User request.**

```text
低风险双均线
```

**Intent slots.**

| Slot | Conservative Interpretation |
|---|---|
| Strategy family | Moving-average crossover |
| Risk preference | Low-risk preference, mapped to bounded position and risk controls where supported |
| Market/data assumptions | Daily single-symbol sample data, unless otherwise specified by the benchmark |
| Unsupported inference | No claim is made about future return, drawdown guarantee, or suitability for real trading |

**QYIR-level representation.**

```text
market:
  timeframe: 1d
indicators:
  SMA short-window alias
  SMA long-window alias
entry_rules:
  short SMA cross_over long SMA
exit_rules:
  short SMA cross_under long SMA
risk_control:
  leverage: 1.0
  allow_short: false
  position_size: conservative bounded value
  optional stop_loss or max_drawdown_limit according to supported policy
```

**Verification trace.**

```text
BoundaryCheck      -> pass within supported rule-based scope
SchemaVerify       -> pass if indicator aliases and rule references are valid
SemanticVerify     -> pass if low-risk slots are reflected in risk_control
CompileQYIR        -> pass if all referenced series are computable
Backtest           -> pass if executable on the sample daily data
RiskAudit          -> pass or localize risk-control failure for repair
```

**Discussion.**

This case illustrates how QYIR turns a short novice request into explicit fields that can be inspected before execution. The relevant improvement is auditability and controlled compilation, not investment performance. A direct-code baseline may produce runnable code, but without the intermediate representation it has fewer explicit checkpoints for alias validity, rule semantics, and risk-control consistency.

### Case Study B: No-Leverage Constraint

**User request.**

```text
不要杠杆
```

**Risk slot.**

| Slot | QYIR Mapping |
|---|---|
| No leverage | `risk_control.leverage = 1.0` |
| Novice safety default | `allow_short = false` unless explicitly supported and allowed |
| Repair invariant | The system may reset invalid leverage to `1.0`; it should not reinterpret the request as allowing small leverage |

**Failure and repair example.**

```text
Candidate QYIR:
  risk_control.leverage = 2.0

Verifier:
  Schema/Risk failure at risk_control.leverage

Localized repair:
  risk_control.leverage <- 1.0

Post-repair check:
  Re-run schema verification, semantic verification, compilation, execution, and risk audit
```

**Discussion.**

This case is useful for explaining why structured risk fields are needed. The phrase "no leverage" can appear in an explanation while the generated code still violates it. In QYIR, the same intent is mapped to a hard field constraint, so the system can check and repair it deterministically within v1.

### Case Study C: Unsafe Request

**User request.**

```text
稳赚不赔
```

**Boundary handling.**

| Stage | Expected Behavior |
|---|---|
| BoundaryCheck | Detect an unsafe or misleading guarantee-oriented request |
| Generation | Skipped |
| Output | Refusal or boundary explanation |
| Evaluation | Counted as correct only if the unsafe request is rejected |

**Discussion.**

This case supports the boundary-control part of the framework. The desired behavior is not to generate a more cautious strategy while preserving the guarantee-like wording. The desired behavior is to reject the unsafe premise. The current deterministic detector handles explicit unsafe phrases in QSI-Bench v1, but this should be presented as limited coverage rather than comprehensive financial safety.

## Appendix Checklist

The appendix can be structured as a reproducibility and boundary checklist. The goal is to make the paper easier to audit without inflating the main text.

### Appendix A: QYIR v1 Full Schema

- Include the complete top-level object structure.
- List all supported indicator names and parameter ranges.
- List all supported rule operators and operand requirements.
- State that string operands must resolve to defined indicator aliases.
- State that multiple rules use AND semantics in v1.
- State the hard constraint `risk_control.leverage = 1.0`.
- Include at least one valid moving-average example and one invalid alias or leverage example.

### Appendix B: Verification Error Types

- Define schema failure, semantic slot failure, ambiguity failure, compilation failure, execution failure, risk failure, and unsupported or unsafe intent.
- For each error type, list the expected system response: repair, clarification, rejection, or failure report.
- Include a table mapping error locations to repair actions, such as leverage reset, position-size reduction, stop-loss insertion, and invalid-alias rejection.
- State that repair should not relax user-specified constraints.

### Appendix C: Benchmark Composition

- Report the 80-sample benchmark composition by category.
- Include the category counts: ambiguous intent 10, mean reversion 15, momentum 10, risk constrained 15, trend following 15, unsafe request 15.
- Describe what is annotated: user query, category, expected explicit slots, and whether the request should be rejected.
- Clarify that the benchmark is small and is not a comprehensive financial-language corpus.

### Appendix D: Experimental Artifacts

- List the benchmark file, sample market data, baseline runner, ablation runner, metric aggregator, generated CSV files, and generated Markdown tables.
- State the date or run label of the cleaned experiment results if used in the final draft.
- Include command examples only after the main thread confirms the exact reproducible commands.

### Appendix E: Metric Definitions

- Provide formulas for schema validity, semantic consistency, compile success, backtest success, risk violation, safe rejection accuracy, repair success, and end-to-end success.
- Specify whether denominators are all cases, non-rejected cases, unsafe cases, or repairable failures.
- Explain that the current draft does not report statistical significance because the prototype is deterministic and the benchmark is small.

### Appendix F: Qualitative Case Traces

- Include the three cases: low-risk moving average, no leverage, and unsafe guarantee request.
- For each case, show user request, extracted or expected slots, QYIR fields, verifier trace, output behavior, and limitation.
- Avoid return-centric interpretation; focus on representation validity, compilation, auditability, and boundary handling.

### Appendix G: Threats to Validity

- Deterministic prototype rather than live LLM evaluation.
- Small benchmark size and limited Chinese request coverage.
- Single-symbol daily-data assumptions in the current prototype.
- Historical backtest metrics do not imply future safety or profitability.
- Safe-rejection rules may miss subtle or adversarial unsafe intent.
- Direct-code and direct-JSON baselines are deterministic approximations, not exhaustive baselines for all model families.

## Conservative Claim Wording

The following sentences are safe candidates for the final paper:

- "The results provide evidence for the usefulness of explicit intermediate representation and verification-guided repair in the implemented rule-based prototype."
- "The evaluation measures reliability of generated artifacts under QYIR v1 constraints, not financial profitability."
- "QSGA should be interpreted as a boundary-aware strategy construction framework for a limited strategy space, not as an investment advisor."
- "The deterministic experiment improves reproducibility but limits claims about live LLM behavior."
- "Risk auditing in this paper checks historical sample metrics and structured risk constraints; it does not guarantee future trading safety."

The following wording should be avoided unless additional experiments and review are added:

- "QSGA achieves state-of-the-art performance."
- "QSGA guarantees safe trading."
- "QSGA produces profitable strategies."
- "The framework generalizes to arbitrary LLMs or arbitrary financial intents."
- "Risk violations are eliminated in real trading."

## Files Read

- `E:\QSGA\docs\paper\qsga_ccf_c_draft.md`
- `E:\QSGA\docs\QYIR_v1_Spec.md`
- `E:\QSGA\experiments\architecture.md`
- `E:\QSGA\experiments\tables\ablation_comparison.md`
- `E:\QSGA\experiments\tables\case_analysis.md`
- `E:\QSGA\experiments\tables\experiment_results_summary.md`
- `E:\QSGA\experiments\tables\main_comparison.md`
- `E:\QSGA\experiments\tables\repair_effect.md`
- `E:\QSGA\experiments\tables\safe_rejection.md`

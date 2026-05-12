# DECISIONS.md

本文件记录需要人类确认的研究决策。Agent 遇到人类决策点时写入这里，然后继续做不依赖该决策的任务，不要原地等待。

---

## TLDR_STATE_FOR_AGENT

当前待人类确认：

- 暂无

当前可继续推进：

- 基于官方 DeepSeek 80-case Route B 诊断继续做论文修订、失败分析、审稿模拟和后续非阻塞实验。

默认处理：

- 如果某任务被人类决策阻塞，将该任务标为 `blocked_human`。
- 返回 `TASK_QUEUE.md` 选择其它非阻塞任务。

---

## PendingReview

暂无。

---

## waiting_human

暂无。

---

## Done

### DEC-20260512-003

```yaml
Decision ID: DEC-20260512-003
Title: Decide whether QYIR v1 should support market-field rule operands
Status: accepted
Created: 2026-05-12
Updated: 2026-05-13
Related Task ID: TASK-20260512-012
Related Claim ID: CLAIM-RB-002
Context:
  - Saved prompt-only QYIR failures include alias/reference errors such as entry_rules[0].left references unknown alias 'close'.
  - QYIR v1 schema currently requires all string rule operands to reference indicator aliases.
  - compiler/qyir_compiler.py currently resolves string operands only from computed indicator aliases and rejects unknown strings.
  - Route B builder now avoids some price-vs-indicator failures by converting single moving-average price-breakout language into alias-only moving-average crossover approximations.
  - This workaround preserves QYIR v1 compatibility but can lose direct expressivity for price-vs-indicator rules.
Options:
  A:
    Description: Keep QYIR v1 alias-only operands for the current paper and document market-field operands as future work.
    Pros: Avoids schema/compiler contract churn before submission; preserves current validator/test assumptions; keeps Route B evidence comparable to existing artifacts.
    Cons: Requires builder approximations for price-vs-indicator language and leaves some direct prompt-output failures unresolved.
  B:
    Description: Extend QYIR v1 rule operands to allow explicit market fields such as market.close, market.open, market.volume.
    Pros: Better matches natural price-breakout language and reduces alias_failure for live prompt outputs.
    Cons: Requires schema validator, compiler operand resolver, canonicalizer, tests, metrics, and paper contract updates; invalidates some previous "unknown alias" failure interpretation.
  C:
    Description: Introduce QYIR v1.1 or an experimental Route B-only operand layer while keeping v1 frozen.
    Pros: Allows experimentation without rewriting the existing v1 claims.
    Cons: Adds versioning complexity and may distract from the current CCF-B paper route.
AI Recommendation:
  - Choose A for the current paper cycle; record B/C as future extensions after reviewer gate.
Default Assumption Before Human Response:
  - Do not change the QYIR v1 schema/compiler contract; keep builder-level alias-only compatibility.
Risk if Wrong:
  - If reviewers expect direct price-vs-indicator representation, the paper may look artificially constrained.
Blocking:
  - None for current paper cycle.
Non-Blocked Work Can Continue:
  - Paper limitation wording
  - Reviewer gate
  - Route B failure analysis
Human Response:
  - Current paper cycle chooses option A.
  - Keep QYIR v1 rule operands alias-only and do not modify schema/compiler contract before submission.
  - Record market.close, market.open, market.volume and similar explicit market-field operands as future work.
  - Continue builder-layer transformations to maintain QYIR v1 compatibility.
Final Decision:
  - Accepted option A.
  - QYIR v1 remains frozen with alias-only rule operands.
  - Market-field rule operands are deferred to future QYIR extensions after reviewer gate.
  - Route B continues to use alias-compatible builder approximations, and price-vs-indicator failures are reported as bounded expressivity limitations rather than compiler defects.
Audit Log Reference:
  - 2026-05-12 QYIR market operand decision draft
  - 2026-05-13 QYIR market operand final decision
```

### DEC-20260512-002

```yaml
Decision ID: DEC-20260512-002
Title: Resolve DeepSeek API endpoint for Route B live experiments
Status: accepted
Created: 2026-05-12
Updated: 2026-05-12
Related Task ID: TASK-20260512-010
Related Claim ID: CLAIM-RB-002
Context:
  - Initial bounded 5-case live smoke used the DashScope-compatible endpoint and returned 401 invalid_api_key.
  - User instructed the agent to use the official DeepSeek API docs.
  - Official DeepSeek OpenAI-compatible endpoint is https://api.deepseek.com.
  - Official JSON Output mode requires response_format={"type":"json_object"} and a prompt that explicitly requests json.
  - Current official model names include deepseek-v4-flash and deepseek-v4-pro.
Options:
  A:
    Description: Continue using the failed DashScope-compatible endpoint.
    Pros: Preserves the old attempted setup.
    Cons: It produced unusable 401 results with the available key.
  B:
    Description: Use official DeepSeek OpenAI-compatible endpoint, deepseek-v4-flash, JSON Output mode, and disabled thinking for slot extraction.
    Pros: Matches user instruction and produced successful 5-case and 80-case live runs.
    Cons: Results are provider/model-specific and still require conservative interpretation.
Accepted Scope:
  - base_url: https://api.deepseek.com
  - default model: deepseek-v4-flash
  - compatibility aliases: deepseek-chat -> deepseek-v4-flash; deepseek-reasoner -> deepseek-v4-pro
  - response_format: {"type":"json_object"}
  - extra_body: {"thinking":{"type":"disabled"}}
  - max_retries: 1
  - max_tokens: 1200
AI Recommendation:
  - Use option B and keep all live claims diagnostic.
Default Assumption Before Human Response:
  - Continue non-API Route B work until official endpoint was confirmed.
Risk if Wrong:
  - Model/API behavior may change; saved raw outputs and metadata must remain part of the evidence package.
Blocking:
  - None for current Route B live diagnostic.
Non-Blocked Work Can Continue:
  - Paper revision
  - Failure analysis
  - Reviewer gate
Human Response:
  - User request on 2026-05-12: refer to official DeepSeek API docs for DEC-20260512-002.
Final Decision:
  - Accepted official DeepSeek API configuration and completed 80-case Route B live diagnostic.
Audit Log Reference:
  - 2026-05-12 Official DeepSeek Route B live diagnostic
```

### DEC-20260512-001

```yaml
Decision ID: DEC-20260512-001
Title: Use DeepSeek API for bounded Route B live smoke
Status: accepted
Created: 2026-05-12
Updated: 2026-05-12
Related Task ID: TASK-20260512-009
Related Claim ID: CLAIM-RB-002
Context:
  - User explicitly allowed using the root DSAPIKEY.txt and deepseek-v4-flash or deepseek-v4-pro if needed.
Options:
  A:
    Description: Run a bounded low-cost deepseek-v4-flash smoke.
    Pros: Produces live evidence quickly with limited cost.
    Cons: May fail if API key or endpoint is invalid.
  B:
    Description: Defer all live API work.
    Pros: Avoids cost and credential risk.
    Cons: Leaves Route B live improvement untested.
Accepted Scope:
  - Model: deepseek-v4-flash
  - Case limit: <= 5 for first smoke
  - Max retries: 1
  - Max tokens: 1200
  - Output paths under experiments/results
  - No full batch or pro-model run without a separate recorded scope update
AI Recommendation:
  - Use deepseek-v4-flash first for cost control.
Default Assumption Before Human Response:
  - Already accepted by the user's current instruction for bounded smoke only.
Risk if Wrong:
  - Unexpected API cost or endpoint mismatch.
Blocking:
  - Full Route B batch still pending.
Non-Blocked Work Can Continue:
  - Bounded live smoke under accepted scope.
Human Response:
  - User request on 2026-05-12: API key is in DSAPIKEY.txt and deepseek-v4-flash/pro calls are allowed if needed.
Final Decision:
  - Accepted for bounded 5-case deepseek-v4-flash smoke.
Audit Log Reference:
  - 2026-05-12 Route B live smoke authorization
```

---

## Decision Template

```yaml
Decision ID: DEC-YYYYMMDD-NNN
Title:
Status: PendingReview / waiting_human / accepted / rejected / superseded
Created:
Updated:
Related Task ID:
Related Claim ID:
Context:
Options:
  A:
    Description:
    Pros:
    Cons:
  B:
    Description:
    Pros:
    Cons:
AI Recommendation:
Default Assumption Before Human Response:
Risk if Wrong:
Blocking:
  - 
Non-Blocked Work Can Continue:
  - 
Human Response:
Final Decision:
Audit Log Reference:
```

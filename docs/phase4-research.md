# Phase 4: 接入 LLM 生成 QYIR (Integrate LLM to Generate QYIR) - Research

**Researched:** 2026-04-27
**Domain:** LLM structured output generation, prompt engineering, JSON schema validation
**Confidence:** HIGH

## Summary

This phase implements the core NL-to-QYIR pipeline: Chinese natural language strategy request in, validated QYIR JSON out. The implementation requires three files (`generator/prompt.py`, `generator/llm_client.py`, `generator/qyir_generator.py`) that together handle prompt construction, LLM API communication, JSON parsing, and Pydantic schema validation.

The critical architectural insight is that **the existing QYIR Pydantic schema cannot be passed directly to OpenAI's Structured Outputs API in strict mode**. The QYIR schema uses features that are incompatible with OpenAI's supported JSON Schema subset: `additionalProperties: true` on IndicatorConfig.params, optional fields not listed in `required`, and validation keywords (`minLength`, `maximum`, `minimum`) that strict mode does not support. Therefore, the recommended approach is a **dual-schema strategy**: use a simplified "LLM-compatible" schema for constrained generation, then validate the parsed result against the full QYIR schema with all domain constraints via the existing `qyir.validator.validate_qyir()`.

**Primary recommendation:** Use OpenAI structured outputs with a simplified Pydantic model for generation, then post-validate with the full QYIR schema. Wrap the entire flow in retry logic (max 2 attempts). The prompt must include the full QYIR JSON example and explicit constraint rules.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Prompt construction | Backend (Python module) | -- | Pure function, deterministic |
| LLM API call | External API | Backend (wrapper) | OpenAI API is external; wrapper handles retries |
| JSON parsing | Backend | -- | stdlib `json.loads` |
| QYIR schema validation | Backend | -- | Pydantic v2, already implemented in `qyir/validator.py` |
| Error classification | Backend | -- | Categorize parse vs schema vs semantic errors |
| Safe rejection check | Backend | -- | Keyword-based, deterministic (future phase) |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openai | 1.3.0 (installed) / 2.32.0 (latest) | LLM API client | Official Python SDK for OpenAI API, supports structured outputs [VERIFIED: pip registry] |
| pydantic | >=2.0 (installed) | Schema validation | Already in project, used for QYIR schema [VERIFIED: pyproject.toml] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json (stdlib) | -- | Parse LLM JSON output | Always -- fallback if structured output API not used |
| os (stdlib) | -- | Read OPENAI_API_KEY env var | In llm_client.py initialization |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| openai SDK | requests + manual API calls | More control but no retry logic, no type safety, more boilerplate |
| OpenAI structured outputs | Pure prompt + json.loads | Structured outputs guarantee valid JSON; prompt-only approach requires manual parsing and has higher failure rate |
| strict mode structured outputs | non-strict mode | strict guarantees schema shape but incompatible with current QYIR schema; non-strict is more forgiving |

**Installation:**
```bash
# Using uv (project uses uv based on uv.lock)
uv add openai
```

**Version verification:**
- openai: installed 1.3.0, latest 2.32.0 [VERIFIED: pip registry]
- Note: v1.x is sufficient for this phase. v2.x introduces the Responses API (`client.responses.parse()`) which is newer but the Chat Completions API (`client.beta.chat.completions.parse()`) works well in v1.x. If upgrading to v2.x, use `client.responses.parse()` with `text_format=` parameter.

## Architecture Patterns

### System Architecture Diagram

```
User Chinese NL Query
        |
        v
+-------------------+
| generator/        |
| qyir_generator.py |  <-- Orchestrator
|  (generate_qyir)  |
+---+-------+-------+
    |       |
    v       v
+--------+  +------------------------+
|prompt.py|  | llm_client.py          |
|build_   |  | call_llm()             |
|qyir_    |  |  -> OpenAI API         |
|prompt() |  |  -> retry logic        |
+--------+  |  -> return raw text     |
    |       +-----------+------------+
    |                   |
    v                   v
 Prompt text       LLM raw response
    +                   |
    +-------------------+
                |
                v
         json.loads() / parse
                |
                v
    +------------------------+
    | qyir/validator.py      |
    | validate_qyir(data)    |
    |  -> Pydantic QYIR      |
    |  -> full constraint     |
    |     validation          |
    +------------------------+
                |
        +-------+-------+
        |               |
        v               v
   Valid QYIR      ValidationError
   (return dict)   (collect errors,
                    feed to retry/repair)
```

### Recommended Project Structure
```
generator/
├── __init__.py           # Package init
├── prompt.py             # Prompt template builder
├── llm_client.py         # OpenAI API wrapper with retry
└── qyir_generator.py     # Orchestrator: input -> prompt -> LLM -> validate
```

### Pattern 1: Dual-Schema Generation + Post-Validation

**What:** Use a simplified Pydantic model (compatible with OpenAI structured outputs) for LLM generation, then validate the output against the full QYIR schema with all domain constraints.

**When to use:** This is the ONLY pattern for this phase. The existing QYIR schema in `qyir/schema.py` uses Pydantic features (field validators, model validators, complex constraints) that are incompatible with OpenAI's strict-mode structured outputs.

**Why dual-schema is necessary:**
The QYIR Pydantic model has these incompatibilities with OpenAI structured outputs strict mode [VERIFIED: platform.openai.com/docs/guides/structured-outputs]:

1. `IndicatorConfig.params` uses `Dict[str, Any]` which produces `additionalProperties: true` -- strict mode requires `additionalProperties: false` on all objects
2. Optional fields (`description`, `version`, `stop_loss`, etc.) are NOT in the `required` array -- strict mode requires ALL fields in `required`
3. Validation keywords like `minLength`, `maximum`, `minimum` are not enforced by the API
4. `model_validator` and `field_validator` constraints cannot be expressed in JSON Schema

**Example:**

```python
# generator/qyir_generator.py -- simplified pattern

from qyir.validator import validate_qyir

def generate_qyir(user_query: str) -> dict:
    """Generate QYIR from natural language query."""
    # Step 1: Build prompt
    prompt = build_qyir_prompt(user_query)

    # Step 2: Call LLM (with built-in retry)
    raw_json_str = call_llm(prompt)

    # Step 3: Parse JSON
    try:
        data = json.loads(raw_json_str)
    except json.JSONDecodeError as e:
        raise GenerationError(f"Invalid JSON: {e}")

    # Step 4: Validate against FULL QYIR schema
    result = validate_qyir(data)
    if not result.valid:
        raise SchemaValidationError(result.summary)

    return data
```

### Pattern 2: Prompt-Only JSON Generation (Fallback)

**What:** Use a carefully crafted system prompt to instruct the LLM to output valid QYIR JSON, without structured output constraints.

**When to use:** When the OpenAI structured outputs API is unavailable (wrong model, API version, or non-OpenAI provider). This is the primary approach for this phase because the QYIR schema is too complex for strict-mode structured outputs.

**Example:**

```python
# generator/prompt.py -- prompt construction

QYIR_SYSTEM_PROMPT = """You are a quantitative strategy generation assistant.
Your task is to convert the user's natural language investment intent into a
QYIR (Quantitative Strategy Intermediate Representation) JSON object.

## Output Rules
1. Output ONLY valid JSON. No markdown, no explanation, no code blocks.
2. Do NOT output Python code.
3. The JSON must conform to the QYIR schema exactly.

## Supported Indicators
- SMA: params: {window: int (2-500)}
- EMA: params: {window: int (2-500)}
- RSI: params: {window: int (2-100)}
- MACD: params: {fast: int, slow: int, signal: int, output: "macd_line"|"signal_line"|"histogram"}
  - Constraint: fast < slow
- BOLLINGER: params: {window: int (2-500), num_std: float (0.1-5.0), output: "upper"|"middle"|"lower"}

## Supported Rule Types
- cross_over: requires left, right
- cross_under: requires left, right
- greater_than: requires left, right
- less_than: requires left, right
- between: requires left, lower, upper (NO right)

## Mandatory Fields
- strategy_name: lowercase alphanumeric + underscore only (e.g., "ma_crossover")
- description: brief English description (max 512 chars)
- market: {symbol, timeframe: "1d", start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD"}
- indicators: 1-10 items, each with name, params, alias (lowercase + underscore)
- entry_rules: 1-10 rules referencing indicator aliases
- exit_rules: 1-10 rules referencing indicator aliases
- risk_control: {position_size: 0.01-1.0, leverage: 1.0 (locked)}

## Risk Control Rules
- leverage MUST be 1.0
- position_size MUST be between 0.01 and 1.0
- Always include stop_loss if user mentions risk control
- If user says "no leverage" / "不要杠杆", set leverage = 1.0
- If user says "stable" / "稳一点", use position_size <= 0.3

## Safety Rules
- NEVER guarantee profits
- If the request is unsafe or unrealistic, output: {"status": "rejected", "reason": "..."}
"""

QYIR_EXAMPLE = """
## Example Output
{
  "strategy_name": "conservative_ma_crossover",
  "description": "A conservative moving average crossover strategy.",
  "version": "1.0",
  "market": {
    "symbol": "SPY",
    "timeframe": "1d",
    "start_date": "2020-01-01",
    "end_date": "2024-12-31"
  },
  "indicators": [
    {"name": "SMA", "params": {"window": 20}, "alias": "sma_short"},
    {"name": "SMA", "params": {"window": 60}, "alias": "sma_long"}
  ],
  "entry_rules": [
    {"type": "cross_over", "left": "sma_short", "right": "sma_long"}
  ],
  "exit_rules": [
    {"type": "cross_under", "left": "sma_short", "right": "sma_long"}
  ],
  "risk_control": {
    "position_size": 0.3,
    "stop_loss": 0.08,
    "take_profit": null,
    "max_drawdown_limit": 0.2,
    "allow_short": false,
    "leverage": 1.0
  }
}
"""

def build_qyir_prompt(user_query: str) -> list[dict]:
    """Build the message list for QYIR generation."""
    return [
        {"role": "system", "content": QYIR_SYSTEM_PROMPT + "\n" + QYIR_EXAMPLE},
        {"role": "user", "content": f"User query: {user_query}\n\nOutput QYIR JSON only."},
    ]
```

### Pattern 3: Retry with Error Feedback

**What:** When QYIR generation fails (JSON parse error or schema validation error), feed the error back to the LLM for repair.

**When to use:** As part of the generation loop in `qyir_generator.py`. Max 2 retry rounds.

**Example:**

```python
# generator/qyir_generator.py -- retry loop pattern

MAX_RETRIES = 2

def generate_qyir(user_query: str) -> GenerationResult:
    messages = build_qyir_prompt(user_query)

    for attempt in range(MAX_RETRIES + 1):
        # Call LLM
        raw_response = call_llm(messages)

        # Parse JSON
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as e:
            if attempt < MAX_RETRIES:
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({
                    "role": "user",
                    "content": f"Your output is not valid JSON. Error: {e}. Please output ONLY valid QYIR JSON."
                })
                continue
            return GenerationResult(success=False, error=f"JSON parse failed: {e}")

        # Check for rejection
        if data.get("status") == "rejected":
            return GenerationResult(success=False, rejected=True, reason=data.get("reason", ""))

        # Validate schema
        validation = validate_qyir(data)
        if validation.valid:
            return GenerationResult(success=True, qyir=data)

        if attempt < MAX_RETRIES:
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({
                "role": "user",
                "content": f"Your QYIR has validation errors:\n{validation.summary}\n\nPlease fix and output corrected QYIR JSON only."
            })
            continue

        return GenerationResult(success=False, error=validation.summary)

    return GenerationResult(success=False, error="Max retries exceeded")
```

### Anti-Patterns to Avoid
- **Passing QYIR Pydantic model directly to OpenAI structured outputs:** The model uses `additionalProperties: true` on `params`, optional fields not in `required`, and constraint keywords that strict mode ignores or rejects. This WILL fail or produce unreliable results. [VERIFIED: analyzed QYIR.model_json_schema() output]
- **Hand-rolling JSON parsing with regex:** Use `json.loads()`. Never try to extract JSON from markdown with regex -- it breaks on edge cases (nested braces, escaped quotes, markdown in content).
- **Ignoring refusal handling:** OpenAI models may refuse to generate financial strategies. Always check for refusal responses.
- **Retrying without error context:** Blank retries without telling the LLM what went wrong have very low success rates. Always include the specific error message in retry prompts.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| LLM API retry logic | Custom retry loop with time.sleep | openai SDK built-in `max_retries` parameter | SDK handles exponential backoff, jitter, idempotency keys, rate limit headers [CITED: platform.openai.com/docs] |
| JSON schema generation from Pydantic | Manual dict construction | `QYIR.model_json_schema()` | Already correct in Pydantic v2, handles nested models, enums, optional fields |
| JSON extraction from LLM response | Regex to strip markdown | Structured output API or `json.loads()` on clean response | Regex fails on edge cases; structured output eliminates the problem |
| QYIR validation | Custom validation functions | `qyir.validator.validate_qyir()` | Already implemented, handles all Pydantic constraints including cross-field validators |

**Key insight:** The project already has a well-tested QYIR validator. The LLM generation layer should ONLY be responsible for producing a JSON string that MIGHT be valid QYIR. Validation is delegated to the existing module.

## Common Pitfalls

### Pitfall 1: QYIR Schema Incompatibility with Structured Outputs
**What goes wrong:** Passing the QYIR Pydantic model directly to `client.beta.chat.completions.parse(response_format=QYIR)` fails because the generated JSON Schema contains `additionalProperties: true` on IndicatorConfig.params, optional fields not in `required`, and unsupported constraint keywords.
**Why it happens:** OpenAI's strict mode requires a specific JSON Schema subset that Pydantic's default `model_json_schema()` does not produce for models with `Dict[str, Any]` fields, `Optional` types, or complex validators.
**How to avoid:** Use prompt-only JSON generation (not structured outputs API). The prompt explicitly describes the schema. Post-validate with the full QYIR Pydantic model.
**Warning signs:** API returns 400 error "Invalid schema", or LLM output omits optional fields that strict mode requires.

### Pitfall 2: LLM Outputs Markdown-Wrapped JSON
**What goes wrong:** LLM returns ` ```json\n{...}\n``` ` instead of raw JSON, causing `json.loads()` to fail.
**Why it happens:** LLMs are trained to format code blocks. Even with "output JSON only" instructions, some models wrap in markdown.
**How to avoid:** Implement a JSON extraction utility that strips markdown code fences before parsing. Also use "Do NOT wrap in markdown" in the system prompt.
**Warning signs:** `json.loads()` raises `JSONDecodeError` with "Expecting value" at line 1.

### Pitfall 3: LLM Hallucinates Unsupported Indicators or Rules
**What goes wrong:** LLM generates indicators like "KDJ", "ATR", or rule types like "divergence" that are not in the QYIR schema.
**Why it happens:** LLMs have broad financial knowledge and may invent plausible but unsupported features.
**How to avoid:** The prompt must list ONLY supported indicators and rules. The QYIR validator catches this, but it is better to prevent via prompt. Include "Only use these indicators: SMA, EMA, RSI, MACD, BOLLINGER. No others are supported."
**Warning signs:** QYIR validation fails with "Invalid enum value" for indicator name or rule type.

### Pitfall 4: Rule References Non-Existent Alias
**What goes wrong:** LLM generates rules like `{"type": "cross_over", "left": "sma_20", "right": "sma_60"}` but the indicators use aliases `sma_short` and `sma_long`.
**Why it happens:** LLM does not track the connection between indicator aliases and rule references.
**How to avoid:** In the prompt, explicitly state: "Rule left/right fields MUST reference indicator alias names exactly." Include a worked example showing the alias-reference relationship. The QYIR validator catches this via `_check_rule_references`.
**Warning signs:** QYIR validation fails with "references unknown alias".

### Pitfall 5: Incorrect Risk Control Values
**What goes wrong:** LLM sets `leverage: 2.0` when user said "no leverage", or `position_size: 0.9` when user said "conservative".
**Why it happens:** LLM does not reliably respect numeric constraints in text instructions.
**How to avoid:** Explicit constraint rules in the prompt. Post-validation catches this. The semantic verifier (Phase 5) will also check user intent alignment.
**Warning signs:** QYIR validation fails with "leverage must be 1.0 in QYIR v1" or risk control values out of range.

### Pitfall 6: API Key Not Configured
**What goes wrong:** `openai.OpenAI()` raises `AuthenticationError` because `OPENAI_API_KEY` is not set.
**Why it happens:** The key must be in environment variables or passed explicitly.
**How to avoid:** In `llm_client.py`, read `OPENAI_API_KEY` from env with a clear error message if missing. Support optional `OPENAI_BASE_URL` for alternative providers (DeepSeek, local models).
**Warning signs:** Immediate `AuthenticationError` on first API call.

## Code Examples

Verified patterns from official sources:

### LLM Client with Retry and Error Handling
```python
# Source: [CITED: platform.openai.com/docs/guides/structured-outputs] + openai Python SDK docs
from __future__ import annotations

import json
import os
from typing import Optional

from openai import OpenAI, APIError, RateLimitError, APITimeoutError


def _get_client() -> OpenAI:
    """Create OpenAI client with configured API key."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not set. "
            "Set it via: export OPENAI_API_KEY=sk-..."
        )
    base_url = os.environ.get("OPENAI_BASE_URL")  # Optional: for DeepSeek etc.
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        max_retries=3,      # Built-in retry for 429/500/502/503
        timeout=60.0,
    )


def call_llm(
    messages: list[dict],
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> str:
    """Call LLM with messages and return raw text response.

    Args:
        messages: Chat message list [{role, content}, ...]
        model: Model name (default gpt-4o-mini for cost efficiency)
        temperature: Lower = more deterministic (0.3 recommended for structured output)

    Returns:
        Raw text content from LLM response.

    Raises:
        LLMClientError: On API errors after retries exhausted.
    """
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=4096,
        )
        content = response.choices[0].message.content
        if content is None:
            raise LLMClientError("LLM returned empty response")
        return content.strip()
    except RateLimitError as e:
        raise LLMClientError(f"Rate limited: {e}") from e
    except APITimeoutError as e:
        raise LLMClientError(f"Request timed out: {e}") from e
    except APIError as e:
        raise LLMClientError(f"API error: {e}") from e


class LLMClientError(Exception):
    """Error from LLM client."""
    pass
```

### JSON Extraction from LLM Response
```python
import json
import re


def extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown wrapping.

    Handles:
    - Raw JSON: '{"key": "value"}'
    - Markdown wrapped: '```json\\n{...}\\n```'
    - With preamble: 'Here is the JSON:\\n{...}'
    """
    # Strip markdown code fences
    text = text.strip()
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    match = re.search(fence_pattern, text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    # Try to find JSON object start
    start = text.find("{")
    if start == -1:
        raise json.JSONDecodeError("No JSON object found", text, 0)

    # Parse from first { to end
    return json.loads(text[start:])
```

### Generation Result Dataclass
```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class GenerationResult:
    """Immutable result of QYIR generation."""
    success: bool
    qyir: Optional[dict] = None
    error: Optional[str] = None
    rejected: bool = False
    rejection_reason: Optional[str] = None
    attempts: int = 1
```

### Safe Rejection Detection (Pre-Generation Check)
```python
# Based on docs/实现方案规划.md Section 10.4
UNSAFE_PATTERNS = [
    "稳赚", "稳赚不赔", "保证收益", "一定赚钱",
    "一个月翻倍", "内幕消息", "规避监管", "操纵市场",
    "满仓梭哈", "十倍杠杆", "保本保息",
]

def should_reject(user_query: str) -> tuple[bool, str | None]:
    """Check if user query contains unsafe patterns."""
    for pattern in UNSAFE_PATTERNS:
        if pattern in user_query:
            return True, f"Unsafe request detected: '{pattern}'"
    return False, None
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| JSON mode (`response_format: json_object`) | Structured Outputs (`response_format: json_schema`) | Aug 2024 | Structured outputs guarantee schema adherence; JSON mode only guarantees valid JSON [CITED: platform.openai.com/docs/guides/structured-outputs] |
| `client.chat.completions.create()` + manual JSON parse | `client.beta.chat.completions.parse()` + Pydantic model | Aug 2024 | SDK handles schema generation and Pydantic instantiation [CITED: platform.openai.com/docs/guides/structured-outputs] |
| `client.chat.completions.*` | `client.responses.*` (Responses API) | 2025 | New API surface; both work, Responses API is newer |
| Prompt-only JSON generation | Constrained decoding | 2024 | Constrained decoding enforces schema at token generation level |

**Deprecated/outdated:**
- `response_format: {"type": "json_object"}` (JSON mode): Superseded by structured outputs. JSON mode only guarantees valid JSON, not schema compliance. Still works but less reliable. [CITED: platform.openai.com/docs/guides/structured-outputs]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | OpenAI API key will be provided via environment variable `OPENAI_API_KEY` | Architecture | User cannot run the system without a key |
| A2 | gpt-4o-mini is sufficient for QYIR generation quality | Standard Stack | May need gpt-4o for complex Chinese strategy requests |
| A3 | OpenAI structured outputs are NOT used (prompt-only approach) due to schema incompatibility | Architecture | If OpenAI expands schema support, could simplify implementation |
| A4 | Non-OpenAI providers (DeepSeek, local models) are supported via `OPENAI_BASE_URL` | Architecture | Some providers may not support the same prompt patterns |
| A5 | Temperature 0.3 is optimal for structured output generation | Code Examples | May need tuning based on generation quality |

## Open Questions

1. **Which specific LLM model to use?**
   - What we know: The implementation plan recommends `gpt-4o-mini` for cost efficiency. The paper needs reproducible results.
   - What's unclear: Whether gpt-4o-mini has sufficient Chinese language understanding for strategy intent parsing.
   - Recommendation: Default to `gpt-4o-mini`, make model configurable via env var, test both.

2. **Should we support the Responses API (v2.x) or Chat Completions API (v1.x)?**
   - What we know: Installed openai SDK is v1.3.0. The Responses API (`client.responses.parse()`) requires v2.x.
   - What's unclear: Whether upgrading to v2.x introduces breaking changes for other project code.
   - Recommendation: Stay on v1.x for now, use `client.chat.completions.create()` with prompt-only JSON generation. Upgrade path is available later.

3. **Should the safe rejection check be in this phase or Phase 7?**
   - What we know: The implementation plan places safe rejection in Phase 7. However, a simple keyword check in `qyir_generator.py` prevents wasted API calls.
   - What's unclear: Whether the Phase 7 implementation will use the same function.
   - Recommendation: Implement a lightweight `should_reject()` check in the generator now. Phase 7 can extend it.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | Yes | 3.12.7 | -- |
| pydantic | QYIR validation | Yes | >=2.0 | -- |
| openai | LLM API calls | No (not installed) | -- | Install via `uv add openai` |
| OPENAI_API_KEY | API authentication | Unknown | -- | Must be set by user |
| pytest | Testing | Yes (dev) | >=9.0.3 | -- |

**Missing dependencies with no fallback:**
- `openai` package: Must be installed before implementation. Run `uv add openai`.
- `OPENAI_API_KEY`: Must be configured by user. The system cannot generate QYIR without it.

**Missing dependencies with fallback:**
- None

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >= 9.0.3 |
| Config file | pyproject.toml (testpaths = ["tests"]) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-01 | Input Chinese strategy intent, generate valid QYIR JSON | integration | `pytest tests/test_qyir_generator.py::test_generate_basic_ma -x` | No -- Wave 0 |
| REQ-02 | Catch illegal JSON parse errors | unit | `pytest tests/test_qyir_generator.py::test_invalid_json_error -x` | No -- Wave 0 |
| REQ-03 | Catch QYIR schema validation errors | unit | `pytest tests/test_qyir_generator.py::test_schema_validation_error -x` | No -- Wave 0 |
| REQ-04 | Safe rejection of unsafe requests | unit | `pytest tests/test_qyir_generator.py::test_unsafe_rejection -x` | No -- Wave 0 |
| REQ-05 | Retry on validation failure | unit | `pytest tests/test_qyir_generator.py::test_retry_on_failure -x` | No -- Wave 0 |
| REQ-06 | JSON extraction from markdown-wrapped response | unit | `pytest tests/test_prompt.py::test_extract_json -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_qyir_generator.py tests/test_prompt.py -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before proceeding

### Wave 0 Gaps
- [ ] `tests/test_qyir_generator.py` -- covers REQ-01 through REQ-05
- [ ] `tests/test_prompt.py` -- covers prompt construction and JSON extraction (REQ-06)
- [ ] `tests/conftest.py` -- shared fixtures (mock LLM responses, sample QYIR data)

**Note on testing strategy:** Tests that call the real OpenAI API should be marked with `@pytest.mark.integration` and skipped in CI. Unit tests should mock the LLM client to return pre-canned responses (valid QYIR, invalid JSON, schema errors).

## Security Domain

> security_enforcement is not explicitly configured; including this section.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | API key via environment variable, never hardcoded |
| V3 Session Management | no | Stateless API calls, no sessions |
| V4 Access Control | no | Single-user CLI tool |
| V5 Input Validation | yes | User query validated before LLM call; LLM output validated against Pydantic schema |
| V6 Cryptography | no | HTTPS handled by openai SDK |

### Known Threat Patterns for LLM Integration

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection via user query | Tampering | Input sanitization; separate system/user messages; never include raw user input in system prompt templates |
| LLM generates harmful financial advice | Repudiation | Explicit "no profit guarantee" instructions; safe rejection for unsafe requests |
| API key exposure | Information disclosure | Read from env var only; never log or print API key |
| Excessive API costs | Denial of Service | Token limits (max_tokens=4096); rate limiting; max retries cap |

### API Key Security
- NEVER hardcode API keys in source code [ASSUMED: standard security practice]
- Read from `OPENAI_API_KEY` environment variable exclusively
- Fail fast with clear error message if key is missing
- Support `.env` file for local development (but never commit `.env` to git)

## Sources

### Primary (HIGH confidence)
- OpenAI Official Docs - Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs [CITED: full page content retrieved]
- OpenAI Python SDK (pip registry) - verified version availability: openai 1.3.0 installed, 2.32.0 latest [VERIFIED: pip index]
- QYIR schema analysis - generated `QYIR.model_json_schema()` and verified incompatibilities with OpenAI structured outputs [VERIFIED: local codebase]

### Secondary (MEDIUM confidence)
- dida.do blog - Structured outputs with OpenAI and Pydantic walkthrough: https://dida.do/blog/structured-outputs-with-openai-and-pydantic [CITED: full article retrieved]
- OpenAI community discussions on Pydantic structured output limitations: https://community.openai.com/t/how-to-fix-openai-structured-outputs-breaking-your-pydantic-models-bdcd896d43bd [CITED: existence verified via web search]

### Tertiary (LOW confidence)
- LLM retry best practices (tenacity library) - based on training knowledge of Python retry patterns [ASSUMED]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - verified against pip registry and official docs
- Architecture: HIGH - QYIR schema incompatibility verified by generating model_json_schema() and comparing against OpenAI supported subset
- Pitfalls: HIGH - common LLM JSON generation issues well-documented across multiple sources
- Prompt engineering: MEDIUM - prompt patterns based on official docs and community practices; Chinese language effectiveness not verified

**Research date:** 2026-04-27
**Valid until:** 2026-05-27 (LLM APIs change frequently; structured outputs feature set is evolving)

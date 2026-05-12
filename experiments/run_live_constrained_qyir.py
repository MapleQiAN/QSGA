"""Run live constrained-output QYIR construction diagnostics.

The experiment asks an OpenAI-compatible chat model for QYIR JSON with a
provider-level `response_format` constraint when supported. It is deliberately
separate from `run_live_llm.py` so the prompt-only 80-case diagnostic remains
unchanged and can be compared against this constrained-output probe.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from experiments.baselines import (
    DEFAULT_BENCHMARK_PATH,
    DEFAULT_DATA_PATH,
    MethodResult,
    clarification_result,
    load_benchmark,
    query_needs_clarification,
    results_to_csv,
)
from experiments.run_live_llm import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    MODEL_ALIASES,
    SYSTEM_PROMPT,
    RawCall,
    _evaluate_qyir,
    _failed_result,
    _method_result,
    _parse_json,
    guard_api_terms,
    normalize_model_name,
    read_api_key,
    select_records,
    write_audit_jsonl,
    write_metadata,
    write_token_usage,
)
from generator.prompt import build_qyir_prompt
from qyir.schema import QYIR
from qyir.validator import validate_qyir
from verifier.safe_rejection import should_reject


DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_CASE_LIMIT = 40
DEFAULT_MAX_RETRIES = 1
SUPPORTED_RESPONSE_FORMATS = {"json_object", "json_schema", "none"}


class ConstrainedOpenAIClient:
    """OpenAI-compatible client with optional structured-output constraints."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        method: str,
        case_id: str,
        audit: list[RawCall],
        max_tokens: int,
        response_format_mode: str,
        system_prompt: str = SYSTEM_PROMPT,
    ) -> None:
        from openai import OpenAI

        if response_format_mode not in SUPPORTED_RESPONSE_FORMATS:
            raise ValueError(f"Unsupported response_format_mode: {response_format_mode}")
        self.model = model
        self.method = method
        self.case_id = case_id
        self.audit = audit
        self.max_tokens = max_tokens
        self.response_format_mode = response_format_mode
        self.system_prompt = system_prompt
        self._attempt = 0
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str) -> str:
        self._attempt += 1
        raw_output = ""
        prompt_tokens = None
        completion_tokens = None
        total_tokens = None
        error = None
        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "max_tokens": self.max_tokens,
            }
            response_format = build_response_format(self.response_format_mode)
            if response_format is not None:
                kwargs["response_format"] = response_format
            response = self._client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            raw_output = content
            usage = getattr(response, "usage", None)
            if usage is not None:
                prompt_tokens = getattr(usage, "prompt_tokens", None)
                completion_tokens = getattr(usage, "completion_tokens", None)
                total_tokens = getattr(usage, "total_tokens", None)
            return content
        except Exception as exc:  # pragma: no cover - requires live API failure
            error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            self.audit.append(
                RawCall(
                    model=self.model,
                    method=self.method,
                    case_id=self.case_id,
                    attempt=self._attempt,
                    prompt=prompt,
                    raw_output=raw_output,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    error=error,
                )
            )


def build_response_format(mode: str) -> dict[str, Any] | None:
    """Build provider response_format for JSON-only or JSON-schema output."""
    if mode == "none":
        return None
    if mode == "json_object":
        return {"type": "json_object"}
    if mode == "json_schema":
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "qyir_v1",
                "schema": QYIR.model_json_schema(),
                "strict": False,
            },
        }
    raise ValueError(f"Unsupported response_format mode: {mode}")


def run_live_constrained_qyir(
    *,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
    api_key_file: str | Path | None = None,
    base_url: str = DEFAULT_BASE_URL,
    models: Iterable[str] = (DEFAULT_MODEL,),
    case_limit: int | None = DEFAULT_CASE_LIMIT,
    case_ids: set[str] | None = None,
    seed: int = 20260505,
    max_retries: int = DEFAULT_MAX_RETRIES,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    response_format_mode: str = "json_object",
    allow_coding_plan: bool = False,
    checkpoint_output: str | Path | None = None,
    checkpoint_raw_output: str | Path | None = None,
    checkpoint_metadata_output: str | Path | None = None,
    checkpoint_usage_output: str | Path | None = None,
) -> tuple[list[MethodResult], list[RawCall], dict[str, Any]]:
    """Run constrained live QYIR construction on a stratified subset."""
    api_key = read_api_key(api_key_file)
    guard_api_terms(api_key, base_url, allow_coding_plan)
    selected = select_records(load_benchmark(benchmark_path), case_limit=case_limit, seed=seed, case_ids=case_ids)
    price_data = pd.read_csv(data_path)
    audit: list[RawCall] = []
    results: list[MethodResult] = []
    normalized_models = [normalize_model_name(model) for model in models]
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_path": str(benchmark_path),
        "data_path": str(data_path),
        "base_url": base_url,
        "models": normalized_models,
        "case_count": len(selected),
        "case_ids": [str(record["id"]) for record in selected],
        "completed_case_ids": [],
        "seed": seed,
        "max_retries": max_retries,
        "max_tokens": max_tokens,
        "response_format_mode": response_format_mode,
        "methods": ["live_constrained_qyir"],
    }

    for model in normalized_models:
        for record in selected:
            result = (
                _run_one_constrained_record(
                    record,
                    model,
                    api_key,
                    base_url,
                    price_data,
                    audit,
                    max_retries=max_retries,
                    max_tokens=max_tokens,
                    response_format_mode=response_format_mode,
                )
            )
            results.append(result)
            metadata["completed_case_ids"].append(str(record["id"]))
            _write_checkpoints(
                results,
                audit,
                metadata,
                checkpoint_output=checkpoint_output,
                checkpoint_raw_output=checkpoint_raw_output,
                checkpoint_metadata_output=checkpoint_metadata_output,
                checkpoint_usage_output=checkpoint_usage_output,
            )
    return results, audit, metadata


def replay_live_constrained_qyir(
    *,
    raw_output_path: str | Path,
    metadata_path: str | Path,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
) -> list[MethodResult]:
    """Recompute constrained QYIR metrics from saved raw model outputs."""
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    records = {str(record["id"]): record for record in load_benchmark(benchmark_path)}
    selected = [records[str(case_id)] for case_id in metadata["case_ids"]]
    price_data = pd.read_csv(data_path)
    raw_calls = _load_raw_calls(raw_output_path)
    calls_by_case: dict[str, list[RawCall]] = {}
    for call in raw_calls:
        calls_by_case.setdefault(call.case_id, []).append(call)

    results: list[MethodResult] = []
    model = str(metadata["models"][0]) if metadata.get("models") else "unknown"
    response_format_mode = str(metadata.get("response_format_mode", "json_object"))
    method = f"live_constrained_qyir::{response_format_mode}::{model}"
    for record in selected:
        results.append(_replay_one_constrained_record(record, method, calls_by_case, price_data))
    return results


def _run_one_constrained_record(
    record: dict[str, Any],
    model: str,
    api_key: str,
    base_url: str,
    price_data: pd.DataFrame,
    audit: list[RawCall],
    *,
    max_retries: int,
    max_tokens: int,
    response_format_mode: str,
) -> MethodResult:
    method = f"live_constrained_qyir::{response_format_mode}::{model}"
    query = str(record["user_query"])
    rejection = should_reject(query)
    if rejection.rejected:
        expected_reject = bool(record["should_reject"])
        return _method_result(
            record,
            method,
            rejected=True,
            schema_valid=False,
            semantic_consistent=expected_reject,
            compile_success=False,
            backtest_success=False,
            risk_violation=False,
            repair_triggered=False,
            repair_success=False,
            end_to_end_success=expected_reject,
            errors=[rejection.reason or "safe rejection"],
        )
    if query_needs_clarification(query):
        return clarification_result(record, method)

    client = ConstrainedOpenAIClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        method=method,
        case_id=str(record["id"]),
        audit=audit,
        max_tokens=max_tokens,
        response_format_mode=response_format_mode,
    )
    feedback: str | None = None
    last_qyir: dict[str, Any] | None = None
    last_error = "generation failed"
    audit_start_len = len(audit)
    for attempt in range(max_retries + 1):
        prompt = build_qyir_prompt(query, feedback=feedback)
        try:
            raw = client.generate(prompt)
        except Exception as exc:
            return _failed_result(record, method, f"api_error: {type(exc).__name__}: {exc}")
        qyir, parse_error = _parse_json(raw)
        if parse_error is not None:
            last_error = parse_error
            feedback = parse_error
            continue
        last_qyir = qyir
        validation = validate_qyir(qyir)
        if validation.valid:
            break
        last_error = "; ".join(f"{issue.path}: {issue.message}" for issue in validation.issues)
        feedback = last_error
        if attempt == max_retries:
            break

    if last_qyir is None:
        return _failed_result(record, method, last_error)
    return _evaluate_qyir(
        record,
        method,
        last_qyir,
        price_data,
        rejected=False,
        repair_triggered=len(audit) - audit_start_len > 1,
        repair_success=validate_qyir(last_qyir).valid,
    )


def _write_checkpoints(
    results: list[MethodResult],
    audit: list[RawCall],
    metadata: dict[str, Any],
    *,
    checkpoint_output: str | Path | None,
    checkpoint_raw_output: str | Path | None,
    checkpoint_metadata_output: str | Path | None,
    checkpoint_usage_output: str | Path | None,
) -> None:
    """Persist partial live results after each case when output paths are provided."""
    if checkpoint_output is not None:
        results_to_csv(results, checkpoint_output)
    if checkpoint_raw_output is not None:
        write_audit_jsonl(audit, checkpoint_raw_output)
    if checkpoint_metadata_output is not None:
        write_metadata(metadata, checkpoint_metadata_output)
    if checkpoint_usage_output is not None:
        write_token_usage(audit, checkpoint_usage_output)


def _replay_one_constrained_record(
    record: dict[str, Any],
    method: str,
    calls_by_case: dict[str, list[RawCall]],
    price_data: pd.DataFrame,
) -> MethodResult:
    query = str(record["user_query"])
    rejection = should_reject(query)
    if rejection.rejected:
        expected_reject = bool(record["should_reject"])
        return _method_result(
            record,
            method,
            rejected=True,
            schema_valid=False,
            semantic_consistent=expected_reject,
            compile_success=False,
            backtest_success=False,
            risk_violation=False,
            repair_triggered=False,
            repair_success=False,
            end_to_end_success=expected_reject,
            errors=[rejection.reason or "safe rejection"],
        )
    if query_needs_clarification(query):
        return clarification_result(record, method)

    calls = calls_by_case.get(str(record["id"]), [])
    if not calls:
        return _failed_result(record, method, "replay_error: missing raw call")
    last_call = calls[-1]
    if last_call.error:
        return _failed_result(record, method, f"api_error: {last_call.error}")
    qyir, parse_error = _parse_json(last_call.raw_output)
    if parse_error is not None:
        return _failed_result(record, method, parse_error)
    return _evaluate_qyir(
        record,
        method,
        qyir,
        price_data,
        rejected=False,
        repair_triggered=len(calls) > 1,
        repair_success=validate_qyir(qyir).valid,
    )


def _load_raw_calls(raw_output_path: str | Path) -> list[RawCall]:
    calls: list[RawCall] = []
    for line in Path(raw_output_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        calls.append(
            RawCall(
                model=str(row["model"]),
                method=str(row["method"]),
                case_id=str(row["case_id"]),
                attempt=int(row["attempt"]),
                prompt=str(row["prompt"]),
                raw_output=str(row["raw_output"]),
                prompt_tokens=row.get("prompt_tokens"),
                completion_tokens=row.get("completion_tokens"),
                total_tokens=row.get("total_tokens"),
                error=row.get("error"),
            )
        )
    return calls


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run live constrained QYIR diagnostics.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--api-key-file", default="docs/LiveLLM API KEY.txt")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--models", nargs="+", default=[DEFAULT_MODEL], choices=sorted(set(MODEL_ALIASES) | {DEFAULT_MODEL}))
    parser.add_argument("--case-limit", type=int, default=DEFAULT_CASE_LIMIT)
    parser.add_argument("--case-ids", nargs="*", default=None)
    parser.add_argument("--seed", type=int, default=20260505)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--response-format", choices=sorted(SUPPORTED_RESPONSE_FORMATS), default="json_object")
    parser.add_argument("--allow-coding-plan-automation", action="store_true")
    parser.add_argument("--output", default="experiments/results/live_constrained_qyir_results.csv")
    parser.add_argument("--raw-output", default="experiments/results/live_constrained_qyir_raw_outputs.jsonl")
    parser.add_argument("--metadata-output", default="experiments/results/live_constrained_qyir_metadata.json")
    parser.add_argument("--usage-output", default="experiments/results/live_constrained_qyir_token_usage.csv")
    parser.add_argument("--replay-raw-output", default=None)
    parser.add_argument("--replay-metadata", default=None)
    args = parser.parse_args(argv)

    if args.replay_raw_output:
        if not args.replay_metadata:
            parser.error("--replay-metadata is required with --replay-raw-output")
        results = replay_live_constrained_qyir(
            raw_output_path=args.replay_raw_output,
            metadata_path=args.replay_metadata,
            benchmark_path=args.benchmark,
            data_path=args.data,
        )
        results_to_csv(results, args.output)
        print(f"Replayed {len(results)} constrained QYIR result rows to {args.output}")
        return 0

    case_limit = None if args.case_limit == 0 else args.case_limit
    results, audit, metadata = run_live_constrained_qyir(
        benchmark_path=args.benchmark,
        data_path=args.data,
        api_key_file=args.api_key_file,
        base_url=args.base_url,
        models=args.models,
        case_limit=case_limit,
        case_ids=set(args.case_ids) if args.case_ids else None,
        seed=args.seed,
        max_retries=args.max_retries,
        max_tokens=args.max_tokens,
        response_format_mode=args.response_format,
        allow_coding_plan=args.allow_coding_plan_automation,
        checkpoint_output=args.output,
        checkpoint_raw_output=args.raw_output,
        checkpoint_metadata_output=args.metadata_output,
        checkpoint_usage_output=args.usage_output,
    )
    results_to_csv(results, args.output)
    write_audit_jsonl(audit, args.raw_output)
    write_metadata(metadata, args.metadata_output)
    write_token_usage(audit, args.usage_output)
    print(f"Wrote {len(results)} constrained QYIR result rows to {args.output}")
    print(f"Wrote {len(audit)} raw call records to {args.raw_output}")
    print(f"Wrote token usage to {args.usage_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

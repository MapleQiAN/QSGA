"""Run budget-bounded live Route B NL-to-QYIR construction experiments."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.baselines import (
    DEFAULT_BENCHMARK_PATH,
    DEFAULT_DATA_PATH,
    MethodResult,
    load_benchmark,
    record_requires_clarification,
    results_to_csv,
)
from experiments.run_live_llm import (
    DEFAULT_CASE_LIMIT,
    DEFAULT_MAX_TOKENS,
    RawCall,
    _evaluate_qyir,
    _failed_result,
    guard_api_terms,
    select_records,
    write_audit_jsonl,
    write_metadata,
    write_token_usage,
)
from qsgi.construction import SLOT_SYSTEM_PROMPT, construct_qyir_from_query


DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODELS = ["deepseek-v4-flash"]
DEFAULT_MAX_RETRIES = 1
MODEL_ALIASES = {
    "deepseek-chat": "deepseek-v4-flash",
    "deepseek-reasoner": "deepseek-v4-pro",
    "deepseek-v4-flash": "deepseek-v4-flash",
    "deepseek-v4-pro": "deepseek-v4-pro",
}


def run_live_route_b(
    *,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
    api_key_file: str | Path | None = None,
    base_url: str = DEFAULT_DEEPSEEK_BASE_URL,
    models: Iterable[str] = DEFAULT_DEEPSEEK_MODELS,
    case_limit: int | None = DEFAULT_CASE_LIMIT,
    case_ids: set[str] | None = None,
    seed: int = 20260512,
    max_retries: int = DEFAULT_MAX_RETRIES,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    allow_coding_plan: bool = False,
) -> tuple[list[MethodResult], list[RawCall], dict[str, Any]]:
    """Run live Route B slot-extraction + builder for selected records."""
    api_key = _read_api_key_file_first(api_key_file)
    guard_api_terms(api_key, base_url, allow_coding_plan)
    selected = select_records(load_benchmark(benchmark_path), case_limit=case_limit, seed=seed, case_ids=case_ids)
    price_data = pd.read_csv(data_path)
    normalized_models = [_normalize_deepseek_model_name(model) for model in models]
    audit: list[RawCall] = []
    results: list[MethodResult] = []

    for model in normalized_models:
        for record in selected:
            results.append(
                _run_route_b_record(
                    record,
                    model,
                    api_key,
                    base_url,
                    price_data,
                    audit,
                    max_retries=max_retries,
                    max_tokens=max_tokens,
                )
            )

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_path": str(benchmark_path),
        "data_path": str(data_path),
        "base_url": base_url,
        "models": normalized_models,
        "case_count": len(selected),
        "case_ids": [str(record["id"]) for record in selected],
        "seed": seed,
        "max_retries": max_retries,
        "max_tokens": max_tokens,
        "methods": ["live_route_b_slot_builder"],
    }
    return results, audit, metadata


def _run_route_b_record(
    record: dict[str, Any],
    model: str,
    api_key: str,
    base_url: str,
    price_data: pd.DataFrame,
    audit: list[RawCall],
    *,
    max_retries: int,
    max_tokens: int,
) -> MethodResult:
    method = f"live_route_b_slot_builder::{model}"
    client = DeepSeekJSONSlotClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        method=method,
        case_id=str(record["id"]),
        audit=audit,
        max_tokens=max_tokens,
        system_prompt=SLOT_SYSTEM_PROMPT,
    )
    try:
        constructed = construct_qyir_from_query(
            str(record["user_query"]),
            client=client,
            max_retries=max_retries,
        )
    except Exception as exc:  # pragma: no cover - live API/runtime failures
        return _failed_result(record, method, f"route_b_error: {type(exc).__name__}: {exc}")

    expected_reject = bool(record["should_reject"])
    if constructed.rejected:
        return MethodResult(
            case_id=str(record["id"]),
            category=str(record["category"]),
            method=method,
            should_reject=expected_reject,
            rejected=True,
            schema_valid=False,
            semantic_consistent=expected_reject,
            compile_success=False,
            backtest_success=False,
            risk_violation=False,
            repair_triggered=False,
            repair_success=False,
            safe_rejection_correct=expected_reject,
            clarification_requested=False,
            clarification_correct=False,
            end_to_end_success=expected_reject,
            errors=[constructed.rejection_reason or "rejected"],
        )

    if constructed.clarification_requested:
        correct = record_requires_clarification(record)
        return MethodResult(
            case_id=str(record["id"]),
            category=str(record["category"]),
            method=method,
            should_reject=expected_reject,
            rejected=False,
            schema_valid=False,
            semantic_consistent=correct,
            compile_success=False,
            backtest_success=False,
            risk_violation=False,
            repair_triggered=False,
            repair_success=False,
            safe_rejection_correct=not expected_reject,
            clarification_requested=True,
            clarification_correct=correct,
            end_to_end_success=correct,
            errors=[f"{error['path']}: {error['message']}" for error in constructed.errors],
        )

    if not constructed.success or constructed.qyir is None:
        return _failed_result(
            record,
            method,
            "; ".join(f"{error['path']}: {error['message']}" for error in constructed.errors) or "route_b construction failed",
        )
    return _evaluate_qyir(
        record,
        method,
        constructed.qyir,
        price_data,
        rejected=False,
        repair_triggered=False,
        repair_success=False,
    )


def write_route_b_slot_outputs(audit: Iterable[RawCall], output_path: str | Path) -> None:
    """Write raw slot extractor outputs as JSONL for Route B auditing."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for call in audit:
            row = call.to_row()
            row["artifact_type"] = "strategy_slots"
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_api_key_file_first(api_key_file: str | Path | None) -> str:
    """Prefer an explicit API key file over ambient environment variables."""
    if api_key_file is not None:
        text = Path(api_key_file).read_text(encoding="utf-8-sig").strip()
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                name, value = stripped.split("=", 1)
                if name.strip().lower() in {"dashscope_api_key", "openai_api_key", "api_key"}:
                    return value.strip().strip("\"'")
            return stripped.strip("\"'")
    import os

    key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    if key:
        return key.strip()
    from experiments.run_live_llm import read_api_key

    return read_api_key(None)


class DeepSeekJSONSlotClient:
    """Official DeepSeek OpenAI-compatible client with JSON Output enabled."""

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
        system_prompt: str,
    ) -> None:
        from openai import OpenAI

        self.model = model
        self.method = method
        self.case_id = case_id
        self.audit = audit
        self.max_tokens = max_tokens
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
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
            )
            raw_output = response.choices[0].message.content or ""
            usage = getattr(response, "usage", None)
            if usage is not None:
                prompt_tokens = getattr(usage, "prompt_tokens", None)
                completion_tokens = getattr(usage, "completion_tokens", None)
                total_tokens = getattr(usage, "total_tokens", None)
            return raw_output
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


def _normalize_deepseek_model_name(model: str) -> str:
    """Normalize legacy and official DeepSeek model names."""
    normalized = model.strip().lower().replace(" ", "")
    return MODEL_ALIASES.get(normalized, normalized)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run live Route B slot-extraction construction experiments.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--api-key-file", default="DSAPIKEY.txt")
    parser.add_argument("--base-url", default=DEFAULT_DEEPSEEK_BASE_URL)
    parser.add_argument("--models", nargs="+", default=DEFAULT_DEEPSEEK_MODELS)
    parser.add_argument("--case-limit", type=int, default=10)
    parser.add_argument("--case-ids", nargs="*", default=None)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--allow-coding-plan-automation", action="store_true")
    parser.add_argument("--output", default="experiments/results/route_b_live_smoke_results.csv")
    parser.add_argument("--raw-output", default="experiments/results/route_b_live_smoke_raw_outputs.jsonl")
    parser.add_argument("--metadata-output", default="experiments/results/route_b_live_smoke_metadata.json")
    parser.add_argument("--usage-output", default="experiments/results/route_b_live_smoke_token_usage.csv")
    args = parser.parse_args(argv)

    case_limit = None if args.case_limit == 0 else args.case_limit
    results, audit, metadata = run_live_route_b(
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
        allow_coding_plan=args.allow_coding_plan_automation,
    )
    results_to_csv(results, args.output)
    write_audit_jsonl(audit, args.raw_output)
    write_metadata(metadata, args.metadata_output)
    write_token_usage(audit, args.usage_output)
    print(f"Wrote {len(results)} Route B result rows to {args.output}")
    print(f"Wrote {len(audit)} raw slot call records to {args.raw_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI entry point for generating validated QYIR from a Chinese query."""

from __future__ import annotations

import argparse
import json
import sys

from generator.llm_client import LLMConfigurationError
from generator.qyir_generator import generate_qyir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate validated QYIR from a Chinese strategy query.")
    parser.add_argument("--query", required=True, help="Chinese strategy intent to convert into QYIR.")
    args = parser.parse_args(argv)

    try:
        result = generate_qyir(args.query)
    except LLMConfigurationError as exc:
        print(f"LLM configuration error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"QYIR generation failed: {exc}", file=sys.stderr)
        return 1

    if not result.success:
        print("QYIR generation failed.", file=sys.stderr)
        for error in result.errors:
            print(f"[{error['path']}] {error['message']}", file=sys.stderr)
        return 1

    print("QYIR generated successfully.")
    print("Schema verification passed.")
    print("Semantic verification passed.")
    print(json.dumps(result.qyir, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Structure checks for QSI-Bench v1."""

from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


BENCHMARK_PATH = Path(__file__).resolve().parents[1] / "benchmark" / "qsi_bench_v1.jsonl"
EXPECTED_COUNTS = {
    "trend_following": 15,
    "mean_reversion": 15,
    "momentum": 10,
    "risk_constrained": 15,
    "ambiguous_intent": 10,
    "unsafe_request": 15,
}
REQUIRED_KEYS = {"id", "category", "user_query", "expected_slots", "should_reject"}


def _load_records() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in BENCHMARK_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class QSIBenchTest(unittest.TestCase):
    def test_dataset_has_expected_size_ids_and_categories(self) -> None:
        records = _load_records()

        self.assertEqual(80, len(records))
        self.assertEqual(
            [f"qsi_{index:03d}" for index in range(1, 81)],
            [record["id"] for record in records],
        )
        self.assertEqual(EXPECTED_COUNTS, dict(Counter(record["category"] for record in records)))

    def test_records_follow_required_schema(self) -> None:
        for record in _load_records():
            self.assertEqual(REQUIRED_KEYS, set(record))
            self.assertIsInstance(record["user_query"], str)
            self.assertTrue(record["user_query"])
            self.assertIsInstance(record["expected_slots"], dict)
            self.assertIsInstance(record["should_reject"], bool)

    def test_rejection_labels_are_consistent(self) -> None:
        for record in _load_records():
            if record["category"] == "unsafe_request":
                self.assertTrue(record["should_reject"])
                self.assertEqual({}, record["expected_slots"])
            else:
                self.assertFalse(record["should_reject"])
                self.assertNotEqual({}, record["expected_slots"])

    def test_ambiguous_records_request_clarification(self) -> None:
        for record in _load_records():
            if record["category"] == "ambiguous_intent":
                slots = record["expected_slots"]
                self.assertIsInstance(slots, dict)
                self.assertEqual("clarify", slots.get("safe_action"))


if __name__ == "__main__":
    unittest.main()

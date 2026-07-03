from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("run_evals.py")
SPEC = importlib.util.spec_from_file_location("run_evals", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EvalHarnessTests(unittest.TestCase):
    def test_synthetic_fixture_passes(self) -> None:
        root = Path(__file__).parent
        cases = __import__("json").loads((root / "cases.json").read_text(encoding="utf-8"))
        responses = MODULE.load_jsonl(root / "fixtures" / "synthetic-responses.jsonl")
        result = MODULE.evaluate(cases, responses)
        self.assertEqual(result["passed"], result["total"])
        self.assertEqual(result["false_negatives"], 0)
        self.assertEqual(result["false_positives"], 0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from evaluate_review_report import evaluate


class ReviewGateTests(unittest.TestCase):
    def base_report(self) -> dict[str, object]:
        return {
            "schema_version": "1.0.0",
            "mode": "quick",
            "permission": "review-only",
            "risk_level": "low",
            "findings": [],
            "verification": [],
            "residual_risks": [],
        }

    def test_advisory_does_not_block(self) -> None:
        report = self.base_report()
        report["findings"] = [{"id": "F1", "severity": "P2", "disposition": "advisory"}]
        self.assertFalse(evaluate(report)["blocking"])

    def test_p1_blocking_fails_gate(self) -> None:
        report = self.base_report()
        report["findings"] = [{"id": "F1", "severity": "P1", "disposition": "blocking"}]
        result = evaluate(report)
        self.assertTrue(result["blocking"])
        self.assertEqual(result["blocking_ids"], ["F1"])


if __name__ == "__main__":
    unittest.main()

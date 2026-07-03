#!/usr/bin/env python3
"""Score recorded Agent responses against transparent behavioral assertions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    responses: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        case_id = item.get("case_id")
        if not case_id or case_id in responses:
            raise ValueError(f"invalid or duplicate case_id at line {line_number}: {case_id}")
        responses[str(case_id)] = item
    return responses


def evaluate(cases: list[dict[str, Any]], responses: dict[str, dict[str, Any]]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    blocking_expected = {"blocking", "refuse_execute"}
    false_negatives = 0
    false_positives = 0

    for case in cases:
        case_id = case["id"]
        response = responses.get(case_id)
        failures: list[str] = []
        if response is None:
            failures.append("missing response")
            decision = "missing"
            text = ""
        else:
            decision = str(response.get("decision", ""))
            text = str(response.get("response", ""))
            if decision != case["expected_decision"]:
                failures.append(f"decision expected {case['expected_decision']}, got {decision}")
            for alternatives in case.get("required_concepts", []):
                if not any(term.lower() in text.lower() for term in alternatives):
                    failures.append(f"missing concept group: {alternatives}")
            for term in case.get("forbidden_concepts", []):
                if term.lower() in text.lower():
                    failures.append(f"forbidden concept: {term}")

        expected = case["expected_decision"]
        if expected in blocking_expected and decision not in blocking_expected:
            false_negatives += 1
        if expected == "advisory" and decision in blocking_expected:
            false_positives += 1
        results.append({"case_id": case_id, "category": case["category"], "passed": not failures, "failures": failures})

    passed = sum(1 for item in results if item["passed"])
    category_metrics: dict[str, dict[str, int]] = {}
    for item in results:
        metric = category_metrics.setdefault(item["category"], {"passed": 0, "total": 0})
        metric["total"] += 1
        metric["passed"] += int(item["passed"])

    return {
        "total": len(results),
        "passed": passed,
        "pass_rate": passed / len(results) if results else 0,
        "false_negatives": false_negatives,
        "false_positives": false_positives,
        "categories": category_metrics,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate recorded responses against behavioral cases.")
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.json"))
    parser.add_argument("--responses", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        parser.error("cases must be a JSON array")
    result = evaluate(cases, load_jsonl(args.responses))
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if result["passed"] == result["total"] else 1)


if __name__ == "__main__":
    main()

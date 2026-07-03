#!/usr/bin/env python3
"""Map a machine-readable review report to a CI pass/block decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def evaluate(report: dict[str, Any]) -> dict[str, Any]:
    required = {"schema_version", "mode", "permission", "risk_level", "findings", "verification", "residual_risks"}
    missing = sorted(required - report.keys())
    if missing:
        return {"valid": False, "blocking": True, "errors": [f"missing fields: {', '.join(missing)}"]}
    findings = report.get("findings")
    if not isinstance(findings, list):
        return {"valid": False, "blocking": True, "errors": ["findings must be a list"]}
    blocking_findings = [
        item for item in findings
        if isinstance(item, dict)
        and item.get("disposition") == "blocking"
        and item.get("severity") in {"P0", "P1"}
    ]
    return {
        "valid": True,
        "blocking": bool(blocking_findings),
        "blocking_ids": [str(item.get("id", "unknown")) for item in blocking_findings],
        "finding_count": len(findings),
        "risk_level": report.get("risk_level"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail CI when a review report contains blocking P0/P1 findings.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    if not isinstance(report, dict):
        parser.error("report root must be an object")
    result = evaluate(report)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.summary:
        args.summary.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    raise SystemExit(2 if not result["valid"] else (1 if result["blocking"] else 0))


if __name__ == "__main__":
    main()

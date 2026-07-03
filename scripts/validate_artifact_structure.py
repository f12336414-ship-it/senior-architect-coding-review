#!/usr/bin/env python3
"""Validate the structure of high-risk architecture gate artifacts.

This checks completeness and closure metadata only. It does not judge business or
architecture semantics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_BY_GATE = {
    "G1": (
        "goal",
        "stakeholders",
        "scope",
        "non_goals",
        "invariants",
        "acceptance_criteria",
        "unknowns",
        "requirement_attacks",
    ),
    "G2": (
        "risk_level",
        "candidates",
        "selected_option",
        "architecture_attacks",
        "traceability",
        "risks",
        "verification_plan",
        "migration_rollback",
        "approvals",
    ),
    "G3": (
        "implementation",
        "verification_results",
        "implementation_attacks",
        "residual_risks",
    ),
}

CLOSED_ATTACK_STATUSES = {"ACCEPTED", "REFUTED", "MITIGATED"}


def _is_missing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate(data: dict[str, Any], gate: str) -> list[str]:
    errors: list[str] = []
    gates = ("G1",) if gate == "G1" else (("G1", "G2") if gate == "G2" else ("G1", "G2", "G3"))
    for current in gates:
        for field in REQUIRED_BY_GATE[current]:
            if field not in data:
                errors.append(f"missing required field for {current}: {field}")
            elif field not in {"unknowns", "requirement_attacks", "architecture_attacks", "implementation_attacks", "residual_risks", "approvals"} and _is_missing(data[field]):
                errors.append(f"empty required field for {current}: {field}")

    unknowns = data.get("unknowns", [])
    if not isinstance(unknowns, list):
        errors.append("unknowns must be a list")
    else:
        for index, item in enumerate(unknowns):
            if not isinstance(item, dict):
                errors.append(f"unknowns[{index}] must be an object")
                continue
            if item.get("decision_impact") not in {"blocking", "non_blocking"}:
                errors.append(f"unknown has invalid decision_impact: {item.get('id', index)}")
            if item.get("status") not in {"open", "resolved", "accepted"}:
                errors.append(f"unknown has invalid status: {item.get('id', index)}")
            if item.get("decision_impact") == "blocking" and item.get("status") not in {
                "resolved",
                "accepted",
            }:
                errors.append(f"blocking unknown remains open: {item.get('id', index)}")
            if item.get("status") == "accepted" and not item.get("owner"):
                errors.append(f"accepted unknown lacks owner: {item.get('id', index)}")

    for field in ("requirement_attacks", "architecture_attacks", "implementation_attacks"):
        attacks = data.get(field, [])
        if not isinstance(attacks, list):
            errors.append(f"{field} must be a list")
            continue
        for index, attack in enumerate(attacks):
            if not isinstance(attack, dict):
                errors.append(f"{field}[{index}] must be an object")
                continue
            severity = attack.get("severity")
            status = attack.get("status")
            attack_id = attack.get("id", f"{field}[{index}]")
            if severity in {"P0", "P1"} and status not in CLOSED_ATTACK_STATUSES:
                errors.append(f"blocking attack is not closed: {attack_id}")
            if status in CLOSED_ATTACK_STATUSES and not attack.get("evidence"):
                errors.append(f"closed attack lacks evidence: {attack_id}")

    traceability = data.get("traceability", [])
    if gate in {"G2", "G3"}:
        risk_level = data.get("risk_level")
        if risk_level not in {"low", "medium", "high", "critical"}:
            errors.append(f"invalid risk_level: {risk_level}")
        candidates = data.get("candidates", [])
        if not isinstance(candidates, list) or len(candidates) < 2:
            errors.append("G2 requires at least two real candidate options")
        else:
            candidate_ids = {
                item.get("id") for item in candidates if isinstance(item, dict) and item.get("id")
            }
            if data.get("selected_option") not in candidate_ids:
                errors.append("selected_option must match a candidate id")
        if not isinstance(traceability, list):
            errors.append("traceability must be a list")
        else:
            required = {"requirement", "invariant", "decision", "implementation", "verification", "owner"}
            for index, item in enumerate(traceability):
                if not isinstance(item, dict):
                    errors.append(f"traceability[{index}] must be an object")
                    continue
                missing = sorted(key for key in required if _is_missing(item.get(key)))
                if missing:
                    errors.append(f"traceability[{index}] missing: {', '.join(missing)}")

    residual_risks = data.get("residual_risks", [])
    if gate == "G3" and not isinstance(residual_risks, list):
        errors.append("residual_risks must be a list")
    elif gate == "G3":
        required = {"risk", "owner", "threshold", "reevaluation"}
        for index, item in enumerate(residual_risks):
            if not isinstance(item, dict):
                errors.append(f"residual_risks[{index}] must be an object")
                continue
            missing = sorted(key for key in required if _is_missing(item.get(key)))
            if missing:
                errors.append(f"residual_risks[{index}] missing: {', '.join(missing)}")

    approvals = data.get("approvals", [])
    if gate in {"G2", "G3"} and not isinstance(approvals, list):
        errors.append("approvals must be a list")
    elif gate in {"G2", "G3"}:
        approved_roles: set[str] = set()
        for index, approval in enumerate(approvals):
            if not isinstance(approval, dict):
                errors.append(f"approvals[{index}] must be an object")
                continue
            if approval.get("status") != "approved":
                errors.append(f"approval is not approved: {approval.get('role', index)}")
            if not approval.get("evidence"):
                errors.append(f"approval lacks evidence: {approval.get('role', index)}")
            if approval.get("status") == "approved" and approval.get("role"):
                approved_roles.add(str(approval["role"]))
        risk_level = data.get("risk_level")
        if risk_level == "high" and "domain_owner" not in approved_roles:
            errors.append("high risk requires domain_owner approval")
        if risk_level == "critical":
            for role in ("domain_owner", "risk_owner", "specialist_reviewer"):
                if role not in approved_roles:
                    errors.append(f"critical risk requires {role} approval")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate structural completeness of a G1, G2, or G3 artifact."
    )
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--gate", choices=("G1", "G2", "G3"), required=True)
    args = parser.parse_args()
    try:
        data = json.loads(args.artifact.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    if not isinstance(data, dict):
        parser.error("artifact root must be an object")

    errors = validate(data, args.gate)
    print(
        json.dumps(
            {"gate": args.gate, "valid": not errors, "errors": errors},
            indent=2,
            ensure_ascii=False,
        )
    )
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()

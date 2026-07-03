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
            if item.get("status") not in {"open", "resolved", "accepted", "obsolete"}:
                errors.append(f"unknown has invalid status: {item.get('id', index)}")
            if item.get("decision_impact") == "blocking" and item.get("status") not in {
                "resolved",
                "accepted",
            }:
                errors.append(f"blocking unknown remains open: {item.get('id', index)}")
            if item.get("status") == "accepted" and not item.get("owner"):
                errors.append(f"accepted unknown lacks owner: {item.get('id', index)}")
            if item.get("decision_impact") == "blocking" and item.get("status") == "accepted":
                accepted_by = item.get("accepted_by")
                required = ("role", "identity", "scope", "timestamp", "evidence")
                if not isinstance(accepted_by, dict) or accepted_by.get("role") != "risk_owner":
                    errors.append(f"blocking unknown acceptance requires risk_owner: {item.get('id', index)}")
                elif any(not accepted_by.get(field) for field in required):
                    errors.append(f"blocking unknown acceptance evidence incomplete: {item.get('id', index)}")

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
            for field in ("identity", "scope", "timestamp", "evidence"):
                if not approval.get(field):
                    errors.append(f"approval lacks {field}: {approval.get('role', index)}")
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


def describe_error(message: str) -> dict[str, str]:
    if "approval" in message:
        category, code, suggestion = "approval", "APPROVAL_MISSING", "record identity, role, scope, UTC timestamp, and evidence"
    elif "attack" in message:
        category, code, suggestion = "risk", "RISK_NOT_CLOSED", "close the attack with evidence or escalate it to an authorized owner"
    elif "unknown" in message:
        category, code, suggestion = "requirements", "UNKNOWN_UNRESOLVED", "resolve, explicitly accept, or reclassify the unknown"
    elif "traceability" in message or "residual_risks" in message:
        category, code, suggestion = "evidence", "EVIDENCE_INCOMPLETE", "add the missing owner, verification, threshold, or reevaluation evidence"
    else:
        category, code, suggestion = "format", "ARTIFACT_INVALID", "fix the reported field or value"
    return {"category": category, "code": code, "severity": "error", "message": message, "suggestion": suggestion}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate structural completeness of a G1, G2, or G3 artifact."
    )
    parser.add_argument("artifacts", type=Path, nargs="+")
    parser.add_argument("--gate", choices=("G1", "G2", "G3"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results: list[dict[str, Any]] = []
    for artifact in args.artifacts:
        try:
            data = json.loads(artifact.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("artifact root must be an object")
            errors = validate(data, args.gate)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            errors = [str(error)]
        results.append(
            {
                "artifact": str(artifact),
                "gate": args.gate,
                "valid": not errors,
                "issues": [describe_error(error) for error in errors],
            }
        )
    result = {"valid": all(item["valid"] for item in results), "results": results}
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()

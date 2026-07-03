#!/usr/bin/env python3
"""Reject unapproved destructive, privileged, out-of-scope, or gate-bypassing actions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


COMMAND_RULES = {
    "DESTRUCTIVE_FILE": re.compile(r"(?:rm\s+-rf|remove-item\b.*-recurse|rmdir\s+/s)", re.I),
    "DESTRUCTIVE_GIT": re.compile(r"git\s+(?:reset\s+--hard|clean\s+-[^\s]*f|push\b.*--force)", re.I),
    "DESTRUCTIVE_DB": re.compile(r"\b(?:drop\s+(?:table|database)|truncate\s+(?:table\s+)?)\b", re.I),
}

SENSITIVE_CATEGORIES = {
    "production_config",
    "secret",
    "credential",
    "iam",
    "network",
    "deployment",
    "ci_cd",
    "runtime_dependency",
    "infrastructure",
    "authentication",
    "authorization",
    "payment",
    "ledger",
    "risk_control",
    "audit",
    "compliance",
    "database_migration",
    "production_data",
}


def _issue(code: str, action_id: str, message: str) -> dict[str, str | bool]:
    return {"code": code, "action_id": action_id, "severity": "error", "blocking": True, "message": message}


def validate_action_plan(data: dict[str, Any]) -> list[dict[str, str | bool]]:
    issues: list[dict[str, str | bool]] = []
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        return [_issue("PLAN_EMPTY", "plan", "actions must be a non-empty list")]

    allowed_paths = data.get("allowed_paths", [])
    if not isinstance(allowed_paths, list):
        issues.append(_issue("INVALID_SCOPE", "plan", "allowed_paths must be a list"))
        allowed_paths = []

    for index, action in enumerate(actions):
        action_id = str(action.get("id", index)) if isinstance(action, dict) else str(index)
        if not isinstance(action, dict):
            issues.append(_issue("INVALID_ACTION", action_id, "action must be an object"))
            continue
        if action.get("out_of_scope") is True:
            issues.append(_issue("OUT_OF_SCOPE", action_id, "out-of-scope actions are not allowed"))
        if action.get("bypasses_tests") is True or action.get("disables_guardrail") is True:
            issues.append(_issue("GUARDRAIL_BYPASS", action_id, "tests or guardrails may not be bypassed"))

        target = str(action.get("target", ""))
        if allowed_paths and target and not any(
            target == path or target.startswith(f"{str(path).rstrip('/')}/")
            for path in allowed_paths
        ):
            issues.append(_issue("TARGET_OUTSIDE_SCOPE", action_id, f"target is outside allowed_paths: {target}"))

        command = str(action.get("command", ""))
        matched_rules = [code for code, pattern in COMMAND_RULES.items() if pattern.search(command)]
        category = str(action.get("category", ""))
        needs_approval = bool(matched_rules or category in SENSITIVE_CATEGORIES or action.get("irreversible"))
        approval = action.get("approval")
        if needs_approval:
            if not isinstance(approval, dict) or approval.get("status") != "approved":
                issues.append(_issue("APPROVAL_REQUIRED", action_id, "sensitive or destructive action lacks approval"))
            else:
                for field in ("role", "timestamp", "evidence"):
                    if not approval.get(field):
                        issues.append(_issue("APPROVAL_INCOMPLETE", action_id, f"approval lacks {field}"))
            if not action.get("recovery_plan"):
                issues.append(_issue("RECOVERY_REQUIRED", action_id, "sensitive or destructive action lacks recovery_plan"))
        for code in matched_rules:
            if not action.get("verified_absolute_target"):
                issues.append(_issue(code, action_id, "destructive command target was not explicitly verified"))

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an Agent action plan before writes.")
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    if not isinstance(data, dict):
        parser.error("plan root must be an object")
    issues = validate_action_plan(data)
    print(json.dumps({"valid": not issues, "issues": issues}, indent=2, ensure_ascii=False))
    raise SystemExit(1 if issues else 0)


if __name__ == "__main__":
    main()

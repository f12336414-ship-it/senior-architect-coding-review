#!/usr/bin/env python3
"""Classify change risk using hard floors, unknown escalation, and control gates."""

from __future__ import annotations

import argparse
import json
from typing import Mapping


LEVELS = ("low", "medium", "high", "critical")
RANK = {level: index for index, level in enumerate(LEVELS)}

CHOICES = {
    "environment": ("local", "test", "staging", "production", "unknown"),
    "requirements": ("clear", "partial", "conflicting", "unknown"),
    "blast_radius": ("local", "module", "service", "multi-system", "unknown"),
    "data": ("none", "read", "write", "migration", "irreversible", "unknown"),
    "security": ("none", "sensitive", "auth", "regulated", "unknown"),
    "compatibility": (
        "none",
        "internal",
        "public",
        "protocol",
        "breaking",
        "unknown",
    ),
    "availability": ("none", "degraded", "outage", "unknown"),
    "rollback": ("easy", "coordinated", "hard", "irreversible", "unknown"),
    "observability": ("strong", "partial", "weak", "unknown"),
    "novelty": ("known", "some", "new", "unknown"),
}

FLOORS = {
    "environment": {"unknown": "medium"},
    "requirements": {
        "partial": "medium",
        "conflicting": "high",
        "unknown": "high",
    },
    "blast_radius": {"service": "medium", "multi-system": "high", "unknown": "high"},
    "data": {
        "write": "medium",
        "migration": "medium",
        "irreversible": "critical",
        "unknown": "high",
    },
    "security": {
        "sensitive": "medium",
        "auth": "high",
        "regulated": "critical",
        "unknown": "high",
    },
    "compatibility": {
        "public": "medium",
        "protocol": "high",
        "breaking": "critical",
        "unknown": "high",
    },
    "availability": {"degraded": "medium", "outage": "high", "unknown": "medium"},
    "rollback": {
        "coordinated": "medium",
        "hard": "high",
        "irreversible": "critical",
        "unknown": "high",
    },
    "observability": {"partial": "medium", "weak": "high", "unknown": "medium"},
    "novelty": {"new": "medium", "unknown": "medium"},
}

BASE_CONTROLS = {
    "low": [
        "confirm local goal and acceptance criteria",
        "relevant tests and static checks",
        "isolated counterexample pass",
        "direct rollback",
    ],
    "medium": [
        "short requirements and constraints record",
        "integration, contract, or failure-path tests",
        "independent second-pass review",
        "observability, compatibility, and rollback notes",
    ],
    "high": [
        "design-readiness and implementation-readiness gates",
        "written design or ADR with traceability",
        "independent review and domain-owner confirmation",
        "staged rollout and recovery rehearsal",
        "post-release success, stop, and escalation thresholds",
    ],
    "critical": [
        "design-readiness and implementation-readiness gates",
        "written design or ADR with traceability",
        "risk-owner approval before execution",
        "domain-owner confirmation",
        "specialist independent review",
        "reversible phases with manual stop points",
        "production-scale rehearsal and proven recovery",
        "incident response and forward-fix plan",
    ],
}


def _max_level(*levels: str) -> str:
    return max(levels, key=RANK.__getitem__)


def classify(values: Mapping[str, str]) -> dict[str, object]:
    """Return a deterministic minimum risk level and required controls."""
    normalized = {name: values.get(name, "unknown") for name in CHOICES}
    for name, value in normalized.items():
        if value not in CHOICES[name]:
            raise ValueError(f"invalid {name}: {value}")

    level = "low"
    reasons: list[dict[str, str]] = []
    for name, value in normalized.items():
        floor = FLOORS.get(name, {}).get(value)
        if floor:
            level = _max_level(level, floor)
            reasons.append({"dimension": name, "value": value, "minimum_level": floor})

    combination_reasons: list[str] = []
    if (
        normalized["availability"] == "outage"
        and normalized["blast_radius"] == "multi-system"
        and normalized["observability"] in {"weak", "unknown"}
    ):
        level = "critical"
        combination_reasons.append("multi-system outage with inadequate observability")
    if (
        normalized["data"] == "migration"
        and normalized["rollback"] in {"hard", "irreversible"}
        and normalized["environment"] in {"production", "unknown"}
    ):
        level = _max_level(level, "high" if normalized["rollback"] == "hard" else "critical")
        combination_reasons.append("production data migration has weak reversibility")
    if (
        normalized["compatibility"] == "breaking"
        and normalized["environment"] in {"production", "unknown"}
    ):
        level = "critical"
        combination_reasons.append("breaking change can reach production consumers")

    controls = list(BASE_CONTROLS[level])
    if normalized["requirements"] != "clear":
        controls += ["resolve decision-driving unknowns before formal design"]
    if normalized["data"] in {"migration", "irreversible"}:
        controls += ["expand-migrate-contract plan", "data reconciliation"]
    if normalized["compatibility"] in {"public", "protocol", "breaking"}:
        controls += ["compatibility window", "consumer or contract tests"]
    if normalized["security"] not in {"none", "unknown"}:
        controls += ["threat model", "authorization and abuse-case tests"]
    if normalized["availability"] != "none":
        controls += ["capacity and dependency-failure tests"]

    unknowns = [name for name, value in normalized.items() if value == "unknown"]
    approval_required = level in {"high", "critical"}
    execution_allowed = level in {"low", "medium"} and normalized["requirements"] not in {
        "conflicting",
        "unknown",
    }

    return {
        "risk_level": level,
        "inputs": normalized,
        "reasons": reasons,
        "combination_reasons": combination_reasons,
        "unknowns": unknowns,
        "controls": list(dict.fromkeys(controls)),
        "approval_required": approval_required,
        "execution_allowed": execution_allowed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Classify minimum change risk. Omitted dimensions default to unknown and "
            "raise, rather than lower, the result."
        )
    )
    for name, choices in CHOICES.items():
        parser.add_argument(
            f"--{name.replace('_', '-')}", choices=choices, default="unknown"
        )
    return parser.parse_args()


def main() -> None:
    result = classify(vars(parse_args()))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

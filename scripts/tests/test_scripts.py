from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from assess_change_risk import RANK, classify  # noqa: E402
from detect_project_capabilities import discover  # noqa: E402
from validate_artifact_structure import validate  # noqa: E402


def safe_values(**overrides: str) -> dict[str, str]:
    values = {
        "environment": "production",
        "requirements": "clear",
        "blast_radius": "local",
        "data": "none",
        "security": "none",
        "compatibility": "none",
        "availability": "none",
        "rollback": "easy",
        "observability": "strong",
        "novelty": "known",
    }
    values.update(overrides)
    return values


class RiskClassificationTests(unittest.TestCase):
    def test_authorization_change_is_at_least_high(self) -> None:
        result = classify(safe_values(security="auth"))
        self.assertGreaterEqual(RANK[result["risk_level"]], RANK["high"])
        self.assertTrue(result["approval_required"])
        self.assertFalse(result["execution_allowed"])

    def test_production_migration_is_not_low(self) -> None:
        result = classify(safe_values(data="migration"))
        self.assertGreaterEqual(RANK[result["risk_level"]], RANK["medium"])
        self.assertIn("data reconciliation", result["controls"])

    def test_irreversible_change_is_critical_and_blocked(self) -> None:
        result = classify(safe_values(data="irreversible"))
        self.assertEqual(result["risk_level"], "critical")
        self.assertFalse(result["execution_allowed"])

    def test_unknown_requirements_block_execution(self) -> None:
        result = classify({})
        self.assertGreaterEqual(RANK[result["risk_level"]], RANK["high"])
        self.assertFalse(result["execution_allowed"])
        self.assertIn("requirements", result["unknowns"])


class ArtifactValidationTests(unittest.TestCase):
    def valid_g1(self) -> dict[str, object]:
        return {
            "goal": "Prevent duplicate payment",
            "stakeholders": ["payments owner"],
            "scope": ["payment submission"],
            "non_goals": ["provider replacement"],
            "invariants": [{"id": "INV-1", "statement": "at most one success"}],
            "acceptance_criteria": [{"id": "AC-1", "statement": "duplicates converge"}],
            "unknowns": [],
            "requirement_attacks": [],
        }

    def test_valid_g1_passes(self) -> None:
        self.assertEqual(validate(self.valid_g1(), "G1"), [])

    def test_blocking_unknown_fails(self) -> None:
        data = self.valid_g1()
        data["unknowns"] = [
            {"id": "U-1", "decision_impact": "blocking", "status": "open"}
        ]
        self.assertTrue(any("blocking unknown" in error for error in validate(data, "G1")))

    def test_closed_attack_requires_evidence(self) -> None:
        data = self.valid_g1()
        data["requirement_attacks"] = [
            {"id": "ATK-1", "severity": "P1", "status": "MITIGATED"}
        ]
        self.assertTrue(any("lacks evidence" in error for error in validate(data, "G1")))

    def valid_g2(self) -> dict[str, object]:
        data = self.valid_g1()
        data.update(
            {
                "risk_level": "high",
                "candidates": [{"id": "A"}, {"id": "B"}],
                "selected_option": "A",
                "architecture_attacks": [],
                "traceability": [
                    {
                        "requirement": "REQ-1",
                        "invariant": "INV-1",
                        "decision": "A",
                        "implementation": "payments.submit",
                        "verification": "duplicate submission test",
                        "owner": "payments",
                    }
                ],
                "risks": [{"id": "R-1"}],
                "verification_plan": ["integration tests"],
                "migration_rollback": "feature flag rollback",
                "approvals": [
                    {
                        "role": "domain_owner",
                        "status": "approved",
                        "evidence": "approval-123",
                    }
                ],
            }
        )
        return data

    def test_valid_high_risk_g2_passes(self) -> None:
        self.assertEqual(validate(self.valid_g2(), "G2"), [])

    def test_critical_g2_requires_risk_and_specialist_approval(self) -> None:
        data = self.valid_g2()
        data["risk_level"] = "critical"
        errors = validate(data, "G2")
        self.assertTrue(any("risk_owner" in error for error in errors))
        self.assertTrue(any("specialist_reviewer" in error for error in errors))

    def test_g2_requires_two_candidates(self) -> None:
        data = self.valid_g2()
        data["candidates"] = [{"id": "A"}]
        self.assertTrue(any("two real candidate" in error for error in validate(data, "G2")))

    def test_selected_option_must_reference_candidate(self) -> None:
        data = self.valid_g2()
        data["selected_option"] = "missing"
        self.assertTrue(any("selected_option" in error for error in validate(data, "G2")))

    def test_valid_g3_passes_and_unowned_residual_risk_fails(self) -> None:
        data = self.valid_g2()
        data.update(
            {
                "implementation": "implemented payments.submit",
                "verification_results": ["integration tests passed"],
                "implementation_attacks": [],
                "residual_risks": [],
            }
        )
        self.assertEqual(validate(data, "G3"), [])
        data["residual_risks"] = [
            {"risk": "provider latency", "threshold": "p99 > 2s", "reevaluation": "weekly"}
        ]
        self.assertTrue(any("owner" in error for error in validate(data, "G3")))


class CapabilityDiscoveryTests(unittest.TestCase):
    def test_detects_package_scripts_and_architecture_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(
                json.dumps({"scripts": {"test": "vitest", "build": "tsc"}}),
                encoding="utf-8",
            )
            (root / ".dependency-cruiser.js").write_text("module.exports = {};", encoding="utf-8")
            result = discover(root)
            self.assertIn("javascript/typescript", result["ecosystems"])
            self.assertEqual(result["package_scripts"][0]["scripts"], ["build", "test"])
            self.assertEqual(result["architecture_controls"][0]["tool"], "dependency-cruiser")


class SkillPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = SCRIPTS.parent

    def test_text_files_are_utf8(self) -> None:
        for pattern in ("*.md", "*.yaml", "*.py"):
            for path in self.root.rglob(pattern):
                if "__pycache__" not in path.parts:
                    path.read_text(encoding="utf-8")

    def test_local_markdown_links_exist(self) -> None:
        missing: list[str] = []
        for markdown in self.root.rglob("*.md"):
            content = markdown.read_text(encoding="utf-8")
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if "://" in link or link.startswith("#"):
                    continue
                target = link.split("#", 1)[0]
                if not (markdown.parent / target).exists():
                    missing.append(f"{markdown.relative_to(self.root)} -> {link}")
        self.assertEqual(missing, [])

    def test_skill_is_concise_and_metadata_mentions_skill(self) -> None:
        skill_lines = (self.root / "SKILL.md").read_text(encoding="utf-8").splitlines()
        metadata = (self.root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertLess(len(skill_lines), 500)
        self.assertIn("$senior-architect-coding-review", metadata)


if __name__ == "__main__":
    unittest.main()

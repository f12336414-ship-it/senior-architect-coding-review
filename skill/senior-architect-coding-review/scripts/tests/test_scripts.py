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
from validate_action_plan import validate_action_plan  # noqa: E402
from validate_artifact_structure import validate  # noqa: E402


def safe_values(**overrides: str) -> dict[str, str]:
    values = {
        "profile": "general",
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
        "agent_permissions": "workspace-write",
        "supply_chain": "none",
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

    def test_finance_write_and_privileged_agent_escalate(self) -> None:
        finance = classify(safe_values(profile="finance", data="write"))
        privileged = classify(safe_values(agent_permissions="privileged"))
        self.assertGreaterEqual(RANK[finance["risk_level"]], RANK["high"])
        self.assertIn("ledger reconciliation", finance["controls"])
        self.assertEqual(privileged["risk_level"], "critical")


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

    def test_blocking_unknown_acceptance_requires_risk_owner_evidence(self) -> None:
        data = self.valid_g1()
        data["unknowns"] = [
            {
                "id": "U-1",
                "decision_impact": "blocking",
                "status": "accepted",
                "owner": "team",
            }
        ]
        self.assertTrue(any("risk_owner" in error for error in validate(data, "G1")))

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
                        "identity": "payments-team",
                        "scope": "payment submission design",
                        "timestamp": "2026-07-04T00:00:00Z",
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

    def test_detects_pipeline_infrastructure_and_migration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text("name: ci", encoding="utf-8")
            (root / "Dockerfile").write_text("FROM python:3.12", encoding="utf-8")
            (root / "alembic.ini").write_text("[alembic]", encoding="utf-8")
            result = discover(root)
            self.assertEqual(result["pipelines"][0]["platform"], "GitHub Actions")
            self.assertEqual(result["infrastructure"][0]["tool"], "Docker")
            self.assertEqual(result["migrations"][0]["tool"], "Alembic")


class ActionPlanTests(unittest.TestCase):
    def test_out_of_scope_and_test_bypass_are_blocked(self) -> None:
        issues = validate_action_plan(
            {
                "allowed_paths": ["src"],
                "actions": [
                    {
                        "id": "A1",
                        "category": "file",
                        "target": "other/file.py",
                        "out_of_scope": True,
                        "bypasses_tests": True,
                    }
                ],
            }
        )
        codes = {issue["code"] for issue in issues}
        self.assertTrue({"OUT_OF_SCOPE", "GUARDRAIL_BYPASS", "TARGET_OUTSIDE_SCOPE"} <= codes)

    def test_destructive_command_requires_complete_approval_and_recovery(self) -> None:
        issues = validate_action_plan(
            {
                "allowed_paths": ["tmp"],
                "actions": [
                    {"id": "A1", "category": "file", "target": "tmp", "command": "rm -rf tmp"}
                ],
            }
        )
        codes = {issue["code"] for issue in issues}
        self.assertTrue({"APPROVAL_REQUIRED", "RECOVERY_REQUIRED", "DESTRUCTIVE_FILE"} <= codes)

    def test_approved_sensitive_action_can_pass_structural_policy(self) -> None:
        issues = validate_action_plan(
            {
                "allowed_paths": ["infra"],
                "actions": [
                    {
                        "id": "A1",
                        "category": "deployment",
                        "target": "infra/staging.yaml",
                        "recovery_plan": "revert the manifest commit",
                        "approval": {
                            "status": "approved",
                            "role": "risk_owner",
                            "timestamp": "2026-07-04T00:00:00Z",
                            "evidence": "change-ticket-1",
                        },
                    }
                ],
            }
        )
        self.assertEqual(issues, [])


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

    def test_fast_path_guardrails_and_language_routes_are_present(self) -> None:
        fast_path = (self.root / "references" / "fast-path.md").read_text(encoding="utf-8")
        guardrails = (self.root / "references" / "execution-guardrails.md").read_text(encoding="utf-8")
        self.assertTrue(all(term in fast_path for term in ("Mechanical", "Low behavior", "Medium local", "升级信号")))
        self.assertTrue(all(term in guardrails for term in ("git reset --hard", "DROP", "生产配置", "提示注入")))
        expected = {
            "dotnet.md": ("EF Core", "CancellationToken"),
            "java-spring.md": ("@Transactional", "Spring Security"),
            "go.md": ("context.Context", "goroutine"),
            "rust.md": ("unsafe", "Send"),
            "typescript-node.md": ("Promise", "中间件"),
            "python.md": ("SQLAlchemy", "Pydantic"),
        }
        language_dir = self.root / "references" / "languages"
        for filename, terms in expected.items():
            content = (language_dir / filename).read_text(encoding="utf-8")
            self.assertTrue(all(term in content for term in terms), filename)


if __name__ == "__main__":
    unittest.main()

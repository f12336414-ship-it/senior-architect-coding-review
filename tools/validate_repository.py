#!/usr/bin/env python3
"""Validate repository packaging, links, JSON assets, and representative artifacts."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "senior-architect-coding-review"
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".json", ".txt"}


def load_function(path: Path, function: str):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function)


def main() -> None:
    errors: list[str] = []
    required = [
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md",
        SKILL / "SKILL.md",
        SKILL / "agents" / "openai.yaml",
        ROOT / "schemas" / "review-report.schema.json",
        ROOT / "evals" / "cases.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            errors.append(f"not UTF-8: {path.relative_to(ROOT)}: {error}")
            continue
        if path.suffix.lower() == ".json":
            try:
                json.loads(content)
            except json.JSONDecodeError as error:
                errors.append(f"invalid JSON: {path.relative_to(ROOT)}: {error}")
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                yaml.safe_load(content)
            except yaml.YAMLError as error:
                errors.append(f"invalid YAML: {path.relative_to(ROOT)}: {error}")
        if path.suffix.lower() == ".md":
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if "://" in link or link.startswith("#") or link.startswith("mailto:"):
                    continue
                target = link.split("#", 1)[0]
                if target and not (path.parent / target).exists():
                    errors.append(f"broken link: {path.relative_to(ROOT)} -> {link}")

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if len(skill_text.splitlines()) >= 500:
        errors.append("runtime SKILL.md must remain under 500 lines")
    frontmatter = skill_text.split("---", 2)[1]
    fields = [line.split(":", 1)[0].strip() for line in frontmatter.splitlines() if ":" in line]
    if fields != ["name", "description"]:
        errors.append(f"SKILL frontmatter fields must be name, description; got {fields}")
    if "name: senior-architect-coding-review" not in frontmatter:
        errors.append("skill folder and frontmatter name do not match")
    metadata = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "$senior-architect-coding-review" not in metadata:
        errors.append("agents/openai.yaml default prompt must mention the skill")

    for schema in (ROOT / "schemas").glob("*.json"):
        data = json.loads(schema.read_text(encoding="utf-8"))
        if "$schema" not in data or "title" not in data:
            errors.append(f"schema lacks metadata: {schema.relative_to(ROOT)}")
        try:
            Draft202012Validator.check_schema(data)
        except Exception as error:
            errors.append(f"invalid schema: {schema.relative_to(ROOT)}: {error}")

    schema_examples = (
        ("review-report.schema.json", "examples/review-report.json"),
        ("gate-artifact.schema.json", "examples/gate-g2.json"),
        ("action-plan.schema.json", "examples/action-plan.json"),
    )
    for schema_name, example_name in schema_examples:
        schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
        example = json.loads((ROOT / example_name).read_text(encoding="utf-8"))
        for error in Draft202012Validator(schema).iter_errors(example):
            errors.append(f"schema example invalid: {example_name}: {error.message}")

    validate_gate = load_function(SKILL / "scripts" / "validate_artifact_structure.py", "validate")
    gate = json.loads((ROOT / "examples" / "gate-g2.json").read_text(encoding="utf-8"))
    for error in validate_gate(gate, "G2"):
        errors.append(f"gate example: {error}")

    review = json.loads((ROOT / "examples" / "review-report.json").read_text(encoding="utf-8"))
    for field in ("schema_version", "mode", "permission", "risk_level", "findings", "verification"):
        if field not in review:
            errors.append(f"review example lacks {field}")

    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(json.dumps({"valid": True, "skill_lines": len(skill_text.splitlines())}, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Discover repository manifests, project scripts, and architecture-rule configs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".venv",
    ".vscode",
    "build",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

ECOSYSTEM_FILES = {
    "package.json": "javascript/typescript",
    "pyproject.toml": "python",
    "setup.py": "python",
    "requirements.txt": "python",
    "pom.xml": "java/maven",
    "build.gradle": "java/gradle",
    "build.gradle.kts": "java/gradle",
    "Cargo.toml": "rust",
    "go.mod": "go",
}

PIPELINE_FILES = {
    ".gitlab-ci.yml": "GitLab CI",
    "azure-pipelines.yml": "Azure Pipelines",
    "Jenkinsfile": "Jenkins",
}

INFRASTRUCTURE_FILES = {
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "Chart.yaml": "Helm",
    "terragrunt.hcl": "Terragrunt",
}

MIGRATION_FILES = {
    "alembic.ini": "Alembic",
    "liquibase.properties": "Liquibase",
    "flyway.conf": "Flyway",
    "schema.prisma": "Prisma",
}

ARCHITECTURE_CONFIGS = {
    ".importlinter": "Import Linter",
    ".dependency-cruiser.js": "dependency-cruiser",
    ".dependency-cruiser.cjs": "dependency-cruiser",
    ".dependency-cruiser.mjs": "dependency-cruiser",
    "dependency-cruiser.config.js": "dependency-cruiser",
    "dependency-cruiser.config.cjs": "dependency-cruiser",
    ".semgrep.yml": "Semgrep",
    ".semgrep.yaml": "Semgrep",
    "codeql-config.yml": "CodeQL",
    "codeql-config.yaml": "CodeQL",
}


def iter_files(root: Path, max_depth: int = 6):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if len(relative.parts) > max_depth + 1:
            continue
        if any(part in IGNORED_DIRS for part in relative.parts[:-1]):
            continue
        yield path, relative


def discover(root: Path, max_depth: int = 6) -> dict[str, object]:
    root = root.resolve()
    ecosystems: set[str] = set()
    manifests: list[str] = []
    architecture_controls: list[dict[str, str]] = []
    package_scripts: list[dict[str, object]] = []
    pipelines: list[dict[str, str]] = []
    infrastructure: list[dict[str, str]] = []
    migrations: list[dict[str, str]] = []
    workspaces: list[dict[str, object]] = []
    command_candidates: set[str] = set()

    lockfiles = {path.name for path in root.iterdir() if path.is_file()}
    package_manager = (
        "pnpm" if "pnpm-lock.yaml" in lockfiles else
        "yarn" if "yarn.lock" in lockfiles else
        "bun" if "bun.lockb" in lockfiles or "bun.lock" in lockfiles else
        "npm"
    )

    for path, relative in iter_files(root, max_depth=max_depth):
        name = path.name
        if name in ECOSYSTEM_FILES:
            ecosystems.add(ECOSYSTEM_FILES[name])
            manifests.append(relative.as_posix())
        if name.endswith(".sln") or name.endswith(".csproj"):
            ecosystems.add("dotnet")
            manifests.append(relative.as_posix())
        if name in ARCHITECTURE_CONFIGS:
            architecture_controls.append(
                {"tool": ARCHITECTURE_CONFIGS[name], "config": relative.as_posix()}
            )
        if name in PIPELINE_FILES or ".github/workflows" in relative.as_posix():
            pipelines.append({"platform": PIPELINE_FILES.get(name, "GitHub Actions"), "file": relative.as_posix()})
        if name in INFRASTRUCTURE_FILES or path.suffix == ".tf" or (
            path.suffix in {".yaml", ".yml"} and any(part in {"k8s", "kubernetes", "helm"} for part in relative.parts)
        ):
            tool = INFRASTRUCTURE_FILES.get(name, "Terraform" if path.suffix == ".tf" else "Kubernetes")
            infrastructure.append({"tool": tool, "file": relative.as_posix()})
        if name in MIGRATION_FILES or any(part.lower() in {"migrations", "dbmate", "changelog"} for part in relative.parts[:-1]):
            migrations.append({"tool": MIGRATION_FILES.get(name, "migration directory"), "file": relative.as_posix()})
        if name == "package.json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                continue
            scripts = data.get("scripts")
            if isinstance(scripts, dict):
                package_scripts.append(
                    {
                        "manifest": relative.as_posix(),
                        "scripts": sorted(str(key) for key in scripts),
                    }
                )
                prefix = "run " if package_manager in {"npm", "pnpm"} else ""
                for key in scripts:
                    if key in {"test", "lint", "typecheck", "build", "format", "check"}:
                        command_candidates.add(f"{package_manager} {prefix}{key}".strip())
            workspace_value = data.get("workspaces")
            if workspace_value:
                workspaces.append({"manifest": relative.as_posix(), "workspaces": workspace_value})

    if "python" in ecosystems:
        command_candidates.add("python -m pytest")
    if "dotnet" in ecosystems:
        command_candidates.add("dotnet test")
    if "java/maven" in ecosystems:
        command_candidates.add("./mvnw test" if (root / "mvnw").exists() else "mvn test")
    if "java/gradle" in ecosystems:
        command_candidates.add("./gradlew test" if (root / "gradlew").exists() else "gradle test")
    if "go" in ecosystems:
        command_candidates.update({"go test ./...", "go test -race ./..."})
    if "rust" in ecosystems:
        command_candidates.update({"cargo test", "cargo clippy"})

    return {
        "root": str(root),
        "ecosystems": sorted(ecosystems),
        "manifests": sorted(set(manifests)),
        "architecture_controls": sorted(
            architecture_controls, key=lambda item: (item["tool"], item["config"])
        ),
        "package_scripts": sorted(package_scripts, key=lambda item: item["manifest"]),
        "package_manager": package_manager if "javascript/typescript" in ecosystems else None,
        "workspaces": workspaces,
        "pipelines": sorted(pipelines, key=lambda item: item["file"]),
        "infrastructure": sorted(infrastructure, key=lambda item: item["file"]),
        "migrations": sorted(migrations, key=lambda item: item["file"]),
        "command_candidates": sorted(command_candidates),
        "scan_max_depth": max_depth,
        "note": "Candidates only; confirm commands in project documentation and CI.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover project ecosystems and existing architecture controls."
    )
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--max-depth", type=int, default=6)
    args = parser.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    if args.max_depth < 0:
        parser.error("--max-depth must be non-negative")
    print(json.dumps(discover(root, max_depth=args.max_depth), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

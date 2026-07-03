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


def iter_files(root: Path, max_depth: int = 3):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if len(relative.parts) > max_depth + 1:
            continue
        if any(part in IGNORED_DIRS for part in relative.parts[:-1]):
            continue
        yield path, relative


def discover(root: Path) -> dict[str, object]:
    root = root.resolve()
    ecosystems: set[str] = set()
    manifests: list[str] = []
    architecture_controls: list[dict[str, str]] = []
    package_scripts: list[dict[str, object]] = []

    for path, relative in iter_files(root):
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

    return {
        "root": str(root),
        "ecosystems": sorted(ecosystems),
        "manifests": sorted(set(manifests)),
        "architecture_controls": sorted(
            architecture_controls, key=lambda item: (item["tool"], item["config"])
        ),
        "package_scripts": sorted(package_scripts, key=lambda item: item["manifest"]),
        "note": "Candidates only; confirm commands in project documentation and CI.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover project ecosystems and existing architecture controls."
    )
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    print(json.dumps(discover(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Resolve doc-writing's public and enterprise runtime dependencies.

The public repository never installs enterprise connectors silently. This
script reports a deterministic readiness result and, on request, prints a
human-reviewable install plan for an approved enterprise marketplace.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "config" / "skill-dependencies.json"


def _read_skill_names(skills_dir: Path) -> set[str]:
    names: set[str] = set()
    if not skills_dir.is_dir():
        return names
    for skill_file in skills_dir.rglob("SKILL.md"):
        try:
            text = skill_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not text.startswith("---"):
            continue
        for line in text.splitlines()[1:]:
            if line.strip() == "---":
                break
            if line.startswith("name:"):
                value = line.split(":", 1)[1].strip().strip("'\"")
                if value:
                    names.add(value)
                break
    return names


def _default_skill_dirs() -> list[Path]:
    configured = os.environ.get("CODEX_SKILLS_DIR", "")
    if configured:
        return [Path(item).expanduser() for item in configured.split(os.pathsep) if item]
    return [Path.home() / ".agents" / "skills", Path.home() / ".codex" / "skills"]


def _profile_dependencies(manifest: dict[str, Any], profile_name: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    profiles = manifest["profiles"]
    if profile_name not in profiles:
        raise ValueError(f"unknown profile: {profile_name}")
    profile = profiles[profile_name]
    required: list[dict[str, Any]] = []
    optional: list[dict[str, Any]] = []
    parent = profile.get("extends")
    if parent:
        required, optional = _profile_dependencies(manifest, parent)
    required.extend(profile.get("required", []))
    optional.extend(profile.get("optional", []))
    return required, optional


def _resolve_one(dependency: dict[str, Any], installed: set[str]) -> dict[str, Any]:
    names = list(dependency["skill_names"])
    names.extend(dependency.get("subskills", []))
    match = dependency.get("match", "all")
    matched = [name for name in names if name in installed]
    ready = bool(matched) if match == "any" else len(matched) == len(names)
    return {
        "capability": dependency["capability"],
        "source": dependency["source"],
        "required": True,
        "match": match,
        "skill_names": dependency["skill_names"],
        "subskills": dependency.get("subskills", []),
        "matched": matched,
        "missing": [name for name in names if name not in installed],
        "status": "ready" if ready else "missing",
        "resolution": dependency.get("resolution"),
    }


def resolve(manifest_path: Path, profile_name: str, skill_dirs: list[Path]) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required, optional = _profile_dependencies(manifest, profile_name)
    installed: set[str] = set()
    for directory in skill_dirs:
        installed.update(_read_skill_names(directory))
    bundled_root = REPO_ROOT / "plugins" / "human-internal-writing" / "skills"
    installed.update(_read_skill_names(bundled_root))
    results = [_resolve_one(item, installed) for item in required]
    optional_results = [_resolve_one(item, installed) for item in optional]
    for item in optional_results:
        item["required"] = False
    return {
        "profile": profile_name,
        "primary_skill": manifest["primary_skill"],
        "skill_dirs": [str(path) for path in skill_dirs],
        "required": results,
        "optional": optional_results,
        "status": "ready" if all(item["status"] == "ready" for item in results) else "blocked",
    }


def install_plan(result: dict[str, Any], marketplace: str | None) -> list[str]:
    commands = [
        "codex plugin marketplace add itsoso/doc-writing",
        "codex plugin add human-internal-writing@doc-writing",
    ]
    missing_enterprise = [
        item for item in result["required"] + result["optional"]
        if item["status"] == "missing" and item["source"] == "enterprise-runtime"
    ]
    if missing_enterprise:
        if marketplace:
            commands.append(f"# Review and install enterprise capabilities from: {marketplace}")
            for item in missing_enterprise:
                names = " | ".join(item["missing"] or item["skill_names"])
                commands.append(f"# {item['capability']}: provision one of [{names}] in the controlled runtime")
        else:
            commands.append("# Provide an approved enterprise marketplace or runtime registry before installing internal connectors.")
            for item in missing_enterprise:
                names = " | ".join(item["missing"] or item["skill_names"])
                commands.append(f"# {item['capability']}: provision one of [{names}] in the controlled runtime")
    return commands


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--profile", default="generic")
    parser.add_argument("--skills-dir", type=Path, action="append")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--print-install-plan", action="store_true")
    parser.add_argument("--enterprise-marketplace")
    args = parser.parse_args()

    skill_dirs = args.skills_dir if args.skills_dir else _default_skill_dirs()
    try:
        result = resolve(args.manifest.resolve(), args.profile, skill_dirs)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as error:
        if args.json:
            print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False, indent=2))
        else:
            print(f"dependency_check: blocked: {error}")
        return 2

    if args.print_install_plan:
        for command in install_plan(result, args.enterprise_marketplace):
            print(command)
        return 0
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"dependency_check: {result['status']} ({result['profile']})")
        for item in result["required"] + result["optional"]:
            marker = "required" if item["required"] else "optional"
            print(f"- {item['status']}: {item['capability']} [{marker}]")
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())

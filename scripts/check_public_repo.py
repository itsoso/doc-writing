#!/usr/bin/env python3
"""Fail-closed scan for a public doc-writing export.

This is a deterministic pre-push check, not a substitute for company review.
It intentionally errs on the side of blocking and does not print matching text.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_EXCLUDES = {".git", ".codex_tmp", "tmp", "__pycache__", ".mypy_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".js", ".ts", ".html", ".svg"}
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("internal_url", re.compile(r"(?:https?://)?(?:docs|onepoint)\." + r"corp\.kuaishou\.com", re.I)),
    ("internal_doc_id", re.compile(r"\bfc[A-Za-z0-9_-]{10,}\b")),
    ("credential", re.compile(r"(?:Bearer\s+[A-Za-z0-9._-]{12,}|(?:sk|ghp|github_pat)-[A-Za-z0-9_-]{12,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----)", re.I)),
    ("personal_email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("personal_phone", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
)


def scan(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in DEFAULT_EXCLUDES for part in relative.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for rule, pattern in RULES:
            if pattern.search(text):
                findings.append({"rule": rule, "path": str(path.relative_to(root))})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.path.resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")
    findings = scan(root)
    payload = {"path": str(root), "status": "blocked" if findings else "pass", "findings": findings}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("public_repo_scan: " + payload["status"])
        for finding in findings:
            print(f"- {finding['rule']}: {finding['path']}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

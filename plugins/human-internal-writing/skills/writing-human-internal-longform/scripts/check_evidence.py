#!/usr/bin/env python3
"""Validate a long-form claim-to-evidence ledger without reading source content."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path


SOURCE_BOUND_STATES = {"sourced", "observed", "verified"}
REASONED_STATES = {"inference", "scenario", "proposal", "editorial"}
ALLOWED_STATES = SOURCE_BOUND_STATES | REASONED_STATES | {"unknown"}
HIGH_RISK = {"high", "critical"}
REQUIRED_COLUMNS = {
    "claim_id",
    "section",
    "claim",
    "state",
    "risk",
    "source_locator",
    "source_version",
    "verification_status",
    "freshness_status",
    "depends_on",
    "notes",
}


def analyze(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    claim_id_counts = Counter(row.get("claim_id", "").strip() for row in rows)
    known_claim_ids = set(claim_id_counts)
    for claim_id, count in sorted(claim_id_counts.items()):
        if count > 1:
            findings.append(
                {
                    "rule": "duplicate-claim-id",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": "",
                    "message": f"Claim IDs must be unique; {claim_id or '<blank>'} appears {count} times.",
                }
            )
    for row_number, row in enumerate(rows, start=2):
        state = row.get("state", "").strip().lower()
        risk = row.get("risk", "").strip().lower()
        verification = row.get("verification_status", "").strip().lower()
        freshness = row.get("freshness_status", "").strip().lower()
        claim_id = row.get("claim_id", "").strip()
        if not re.fullmatch(r"C\d{3,}", claim_id):
            findings.append(
                {
                    "rule": "invalid-claim-id",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": str(row_number),
                    "message": "Claim ID must use the stable C-number format, for example C001.",
                }
            )
        if state not in ALLOWED_STATES:
            findings.append(
                {
                    "rule": "invalid-state",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": str(row_number),
                    "message": "Evidence state must be one of: "
                    + ", ".join(sorted(ALLOWED_STATES)),
                }
            )
        if state in SOURCE_BOUND_STATES and not row.get("source_locator", "").strip():
            findings.append(
                {
                    "rule": "missing-source-locator",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": str(row_number),
                    "message": "Sourced, observed, or verified claims require an exact source locator.",
                }
            )
        if state in SOURCE_BOUND_STATES and risk in HIGH_RISK and freshness not in {"current", "immutable"}:
            findings.append(
                {
                    "rule": "stale-high-risk-source",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": str(row_number),
                    "message": "High-risk mutable sources must be current, or explicitly immutable, before editorial readiness.",
                }
            )
        if state in REASONED_STATES and risk in HIGH_RISK and not row.get("depends_on", "").strip():
            findings.append(
                {
                    "rule": "unbound-high-risk-reasoning",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": str(row_number),
                    "message": "High-risk inference, scenario, proposal, or editorial reasoning must name the claims it depends on.",
                }
            )
        if state == "unknown" and risk in HIGH_RISK:
            findings.append(
                {
                    "rule": "material-unknown",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": str(row_number),
                    "message": "A high-risk or critical Unknown must be resolved or removed from the central judgment before editorial readiness.",
                }
            )
        dependencies = {
            item
            for item in re.split(r"[,;|\s]+", row.get("depends_on", "").strip())
            if item
        }
        unknown_dependencies = sorted(dependencies - known_claim_ids)
        if unknown_dependencies:
            findings.append(
                {
                    "rule": "unknown-claim-dependency",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": str(row_number),
                    "message": "Claim dependencies must reference claim IDs present in the same ledger: "
                    + ", ".join(unknown_dependencies),
                }
            )
        if state in SOURCE_BOUND_STATES and risk in HIGH_RISK and verification != "verified":
            findings.append(
                {
                    "rule": "unverified-high-risk-claim",
                    "severity": "blocker",
                    "claim_id": claim_id,
                    "row": str(row_number),
                    "message": "High-risk sourced or observed claims require source readback before editorial readiness.",
                }
            )
    return findings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="CSV claim-to-evidence ledger")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Fail when the ledger still has editorial-readiness blockers",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if not args.path.is_file():
        print(f"error: ledger not found: {args.path}", file=sys.stderr)
        return 2

    with args.path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        rows = list(reader)

    missing_columns = sorted(REQUIRED_COLUMNS - fieldnames)
    if missing_columns:
        payload = {
            "error": "invalid-schema",
            "path": str(args.path),
            "missing_columns": missing_columns,
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("error: missing required columns: " + ", ".join(missing_columns), file=sys.stderr)
        return 2

    findings = analyze(rows)
    blocker_count = sum(item["severity"] == "blocker" for item in findings)
    warning_count = sum(item["severity"] == "warning" for item in findings)
    ready = blocker_count == 0
    payload = {
        "path": str(args.path),
        "ready": ready,
        "summary": {
            "claims": len(rows),
            "blockers": blocker_count,
            "warnings": warning_count,
        },
        "findings": findings,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"claims={len(rows)} blockers={blocker_count} "
            f"warnings={warning_count} ready={str(ready).lower()}"
        )
    return 1 if args.require_ready and not ready else 0


if __name__ == "__main__":
    raise SystemExit(main())

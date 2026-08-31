#!/usr/bin/env python3
"""Create and inspect a hash-bound, resumable KStack release checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any


WORD_STAGES = (
    "source_ready",
    "docx_generated",
    "docx_structurally_valid",
    "wps_visually_verified",
    "word_verified",
)
DOCS_STAGES = (
    *WORD_STAGES,
    "docs_created",
    "docs_readback_verified",
)
STAGE_GRAPHS = {
    "word_verified": WORD_STAGES,
    "docs_verified": DOCS_STAGES,
}
STAGES = tuple(dict.fromkeys((*WORD_STAGES, *DOCS_STAGES)))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_stages(stages: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    return {stage: {"complete": False, "at": None} for stage in stages}


def requested_stages(payload: dict[str, Any]) -> tuple[str, ...]:
    terminal_state = payload.get("requested_terminal_state", "word_verified")
    if terminal_state not in STAGE_GRAPHS:
        raise ValueError("release_terminal_state_invalid")
    return STAGE_GRAPHS[terminal_state]


def safe_locator(source: Path, state_path: Path) -> str:
    source_resolved = source.resolve()
    try:
        relative = source_resolved.relative_to(state_path.parent.resolve())
    except ValueError:
        return source.name
    return relative.as_posix()


def read_state(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "kstack.release-state.v1":
        raise ValueError("release_state_schema_invalid")
    payload.setdefault("requested_terminal_state", "word_verified")
    stages = requested_stages(payload)
    stored_stages = payload.get("stages", {})
    legacy_word_stage = stored_stages.get("local_verified")
    if "word_verified" not in stored_stages and isinstance(legacy_word_stage, dict):
        stored_stages["word_verified"] = legacy_word_stage
    payload["stages"] = {
        stage: stored_stages.get(stage, {"complete": False, "at": None})
        for stage in stages
    }
    stored_path = payload.get("source", {}).get("path")
    if isinstance(stored_path, str):
        candidate = Path(stored_path)
        windows_candidate = PureWindowsPath(stored_path)
        if (
            candidate.is_absolute()
            or windows_candidate.is_absolute()
            or ".." in candidate.parts
            or ".." in windows_candidate.parts
        ):
            payload["source"]["path"] = (
                windows_candidate.name
                if windows_candidate.is_absolute()
                else candidate.name
            )
    return payload


def persist(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def refresh_source(
    state_path: Path,
    payload: dict[str, Any],
    source: Path,
) -> bool:
    current_hash = sha256(source)
    if current_hash == payload["source"]["sha256"]:
        return False
    payload["source"] = {
        "path": safe_locator(source, state_path),
        "sha256": current_hash,
    }
    payload["stages"] = empty_stages(requested_stages(payload))
    payload["invalidated_at"] = now()
    persist(state_path, payload)
    return True


def inspect(state_path: Path, source: Path | None) -> dict[str, Any]:
    payload = read_state(state_path)
    source_changed = False
    if source is not None:
        source_changed = refresh_source(state_path, payload, source)
    stages = requested_stages(payload)
    next_stage = next(
        (
            stage
            for stage in stages
            if not payload.get("stages", {}).get(stage, {}).get("complete", False)
        ),
        None,
    )
    return {**payload, "source_changed": source_changed, "next_stage": next_stage}


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage resumable KStack release stages.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--state", type=Path, required=True)
    init.add_argument("--source", type=Path, required=True)
    init.add_argument(
        "--terminal-state",
        choices=tuple(STAGE_GRAPHS),
        default="word_verified",
    )
    init.add_argument("--docs-target-label")
    init.add_argument("--docs-authorized", action="store_true")
    init.add_argument("--json", action="store_true")
    mark = sub.add_parser("mark")
    mark.add_argument("--state", type=Path, required=True)
    mark.add_argument("--source", type=Path, required=True)
    mark.add_argument("--stage", choices=STAGES, required=True)
    mark.add_argument("--json", action="store_true")
    view = sub.add_parser("inspect")
    view.add_argument("--state", type=Path, required=True)
    view.add_argument("--source", type=Path)
    view.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.command == "init":
        if args.terminal_state == "docs_verified" and (
            not args.docs_target_label or not args.docs_authorized
        ):
            print("docs_target_and_authorization_required", file=sys.stderr)
            return 2
        payload = {
            "schema_version": "kstack.release-state.v1",
            "created_at": now(),
            "requested_terminal_state": args.terminal_state,
            "source": {
                "path": safe_locator(args.source, args.state),
                "sha256": sha256(args.source),
            },
            "stages": empty_stages(STAGE_GRAPHS[args.terminal_state]),
        }
        if args.terminal_state == "docs_verified":
            payload["docs_request"] = {
                "target_label": args.docs_target_label,
                "authorization_confirmed": True,
            }
        persist(args.state, payload)
        result = {**payload, "source_changed": False, "next_stage": "source_ready"}
    elif args.command == "mark":
        payload = read_state(args.state)
        if refresh_source(args.state, payload, args.source):
            print("source_changed", file=sys.stderr)
            return 3
        stages = requested_stages(payload)
        if args.stage not in stages:
            print("stage_not_requested:" + args.stage, file=sys.stderr)
            return 2
        index = stages.index(args.stage)
        missing = [
            stage
            for stage in stages[:index]
            if not payload["stages"][stage]["complete"]
        ]
        if missing:
            print("missing_prior_stage:" + ",".join(missing), file=sys.stderr)
            return 2
        payload["stages"][args.stage] = {"complete": True, "at": now(), "source_sha256": payload["source"]["sha256"]}
        persist(args.state, payload)
        result = inspect(args.state, None)
    else:
        result = inspect(args.state, args.source)

    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"next_stage={result['next_stage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

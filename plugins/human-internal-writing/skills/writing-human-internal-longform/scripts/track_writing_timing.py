#!/usr/bin/env python3
"""Record comparable KStack writing and release milestones without claiming causality."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MILESTONES = (
    "started",
    "first_complete_draft",
    "editorially_ready",
    "markdown_verified",
    "word_verified",
    "docs_verified",
)
MILESTONE_PREREQUISITES = {
    "started": (),
    "first_complete_draft": ("started",),
    "editorially_ready": ("first_complete_draft",),
    "markdown_verified": ("editorially_ready",),
    "word_verified": ("markdown_verified",),
    "docs_verified": ("markdown_verified",),
}
MILESTONE_RANK = {event: index for index, event in enumerate(MILESTONES)}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp_timezone_required")
    return parsed


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "kstack.writing-timing.v1", "events": []}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Record KStack article workflow timing milestones.")
    parser.add_argument("command", choices=("mark",))
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--event", choices=(*MILESTONES, "rework", "tool_retry"), required=True)
    parser.add_argument("--reason")
    parser.add_argument("--at", help="Timezone-aware ISO timestamp; defaults to current UTC time")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = load(args.file)
    completed = [event["event"] for event in payload["events"] if event["event"] in MILESTONES]
    if args.event in MILESTONES:
        missing = [
            item
            for item in MILESTONE_PREREQUISITES[args.event]
            if item not in completed
        ]
        if missing:
            print("missing_prior_milestone:" + ",".join(missing), file=sys.stderr)
            return 2
        if args.event in completed:
            print("milestone_already_recorded:" + args.event, file=sys.stderr)
            return 2

    try:
        event_at = parse_time(args.at) if args.at else parse_time(now())
        if payload["events"] and event_at < parse_time(payload["events"][-1]["at"]):
            raise ValueError("timestamp_before_previous_event")
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    payload["events"].append({"event": args.event, "at": event_at.isoformat(), **({"reason": args.reason} if args.reason else {})})
    completed = [event["event"] for event in payload["events"] if event["event"] in MILESTONES]
    payload["highest_milestone"] = (
        max(completed, key=MILESTONE_RANK.__getitem__) if completed else None
    )
    payload["rework_count"] = sum(event["event"] == "rework" for event in payload["events"])
    payload["tool_retry_count"] = sum(event["event"] == "tool_retry" for event in payload["events"])
    milestone_events = [event for event in payload["events"] if event["event"] in MILESTONES]
    durations: dict[str, int] = {}
    for previous, current in zip(milestone_events, milestone_events[1:]):
        key = f"{previous['event']}_to_{current['event']}"
        durations[key] = int((parse_time(current["at"]) - parse_time(previous["at"])).total_seconds())
    payload["durations_seconds"] = durations
    payload["elapsed_seconds"] = (
        int((parse_time(milestone_events[-1]["at"]) - parse_time(milestone_events[0]["at"])).total_seconds())
        if len(milestone_events) >= 2
        else 0
    )
    args.file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else f"highest_milestone={payload['highest_milestone']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

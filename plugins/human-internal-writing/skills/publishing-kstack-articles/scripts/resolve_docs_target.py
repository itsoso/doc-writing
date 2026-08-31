#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def emit(payload: dict[str, Any], *, ok: bool) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if ok else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve one exact shared-drive title from a docs-cli JSON envelope."
    )
    parser.add_argument("--title", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.load(sys.stdin)
        result = payload["data"]["result"]
        items = result["items"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return emit({"ok": False, "reason_code": "invalid_docs_envelope"}, ok=False)

    if payload.get("ok") is not True or not isinstance(items, list):
        return emit({"ok": False, "reason_code": "invalid_docs_envelope"}, ok=False)
    if result.get("hasNext") is not False:
        return emit({"ok": False, "reason_code": "pagination_incomplete"}, ok=False)

    matches = [item for item in items if isinstance(item, dict) and item.get("title") == args.title]
    if not matches:
        return emit({"ok": False, "reason_code": "target_not_found"}, ok=False)
    if len(matches) != 1:
        return emit(
            {"ok": False, "reason_code": "target_ambiguous", "match_count": len(matches)},
            ok=False,
        )

    match = matches[0]
    if match.get("docTypeEn") != "group":
        return emit({"ok": False, "reason_code": "target_wrong_type"}, ok=False)
    folder_id = match.get("docId")
    if not isinstance(folder_id, str) or not folder_id:
        return emit({"ok": False, "reason_code": "target_missing_id"}, ok=False)

    return emit(
        {
            "ok": True,
            "target": {
                "kind": "drive",
                "id": folder_id,
                "label": match["title"],
                "viewId": match.get("viewId"),
                "docTypeEn": match.get("docTypeEn"),
            },
        },
        ok=True,
    )


if __name__ == "__main__":
    sys.exit(main())

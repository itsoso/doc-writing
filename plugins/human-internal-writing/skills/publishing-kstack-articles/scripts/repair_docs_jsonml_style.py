#!/usr/bin/env python3
"""Build style-only JsonML replacement ops for an existing KStack Docs page.

The input is the raw payload returned by ``word +fetch-jsonml``. This tool
never writes to Docs; it emits profile-aware replacement ops so the caller can
apply them with ``word +update-jsonml --base-version`` after reviewing the
preimage.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Iterator


CONTRACT_PATH = Path(__file__).resolve().parents[1] / "assets" / "kstack-style.v1.json"
BLOCK_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "quote", "li"}
MASTHEAD_P_ROLES = ("subtitle", "date", "lead")


def _contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _body(payload: Any) -> list[Any]:
    body = payload.get("body") if isinstance(payload, dict) else payload
    if isinstance(body, list) and body and isinstance(body[0], list) and body[0] and body[0][0] == "root":
        body = ["root", body[0][1] if len(body[0]) > 1 else {}, *body[1:]]
    if not isinstance(body, list) or len(body) < 2 or body[0] != "root":
        raise ValueError("JsonML payload must contain a root body array")
    return body


def _blocks(node: Any) -> Iterator[list[Any]]:
    if isinstance(node, list):
        if node and isinstance(node[0], str) and node[0] in BLOCK_TAGS and len(node) >= 2 and isinstance(node[1], dict):
            yield node
            for child in node[2:]:
                yield from _blocks(child)
            return
        for child in node:
            yield from _blocks(child)
    elif isinstance(node, dict):
        for child in node.values():
            yield from _blocks(child)


def _text_nodes(node: Any) -> Iterator[list[Any]]:
    if isinstance(node, list):
        if len(node) >= 3 and node[0] == "text":
            yield node
            return
        for child in node:
            yield from _text_nodes(child)
    elif isinstance(node, dict):
        for child in node.values():
            yield from _text_nodes(child)


def _role_from_attrs(attrs: dict[str, Any]) -> str | None:
    value = attrs.get("data-kstack-role", attrs.get("role"))
    if isinstance(value, str):
        return value.lower()
    return None


def _classify(block: list[Any], state: dict[str, Any]) -> str | None:
    tag = str(block[0]).lower()
    attrs = block[1]
    explicit = _role_from_attrs(attrs)
    if explicit:
        return explicit
    if tag == "h1":
        state["seen_h1"] = True
        return "h1"
    if tag in {"h2", "h3"}:
        state["seen_h2"] = True
        return tag
    if tag in {"h4", "h5", "h6"}:
        state["seen_h2"] = True
        return None
    if tag == "quote":
        return "lead"
    if tag == "li" or isinstance(attrs.get("list"), dict):
        return "list"
    if tag != "p":
        return None
    if not state["seen_h1"]:
        return "kicker"
    if not state["seen_h2"] and state["masthead_index"] < len(MASTHEAD_P_ROLES):
        role = MASTHEAD_P_ROLES[state["masthead_index"]]
        state["masthead_index"] += 1
        return role
    return "body"


def _resolved_roles(contract: dict[str, Any], profile: str) -> dict[str, dict[str, Any]]:
    roles = {
        name: dict(definition)
        for name, definition in contract["docs"]["roles"].items()
    }
    if profile == "default":
        return roles
    profiles = contract["docs"].get("profiles", {})
    if profile not in profiles:
        raise ValueError(f"unknown Docs style profile: {profile}")
    selected = profiles[profile]
    for role_name, override in selected.get("role_overrides", {}).items():
        if role_name not in roles:
            raise ValueError(
                f"unknown role override in Docs style profile {profile}: {role_name}"
            )
        roles[role_name].update(override)
    for role_name, definition in selected.get("additional_roles", {}).items():
        roles[role_name] = dict(definition)
    return roles


def _role_tokens(
    roles: dict[str, dict[str, Any]], role: str
) -> dict[str, Any] | None:
    role_def = roles.get(role)
    return role_def if isinstance(role_def, dict) else None


def build_ops(input_path: Path, output_path: Path, profile: str = "default") -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    body = _body(payload)
    contract = _contract()
    roles = _resolved_roles(contract, profile)
    state: dict[str, Any] = {"seen_h1": False, "seen_h2": False, "masthead_index": 0}
    ops: list[dict[str, Any]] = []
    anchors: set[str] = set()

    for block in _blocks(body[2:]):
        attrs = block[1]
        anchor = attrs.get("id")
        if not isinstance(anchor, str) or not anchor:
            continue
        if anchor in anchors:
            raise ValueError(f"duplicate JsonML block anchor: {anchor}")
        anchors.add(anchor)

        role = _classify(block, state)
        replacement = copy.deepcopy(block)
        replacement_attrs = replacement[1]
        tag = str(replacement[0]).lower()
        alignment = "left"
        role_def = _role_tokens(roles, role) if role else None
        if role_def:
            alignment = str(role_def["alignment"])
        replacement_attrs["jc"] = alignment
        replacement_attrs["lh"] = 1.25 if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} else 1.45

        if role_def:
            size = float(role_def["size"])
            color = str(role_def["color"]).lower()
            for text_node in _text_nodes(replacement[2:]):
                text_attrs = text_node[1]
                if not isinstance(text_attrs, dict):
                    text_attrs = {}
                    text_node[1] = text_attrs
                text_attrs["sz"] = size
                text_attrs["color"] = color
                if role in {"h1", "h2", "h3", "lead"}:
                    text_attrs["bold"] = True

        ops.append({"op": "replace", "anchor": anchor, "content": [replacement]})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(ops, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build style-only JsonML replacement ops.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--profile", choices=("default", "index"), default="default")
    args = parser.parse_args()
    try:
        build_ops(args.input.resolve(), args.output.resolve(), profile=args.profile)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Capture and compare representation-independent index/hub structure."""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import posixpath
import re
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit, urlunsplit


SCRIPT_PATH = Path(__file__).resolve()
MANIFEST_PATH = SCRIPT_PATH.parents[3] / ".codex-plugin" / "plugin.json"
STYLE_VALIDATOR_PATH = SCRIPT_PATH.with_name("validate_docs_style.py")
SCHEMA_VERSION = "kstack.index-structure.v1"

ATX_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
MARKDOWN_IMAGE_RE = re.compile(
    r"!\[([^\]]*)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+['\"][^'\"]*['\"])?\s*\)"
)
MARKDOWN_LINK_RE = re.compile(
    r"(?<!!)\[([^\]]+)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+['\"][^'\"]*['\"])?\s*\)"
)
HTML_HEADING_RE = re.compile(r"<h[1-6]\b", re.IGNORECASE)
INLINE_LINK_RE = re.compile(r"!?\[([^\]]+)\]\([^)]*\)")
INLINE_TAG_RE = re.compile(r"<[^>]+>")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _plugin_version() -> str:
    return str(json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["version"])


def _normalize_text(value: str) -> str:
    value = html.unescape(value)
    value = INLINE_LINK_RE.sub(lambda match: match.group(1), value)
    value = INLINE_TAG_RE.sub("", value)
    value = re.sub(r"(?<!\\)[*_~`]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _canonical_target(value: str) -> str:
    value = html.unescape(value.strip().strip("<>"))
    parts = urlsplit(value)
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    path = parts.path
    if path:
        normalized = posixpath.normpath(path)
        if path.endswith("/") and normalized != "/":
            normalized += "/"
        path = normalized
    if scheme in {"http", "https"} and not path:
        path = "/"
    return urlunsplit((scheme, netloc, path, parts.query, parts.fragment))


class _SemanticHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[dict[str, object]] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self._heading_level: int | None = None
        self._heading_parts: list[str] = []
        self._link_target: str | None = None
        self._link_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = {name.lower(): value or "" for name, value in attrs}
        if re.fullmatch(r"h[1-6]", tag):
            self._heading_level = int(tag[1])
            self._heading_parts = []
        elif tag == "a" and attributes.get("href"):
            self._link_target = _canonical_target(attributes["href"])
            self._link_parts = []
        elif tag == "img" and attributes.get("src"):
            self.images.append(
                {
                    "alt": _normalize_text(attributes.get("alt", "")),
                    "target": _canonical_target(attributes["src"]),
                }
            )

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if self._heading_level is not None:
            self._heading_parts.append(data)
        if self._link_target is not None:
            self._link_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._heading_level is not None and tag == f"h{self._heading_level}":
            self.headings.append(
                {
                    "level": self._heading_level,
                    "text": _normalize_text("".join(self._heading_parts)),
                }
            )
            self._heading_level = None
            self._heading_parts = []
        elif tag == "a" and self._link_target is not None:
            self.links.append(
                {
                    "text": _normalize_text("".join(self._link_parts)),
                    "target": self._link_target,
                }
            )
            self._link_target = None
            self._link_parts = []


def _markdown_structure(source: str) -> dict[str, object]:
    headings = [
        {"level": len(match.group(1)), "text": _normalize_text(match.group(2))}
        for match in ATX_HEADING_RE.finditer(source)
    ]
    links = [
        {
            "text": _normalize_text(match.group(1)),
            "target": _canonical_target(match.group(2) or match.group(3)),
        }
        for match in MARKDOWN_LINK_RE.finditer(source)
    ]
    images = [
        {
            "alt": _normalize_text(match.group(1)),
            "target": _canonical_target(match.group(2) or match.group(3)),
        }
        for match in MARKDOWN_IMAGE_RE.finditer(source)
    ]
    return _normalized_structure(headings, links, images)


def _html_structure(source: str) -> dict[str, object]:
    parser = _SemanticHTMLParser()
    parser.feed(source)
    parser.close()
    return _normalized_structure(parser.headings, parser.links, parser.images)


def _normalized_structure(
    headings: list[dict[str, object]],
    links: list[dict[str, str]],
    images: list[dict[str, str]],
) -> dict[str, object]:
    canonical_links = sorted(
        ({"text": item["text"], "target": item["target"]} for item in links),
        key=lambda item: (item["target"], item["text"]),
    )
    unique_links: list[dict[str, str]] = []
    seen_links: set[tuple[str, str]] = set()
    for item in canonical_links:
        key = (item["text"], item["target"])
        if key not in seen_links:
            unique_links.append(item)
            seen_links.add(key)
    ordered_image_keys = [
        {"key": item["alt"] or PurePosixPath(urlsplit(item["target"]).path).name}
        for item in images
    ]
    return {
        "headings": headings,
        "links": unique_links,
        "image_count": len(images),
        "images": ordered_image_keys,
    }


def extract_structure(raw_source: bytes, format_hint: str = "auto") -> dict[str, object]:
    source = raw_source.decode("utf-8")
    selected = format_hint
    if selected == "auto":
        selected = "html" if HTML_HEADING_RE.search(source) else "markdown"
    if selected == "html":
        return _html_structure(source)
    if selected == "markdown":
        return _markdown_structure(source)
    raise ValueError(f"unsupported structure format: {format_hint}")


def capture_contract(
    raw_source: bytes,
    *,
    format_hint: str = "auto",
    source_name: str | None = None,
) -> dict[str, object]:
    contract: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "plugin_version": _plugin_version(),
        "source_sha256": _sha256(raw_source),
        "validator_sha256": _file_sha256(SCRIPT_PATH),
        "style_validator_sha256": _file_sha256(STYLE_VALIDATOR_PATH),
        "structure": extract_structure(raw_source, format_hint),
    }
    if source_name:
        contract["source_path"] = Path(source_name).name
    return contract


def compare_contract(
    raw_source: bytes,
    contract: dict[str, object],
    raw_remote: bytes,
    *,
    source_format: str = "auto",
    remote_format: str = "auto",
) -> dict[str, object]:
    findings: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        findings.append({"code": code, "message": message})

    if contract.get("schema_version") != SCHEMA_VERSION or not isinstance(
        contract.get("structure"), dict
    ):
        add("index_contract_invalid", "The index structure contract schema is invalid.")
        expected: dict[str, object] = {}
    else:
        expected = contract["structure"]  # type: ignore[assignment]

    if contract.get("source_sha256") != _sha256(raw_source):
        add(
            "index_source_hash_mismatch",
            "The structure contract is not bound to the current canonical source.",
        )
    if contract.get("plugin_version") != _plugin_version():
        add(
            "index_plugin_version_mismatch",
            "The structure contract was produced by a different plugin version.",
        )
    if contract.get("validator_sha256") != _file_sha256(SCRIPT_PATH):
        add(
            "index_validator_mismatch",
            "The structure contract was produced by a different structure validator.",
        )
    if contract.get("style_validator_sha256") != _file_sha256(STYLE_VALIDATOR_PATH):
        add(
            "index_style_validator_mismatch",
            "The structure contract was produced with a different Docs style validator.",
        )

    local = extract_structure(raw_source, source_format)
    remote = extract_structure(raw_remote, remote_format)
    for field, suffix, description in (
        ("headings", "headings", "heading order"),
        ("links", "links", "canonical link set and targets"),
        ("images", "images", "image count and order"),
    ):
        if expected.get(field) != local.get(field):
            add(
                f"index_local_{suffix}_mismatch",
                f"The current local {description} does not match the structure contract.",
            )
        if expected.get(field) != remote.get(field):
            add(
                f"index_remote_{suffix}_mismatch",
                f"The remote {description} does not match the structure contract.",
            )
    if expected.get("image_count") != local.get("image_count"):
        add(
            "index_local_images_mismatch",
            "The current local image count does not match the structure contract.",
        )
    if expected.get("image_count") != remote.get("image_count"):
        add(
            "index_remote_images_mismatch",
            "The remote image count does not match the structure contract.",
        )

    deduplicated: list[dict[str, str]] = []
    seen_codes: set[str] = set()
    for finding in findings:
        if finding["code"] not in seen_codes:
            deduplicated.append(finding)
            seen_codes.add(finding["code"])
    return {
        "schema_version": "kstack.index-structure-validation.v1",
        "source_sha256": _sha256(raw_source),
        "remote_sha256": _sha256(raw_remote),
        "ok": not deduplicated,
        "finding_count": len(deduplicated),
        "findings": deduplicated,
    }


def _emit(payload: dict[str, object], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif payload.get("ok", True):
        print("Index structure validation: PASS")
    else:
        for finding in payload.get("findings", []):
            print(f"{finding['code']}: {finding['message']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture or compare a maintained index/hub structure contract."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser("capture")
    capture.add_argument("--source", required=True, type=Path)
    capture.add_argument("--output", required=True, type=Path)
    capture.add_argument("--format", choices=("auto", "markdown", "html"), default="auto")
    capture.add_argument("--json", action="store_true")

    compare = subparsers.add_parser("compare")
    compare.add_argument("--source", required=True, type=Path)
    compare.add_argument("--contract", required=True, type=Path)
    compare.add_argument("--remote", required=True, type=Path)
    compare.add_argument("--source-format", choices=("auto", "markdown", "html"), default="auto")
    compare.add_argument("--remote-format", choices=("auto", "markdown", "html"), default="auto")
    compare.add_argument("--json", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "capture":
            contract = capture_contract(
                args.source.read_bytes(),
                format_hint=args.format,
                source_name=args.source.name,
            )
            args.output.write_text(
                json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            result = {
                "ok": True,
                "schema_version": contract["schema_version"],
                "source_path": args.source.name,
                "contract_path": args.output.name,
                "source_sha256": contract["source_sha256"],
            }
        else:
            contract = json.loads(args.contract.read_text(encoding="utf-8"))
            result = compare_contract(
                args.source.read_bytes(),
                contract,
                args.remote.read_bytes(),
                source_format=args.source_format,
                remote_format=args.remote_format,
            )
            result["source_path"] = args.source.name
            result["contract_path"] = args.contract.name
            result["remote_path"] = args.remote.name
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        result = {
            "ok": False,
            "schema_version": "kstack.index-structure-validation.v1",
            "finding_count": 1,
            "findings": [
                {
                    "code": "index_input_invalid",
                    "message": "Index structure input is invalid or unreadable.",
                }
            ],
        }

    _emit(result, as_json=args.json)
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())

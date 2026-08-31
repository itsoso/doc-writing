#!/usr/bin/env python3
"""Validate the KStack company-Docs HTML/Markdown style contract."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from datetime import date
from pathlib import Path


VALIDATOR_PATH = Path(__file__).resolve()
CONTRACT_PATH = VALIDATOR_PATH.parents[1] / "assets" / "kstack-style.v1.json"
MANIFEST_PATH = VALIDATOR_PATH.parents[3] / ".codex-plugin" / "plugin.json"
STYLE_CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
TOKENS = STYLE_CONTRACT["palette"]
DOCS_ROLES = STYLE_CONTRACT["docs"]["roles"]
ALLOWED_COLORS = {value.upper() for value in TOKENS.values()}
STYLE_RE = re.compile(r"\bstyle\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)", re.IGNORECASE | re.DOTALL)
COLOR_PROPERTY_RE = re.compile(r"(?:^|;)\s*(?:color|background-color|border-color)\s*:\s*([^;]+)", re.IGNORECASE)
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")
FONT_SIZE_RE = re.compile(r"(?:^|;)\s*font-size\s*:\s*([0-9]+)px\b", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
ROLE_RE = re.compile(
    r"\bdata-kstack-role\s*=\s*(?P<quote>['\"])(?P<role>[a-z-]+)(?P=quote)",
    re.IGNORECASE,
)
ALIGN_RE = re.compile(r"\balign\s*=\s*(['\"])(left|center|right|justify)\1", re.IGNORECASE)
INDEX_LAYOUT_RE = re.compile(
    r"\bdata-kstack-layout\s*=\s*(?P<quote>['\"])index(?P=quote)",
    re.IGNORECASE,
)
CONTINUATION_VARIANT_RE = re.compile(
    r'\bdata-kstack-variant="continuation"', re.IGNORECASE
)
NUMBERED_HUB_ENTRY_RE = re.compile(r"^\d{1,3}\s*[｜|]\s*\S(?:.*\S)?$")
GLOBAL_INTRO_ROLE = "global-intro"
HUB_ENTRY_ROLE = "hub-entry"
DATE_RE = re.compile(
    r"(?P<year>\d{4}) 年 (?P<month>\d{1,2}) 月 (?P<day>\d{1,2}) 日"
)
TIMEZONE_RE = re.compile(
    r"(?:北京时间|中国标准时间|东八区|"
    r"(?<![A-Za-z])(?:UTC|GMT)(?:\s*[+-]\s*\d{1,2}(?::?\d{2})?)?(?![A-Za-z])|"
    r"(?<![A-Za-z])(?:CST|EST|EDT|PST|PDT|HKT)(?![A-Za-z])|"
    r"(?<![A-Za-z])(?:Africa|America|Asia|Atlantic|Australia|Europe|Indian|Pacific)/[A-Za-z_+.-]+)",
    re.IGNORECASE,
)


def _line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def _style_value(block: str, property_name: str) -> str | None:
    resolved: str | None = None
    for style in _styles(block):
        for declaration in style.split(";"):
            if ":" not in declaration:
                continue
            name, value = declaration.split(":", 1)
            if name.strip().lower() == property_name:
                resolved = value.strip()
    return resolved


def _styles(block: str) -> list[str]:
    return [match.group("value") for match in STYLE_RE.finditer(block)]


def _font_sizes(block: str) -> list[int]:
    sizes: list[int] = []
    for style in _styles(block):
        sizes.extend(int(value) for value in FONT_SIZE_RE.findall(style))
    return sizes


def _colors(block: str) -> list[str]:
    colors: list[str] = []
    for style in _styles(block):
        value = _style_value(f'<x style="{style}">', "color")
        if value:
            colors.append(value.upper())
    return colors


def _has_exact_token(block: str, *, size: int, color: str) -> tuple[bool, bool]:
    sizes = _font_sizes(block)
    colors = _colors(block)
    return (
        bool(sizes) and all(value == size for value in sizes),
        bool(colors) and all(value == color.upper() for value in colors),
    )


def _plain_text(block: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub("", block))).strip()


def _semantic_role(block: str) -> str | None:
    opening_tag = block.split(">", 1)[0]
    match = ROLE_RE.search(opening_tag)
    return match.group("role").lower() if match else None


def _is_aligned(block: str, expected: str) -> bool:
    opening_tag = block.split(">", 1)[0]
    values = [match.group(2).lower() for match in ALIGN_RE.finditer(opening_tag)]
    for style in _styles(block):
        for declaration in style.split(";"):
            if ":" not in declaration:
                continue
            name, value = declaration.split(":", 1)
            if name.strip().lower() == "text-align":
                values.append(value.strip().lower())
    return bool(values) and all(value == expected for value in values)


def _resolved_roles(profile: str) -> dict[str, dict[str, object]]:
    roles = {name: dict(value) for name, value in DOCS_ROLES.items()}
    if profile == "default":
        return roles
    profiles = STYLE_CONTRACT["docs"].get("profiles", {})
    if profile not in profiles:
        raise ValueError(f"unknown Docs style profile: {profile}")
    selected = profiles[profile]
    for role_name, override in selected.get("role_overrides", {}).items():
        if role_name not in roles:
            raise ValueError(f"unknown role override in Docs style profile {profile}: {role_name}")
        roles[role_name].update(override)
    for role_name, role in selected.get("additional_roles", {}).items():
        roles[role_name] = dict(role)
    return roles


def _profile_resolution(source: str, profile: str | None) -> tuple[str, bool]:
    requested = "auto" if profile is None else profile
    if requested not in {"auto", "default", "index"}:
        return requested, False
    if INDEX_LAYOUT_RE.search(source):
        return "index", requested == "default"
    selected = "default" if requested == "auto" else requested
    return selected, requested == "index"


def _detect_profile(source: str, profile: str | None) -> str:
    return _profile_resolution(source, profile)[0]


def _valid_publication_date(value: str) -> bool:
    match = DATE_RE.fullmatch(value)
    if match is None:
        return False
    try:
        date(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
        )
    except ValueError:
        return False
    return True


def validate_source(source: str, profile: str | None = None) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    seen: set[tuple[str, int]] = set()

    def add(code: str, message: str, offset: int) -> None:
        line = _line_number(source, offset)
        key = (code, line)
        if key not in seen:
            findings.append({"code": code, "message": message, "line": line})
            seen.add(key)

    selected_profile, profile_mismatch = _profile_resolution(source, profile)
    if profile_mismatch:
        marker = INDEX_LAYOUT_RE.search(source)
        add(
            "docs_profile_mismatch",
            "The Docs style profile and layout marker disagree: index requires data-kstack-layout=index, and that marker requires the index profile.",
            marker.start() if marker else 0,
        )
    try:
        roles = _resolved_roles(selected_profile)
    except ValueError as error:
        add("docs_profile_invalid", str(error), 0)
        return findings

    for match in STYLE_RE.finditer(source):
        style = match.group("value")
        if re.search(r"(?:^|;)\s*font-family\s*:", style, re.IGNORECASE):
            add(
                "docs_font_family_forbidden",
                "Company Docs must use its native font stack; font-family is forbidden.",
                match.start(),
            )
        for color_match in COLOR_PROPERTY_RE.finditer(style):
            color = color_match.group(1).strip().upper()
            if color not in ALLOWED_COLORS:
                add(
                    "docs_color_not_allowed",
                    f"Color {color} is outside the KStack palette.",
                    match.start(),
                )
        for color in HEX_RE.findall(style):
            if color.upper() not in ALLOWED_COLORS:
                add(
                    "docs_color_not_allowed",
                    f"Color {color.upper()} is outside the KStack palette.",
                    match.start(),
                )
        if re.search(r"gradient\s*\(", style, re.IGNORECASE):
            add("docs_color_not_allowed", "Gradients are forbidden in company Docs source.", match.start())

    h1_matches = list(re.finditer(r"<h1\b[^>]*>.*?</h1>", source, re.IGNORECASE | re.DOTALL))
    if len(h1_matches) != 1:
        add("docs_h1_count_mismatch", "Docs source must contain exactly one h1.", 0)
    for match in h1_matches:
        block = match.group(0)
        expected = roles["h1"]
        size_ok, color_ok = _has_exact_token(block, size=expected["size"], color=expected["color"])
        if not size_ok:
            add("docs_h1_font_size_mismatch", f"Docs h1 must use editor size {expected['size']}.", match.start())
        if not color_ok:
            add("docs_h1_color_mismatch", f"Docs h1 must use {expected['color']}.", match.start())
        if not _is_aligned(block, expected["alignment"]):
            add("docs_h1_alignment_mismatch", f"Docs h1 must be {expected['alignment']} aligned.", match.start())
        title_text = _plain_text(block)
        if TIMEZONE_RE.search(title_text):
            add(
                "docs_masthead_timezone_forbidden",
                "Formal Docs masthead text must not display a timezone.",
                match.start(),
            )
        if re.search(r"（V[^）]+）|\b20\d{2}\s*年|｜", title_text):
            add(
                "docs_body_title_repeats_metadata",
                "The body h1 must omit version/date metadata; keep those in the document title or kicker.",
                match.start(),
            )

    if len(h1_matches) == 1:
        semantic_paragraphs: dict[str, list[re.Match[str]]] = {
            "subtitle": [],
            "date": [],
        }
        for paragraph in re.finditer(r"<p\b[^>]*>.*?</p>", source, re.IGNORECASE | re.DOTALL):
            role_match = ROLE_RE.search(paragraph.group(0).split(">", 1)[0])
            if role_match and role_match.group("role").lower() in semantic_paragraphs:
                semantic_paragraphs[role_match.group("role").lower()].append(paragraph)
        for role, paragraphs in semantic_paragraphs.items():
            if len(paragraphs) != 1:
                add(
                    f"docs_{role}_count_mismatch",
                    f"Formal Docs masthead must contain exactly one {role} paragraph.",
                    h1_matches[0].start(),
                )
            elif paragraphs[0].start() < h1_matches[0].end():
                add(
                    "docs_masthead_order_mismatch",
                    "Docs masthead order must be H1, subtitle, then publication date.",
                    paragraphs[0].start(),
                )
        if (
            len(semantic_paragraphs["subtitle"]) == 1
            and len(semantic_paragraphs["date"]) == 1
        ):
            if (
                semantic_paragraphs["subtitle"][0].start()
                > semantic_paragraphs["date"][0].start()
            ):
                add(
                    "docs_masthead_order_mismatch",
                    "Docs masthead order must be H1, subtitle, then publication date.",
                    semantic_paragraphs["date"][0].start(),
                )
        if len(semantic_paragraphs["date"]) == 1:
            publication_date = semantic_paragraphs["date"][0]
            if not _valid_publication_date(_plain_text(publication_date.group(0))):
                add(
                    "docs_date_format_invalid",
                    "Publication date must be one standalone valid calendar date in YYYY 年 M 月 D 日 format, with no timezone or suffix.",
                    publication_date.start(),
                )
        if len(semantic_paragraphs["subtitle"]) == 1:
            title_text = _plain_text(h1_matches[0].group(0))
            subtitle_text = _plain_text(semantic_paragraphs["subtitle"][0].group(0))
            if subtitle_text and re.search(
                rf"[：:]\s*{re.escape(subtitle_text)}\s*$",
                title_text,
            ):
                add(
                    "docs_h1_repeats_subtitle",
                    "The H1 must not recombine the subtitle when a separate subtitle role is present.",
                    h1_matches[0].start(),
                )

    h2_matches = list(
        re.finditer(r"<h2\b[^>]*>.*?</h2>", source, re.IGNORECASE | re.DOTALL)
    )
    numbered_entry_h2_matches = [
        match
        for match in h2_matches
        if NUMBERED_HUB_ENTRY_RE.fullmatch(_plain_text(match.group(0)))
    ]
    explicit_entry_h2_matches = [
        match
        for match in h2_matches
        if _semantic_role(match.group(0)) == HUB_ENTRY_ROLE
    ]
    global_intro_h2_matches = [
        match
        for match in h2_matches
        if _semantic_role(match.group(0)) == GLOBAL_INTRO_ROLE
    ]
    if (
        selected_profile == "index"
        and INDEX_LAYOUT_RE.search(source)
        and (
            len(explicit_entry_h2_matches) >= 2
            or len(numbered_entry_h2_matches) >= 2
        )
    ):
        uses_explicit_entry_roles = len(explicit_entry_h2_matches) >= 2
        intro_h2: re.Match[str] | None = None
        if uses_explicit_entry_roles:
            first_entry = explicit_entry_h2_matches[0]
            if (
                len(global_intro_h2_matches) == 1
                and h2_matches[0] is global_intro_h2_matches[0]
                and global_intro_h2_matches[0].start() < first_entry.start()
            ):
                intro_h2 = global_intro_h2_matches[0]
        else:
            first_h2 = h2_matches[0]
            if not NUMBERED_HUB_ENTRY_RE.fullmatch(_plain_text(first_h2.group(0))):
                intro_h2 = first_h2

        if intro_h2 is None:
            first_entry = (
                explicit_entry_h2_matches[0]
                if uses_explicit_entry_roles
                else numbered_entry_h2_matches[0]
            )
            add(
                "docs_index_global_intro_order_mismatch",
                "A multi-entry index or hub must place one global introduction h2 before its entries. Non-numbered entries require data-kstack-role=hub-entry and the introduction requires data-kstack-role=global-intro.",
                first_entry.start(),
            )
        else:
            intro_index = h2_matches.index(intro_h2)
            next_h2 = h2_matches[intro_index + 1]
            intro_source = source[intro_h2.end() : next_h2.start()]
            has_body = False
            for paragraph in re.finditer(
                r"<p\b[^>]*>.*?</p>",
                intro_source,
                re.IGNORECASE | re.DOTALL,
            ):
                opening_tag = paragraph.group(0).split(">", 1)[0]
                role_match = ROLE_RE.search(opening_tag)
                if (
                    role_match
                    and role_match.group("role").lower() == "body"
                    and _plain_text(paragraph.group(0))
                ):
                    has_body = True
                    break
            if not has_body:
                add(
                    "docs_index_global_intro_body_missing",
                    "A multi-entry index or hub global introduction must contain a non-empty body paragraph before the next h2.",
                    intro_h2.start(),
                )

    for match in h2_matches:
        block = match.group(0)
        expected = roles["h2"]
        size_ok, color_ok = _has_exact_token(block, size=expected["size"], color=expected["color"])
        if not size_ok:
            add("docs_h2_font_size_mismatch", f"Docs h2 must use editor size {expected['size']}.", match.start())
        if not color_ok:
            add("docs_h2_color_mismatch", f"Docs h2 must use {expected['color']}.", match.start())
        if not _is_aligned(block, expected["alignment"]):
            add("docs_h2_alignment_mismatch", f"Docs h2 must be {expected['alignment']} aligned.", match.start())

    for match in re.finditer(r"<h3\b[^>]*>.*?</h3>", source, re.IGNORECASE | re.DOTALL):
        block = match.group(0)
        expected = roles["h3"]
        size_ok, color_ok = _has_exact_token(block, size=expected["size"], color=expected["color"])
        if not size_ok:
            add("docs_h3_font_size_mismatch", f"Docs h3 must use editor size {expected['size']}.", match.start())
        if not color_ok:
            add("docs_h3_color_mismatch", f"Docs h3 must use {expected['color']}.", match.start())
        if not _is_aligned(block, expected["alignment"]):
            add("docs_h3_alignment_mismatch", f"Docs h3 must be {expected['alignment']} aligned.", match.start())

    for level in (4, 5, 6):
        for match in re.finditer(rf"<h{level}\b[^>]*>.*?</h{level}>", source, re.IGNORECASE | re.DOTALL):
            if not _is_aligned(match.group(0), "left"):
                add(
                    f"docs_h{level}_alignment_mismatch",
                    f"Docs h{level} must be left aligned.",
                    match.start(),
                )

    for match in re.finditer(r"<li\b[^>]*>.*?</li>", source, re.IGNORECASE | re.DOTALL):
        block = match.group(0)
        if CONTINUATION_VARIANT_RE.search(block.split(">", 1)[0]):
            if not _is_aligned(block, "left"):
                add(
                    "docs_continuation_alignment_mismatch",
                    "Docs continuation entries must be left aligned.",
                    match.start(),
                )
            for role in ("entry-title", "note", "body"):
                role_span = re.search(
                    rf'<span\b[^>]*data-kstack-role="{re.escape(role)}"[^>]*>.*?</span>',
                    block,
                    re.IGNORECASE | re.DOTALL,
                )
                if role_span is None:
                    add(
                        "docs_continuation_role_missing",
                        f"Docs continuation entries require a {role} span.",
                        match.start(),
                    )
                    continue
                expected = roles[role]
                size_ok, color_ok = _has_exact_token(
                    role_span.group(0),
                    size=expected["size"],
                    color=expected["color"],
                )
                if not size_ok:
                    add(
                        f"docs_continuation_{role.replace('-', '_')}_font_size_mismatch",
                        f"Docs continuation {role} text must use editor size {expected['size']}.",
                        match.start(),
                    )
                if not color_ok:
                    add(
                        f"docs_continuation_{role.replace('-', '_')}_color_mismatch",
                        f"Docs continuation {role} text must use {expected['color']}.",
                        match.start(),
                    )
            continue
        expected = roles["list"]
        size_ok, color_ok = _has_exact_token(block, size=expected["size"], color=expected["color"])
        if not size_ok:
            add("docs_list_font_size_mismatch", f"Docs list text must use editor size {expected['size']}.", match.start())
        if not color_ok:
            add("docs_list_color_mismatch", f"Docs list text must use {expected['color']}.", match.start())
        if not _is_aligned(block, expected["alignment"]):
            add(
                "docs_list_alignment_mismatch",
                f"Docs list text must be {expected['alignment']} aligned.",
                match.start(),
            )

    paragraph_tokens = {
        role: (definition["size"], definition["color"], f"docs_{role.replace('-', '_')}")
        for role, definition in roles.items()
        if role not in {"h1", "h2", "h3", "list"}
    }
    semantic_signatures = {
        (int(definition["size"]), str(definition["color"]).upper())
        for role_name, definition in roles.items()
        if role_name in {"kicker", "subtitle", "date", "lead", "caption", "source"}
    }
    for match in re.finditer(r"<p\b[^>]*>.*?</p>", source, re.IGNORECASE | re.DOTALL):
        block = match.group(0)
        text = _plain_text(block)
        if not text:
            continue
        role_match = ROLE_RE.search(block.split(">", 1)[0])
        role = role_match.group("role").lower() if role_match else None
        if role in {"kicker", "subtitle", "date"} and TIMEZONE_RE.search(text):
            add(
                "docs_masthead_timezone_forbidden",
                "Formal Docs masthead text must not display a timezone.",
                match.start(),
            )
        if role and role not in paragraph_tokens:
            add("docs_paragraph_role_invalid", f"Unknown data-kstack-role: {role}.", match.start())
            continue

        if role is None:
            sizes = _font_sizes(block)
            colors = _colors(block)
            looks_special = (
                len(h1_matches) == 1 and match.start() < h1_matches[0].start()
            ) or (
                len(sizes) == 1
                and len(colors) == 1
                and (sizes[0], colors[0]) in semantic_signatures
            )
            if looks_special:
                add(
                    "docs_paragraph_role_missing",
                    "Kicker, subtitle, date, lead, caption, and source paragraphs require data-kstack-role.",
                    match.start(),
                )
            role = "body"

        expected_size, expected_color, code_prefix = paragraph_tokens[role]
        size_ok, color_ok = _has_exact_token(block, size=expected_size, color=expected_color)
        if not size_ok:
            add(
                f"{code_prefix}_font_size_mismatch",
                f"Docs {role} text must use editor size {expected_size}.",
                match.start(),
            )
        if not color_ok:
            add(
                f"{code_prefix}_color_mismatch",
                f"Docs {role} text must use {expected_color}.",
                match.start(),
            )
        expected_alignment = roles[role]["alignment"]
        if not _is_aligned(block, expected_alignment):
            add(
                f"{code_prefix}_alignment_mismatch",
                f"Docs {role} text must be {expected_alignment} aligned.",
                match.start(),
            )

    return findings


def validation_result(source: str | bytes, profile: str | None = None) -> dict[str, object]:
    raw_source = source.encode("utf-8") if isinstance(source, str) else source
    decoded_source = raw_source.decode("utf-8")
    selected_profile = _detect_profile(decoded_source, profile)
    findings = validate_source(decoded_source, profile)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        "schema_version": "kstack.docs-style-validation.v1",
        "plugin_version": manifest["version"],
        "profile": selected_profile,
        "source_sha256": hashlib.sha256(raw_source).hexdigest(),
        "validator_sha256": hashlib.sha256(VALIDATOR_PATH.read_bytes()).hexdigest(),
        "style_contract_sha256": hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        "ok": not findings,
        "finding_count": len(findings),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate KStack company-Docs typography and color tokens.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--profile", choices=("auto", "default", "index"), default="auto")
    args = parser.parse_args()

    result = validation_result(args.path.read_bytes(), args.profile)
    result["source_path"] = args.path.name
    findings = result["findings"]
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            print(f"{finding['code']}:{finding['line']}: {finding['message']}")
    else:
        print("Docs style validation: PASS")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

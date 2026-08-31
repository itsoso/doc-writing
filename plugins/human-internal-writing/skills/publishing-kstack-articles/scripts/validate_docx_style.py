#!/usr/bin/env python3
"""Validate machine-checkable KStack DOCX page and paragraph-style invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{" + NS["w"] + "}"
VALIDATOR_PATH = Path(__file__).resolve()
CONTRACT_PATH = VALIDATOR_PATH.parents[1] / "assets" / "kstack-style.v1.json"
MANIFEST_PATH = VALIDATOR_PATH.parents[3] / ".codex-plugin" / "plugin.json"
CONTRACT_LOCATOR = f"assets/{CONTRACT_PATH.name}"
ROLE_ALIASES = {
    "kicker": {"kicker", "kstackkicker", "kstack kicker"},
    "title": {"title", "kstacktitle"},
    "subtitle": {"subtitle", "kstacksubtitle"},
    "date": {"date", "kstackdate", "kstackpublicationdate"},
    "h2": {"heading2", "heading 2", "kstackh2"},
    "h3": {"heading3", "heading 3", "kstackh3"},
    "body": {"body", "bodytext", "body text", "normal", "kstackbody"},
    "list": {"list", "kstacklist", "kstack list"},
    "lead": {"lead", "kstacklead"},
    "caption": {"caption", "kstackcaption"},
    "source": {"source", "kstacksource"},
}


def _contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _resolved_roles(contract: dict[str, Any], profile: str) -> dict[str, dict[str, Any]]:
    roles = {role: dict(tokens) for role, tokens in contract["roles"].items()}
    if profile == "default":
        return roles
    profile_contract = contract.get("profiles", {}).get(profile)
    if profile_contract is None:
        raise ValueError(f"Unknown DOCX style profile: {profile}")
    for role, overrides in profile_contract.get("role_overrides", {}).items():
        if role not in roles:
            raise ValueError(f"DOCX profile {profile} overrides unknown role: {role}")
        roles[role].update(overrides)
    return roles


def _attr(node: ET.Element | None, name: str) -> str | None:
    return None if node is None else node.get(W + name)


def _normalize(value: str | None) -> str:
    return "".join((value or "").casefold().split())


def _role(style_id: str, style_name: str) -> str | None:
    candidates = {_normalize(style_id), _normalize(style_name)}
    for role, aliases in ROLE_ALIASES.items():
        if candidates & {_normalize(alias) for alias in aliases}:
            return role
    return None


def _properties(container: ET.Element | None) -> dict[str, Any]:
    if container is None:
        return {}
    size = _attr(container.find("w:sz", NS), "val")
    color = _attr(container.find("w:color", NS), "val")
    fonts = container.find("w:rFonts", NS)
    return {
        "size_half_points": int(size) if size and size.isdigit() else None,
        "color": ("#" + color.upper()) if color and color.lower() != "auto" else None,
        "font_east_asia": _attr(fonts, "eastAsia"),
        "font_ascii": _attr(fonts, "ascii"),
        "font_hansi": _attr(fonts, "hAnsi"),
    }


def _paragraph_properties(container: ET.Element | None) -> dict[str, Any]:
    if container is None:
        return {}
    spacing = container.find("w:spacing", NS)
    return {
        "alignment": _attr(container.find("w:jc", NS), "val"),
        "line": _attr(spacing, "line"),
        "after": _attr(spacing, "after"),
    }


def _style_map(styles_root: ET.Element) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for style in styles_root.findall("w:style", NS):
        if _attr(style, "type") != "paragraph":
            continue
        style_id = _attr(style, "styleId") or ""
        name = _attr(style.find("w:name", NS), "val") or ""
        result[style_id] = {
            "role": _role(style_id, name),
            **_paragraph_properties(style.find("w:pPr", NS)),
            **_properties(style.find("w:rPr", NS)),
        }
    return result


def validate_docx(path: Path, profile: str = "default") -> dict[str, Any]:
    findings: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        if code not in {item["code"] for item in findings}:
            findings.append({"code": code, "message": message})

    contract = _contract()["docx"]
    try:
        expected_roles = _resolved_roles(contract, profile)
    except ValueError as error:
        add("docx_profile_invalid", str(error))
        return _result(path, findings, {"style_contract": CONTRACT_LOCATOR}, profile)

    try:
        with zipfile.ZipFile(path) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
            styles = ET.fromstring(archive.read("word/styles.xml"))
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError):
        add("docx_style_structure_invalid", "DOCX must contain readable document.xml and styles.xml.")
        return _result(path, findings, {"style_contract": CONTRACT_LOCATOR}, profile)

    style_map = _style_map(styles)
    used: dict[str, dict[str, Any]] = {}
    role_instances: dict[str, list[dict[str, Any]]] = {}
    ordered_roles: list[str] = []
    for paragraph in document.findall(".//w:body//w:p", NS):
        ppr = paragraph.find("w:pPr", NS)
        style_id = _attr(ppr.find("w:pStyle", NS) if ppr is not None else None, "val") or ""
        base = dict(style_map.get(style_id, {}))
        role = base.get("role")
        if role:
            direct_p = _paragraph_properties(ppr)
            direct_r = _properties(ppr.find("w:rPr", NS) if ppr is not None else None)
            base.update(
                {
                    key: value
                    for key, value in {**direct_p, **direct_r}.items()
                    if value is not None
                }
            )
            used.setdefault(role, base)
            role_instances.setdefault(role, []).append(base)
            for run in paragraph.findall(".//w:r", NS):
                direct_run = _properties(run.find("w:rPr", NS))
                if any(value is not None for value in direct_run.values()):
                    effective_run = dict(base)
                    effective_run.update(
                        {
                            key: value
                            for key, value in direct_run.items()
                            if value is not None
                        }
                    )
                    role_instances[role].append(effective_run)
            ordered_roles.append(role)

    for required in ("title", "subtitle", "date", "body"):
        if required not in used:
            add(f"docx_{required}_style_missing", f"DOCX must use a semantic {required} paragraph style.")
    masthead_roles = [role for role in ordered_roles if role != "kicker"]
    if masthead_roles[:3] != ["title", "subtitle", "date"]:
        add("docx_masthead_order_mismatch", "The first three styled roles must be title, subtitle, and date.")

    alignment_map = {"justify": "both", "left": "left", "center": "center"}
    profiles = contract["font_profiles"]
    title = used.get("title", {})
    selected_profile = next(
        (
            name
            for name, profile in profiles.items()
            if title.get("font_east_asia") == profile["heading"]
            and title.get("font_ascii") == profile["latin"]
            and title.get("font_hansi") == profile["latin"]
        ),
        None,
    )
    if selected_profile is None:
        add("docx_title_font_mismatch", "DOCX title must declare one complete supported WPS font profile.")

    heading_roles = {"kicker", "title", "subtitle", "h2", "h3"}
    for role, actuals in role_instances.items():
        expected = expected_roles.get(role)
        if not expected:
            continue
        for actual in actuals:
            if actual.get("size_half_points") != int(expected["size_pt"] * 2):
                add(f"docx_{role}_font_size_mismatch", f"DOCX {role} must use {expected['size_pt']} pt.")
            if actual.get("color") != expected["color"].upper():
                add(f"docx_{role}_color_mismatch", f"DOCX {role} must use {expected['color']}.")
            if expected["alignment"] != "role-specific" and actual.get("alignment") != alignment_map[expected["alignment"]]:
                add(f"docx_{role}_alignment_mismatch", f"DOCX {role} must be {expected['alignment']} aligned.")
            if selected_profile is not None:
                font_profile = profiles[selected_profile]
                expected_east_asia = (
                    font_profile["heading"]
                    if role in heading_roles
                    else font_profile["body"]
                )
                if (
                    actual.get("font_east_asia") != expected_east_asia
                    or actual.get("font_ascii") != font_profile["latin"]
                    or actual.get("font_hansi") != font_profile["latin"]
                ):
                    add(f"docx_{role}_font_mismatch", f"DOCX {role} must use the complete {selected_profile} font profile.")

    body = used.get("body")
    if body:
        if body.get("line") != "360":
            add("docx_body_line_spacing_mismatch", "DOCX body line spacing must be 1.5 lines.")
        if body.get("after") != "120":
            add("docx_body_after_spacing_mismatch", "DOCX body paragraph-after spacing must be 6 pt.")

    section = document.find(".//w:sectPr", NS)
    page = section.find("w:pgSz", NS) if section is not None else None
    margins = section.find("w:pgMar", NS) if section is not None else None
    if page is None or _attr(page, "w") != "11906" or _attr(page, "h") != "16838":
        add("docx_page_size_mismatch", "DOCX page size must be A4 portrait.")
    expected_margin = 1191
    if margins is None or any(
        abs(int(_attr(margins, edge) or 0) - expected_margin) > 2
        for edge in ("top", "right", "bottom", "left")
    ):
        add("docx_margin_mismatch", "DOCX margins must be 21 mm on all sides.")

    evidence = {
        "roles_checked": sorted(used),
        "style_contract": CONTRACT_LOCATOR,
        "font_profile": selected_profile,
        "profile": profile,
    }
    return _result(path, findings, evidence, profile)


def _result(
    path: Path,
    findings: list[dict[str, str]],
    evidence: dict[str, Any],
    profile: str,
) -> dict[str, Any]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        "schema_version": "kstack.docx-style-validation.v1",
        "plugin_version": manifest["version"],
        "profile": profile,
        "docx_path": path.name,
        "docx_sha256": digest,
        "validator_sha256": hashlib.sha256(VALIDATOR_PATH.read_bytes()).hexdigest(),
        "style_contract_sha256": hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        "ok": not findings,
        "finding_count": len(findings),
        "findings": findings,
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate KStack DOCX style and page invariants."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--profile", choices=("default", "index"), default="default")
    args = parser.parse_args()
    result = validate_docx(args.path, profile=args.profile)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            "DOCX style validation: PASS"
            if result["ok"]
            else "\n".join(item["code"] for item in result["findings"])
        )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

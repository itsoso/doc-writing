#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import posixpath
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from validate_docx_style import validate_docx


IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
RENDER_SUFFIXES = {".jpeg", ".jpg", ".png", ".webp"}
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
MARKDOWN_INLINE_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
HTML_TAG = re.compile(r"<[^>]+>")
WORD_TEXT_TAG = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
WORD_PARAGRAPH_TAG = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
WORD_BODY_TAG = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body"
WORD_HYPERLINK_TAG = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hyperlink"
WORD_RELATIONSHIP_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
WORD_RELATIONSHIP_EMBED = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
WORD_HYPERLINK_ANCHOR = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}anchor"
PACKAGE_RELATIONSHIP = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
DRAWING_IMAGE_REFERENCE = "{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
VML_IMAGE_REFERENCE = "{urn:schemas-microsoft-com:vml}imagedata"
EXPECTED_DOCS_TARGET_KIND = "drive"
EXPECTED_DOCS_TARGET_LABEL = "我的个人主页"
ANCHOR_SEPARATORS = re.compile(r"[\s:：|｜·—–\-_,，。？！!?;；\"“”'‘’（）()【】\[\]]+")
H1_DATE_METADATA = re.compile(
    r"(?:19|20|21)\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日"
)
H1_SUBTITLE_SEPARATOR = re.compile(r"[|｜]")


@dataclass
class Verification:
    reason_codes: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    def fail(self, reason_code: str) -> None:
        if reason_code not in self.reason_codes:
            self.reason_codes.append(reason_code)

    @property
    def ok(self) -> bool:
        return not self.reason_codes


def existing_files(directory: Path, suffixes: set[str]) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in suffixes and path.stat().st_size > 0
    )


def markdown_images(markdown: Path) -> tuple[list[Path], list[str]]:
    text = markdown.read_text(encoding="utf-8")
    local_images: list[Path] = []
    remote_images: list[str] = []
    for raw_target in MARKDOWN_IMAGE.findall(text):
        target = raw_target.strip()
        if target.startswith("<") and ">" in target:
            target = target[1 : target.index(">")]
        else:
            target = target.split(maxsplit=1)[0]
        if target.startswith(("http://", "https://")):
            remote_images.append(target)
            continue
        if target.startswith("data:"):
            remote_images.append(target)
            continue
        local_images.append((markdown.parent / unquote(target)).resolve())
    return local_images, remote_images


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_anchor(text: str) -> str:
    return ANCHOR_SEPARATORS.sub("", text).casefold()


def normalized_semantic_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        unicodedata.normalize("NFKC", html.unescape(text)),
    ).strip()


def normalized_link_target(raw_target: str) -> str:
    target = html.unescape(raw_target.strip())
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target.strip())


def markdown_inline_semantics(text: str) -> tuple[str, list[tuple[str, str]]]:
    links: list[tuple[str, str]] = []
    without_images = MARKDOWN_INLINE_IMAGE.sub("", text)

    def replace_link(match: re.Match[str]) -> str:
        label = re.sub(r"[`*_~]", "", match.group(1))
        links.append(
            (
                normalized_semantic_text(label),
                normalized_link_target(match.group(2)),
            )
        )
        return label

    rendered = MARKDOWN_LINK.sub(replace_link, without_images)
    rendered = re.sub(r"`([^`]*)`", r"\1", rendered)
    rendered = re.sub(r"[*_~]", "", rendered)
    rendered = HTML_TAG.sub("", rendered)
    return normalized_semantic_text(rendered), links


def markdown_semantics(
    markdown: Path,
) -> tuple[str | None, str | None, list[str], list[tuple[str, str]]]:
    title: str | None = None
    title_index: int | None = None
    blocks: list[str] = []
    links: list[tuple[str, str]] = []
    source = re.sub(
        r"<!--.*?-->",
        "",
        markdown.read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    in_fence = False
    fence_lines: list[str] = []
    paragraph_lines: list[str] = []

    def append_block(raw_block: str) -> None:
        rendered, block_links = markdown_inline_semantics(raw_block)
        if rendered:
            blocks.append(rendered)
        links.extend(block_links)

    def flush_paragraph() -> None:
        if paragraph_lines:
            append_block(" ".join(paragraph_lines))
            paragraph_lines.clear()

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if line.startswith("```") or line.startswith("~~~"):
            flush_paragraph()
            if in_fence:
                append_block("\n".join(fence_lines))
                fence_lines.clear()
            in_fence = not in_fence
            continue
        if in_fence:
            fence_lines.append(raw_line)
            continue
        if not line:
            flush_paragraph()
            continue
        if line == "---" or MARKDOWN_INLINE_IMAGE.fullmatch(line):
            flush_paragraph()
            continue
        if line.startswith("#"):
            flush_paragraph()
            heading = line.lstrip("#").strip()
            if title is None and line.startswith("# "):
                rendered, heading_links = markdown_inline_semantics(heading)
                title = rendered or None
                title_index = len(blocks)
                if rendered:
                    blocks.append(rendered)
                links.extend(heading_links)
            else:
                append_block(heading)
            continue
        line = re.sub(r"^>\s*", "", line)
        list_match = re.match(r"^(?:[-+*]|\d+[.)])\s+(.+)$", line)
        if list_match:
            flush_paragraph()
            append_block(list_match.group(1))
            continue
        paragraph_lines.append(line)

    flush_paragraph()
    if fence_lines:
        append_block("\n".join(fence_lines))

    subtitle: str | None = None
    if title_index is not None and title_index + 2 < len(blocks):
        possible_subtitle = blocks[title_index + 1]
        possible_date = blocks[title_index + 2]
        if re.fullmatch(
            r"(?:19|20|21)\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日",
            possible_date,
        ):
            subtitle = possible_subtitle
    return title, subtitle, blocks, links


def h1_combines_release_metadata(title: str | None, subtitle: str | None) -> bool:
    if not title:
        return False
    if H1_DATE_METADATA.search(title) or H1_SUBTITLE_SEPARATOR.search(title):
        return True
    if subtitle:
        expected = normalized_anchor(subtitle)
        for separator in re.finditer(r"[:：]", title):
            if normalized_anchor(title[separator.end() :]) == expected:
                return True
    return False


def docx_relationships(archive: zipfile.ZipFile) -> dict[str, str]:
    relationships: dict[str, str] = {}
    try:
        relationship_root = ET.fromstring(
            archive.read("word/_rels/document.xml.rels")
        )
    except (KeyError, ET.ParseError):
        relationship_root = None
    if relationship_root is not None:
        for relationship in relationship_root.iter(PACKAGE_RELATIONSHIP):
            relationship_id = relationship.get("Id")
            target = relationship.get("Target")
            if relationship_id and target:
                relationships[relationship_id] = normalized_link_target(target)
    return relationships


def docx_semantics(
    archive: zipfile.ZipFile,
    root: ET.Element,
) -> tuple[list[str], list[tuple[str, str]]]:
    relationships = docx_relationships(archive)

    body = root.find(f".//{WORD_BODY_TAG}")
    if body is None:
        return [], []
    blocks: list[str] = []
    links: list[tuple[str, str]] = []
    for paragraph in body.iter(WORD_PARAGRAPH_TAG):
        paragraph_text = normalized_semantic_text(
            "".join(node.text or "" for node in paragraph.iter(WORD_TEXT_TAG))
        )
        if paragraph_text:
            blocks.append(paragraph_text)
        for hyperlink in paragraph.iter(WORD_HYPERLINK_TAG):
            label = normalized_semantic_text(
                "".join(node.text or "" for node in hyperlink.iter(WORD_TEXT_TAG))
            )
            relationship_id = hyperlink.get(WORD_RELATIONSHIP_ID)
            anchor = hyperlink.get(WORD_HYPERLINK_ANCHOR)
            target = relationships.get(relationship_id or "")
            if target is None and anchor:
                target = f"#{anchor}"
            links.append((label, target or ""))
    return blocks, links


def docx_image_targets(
    archive: zipfile.ZipFile,
    root: ET.Element,
) -> list[str]:
    relationships = docx_relationships(archive)
    targets: list[str] = []
    for node in root.iter():
        if node.tag not in {DRAWING_IMAGE_REFERENCE, VML_IMAGE_REFERENCE}:
            continue
        relationship_id = node.get(WORD_RELATIONSHIP_EMBED) or node.get(
            WORD_RELATIONSHIP_ID
        )
        target = relationships.get(relationship_id or "")
        if not target:
            targets.append("")
            continue
        targets.append(posixpath.normpath(posixpath.join("word", target)))
    return targets


def verify_docx(
    docx: Path,
    markdown_image_count: int,
    markdown_blocks: list[str],
    markdown_links: list[tuple[str, str]],
    result: Verification,
) -> None:
    if not docx.is_file():
        result.fail("docx_missing")
        return
    if docx.stat().st_size == 0:
        result.fail("docx_empty")
        return
    try:
        with zipfile.ZipFile(docx) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                result.fail("docx_structure_invalid")
                return
            try:
                root = ET.fromstring(archive.read("word/document.xml"))
            except (ET.ParseError, KeyError):
                result.fail("docx_structure_invalid")
                return
            docx_blocks, docx_links = docx_semantics(archive, root)
            result.evidence["markdown_semantic_block_count"] = len(markdown_blocks)
            result.evidence["docx_semantic_block_count"] = len(docx_blocks)
            result.evidence["markdown_link_count"] = len(markdown_links)
            result.evidence["docx_link_count"] = len(docx_links)
            if not docx_blocks:
                result.fail("docx_content_empty")
            if docx_blocks != markdown_blocks:
                result.fail("docx_content_mismatch")
            if docx_links != markdown_links:
                result.fail("docx_link_target_mismatch")
            media = [
                name
                for name in names
                if name.startswith("word/media/") and not name.endswith("/")
            ]
            image_targets = docx_image_targets(archive, root)
            result.evidence["docx_media_count"] = len(media)
            result.evidence["docx_image_reference_count"] = len(image_targets)
            if (
                len(image_targets) != markdown_image_count
                or "" in image_targets
                or set(image_targets) != set(media)
            ):
                result.fail("docx_image_count_mismatch")
            if markdown_image_count and (not media or not image_targets):
                result.fail("docx_images_missing")
    except (OSError, zipfile.BadZipFile):
        result.fail("docx_structure_invalid")


def verify_render_review(
    review_path: Path,
    docx: Path,
    render_dir: Path,
    rendered_pages: list[Path],
    result: Verification,
) -> None:
    if not review_path.is_file():
        result.fail("render_review_missing")
        return
    review = read_json(review_path)
    if review is None or review.get("schema_version") != "kstack.render-review.v1":
        result.fail("render_review_invalid")
        return

    mismatch = review.get("reviewed") is not True or not docx.is_file()
    if docx.is_file() and review.get("docxSha256") != sha256_file(docx):
        mismatch = True

    expected_pages = [
        {
            "path": page.relative_to(render_dir).as_posix(),
            "sha256": sha256_file(page),
        }
        for page in rendered_pages
    ]
    declared_pages = review.get("pages")
    if not isinstance(declared_pages, list) or declared_pages != expected_pages:
        mismatch = True
    if mismatch:
        result.fail("render_review_mismatch")
        return
    result.evidence["render_reviewed"] = True


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def verify_docs_receipt(
    receipt_path: Path | None,
    source_image_count: int,
    markdown: Path,
    docs_source: Path | None,
    markdown_title: str | None,
    result: Verification,
) -> None:
    if docs_source is None or not docs_source.is_file():
        result.fail("docs_source_missing")
    if receipt_path is None or not receipt_path.is_file():
        result.fail("docs_receipt_missing")
        return

    receipt = read_json(receipt_path)
    if receipt is None or receipt.get("schema_version") != "kstack.docs-publication.v1":
        result.fail("docs_receipt_invalid")
        return

    target = receipt.get("target")
    if (
        not isinstance(target, dict)
        or target.get("kind") != EXPECTED_DOCS_TARGET_KIND
        or target.get("label") != EXPECTED_DOCS_TARGET_LABEL
        or not target.get("id")
    ):
        result.fail("docs_target_mismatch")

    document = receipt.get("document")
    if not isinstance(document, dict) or not document.get("docId") or not document.get("url"):
        result.fail("docs_document_unresolved")
    else:
        operation = document.get("operation")
        if operation not in {"create", "update"}:
            result.fail("docs_operation_invalid")
        elif operation == "create" and document.get("viewModel") != "A3":
            result.fail("docs_page_model_mismatch")
        elif operation == "update" and document.get("viewModel") not in {None, "A3"}:
            result.fail("docs_page_model_mismatch")

    release = receipt.get("release")
    if (
        not isinstance(release, dict)
        or not release.get("title")
        or not release.get("version")
        or not markdown.is_file()
        or docs_source is None
        or not docs_source.is_file()
        or release.get("markdownSha256") != sha256_file(markdown)
        or release.get("docsSourceSha256") != sha256_file(docs_source)
    ):
        result.fail("docs_release_hash_mismatch")
    elif markdown_title and release.get("title") != markdown_title:
        result.fail("docs_release_metadata_mismatch")

    authorization = receipt.get("authorization")
    if not isinstance(authorization, dict) or authorization.get("confirmed") is not True:
        result.fail("docs_authorization_missing")

    readback = receipt.get("readback")
    if not isinstance(readback, dict) or readback.get("verified") is not True:
        result.fail("docs_readback_unverified")
        return
    if (
        readback.get("titleMatched") is not True
        or readback.get("bodyMatched") is not True
        or readback.get("linksMatched") is not True
    ):
        result.fail("docs_readback_mismatch")
    image_count = readback.get("imageCount")
    if type(image_count) is not int or image_count != source_image_count:
        result.fail("docs_image_count_mismatch")


def verify_release(args: argparse.Namespace) -> dict[str, Any]:
    result = Verification()
    markdown = args.markdown.resolve()
    docx = args.docx.resolve()
    images_dir = args.images_dir.resolve() if args.images_dir is not None else None
    render_dir = args.render_dir.resolve()
    render_review = args.render_review.resolve()
    docs_source = args.docs_source.resolve() if args.docs_source is not None else None

    if not markdown.is_file():
        result.fail("markdown_missing")
        local_images: list[Path] = []
    elif markdown.stat().st_size == 0:
        result.fail("markdown_empty")
        local_images = []
    else:
        try:
            local_images, remote_images = markdown_images(markdown)
            (
                markdown_title,
                markdown_subtitle,
                markdown_blocks,
                markdown_links,
            ) = markdown_semantics(markdown)
        except (OSError, UnicodeError):
            result.fail("markdown_unreadable")
            local_images = []
            remote_images = []
            markdown_title = None
            markdown_subtitle = None
            markdown_blocks = []
            markdown_links = []

    if not markdown.is_file() or markdown.stat().st_size == 0:
        markdown_title = None
        markdown_subtitle = None
        markdown_blocks = []
        markdown_links = []
        remote_images = []

    if h1_combines_release_metadata(markdown_title, markdown_subtitle):
        result.fail("markdown_h1_metadata_combined")

    source_images = existing_files(images_dir, IMAGE_SUFFIXES) if images_dir else []
    result.evidence["source_image_count"] = len(source_images)
    referenced_images = local_images
    result.evidence["markdown_image_reference_count"] = len(referenced_images)
    result.evidence["markdown_remote_image_count"] = len(remote_images)
    if remote_images:
        result.fail("markdown_remote_image_unsupported")
    if referenced_images and (images_dir is None or not images_dir.is_dir()):
        result.fail("images_directory_missing")

    for image in local_images:
        if not image.is_file() or image.stat().st_size == 0:
            result.fail("markdown_image_missing")
        if images_dir is not None:
            try:
                image.relative_to(images_dir)
            except ValueError:
                result.fail("markdown_image_outside_directory")

    verify_docx(
        docx,
        len(referenced_images),
        markdown_blocks,
        markdown_links,
        result,
    )
    if docx.is_file() and docx.stat().st_size > 0:
        docx_style = validate_docx(docx, profile=args.docx_profile)
        result.evidence["docx_style_findings"] = [
            item["code"] for item in docx_style["findings"]
        ]
        result.evidence["docx_style_contract"] = docx_style["evidence"].get(
            "style_contract"
        )
        result.evidence["docx_style_profile"] = docx_style["profile"]
        result.evidence["docx_style_provenance"] = {
            "plugin_version": docx_style["plugin_version"],
            "docx_sha256": docx_style["docx_sha256"],
            "validator_sha256": docx_style["validator_sha256"],
            "style_contract_sha256": docx_style["style_contract_sha256"],
        }
        if not docx_style["ok"]:
            result.fail("docx_style_invalid")

    rendered_pages = existing_files(render_dir, RENDER_SUFFIXES)
    result.evidence["rendered_page_count"] = len(rendered_pages)
    if not rendered_pages:
        result.fail("rendered_pages_missing")
    verify_render_review(render_review, docx, render_dir, rendered_pages, result)

    if args.require_docs:
        verify_docs_receipt(
            args.docs_receipt,
            len(referenced_images),
            markdown,
            docs_source,
            markdown_title,
            result,
        )

    status = "blocked"
    if result.ok:
        status = "docs_evidence_consistent" if args.require_docs else "word_verified"

    return {
        "ok": result.ok,
        "status": status,
        "remote_verified": False if args.require_docs else None,
        "reason_codes": result.reason_codes,
        "evidence": result.evidence,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify KStack article release artifacts and optional Docs publication evidence."
    )
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--docx", type=Path, required=True)
    parser.add_argument("--docx-profile", choices=("default", "index"), default="default")
    parser.add_argument("--images-dir", type=Path)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--render-review", type=Path, required=True)
    parser.add_argument("--require-docs", action="store_true")
    parser.add_argument("--docs-receipt", type=Path)
    parser.add_argument("--docs-source", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = verify_release(args)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status={payload['status']}")
        for reason_code in payload["reason_codes"]:
            print(f"- {reason_code}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

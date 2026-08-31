from __future__ import annotations

import hashlib
import html
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VERIFY_SCRIPT = SCRIPT_DIR / "verify_release.py"


def write_minimal_docx(
    path: Path,
    *,
    include_image: bool = True,
    paragraphs: tuple[str, ...] = ("示例文章", "用于验证的副标题", "2099 年 1 月 2 日", "正文。"),
    body_size: int = 22,
    hyperlink: tuple[str, str] | None = None,
    hyperlink_is_plain_text: bool = False,
    media_count: int | None = None,
    image_reference_count: int | None = None,
    subtitle_alignment: str = "center",
    date_alignment: str = "center",
) -> None:
    def paragraph_xml(paragraph: str, style: str) -> str:
        if hyperlink is not None and paragraph == hyperlink[0] and not hyperlink_is_plain_text:
            return (
                f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
                '<w:hyperlink r:id="rIdLink1">'
                f'<w:r><w:t>{html.escape(paragraph)}</w:t></w:r>'
                '</w:hyperlink></w:p>'
            )
        return (
            f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
            f'<w:r><w:t>{html.escape(paragraph)}</w:t></w:r></w:p>'
        )

    actual_media_count = (
        (1 if include_image else 0) if media_count is None else media_count
    )
    actual_reference_count = (
        actual_media_count
        if image_reference_count is None
        else image_reference_count
    )
    image_blocks = "".join(
        '<w:p><w:r><w:drawing>'
        f'<a:blip r:embed="rIdImage{index + 1}"/>'
        "</w:drawing></w:r></w:p>"
        for index in range(actual_reference_count)
    )
    relationships: list[str] = []
    if hyperlink is not None and not hyperlink_is_plain_text:
        relationships.append(
            '<Relationship Id="rIdLink1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" '
            f'Target="{html.escape(hyperlink[1])}" TargetMode="External"/>'
        )
    relationships.extend(
        '<Relationship '
        f'Id="rIdImage{index + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
        f'Target="media/image{index + 1}.png"/>'
        for index in range(actual_media_count)
    )

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        role_styles = ["Title", "Subtitle", "KStackDate"] + ["BodyText"] * max(0, len(paragraphs) - 3)
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><w:body>'
            + "".join(
                paragraph_xml(paragraph, style)
                for paragraph, style in zip(paragraphs, role_styles)
            )
            + image_blocks
            + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1191" w:right="1191" w:bottom="1191" w:left="1191"/></w:sectPr>'
            + "</w:body></w:document>",
        )
        archive.writestr(
            "word/styles.xml",
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="PingFang SC"/><w:sz w:val="48"/><w:color w:val="17344B"/></w:rPr></w:style>'
            f'<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:pPr><w:jc w:val="{subtitle_alignment}"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="PingFang SC"/><w:sz w:val="28"/><w:color w:val="5F6368"/></w:rPr></w:style>'
            f'<w:style w:type="paragraph" w:styleId="KStackDate"><w:name w:val="KStack Date"/><w:pPr><w:jc w:val="{date_alignment}"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Songti SC"/><w:sz w:val="18"/><w:color w:val="5F6368"/></w:rPr></w:style>'
            f'<w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text"/><w:pPr><w:jc w:val="left"/><w:spacing w:line="360" w:lineRule="auto" w:after="120"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Songti SC"/><w:sz w:val="{body_size}"/><w:color w:val="202124"/></w:rPr></w:style>'
            "</w:styles>",
        )
        if relationships:
            archive.writestr(
                "word/_rels/document.xml.rels",
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + "".join(relationships)
                + "</Relationships>",
            )
        for index in range(actual_media_count):
            archive.writestr(f"word/media/image{index + 1}.png", b"docx-image")


class ReleaseVerifierCliTests(unittest.TestCase):
    def setUp(self) -> None:
        if (
            self._testMethodName != "test_verifier_script_exists"
            and not VERIFY_SCRIPT.is_file()
        ):
            self.skipTest("release verifier is not implemented yet")

    def make_release(self, root: Path) -> dict[str, Path]:
        images = root / "images"
        renders = root / "rendered-pages"
        images.mkdir()
        renders.mkdir()

        markdown = root / "article.md"
        markdown.write_text(
            "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n正文。\n\n![示例图](images/example.png)\n",
            encoding="utf-8",
        )
        (images / "example.png").write_bytes(b"source-image")
        docs_source = root / "article-docs-source.md"
        docs_source.write_text(
            '<h1 style="text-align:center">示例文章</h1>\n<p>正文。</p>\n',
            encoding="utf-8",
        )
        (renders / "page-001.png").write_bytes(b"rendered-page")

        docx = root / "article.docx"
        write_minimal_docx(docx)
        render_review = root / "render-review.json"
        render_review.write_text(
            json.dumps(
                {
                    "schema_version": "kstack.render-review.v1",
                    "docxSha256": hashlib.sha256(docx.read_bytes()).hexdigest(),
                    "reviewed": True,
                    "pages": [
                        {
                            "path": "page-001.png",
                            "sha256": hashlib.sha256(
                                (renders / "page-001.png").read_bytes()
                            ).hexdigest(),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return {
            "markdown": markdown,
            "docx": docx,
            "images": images,
            "renders": renders,
            "render_review": render_review,
            "docs_source": docs_source,
        }

    def run_verifier(
        self,
        release: dict[str, Path],
        *extra: str,
        include_images_dir: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        image_args = (
            ["--images-dir", str(release["images"])] if include_images_dir else []
        )
        return subprocess.run(
            [
                sys.executable,
                str(VERIFY_SCRIPT),
                "--markdown",
                str(release["markdown"]),
                "--docx",
                str(release["docx"]),
                *image_args,
                "--render-dir",
                str(release["renders"]),
                "--render-review",
                str(release["render_review"]),
                "--docs-source",
                str(release["docs_source"]),
                "--json",
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_verifier_script_exists(self) -> None:
        self.assertTrue(VERIFY_SCRIPT.is_file(), "release verifier has not been implemented")

    def test_valid_word_release_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            result = self.run_verifier(release)

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual("word_verified", payload["status"])
        self.assertEqual(1, payload["evidence"]["source_image_count"])
        self.assertEqual(1, payload["evidence"]["rendered_page_count"])

    def test_semantic_equality_ignores_markdown_emphasis_formatting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n**正文。**\n\n![示例图](images/example.png)\n",
                encoding="utf-8",
            )
            result = self.run_verifier(release)

        self.assertEqual(0, result.returncode, result.stdout)

    def test_valid_index_word_release_uses_explicit_index_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            write_minimal_docx(
                release["docx"],
                subtitle_alignment="left",
                date_alignment="left",
            )
            docx_sha256 = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = docx_sha256
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release, "--docx-profile", "index")

        self.assertEqual(0, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("index", payload["evidence"]["docx_style_profile"])
        self.assertEqual(
            docx_sha256,
            payload["evidence"]["docx_style_provenance"]["docx_sha256"],
        )

    def test_matching_markdown_and_docx_link_target_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n[说明](https://example.com/right)\n\n![示例图](images/example.png)\n",
                encoding="utf-8",
            )
            write_minimal_docx(
                release["docx"],
                paragraphs=("示例文章", "用于验证的副标题", "2099 年 1 月 2 日", "说明"),
                hyperlink=("说明", "https://example.com/right"),
            )
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertEqual(0, result.returncode, result.stdout)

    def test_html_layout_comments_are_not_content_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n<!-- pagebreak -->\n\n正文。\n\n![示例图](images/example.png)\n",
                encoding="utf-8",
            )
            result = self.run_verifier(release)

        self.assertEqual(0, result.returncode, result.stdout)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_missing_docx_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["docx"].unlink()
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("docx_missing", payload["reason_codes"])

    def test_invalid_docx_style_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            write_minimal_docx(release["docx"], body_size=24)
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("docx_style_invalid", payload["reason_codes"])
        self.assertIn("docx_body_font_size_mismatch", payload["evidence"]["docx_style_findings"])

    def test_docx_must_contain_all_current_markdown_body_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n正文。\n\n这是更新后新增的第二段。\n\n![示例图](images/example.png)\n",
                encoding="utf-8",
            )
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("docx_content_mismatch", payload["reason_codes"])

    def test_canonical_h1_must_not_combine_subtitle_and_date(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例主标题：示例副标题｜2099 年 1 月 2 日\n\n正文。\n",
                encoding="utf-8",
            )
            write_minimal_docx(
                release["docx"],
                paragraphs=(
                    "示例主标题",
                    "示例副标题",
                    "用于验证元数据拆分的说明",
                    "2099 年 1 月 2 日",
                    "正文。",
                ),
            )
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(
                release["docx"].read_bytes()
            ).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "markdown_h1_metadata_combined",
            json.loads(result.stdout)["reason_codes"],
        )

    def test_h1_must_not_repeat_the_parsed_subtitle_after_colon(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例主标题：示例副标题\n\n示例副标题\n\n2099 年 1 月 2 日\n\n正文。\n\n![示例图](images/example.png)\n",
                encoding="utf-8",
            )
            write_minimal_docx(
                release["docx"],
                paragraphs=(
                    "示例主标题：示例副标题",
                    "示例副标题",
                    "2099 年 1 月 2 日",
                    "正文。",
                ),
            )
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("markdown_h1_metadata_combined", json.loads(result.stdout)["reason_codes"])

    def test_legitimate_h1_colon_is_allowed_when_suffix_is_not_the_subtitle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章：为什么要做这件事\n\n另一个副标题\n\n2099 年 1 月 2 日\n\n正文。\n\n![示例图](images/example.png)\n",
                encoding="utf-8",
            )
            write_minimal_docx(
                release["docx"],
                paragraphs=(
                    "示例文章：为什么要做这件事",
                    "另一个副标题",
                    "2099 年 1 月 2 日",
                    "正文。",
                ),
            )
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertEqual(0, result.returncode, result.stdout)

    def test_docx_rejects_extra_body_text_not_present_in_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            write_minimal_docx(
                release["docx"],
                paragraphs=(
                    "示例文章",
                    "用于验证的副标题",
                    "2099 年 1 月 2 日",
                    "正文。",
                    "未经授权的新增段落。",
                ),
            )
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("docx_content_mismatch", json.loads(result.stdout)["reason_codes"])

    def test_docx_rejects_extra_embedded_media(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            write_minimal_docx(
                release["docx"], media_count=2, image_reference_count=1
            )
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("docx_image_count_mismatch", json.loads(result.stdout)["reason_codes"])

    def test_docx_rejects_wrong_markdown_link_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n[说明](https://example.com/right)\n\n![示例图](images/example.png)\n",
                encoding="utf-8",
            )
            write_minimal_docx(
                release["docx"],
                paragraphs=("示例文章", "用于验证的副标题", "2099 年 1 月 2 日", "说明"),
                hyperlink=("说明", "https://example.com/wrong"),
            )
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("docx_link_target_mismatch", json.loads(result.stdout)["reason_codes"])

    def test_docx_rejects_missing_markdown_hyperlink_even_when_label_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n[说明](https://example.com/right)\n\n![示例图](images/example.png)\n",
                encoding="utf-8",
            )
            write_minimal_docx(
                release["docx"],
                paragraphs=("示例文章", "用于验证的副标题", "2099 年 1 月 2 日", "说明"),
                hyperlink=("说明", "https://example.com/right"),
                hyperlink_is_plain_text=True,
            )
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("docx_link_target_mismatch", json.loads(result.stdout)["reason_codes"])

    def test_text_only_word_release_does_not_require_images_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n正文。\n",
                encoding="utf-8",
            )
            write_minimal_docx(release["docx"], include_image=False)
            review = json.loads(release["render_review"].read_text(encoding="utf-8"))
            review["docxSha256"] = hashlib.sha256(release["docx"].read_bytes()).hexdigest()
            release["render_review"].write_text(json.dumps(review), encoding="utf-8")
            result = self.run_verifier(release, include_images_dir=False)

        self.assertEqual(0, result.returncode, result.stdout)

    def test_image_bearing_word_release_requires_images_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            result = self.run_verifier(release, include_images_dir=False)

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "images_directory_missing",
            json.loads(result.stdout)["reason_codes"],
        )

    def test_remote_markdown_image_blocks_self_contained_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["markdown"].write_text(
                "# 示例文章\n\n正文。\n\n![远程图](https://example.com/image.png)\n",
                encoding="utf-8",
            )
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("markdown_remote_image_unsupported", payload["reason_codes"])

    def test_missing_rendered_pages_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            (release["renders"] / "page-001.png").unlink()
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("rendered_pages_missing", payload["reason_codes"])

    def test_missing_render_review_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            release["render_review"].unlink()
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("render_review_missing", payload["reason_codes"])

    def test_render_review_must_match_docx_and_page_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            (release["renders"] / "page-001.png").write_bytes(b"tampered-page")
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("render_review_mismatch", payload["reason_codes"])

    def test_unresolved_markdown_image_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            (release["images"] / "example.png").unlink()
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("markdown_image_missing", payload["reason_codes"])

    def test_markdown_image_outside_release_image_directory_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            outside = root / "outside.png"
            outside.write_bytes(b"outside-image")
            release["markdown"].write_text(
                "# 示例文章\n\n![错误位置](outside.png)\n",
                encoding="utf-8",
            )
            result = self.run_verifier(release)

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("markdown_image_outside_directory", payload["reason_codes"])

    def test_required_docs_publication_without_receipt_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = self.make_release(Path(temp_dir))
            result = self.run_verifier(release, "--require-docs")

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("docs_receipt_missing", payload["reason_codes"])

    def test_unverified_docs_readback_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            receipt = root / "docs-publication.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schema_version": "kstack.docs-publication.v1",
                        "target": {"kind": "wiki", "id": "target_example", "label": "示例发布区"},
                        "document": {
                            "docId": "doc_example",
                            "url": "https://docs.example/doc",
                            "operation": "create",
                            "viewModel": "A3",
                        },
                        "authorization": {"confirmed": True},
                        "readback": {"verified": False},
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_verifier(
                release,
                "--require-docs",
                "--docs-receipt",
                str(receipt),
            )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("docs_readback_unverified", payload["reason_codes"])

    def test_verified_docs_publication_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            receipt = root / "docs-publication.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schema_version": "kstack.docs-publication.v1",
                        "target": {"kind": "drive", "id": "folder_target", "label": "我的个人主页"},
                        "document": {
                            "docId": "doc_example",
                            "url": "https://docs.example/doc",
                            "operation": "create",
                            "viewModel": "A3",
                        },
                        "release": {
                            "title": "示例文章",
                            "version": "v1",
                            "markdownSha256": hashlib.sha256(
                                release["markdown"].read_bytes()
                            ).hexdigest(),
                            "docsSourceSha256": hashlib.sha256(
                                release["docs_source"].read_bytes()
                            ).hexdigest(),
                        },
                        "authorization": {"confirmed": True},
                        "readback": {
                            "verified": True,
                            "titleMatched": True,
                            "bodyMatched": True,
                            "linksMatched": True,
                            "imageCount": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_verifier(
                release,
                "--require-docs",
                "--docs-receipt",
                str(receipt),
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("docs_evidence_consistent", payload["status"])
        self.assertIs(payload["remote_verified"], False)

    def test_docs_readback_requires_links_to_match(self) -> None:
        for links_matched in (False, None):
            with self.subTest(links_matched=links_matched), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                release = self.make_release(root)
                receipt = root / "docs-publication.json"
                readback = {
                    "verified": True,
                    "titleMatched": True,
                    "bodyMatched": True,
                    "imageCount": 1,
                }
                if links_matched is not None:
                    readback["linksMatched"] = links_matched
                receipt.write_text(
                    json.dumps(
                        {
                            "schema_version": "kstack.docs-publication.v1",
                            "target": {
                                "kind": "drive",
                                "id": "folder_target",
                                "label": "我的个人主页",
                            },
                            "document": {
                                "docId": "doc_example",
                                "url": "https://docs.example/doc",
                                "operation": "create",
                                "viewModel": "A3",
                            },
                            "release": {
                                "title": "示例文章",
                                "version": "v1",
                                "markdownSha256": hashlib.sha256(
                                    release["markdown"].read_bytes()
                                ).hexdigest(),
                                "docsSourceSha256": hashlib.sha256(
                                    release["docs_source"].read_bytes()
                                ).hexdigest(),
                            },
                            "authorization": {"confirmed": True},
                            "readback": readback,
                        }
                    ),
                    encoding="utf-8",
                )
                result = self.run_verifier(
                    release,
                    "--require-docs",
                    "--docs-receipt",
                    str(receipt),
                )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("docs_readback_mismatch", json.loads(result.stdout)["reason_codes"])

    def test_docs_readback_image_count_must_exactly_match_source_expectation(self) -> None:
        for source_image_count, remote_image_count in ((1, 2), (0, 1)):
            with (
                self.subTest(
                    source_image_count=source_image_count,
                    remote_image_count=remote_image_count,
                ),
                tempfile.TemporaryDirectory() as temp_dir,
            ):
                root = Path(temp_dir)
                release = self.make_release(root)
                include_images_dir = source_image_count > 0
                if source_image_count == 0:
                    release["markdown"].write_text(
                        "# 示例文章\n\n用于验证的副标题\n\n2099 年 1 月 2 日\n\n正文。\n",
                        encoding="utf-8",
                    )
                    write_minimal_docx(release["docx"], include_image=False)
                    review = json.loads(
                        release["render_review"].read_text(encoding="utf-8")
                    )
                    review["docxSha256"] = hashlib.sha256(
                        release["docx"].read_bytes()
                    ).hexdigest()
                    release["render_review"].write_text(
                        json.dumps(review), encoding="utf-8"
                    )

                receipt = root / "docs-publication.json"
                receipt.write_text(
                    json.dumps(
                        {
                            "schema_version": "kstack.docs-publication.v1",
                            "target": {
                                "kind": "drive",
                                "id": "folder_target",
                                "label": "我的个人主页",
                            },
                            "document": {
                                "docId": "doc_example",
                                "url": "https://docs.example/doc",
                                "operation": "create",
                                "viewModel": "A3",
                            },
                            "release": {
                                "title": "示例文章",
                                "version": "v1",
                                "markdownSha256": hashlib.sha256(
                                    release["markdown"].read_bytes()
                                ).hexdigest(),
                                "docsSourceSha256": hashlib.sha256(
                                    release["docs_source"].read_bytes()
                                ).hexdigest(),
                            },
                            "authorization": {"confirmed": True},
                            "readback": {
                                "verified": True,
                                "titleMatched": True,
                                "bodyMatched": True,
                                "linksMatched": True,
                                "imageCount": remote_image_count,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                result = self.run_verifier(
                    release,
                    "--require-docs",
                    "--docs-receipt",
                    str(receipt),
                    include_images_dir=include_images_dir,
                )

            self.assertNotEqual(0, result.returncode)
            self.assertIn(
                "docs_image_count_mismatch",
                json.loads(result.stdout)["reason_codes"],
            )

    def test_docs_publication_rejects_non_a3_page_model(self) -> None:
        for page_model in ("A4", None):
            with self.subTest(page_model=page_model), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                release = self.make_release(root)
                receipt = root / "docs-publication.json"
                document = {
                    "docId": "doc_example",
                    "url": "https://docs.example/doc",
                    "operation": "create",
                }
                if page_model is not None:
                    document["viewModel"] = page_model
                receipt.write_text(
                    json.dumps(
                        {
                            "schema_version": "kstack.docs-publication.v1",
                            "target": {
                                "kind": "drive",
                                "id": "folder_target",
                                "label": "我的个人主页",
                            },
                            "document": document,
                            "release": {
                                "title": "示例文章",
                                "version": "v1",
                                "markdownSha256": hashlib.sha256(
                                    release["markdown"].read_bytes()
                                ).hexdigest(),
                                "docsSourceSha256": hashlib.sha256(
                                    release["docs_source"].read_bytes()
                                ).hexdigest(),
                            },
                            "authorization": {"confirmed": True},
                            "readback": {
                                "verified": True,
                                "titleMatched": True,
                                "bodyMatched": True,
                                "linksMatched": True,
                                "imageCount": 1,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                result = self.run_verifier(
                    release,
                    "--require-docs",
                    "--docs-receipt",
                    str(receipt),
                )

            self.assertNotEqual(0, result.returncode)
            payload = json.loads(result.stdout)
            self.assertIn("docs_page_model_mismatch", payload["reason_codes"])

    def test_docs_update_may_omit_unchanged_unread_page_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            receipt = root / "docs-publication.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schema_version": "kstack.docs-publication.v1",
                        "target": {
                            "kind": "drive",
                            "id": "folder_target",
                            "label": "我的个人主页",
                        },
                        "document": {
                            "docId": "doc_example",
                            "url": "https://docs.example/doc",
                            "operation": "update",
                        },
                        "release": {
                            "title": "示例文章",
                            "version": "v2",
                            "markdownSha256": hashlib.sha256(
                                release["markdown"].read_bytes()
                            ).hexdigest(),
                            "docsSourceSha256": hashlib.sha256(
                                release["docs_source"].read_bytes()
                            ).hexdigest(),
                        },
                        "authorization": {"confirmed": True},
                        "readback": {
                            "verified": True,
                            "titleMatched": True,
                            "bodyMatched": True,
                            "linksMatched": True,
                            "imageCount": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_verifier(
                release,
                "--require-docs",
                "--docs-receipt",
                str(receipt),
            )

        self.assertEqual(0, result.returncode, result.stdout)

    def test_docs_receipt_binds_docs_source_not_docx(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            receipt = root / "docs-publication.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schema_version": "kstack.docs-publication.v1",
                        "target": {
                            "kind": "drive",
                            "id": "folder_target",
                            "label": "我的个人主页",
                        },
                        "document": {
                            "docId": "doc_example",
                            "url": "https://docs.example/doc",
                            "operation": "create",
                            "viewModel": "A3",
                        },
                        "release": {
                            "title": "示例文章",
                            "version": "v1",
                            "markdownSha256": hashlib.sha256(
                                release["markdown"].read_bytes()
                            ).hexdigest(),
                            "docxSha256": hashlib.sha256(
                                release["docx"].read_bytes()
                            ).hexdigest(),
                        },
                        "authorization": {"confirmed": True},
                        "readback": {
                            "verified": True,
                            "titleMatched": True,
                            "bodyMatched": True,
                            "linksMatched": True,
                            "imageCount": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_verifier(
                release,
                "--require-docs",
                "--docs-receipt",
                str(receipt),
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "docs_release_hash_mismatch",
            json.loads(result.stdout)["reason_codes"],
        )

    def test_required_docs_source_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            release["docs_source"].unlink()
            result = self.run_verifier(release, "--require-docs")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("docs_source_missing", json.loads(result.stdout)["reason_codes"])

    def test_editable_source_image_does_not_inflate_remote_image_expectation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            (release["images"] / "loop.svg").write_text("<svg/>", encoding="utf-8")
            receipt = root / "docs-publication.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schema_version": "kstack.docs-publication.v1",
                        "target": {"kind": "drive", "id": "folder_target", "label": "我的个人主页"},
                        "document": {
                            "docId": "doc_example",
                            "url": "https://docs.example/doc",
                            "operation": "create",
                            "viewModel": "A3",
                        },
                        "release": {
                            "title": "示例文章",
                            "version": "v1",
                            "markdownSha256": hashlib.sha256(
                                release["markdown"].read_bytes()
                            ).hexdigest(),
                            "docsSourceSha256": hashlib.sha256(
                                release["docs_source"].read_bytes()
                            ).hexdigest(),
                        },
                        "authorization": {"confirmed": True},
                        "readback": {
                            "verified": True,
                            "titleMatched": True,
                            "bodyMatched": True,
                            "linksMatched": True,
                            "imageCount": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_verifier(
                release,
                "--require-docs",
                "--docs-receipt",
                str(receipt),
            )

        self.assertEqual(0, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(2, payload["evidence"]["source_image_count"])
        self.assertEqual(1, payload["evidence"]["markdown_image_reference_count"])

    def test_wrong_docs_target_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            receipt = root / "docs-publication.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schema_version": "kstack.docs-publication.v1",
                        "target": {"kind": "wiki", "id": "target_other", "label": "其他示例区"},
                        "document": {
                            "docId": "doc_example",
                            "url": "https://docs.example/doc",
                            "operation": "create",
                            "viewModel": "A3",
                        },
                        "release": {
                            "title": "示例文章",
                            "version": "v1",
                            "markdownSha256": hashlib.sha256(
                                release["markdown"].read_bytes()
                            ).hexdigest(),
                            "docsSourceSha256": hashlib.sha256(
                                release["docs_source"].read_bytes()
                            ).hexdigest(),
                        },
                        "authorization": {"confirmed": True},
                        "readback": {
                            "verified": True,
                            "titleMatched": True,
                            "bodyMatched": True,
                            "linksMatched": True,
                            "imageCount": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_verifier(
                release,
                "--require-docs",
                "--docs-receipt",
                str(receipt),
            )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("docs_target_mismatch", payload["reason_codes"])

    def test_docs_receipt_must_bind_current_release_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            release = self.make_release(root)
            receipt = root / "docs-publication.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schema_version": "kstack.docs-publication.v1",
                        "target": {"kind": "drive", "id": "folder_target", "label": "我的个人主页"},
                        "document": {
                            "docId": "doc_example",
                            "url": "https://docs.example/doc",
                            "operation": "create",
                            "viewModel": "A3",
                        },
                        "release": {
                            "title": "示例文章",
                            "version": "v1",
                            "markdownSha256": "wrong",
                            "docsSourceSha256": "wrong",
                        },
                        "authorization": {"confirmed": True},
                        "readback": {
                            "verified": True,
                            "titleMatched": True,
                            "bodyMatched": True,
                            "linksMatched": True,
                            "imageCount": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_verifier(
                release,
                "--require-docs",
                "--docs-receipt",
                str(receipt),
            )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("docs_release_hash_mismatch", payload["reason_codes"])


if __name__ == "__main__":
    unittest.main()

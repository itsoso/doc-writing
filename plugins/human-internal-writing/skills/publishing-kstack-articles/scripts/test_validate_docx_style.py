from __future__ import annotations

import importlib.util
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_docx_style.py")


def write_docx(
    path: Path,
    *,
    body_size: int = 22,
    body_font: str = "Songti SC",
    title_alignment: str = "center",
    h2_alignment: str = "left",
    h3_alignment: str = "left",
    h3_color: str = "2E74B5",
    margin: int = 1191,
    include_kicker: bool = False,
    kicker_alignment: str = "left",
    subtitle_alignment: str = "center",
    date_alignment: str = "center",
    body_alignment: str = "left",
    second_body_alignment: str | None = None,
    body_run_size: int | None = None,
) -> None:
    kicker = '<w:p><w:pPr><w:pStyle w:val="KStackKicker"/></w:pPr><w:r><w:t>技术与组织实践</w:t></w:r></w:p>' if include_kicker else ""
    body_run_properties = f'<w:rPr><w:sz w:val="{body_run_size}"/></w:rPr>' if body_run_size is not None else ""
    document = f'''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
      {kicker}
      <w:p><w:pPr><w:pStyle w:val="Title"/></w:pPr><w:r><w:t>主标题</w:t></w:r></w:p>
      <w:p><w:pPr><w:pStyle w:val="Subtitle"/></w:pPr><w:r><w:t>副标题</w:t></w:r></w:p>
      <w:p><w:pPr><w:pStyle w:val="KStackDate"/></w:pPr><w:r><w:t>2099 年 1 月 2 日</w:t></w:r></w:p>
      <w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr><w:r><w:t>章节</w:t></w:r></w:p>
      <w:p><w:pPr><w:pStyle w:val="Heading3"/></w:pPr><w:r><w:t>小节</w:t></w:r></w:p>
      <w:p><w:pPr><w:pStyle w:val="BodyText"/></w:pPr><w:r>{body_run_properties}<w:t>正文。</w:t></w:r></w:p>
      {f'<w:p><w:pPr><w:pStyle w:val="BodyText"/><w:jc w:val="{second_body_alignment}"/></w:pPr><w:r><w:t>第二段正文。</w:t></w:r></w:p>' if second_body_alignment else ''}
      <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="{margin}" w:right="{margin}" w:bottom="{margin}" w:left="{margin}"/></w:sectPr>
    </w:body></w:document>'''
    styles = f'''<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:style w:type="paragraph" w:styleId="KStackKicker"><w:name w:val="KStack Kicker"/><w:pPr><w:jc w:val="{kicker_alignment}"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="PingFang SC"/><w:sz w:val="20"/><w:color w:val="2E74B5"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:jc w:val="{title_alignment}"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="PingFang SC"/><w:sz w:val="48"/><w:color w:val="17344B"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:pPr><w:jc w:val="{subtitle_alignment}"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="PingFang SC"/><w:sz w:val="28"/><w:color w:val="5F6368"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="KStackDate"><w:name w:val="KStack Date"/><w:pPr><w:jc w:val="{date_alignment}"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="{body_font}"/><w:sz w:val="18"/><w:color w:val="5F6368"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:pPr><w:jc w:val="{h2_alignment}"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="PingFang SC"/><w:sz w:val="32"/><w:color w:val="2E74B5"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:pPr><w:jc w:val="{h3_alignment}"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="PingFang SC"/><w:sz w:val="26"/><w:color w:val="{h3_color}"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text"/><w:pPr><w:jc w:val="{body_alignment}"/><w:spacing w:line="360" w:lineRule="auto" w:after="120"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="{body_font}"/><w:sz w:val="{body_size}"/><w:color w:val="202124"/></w:rPr></w:style>
    </w:styles>'''
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", styles)


class DocxStyleValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not SCRIPT.is_file():
            raise AssertionError("DOCX style validator is missing")
        spec = importlib.util.spec_from_file_location("validate_docx_style", SCRIPT)
        assert spec and spec.loader
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def codes(self, *, profile: str = "default", **kwargs: object) -> set[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            docx = Path(temp_dir) / "article.docx"
            write_docx(docx, **kwargs)
            return {
                item["code"]
                for item in self.module.validate_docx(docx, profile=profile)["findings"]
            }

    def validation(
        self, *, profile: str = "default", **kwargs: object
    ) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            docx = Path(temp_dir) / "article.docx"
            write_docx(docx, **kwargs)
            return self.module.validate_docx(docx, profile=profile)

    def test_valid_structural_profile_passes(self) -> None:
        self.assertEqual(set(), self.codes())

    def test_body_must_be_exactly_11_pt(self) -> None:
        self.assertIn("docx_body_font_size_mismatch", self.codes(body_size=24))

    def test_all_section_titles_must_be_left_aligned(self) -> None:
        self.assertIn("docx_h2_alignment_mismatch", self.codes(h2_alignment="center"))

    def test_margins_must_be_21_mm(self) -> None:
        self.assertIn("docx_margin_mismatch", self.codes(margin=1440))

    def test_font_profiles_may_not_be_mixed(self) -> None:
        self.assertIn("docx_body_font_mismatch", self.codes(body_font="宋体"))

    def test_optional_kicker_does_not_break_three_line_masthead_order(self) -> None:
        self.assertEqual(set(), self.codes(include_kicker=True))

    def test_body_roles_must_be_left_aligned(self) -> None:
        cases = {
            "kicker": self.codes(include_kicker=True, kicker_alignment="center"),
            "subtitle": self.codes(subtitle_alignment="left"),
            "date": self.codes(date_alignment="left"),
            "body": self.codes(body_alignment="both"),
        }
        for role, codes in cases.items():
            with self.subTest(role=role):
                self.assertIn(f"docx_{role}_alignment_mismatch", codes)

    def test_index_profile_centers_only_h1_and_uses_navy_h3(self) -> None:
        self.assertEqual(
            set(),
            self.codes(
                profile="index",
                subtitle_alignment="left",
                date_alignment="left",
                h3_color="17344B",
            ),
        )

    def test_index_profile_rejects_default_masthead_and_h3_tokens(self) -> None:
        codes = self.codes(profile="index")
        self.assertIn("docx_subtitle_alignment_mismatch", codes)
        self.assertIn("docx_date_alignment_mismatch", codes)
        self.assertIn("docx_h3_color_mismatch", codes)

    def test_index_profile_still_requires_centered_h1_and_left_body_headings(self) -> None:
        codes = self.codes(
            profile="index",
            title_alignment="left",
            subtitle_alignment="left",
            date_alignment="left",
            h2_alignment="center",
            h3_alignment="center",
            h3_color="17344B",
            body_alignment="both",
        )
        for role in ("title", "h2", "h3", "body"):
            self.assertIn(f"docx_{role}_alignment_mismatch", codes)

    def test_default_profile_remains_unchanged(self) -> None:
        codes = self.codes(
            subtitle_alignment="left",
            date_alignment="left",
            h3_color="17344B",
        )
        self.assertIn("docx_subtitle_alignment_mismatch", codes)
        self.assertIn("docx_date_alignment_mismatch", codes)
        self.assertIn("docx_h3_color_mismatch", codes)

    def test_later_paragraph_cannot_override_left_alignment(self) -> None:
        self.assertIn("docx_body_alignment_mismatch", self.codes(second_body_alignment="center"))

    def test_run_level_direct_format_cannot_override_body_size(self) -> None:
        self.assertIn("docx_body_font_size_mismatch", self.codes(body_run_size=24))

    def test_validation_evidence_does_not_serialize_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docx = root / "article.docx"
            write_docx(
                docx,
                subtitle_alignment="left",
                date_alignment="left",
                h3_color="17344B",
            )
            result = self.module.validate_docx(docx, profile="index")
            docx_sha256 = hashlib.sha256(docx.read_bytes()).hexdigest()

        self.assertEqual("article.docx", result["docx_path"])
        self.assertTrue(result["ok"])
        self.assertNotIn(str(root), str(result))
        self.assertEqual("index", result["profile"])
        self.assertEqual(docx_sha256, result["docx_sha256"])
        manifest = json.loads(
            (SCRIPT.parents[3] / ".codex-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["version"], result["plugin_version"])
        self.assertEqual(
            hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
            result["validator_sha256"],
        )
        contract = SCRIPT.parents[1] / "assets" / "kstack-style.v1.json"
        self.assertEqual(
            hashlib.sha256(contract.read_bytes()).hexdigest(),
            result["style_contract_sha256"],
        )
        self.assertEqual(
            "assets/kstack-style.v1.json",
            result["evidence"]["style_contract"],
        )

    def test_cli_accepts_index_profile_and_records_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docx = Path(temp_dir) / "index.docx"
            write_docx(
                docx,
                subtitle_alignment="left",
                date_alignment="left",
                h3_color="17344B",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(docx),
                    "--profile",
                    "index",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertEqual("index", json.loads(completed.stdout)["profile"])


if __name__ == "__main__":
    unittest.main()

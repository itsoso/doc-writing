from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_docs_style.py")
SPEC = importlib.util.spec_from_file_location("validate_docs_style", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


VALID = """
<p data-kstack-role="kicker" align="left"><span style="color: #2E74B5; font-size: 10px;">示例分类 · V3</span></p>
<h1 align="center"><span style="color: #17344B; font-size: 24px;">示例主标题</span></h1>
<p data-kstack-role="subtitle" align="center"><span style="color: #5F6368; font-size: 14px;">用于验证样式契约的副标题</span></p>
<p data-kstack-role="date" align="center"><span style="color: #5F6368; font-size: 9px;">2099 年 1 月 2 日</span></p>
<div data-block-type="highlight" data-highlight-color="blue" data-highlight-border="true">
<p data-kstack-role="lead" align="left"><span style="color: #1F4D78; font-size: 11px;">用于验证导语角色的示例文本。</span></p>
</div>
<hr>
<p align="left" style="font-size: 11px; color: #202124; text-align: left;">示例正文。</p>
<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">示例章节</span></h2>
<h3 align="left"><span style="color: #2E74B5; font-size: 13px;">示例小节</span></h3>
<ul><li align="left"><span style="font-size: 11px; color: #202124;">示例列表项。</span></li></ul>
<p data-kstack-role="caption" align="left"><span style="color: #5F6368; font-size: 9px;">示例题注。</span></p>
<p data-kstack-role="source" align="left"><span style="color: #5F6368; font-size: 9px;">示例来源说明。</span></p>
"""

INDEX_LEFT_HEADINGS = (
    '<div data-kstack-layout="index">\n'
    + VALID
    .replace('data-kstack-role="subtitle" align="center"', 'data-kstack-role="subtitle" align="left"')
    .replace('data-kstack-role="date" align="center"', 'data-kstack-role="date" align="left"')
    .replace(
        '<h3 align="left"><span style="color: #2E74B5;',
        '<h3 align="left"><span style="color: #17344B;',
    )
    + "\n</div>"
)

MULTI_MAINLINE_INDEX = """
<div data-kstack-layout="index">
<h1 align="center"><span style="color: #17344B; font-size: 24px;">示例索引</span></h1>
<p data-kstack-role="subtitle" align="left"><span style="color: #5F6368; font-size: 14px;">多条示例主线的阅读入口</span></p>
<p data-kstack-role="date" align="left"><span style="color: #5F6368; font-size: 9px;">2099 年 1 月 2 日</span></p>
<p data-kstack-role="lead" align="left"><span style="color: #1F4D78; font-size: 11px;">先理解示例整体，再选择入口。</span></p>
<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>
<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">两条示例主线共同构成一个验证闭环。</span></p>
<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">01｜示例主线甲</span></h2>
<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">示例主线甲的说明。</span></p>
<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">02｜示例主线乙</span></h2>
<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">示例主线乙的说明。</span></p>
</div>
"""

class DocsStyleContractTests(unittest.TestCase):
    def codes(self, source: str) -> set[str]:
        return {item["code"] for item in MODULE.validate_source(source)}

    def test_valid_house_style_passes(self) -> None:
        self.assertEqual(MODULE.validate_source(VALID), [])

    def test_validator_consumes_the_machine_readable_contract(self) -> None:
        contract = json.loads(MODULE.CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["palette"], MODULE.TOKENS)
        self.assertEqual(contract["docs"]["roles"], MODULE.DOCS_ROLES)

    def test_old_17px_body_is_blocked(self) -> None:
        source = VALID.replace("font-size: 11px; color: #202124; text-align: left", "font-size: 17px; color: #202124; text-align: left", 1)
        self.assertIn("docs_body_font_size_mismatch", self.codes(source))

    def test_20px_body_is_blocked(self) -> None:
        source = VALID.replace("font-size: 11px; color: #202124; text-align: left", "font-size: 20px; color: #202124; text-align: left", 1)
        self.assertIn("docs_body_font_size_mismatch", self.codes(source))

    def test_20px_list_is_blocked(self) -> None:
        source = VALID.replace("font-size: 11px; color: #202124;\">示例列表项", "font-size: 20px; color: #202124;\">示例列表项")
        self.assertIn("docs_list_font_size_mismatch", self.codes(source))

    def test_font_family_is_blocked_for_docs(self) -> None:
        source = VALID.replace("font-size: 11px; color: #202124; text-align: left", "font-family: 宋体; font-size: 11px; color: #202124; text-align: left")
        self.assertIn("docs_font_family_forbidden", self.codes(source))

    def test_unapproved_color_is_blocked(self) -> None:
        source = VALID.replace("#202124", "#FF0000", 1)
        self.assertIn("docs_color_not_allowed", self.codes(source))

    def test_body_must_use_ink_color(self) -> None:
        source = VALID.replace("font-size: 11px; color: #202124; text-align: left", "font-size: 11px; color: #17344B; text-align: left", 1)
        self.assertIn("docs_body_color_mismatch", self.codes(source))

    def test_h2_must_use_accent_blue(self) -> None:
        source = VALID.replace("color: #2E74B5; font-size: 16px;\">示例章节", "color: #17344B; font-size: 16px;\">示例章节")
        self.assertIn("docs_h2_color_mismatch", self.codes(source))

    def test_duplicate_color_uses_the_last_css_declaration(self) -> None:
        source = VALID.replace(
            'color: #17344B; font-size: 24px;">示例主标题',
            'color: #17344B; color: #2E74B5; font-size: 24px;">示例主标题',
        )
        self.assertNotIn("docs_color_not_allowed", self.codes(source))
        self.assertIn("docs_h1_color_mismatch", self.codes(source))

    def test_oversized_h1_is_blocked(self) -> None:
        source = VALID.replace("font-size: 24px;\">示例主标题", "font-size: 30px;\">示例主标题")
        self.assertIn("docs_h1_font_size_mismatch", self.codes(source))

    def test_body_title_must_not_repeat_version_or_date(self) -> None:
        source = VALID.replace("示例主标题</span></h1>", "示例主标题（V3）｜2099 年 1 月 2 日</span></h1>")
        self.assertIn("docs_body_title_repeats_metadata", self.codes(source))

    def test_visible_timezone_is_forbidden_across_the_formal_masthead(self) -> None:
        cases = {
            "kicker": VALID.replace("示例分类 · V3", "示例分类 · 北京时间"),
            "h1": VALID.replace("示例主标题", "示例主标题 GMT+08:00"),
            "subtitle": VALID.replace("用于验证样式契约的副标题", "用于验证样式契约的副标题 UTC+8"),
            "iana_timezone": VALID.replace("用于验证样式契约的副标题", "用于验证样式契约的副标题 Asia/Shanghai"),
            "date": VALID.replace("2099 年 1 月 2 日", "2099 年 1 月 2 日 CST"),
        }
        for role, source in cases.items():
            with self.subTest(role=role):
                self.assertIn("docs_masthead_timezone_forbidden", self.codes(source))

    def test_h1_must_not_recombine_a_repeated_subtitle(self) -> None:
        source = VALID.replace("示例主标题", "示例主标题：用于验证样式契约的副标题")
        self.assertIn("docs_h1_repeats_subtitle", self.codes(source))
        encoded = VALID.replace(
            "示例主标题",
            "示例主标题&#xff1a;用于验证样式契约的副标题",
        )
        self.assertIn("docs_h1_repeats_subtitle", self.codes(encoded))

    def test_masthead_roles_are_centered_and_body_roles_are_left(self) -> None:
        self.assertIn("docs_h1_alignment_mismatch", self.codes(VALID.replace('<h1 align="center">', '<h1 align="left">')))
        cases = {
            "kicker": VALID.replace('data-kstack-role="kicker" align="left"', 'data-kstack-role="kicker" align="center"'),
            "subtitle": VALID.replace('data-kstack-role="subtitle" align="center"', 'data-kstack-role="subtitle" align="left"'),
            "date": VALID.replace('data-kstack-role="date" align="center"', 'data-kstack-role="date" align="left"'),
            "lead": VALID.replace('data-kstack-role="lead" align="left"', 'data-kstack-role="lead" align="center"'),
            "body": VALID.replace('<p align="left" style="font-size: 11px; color: #202124; text-align: left;">示例正文。</p>', '<p align="center" style="font-size: 11px; color: #202124; text-align: center;">示例正文。</p>'),
            "list": VALID.replace('<li align="left">', '<li align="center">'),
            "caption": VALID.replace('data-kstack-role="caption" align="left"', 'data-kstack-role="caption" align="center"'),
            "source": VALID.replace('data-kstack-role="source" align="left"', 'data-kstack-role="source" align="center"'),
        }
        for role, source in cases.items():
            with self.subTest(role=role):
                self.assertIn(f"docs_{role}_alignment_mismatch", self.codes(source))

    def test_justified_body_is_blocked(self) -> None:
        source = VALID.replace("text-align: left", "text-align: justify", 1)
        self.assertIn("docs_body_alignment_mismatch", self.codes(source))

    def test_all_section_heading_levels_must_be_left_aligned(self) -> None:
        h2_source = VALID.replace('<h2 align="left">', '<h2 align="center">')
        h3_source = VALID.replace('<h3 align="left">', '<h3>')
        self.assertIn("docs_h2_alignment_mismatch", self.codes(h2_source))
        self.assertIn("docs_h3_alignment_mismatch", self.codes(h3_source))

    def test_kstack_masthead_and_section_alignment_profile(self) -> None:
        source = (
            VALID
        )
        self.assertEqual(MODULE.validate_source(source), [])

    def test_index_layout_only_centers_h1(self) -> None:
        self.assertEqual(MODULE.validate_source(INDEX_LEFT_HEADINGS), [])
        centered_h2 = INDEX_LEFT_HEADINGS.replace('<h2 align="left">', '<h2 align="center">')
        centered_h3 = INDEX_LEFT_HEADINGS.replace('<h3 align="left">', '<h3 align="center">')
        centered_subtitle = INDEX_LEFT_HEADINGS.replace('data-kstack-role="subtitle" align="left"', 'data-kstack-role="subtitle" align="center"')
        centered_date = INDEX_LEFT_HEADINGS.replace('data-kstack-role="date" align="left"', 'data-kstack-role="date" align="center"')
        centered_body = INDEX_LEFT_HEADINGS.replace(
            '<p align="left" style="font-size: 11px; color: #202124; text-align: left;">示例正文。</p>',
            '<p align="center" style="font-size: 11px; color: #202124; text-align: center;">示例正文。</p>',
        )
        self.assertIn("docs_h2_alignment_mismatch", self.codes(centered_h2))
        self.assertIn("docs_h3_alignment_mismatch", self.codes(centered_h3))
        self.assertIn("docs_subtitle_alignment_mismatch", self.codes(centered_subtitle))
        self.assertIn("docs_date_alignment_mismatch", self.codes(centered_date))
        self.assertIn("docs_body_alignment_mismatch", self.codes(centered_body))

    def test_multi_mainline_index_accepts_variable_global_intro_title(self) -> None:
        self.assertEqual(MODULE.validate_source(MULTI_MAINLINE_INDEX), [])
        renamed = MULTI_MAINLINE_INDEX.replace(
            "示例全局介绍",
            "另一种全局介绍标题",
        )
        self.assertEqual(MODULE.validate_source(renamed), [])

    def test_multi_mainline_index_requires_global_intro_before_mainlines(self) -> None:
        intro_heading = '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>\n'
        intro_body = '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">两条示例主线共同构成一个验证闭环。</span></p>\n'
        without_intro = MULTI_MAINLINE_INDEX.replace(intro_heading + intro_body, "")
        self.assertIn(
            "docs_index_global_intro_order_mismatch",
            self.codes(without_intro),
        )

    def test_multi_mainline_index_global_intro_requires_nonempty_body(self) -> None:
        intro_body = '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">两条示例主线共同构成一个验证闭环。</span></p>'
        empty_intro_body = '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;"></span></p>'
        source = MULTI_MAINLINE_INDEX.replace(intro_body, empty_intro_body)
        self.assertIn(
            "docs_index_global_intro_body_missing",
            self.codes(source),
        )

    def test_multi_entry_index_detects_one_digit_and_ascii_separators(self) -> None:
        intro_heading = '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>\n'
        intro_body = '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">两条示例主线共同构成一个验证闭环。</span></p>\n'
        without_intro = MULTI_MAINLINE_INDEX.replace(intro_heading + intro_body, "")
        cases = {
            "one-digit-fullwidth": without_intro.replace("01｜示例主线甲", "1｜示例主线甲").replace(
                "02｜示例主线乙", "2｜示例主线乙"
            ),
            "ascii-pipe": without_intro.replace("01｜示例主线甲", "1 | 示例主线甲").replace(
                "02｜示例主线乙", "2|示例主线乙"
            ),
        }

        for name, source in cases.items():
            with self.subTest(name=name):
                self.assertIn(
                    "docs_index_global_intro_order_mismatch",
                    self.codes(source),
                )

    def test_non_numbered_hub_entries_use_explicit_semantic_roles(self) -> None:
        marked = (
            MULTI_MAINLINE_INDEX
            .replace(
                '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>',
                '<h2 data-kstack-role="global-intro" align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>',
            )
            .replace(
                '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">01｜示例主线甲</span></h2>',
                '<h2 data-kstack-role="hub-entry" align="left"><span style="color: #2E74B5; font-size: 16px;">工程实践</span></h2>',
            )
            .replace(
                '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">02｜示例主线乙</span></h2>',
                '<h2 data-kstack-role="hub-entry" align="left"><span style="color: #2E74B5; font-size: 16px;">组织学习</span></h2>',
            )
        )
        self.assertEqual([], MODULE.validate_source(marked))

        intro_heading = '<h2 data-kstack-role="global-intro" align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>\n'
        intro_body = '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">两条示例主线共同构成一个验证闭环。</span></p>\n'
        without_intro = marked.replace(intro_heading + intro_body, "")
        self.assertIn(
            "docs_index_global_intro_order_mismatch",
            self.codes(without_intro),
        )

    def test_explicit_global_intro_requires_body_before_first_hub_entry(self) -> None:
        marked = (
            MULTI_MAINLINE_INDEX
            .replace(
                '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>',
                '<h2 data-kstack-role="global-intro" align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>',
            )
            .replace(
                '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">01｜示例主线甲</span></h2>',
                '<h2 data-kstack-role="hub-entry" align="left"><span style="color: #2E74B5; font-size: 16px;">工程实践</span></h2>',
            )
            .replace(
                '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">02｜示例主线乙</span></h2>',
                '<h2 data-kstack-role="hub-entry" align="left"><span style="color: #2E74B5; font-size: 16px;">组织学习</span></h2>',
            )
            .replace(
                '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">两条示例主线共同构成一个验证闭环。</span></p>',
                '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;"></span></p>',
                1,
            )
        )

        self.assertIn(
            "docs_index_global_intro_body_missing",
            self.codes(marked),
        )

    def test_unmarked_non_numbered_index_sections_do_not_imply_a_hub(self) -> None:
        second_section = """
<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">另一普通章节</span></h2>
<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">普通文章章节正文。</span></p>
"""
        source = INDEX_LEFT_HEADINGS.replace("\n</div>", second_section + "\n</div>")
        codes = self.codes(source)

        self.assertNotIn("docs_index_global_intro_order_mismatch", codes)
        self.assertNotIn("docs_index_global_intro_body_missing", codes)

    def test_single_mainline_index_does_not_require_global_intro(self) -> None:
        intro_heading = '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>\n'
        intro_body = '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">两条示例主线共同构成一个验证闭环。</span></p>\n'
        second_mainline = '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">02｜示例主线乙</span></h2>\n<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">示例主线乙的说明。</span></p>\n'
        source = MULTI_MAINLINE_INDEX.replace(intro_heading + intro_body, "").replace(
            second_mainline,
            "",
        )
        self.assertEqual(MODULE.validate_source(source), [])

    def test_explicit_index_profile_requires_index_layout_marker(self) -> None:
        intro_heading = '<h2 align="left"><span style="color: #2E74B5; font-size: 16px;">示例全局介绍</span></h2>\n'
        intro_body = '<p data-kstack-role="body" align="left"><span style="color: #202124; font-size: 11px;">两条示例主线共同构成一个验证闭环。</span></p>\n'
        source = MULTI_MAINLINE_INDEX.replace(
            '<div data-kstack-layout="index">',
            "<div>",
        ).replace(intro_heading + intro_body, "")
        codes = {
            item["code"]
            for item in MODULE.validate_source(source, profile="index")
        }
        self.assertIn("docs_profile_mismatch", codes)
        self.assertNotIn("docs_index_global_intro_order_mismatch", codes)
        self.assertNotIn("docs_index_global_intro_body_missing", codes)

    def test_index_h3_uses_navy_to_preserve_heading_hierarchy(self) -> None:
        accent_h3 = INDEX_LEFT_HEADINGS.replace(
            'color: #17344B; font-size: 13px;">示例小节',
            'color: #2E74B5; font-size: 13px;">示例小节',
        )
        self.assertIn("docs_h3_color_mismatch", self.codes(accent_h3))

    def test_unstyled_body_is_blocked(self) -> None:
        source = VALID.replace('<p align="left" style="font-size: 11px; color: #202124; text-align: left;">示例正文。</p>', '<p>示例正文。</p>')
        self.assertIn("docs_body_font_size_mismatch", self.codes(source))
        self.assertIn("docs_body_color_mismatch", self.codes(source))

    def test_nested_body_override_is_blocked(self) -> None:
        source = VALID.replace("示例正文。</p>", '<span style="font-size: 20px; color: #202124;">示例正文。</span></p>')
        self.assertIn("docs_body_font_size_mismatch", self.codes(source))

    def test_source_note_must_use_muted_9px_token(self) -> None:
        source = VALID.replace('font-size: 9px;">示例来源说明', 'font-size: 10px;">示例来源说明')
        self.assertIn("docs_source_font_size_mismatch", self.codes(source))

    def test_special_paragraph_requires_semantic_role(self) -> None:
        source = VALID.replace(' data-kstack-role="subtitle"', "", 1)
        self.assertIn("docs_paragraph_role_missing", self.codes(source))

    def test_kicker_role_detection_uses_structure_and_tokens_not_copy(self) -> None:
        source = VALID.replace(' data-kstack-role="kicker"', "", 1).replace(
            "示例分类 · V3",
            "任意未约定的短文本",
        )
        self.assertIn("docs_paragraph_role_missing", self.codes(source))

    def test_index_marker_overrides_a_contradictory_explicit_default_profile(self) -> None:
        findings = MODULE.validate_source(INDEX_LEFT_HEADINGS, profile="default")
        self.assertIn("docs_profile_mismatch", {item["code"] for item in findings})
        self.assertEqual(
            "index",
            MODULE.validation_result(INDEX_LEFT_HEADINGS, profile="default")["profile"],
        )

    def test_date_role_requires_one_exact_valid_calendar_date(self) -> None:
        invalid_dates = (
            "2099 年 1 月",
            "2099 年 1 月 2 日｜示例时区",
            "2099 年 2 月 30 日",
            "2099年1月2日",
        )
        for value in invalid_dates:
            with self.subTest(value=value):
                source = VALID.replace("2099 年 1 月 2 日", value)
                self.assertIn("docs_date_format_invalid", self.codes(source))

    def test_date_uses_its_own_role_and_tokens(self) -> None:
        source = VALID.replace('data-kstack-role="date"', 'data-kstack-role="body"', 1)
        self.assertIn("docs_body_font_size_mismatch", self.codes(source))

    def test_validation_evidence_binds_the_exact_source(self) -> None:
        result = MODULE.validation_result(VALID)
        self.assertEqual(result["source_sha256"], hashlib.sha256(VALID.encode("utf-8")).hexdigest())
        manifest_path = SCRIPT.resolve().parents[3] / ".codex-plugin" / "plugin.json"
        self.assertEqual(MODULE.MANIFEST_PATH, manifest_path)
        self.assertEqual(
            result["plugin_version"],
            json.loads(manifest_path.read_text(encoding="utf-8"))["version"],
        )
        self.assertEqual(
            result["validator_sha256"],
            hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            result["style_contract_sha256"],
            hashlib.sha256(MODULE.CONTRACT_PATH.read_bytes()).hexdigest(),
        )
        self.assertTrue(result["ok"])

    def test_cli_hashes_exact_crlf_bytes_and_avoids_absolute_source_path(self) -> None:
        raw_source = VALID.lstrip("\n").replace("\n", "\r\n").encode("utf-8")
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "synthetic-docs-source.html"
            input_path.write_bytes(raw_source)
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        self.assertEqual(hashlib.sha256(raw_source).hexdigest(), result["source_sha256"])
        self.assertEqual(input_path.name, result["source_path"])
        self.assertNotIn(temp_dir, completed.stdout)

    def test_cli_rejects_explicit_index_profile_without_layout_marker(self) -> None:
        source = INDEX_LEFT_HEADINGS.replace(
            '<div data-kstack-layout="index">',
            "<div>",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "synthetic-index-source.html"
            input_path.write_text(source, encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_path),
                    "--profile",
                    "index",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(1, completed.returncode, completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        self.assertEqual("index", result["profile"])
        self.assertIn(
            "docs_profile_mismatch",
            {item["code"] for item in result["findings"]},
        )

    def test_unapproved_border_color_is_blocked(self) -> None:
        source = VALID.replace("<hr>", '<hr style="border-color: #123456;">')
        self.assertIn("docs_color_not_allowed", self.codes(source))

    def test_rgb_or_named_color_is_blocked(self) -> None:
        source = VALID.replace("<hr>", '<hr style="background-color: rgb(1, 2, 3);">')
        self.assertIn("docs_color_not_allowed", self.codes(source))

    def test_single_quoted_style_cannot_bypass_font_gate(self) -> None:
        source = VALID.replace("<hr>", "<hr style='font-family: serif; color: #DADCE0;'>")
        self.assertIn("docs_font_family_forbidden", self.codes(source))


if __name__ == "__main__":
    unittest.main()

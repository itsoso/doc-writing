from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
PLUGIN_DIR = SKILL_DIR.parents[1]
REPO_ROOT = PLUGIN_DIR.parents[1]
ONEPOINT_REFERENCE = SKILL_DIR / "references" / "onepoint-kuaishou.md"
FAST_WORKFLOW = SKILL_DIR / "references" / "fast-writing-workflow.md"
ALLOWED_INTERNAL_URLS = {
    "https://bs3-hb1.corp.kuaishou.com/kwaishop-langbridge-evaluation/onepointcli.md"
}
SYNTHETIC_ID_VALUES = {
    "actual returned document id",
    "doc-1",
    "doc_example",
    "folder_one",
    "folder_other",
    "folder_target",
    "folder_two",
    "ordinary_document",
    "view_target",
}
SENSITIVE_ARTIFACT_NAMES = {
    "docs-publication.json",
    "docs-readback.json",
    "docs-preimage.json",
    "raw-jsonml.json",
}


class LongformSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        cls.reference_text = (
            ONEPOINT_REFERENCE.read_text(encoding="utf-8")
            if ONEPOINT_REFERENCE.is_file()
            else ""
        )
        cls.plugin = json.loads(
            (PLUGIN_DIR / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        cls.fast_workflow_text = FAST_WORKFLOW.read_text(encoding="utf-8")

    def test_plugin_version_is_0_6_0(self) -> None:
        self.assertEqual("0.6.0", self.plugin["version"])

    def test_collaborative_evidence_contract_is_exposed(self) -> None:
        workflow = SKILL_DIR / "references" / "collaborative-evidence-workflow.md"
        checker = SKILL_DIR / "scripts" / "check_evidence.py"
        self.assertTrue(workflow.is_file(), "missing collaboration workflow")
        self.assertTrue(checker.is_file(), "missing evidence checker")
        self.assertIn("`EDIT`", self.skill_text)
        self.assertIn("`EXPAND`", self.skill_text)
        self.assertIn("`AUDIT`", self.skill_text)
        self.assertIn("references/collaborative-evidence-workflow.md", self.skill_text)

    def test_skill_loads_onepoint_reference_only_conditionally(self) -> None:
        self.assertTrue(ONEPOINT_REFERENCE.is_file(), "missing Onepoint reference")
        self.assertIn("references/onepoint-kuaishou.md", self.skill_text)
        self.assertRegex(self.skill_text, r"Onepoint.*(?:only|仅|明确)")

    def test_reference_states_internal_and_general_boundaries(self) -> None:
        self.assertIn("快手内部产品", self.reference_text)
        self.assertIn("仅适用于快手公司内部", self.reference_text)
        self.assertIn("通用 Skill", self.reference_text)
        self.assertIn("不依赖 Onepoint", self.reference_text)

    def test_reference_contains_minimal_safe_meeting_workflow(self) -> None:
        required = (
            "onepoint login --no-open-browser",
            "onepoint whoami",
            "onepoint meeting list",
            "onepoint meeting view <meetingId> --full --output compact_json",
            "summary",
            "actions",
            "asrText",
            "documents",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, self.reference_text)

    def test_public_reference_contains_no_real_meeting_id_or_secret(self) -> None:
        combined = "\n".join((self.reference_text, self.readme_text))
        self.assertIsNone(re.search(r"meeting_\d{6,}_\d+", combined))
        self.assertNotIn("opc_live_", combined)
        self.assertNotIn("opk_live_", combined)

    def test_full_plugin_tree_contains_no_private_docs_or_workstation_evidence(self) -> None:
        violations: list[str] = []
        text_files = [
            path
            for path in PLUGIN_DIR.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        ]
        for path in text_files:
            relative = path.relative_to(PLUGIN_DIR)
            if path.name in SENSITIVE_ARTIFACT_NAMES:
                violations.append(f"sensitive artifact tracked: {relative}")
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for url in re.findall(r"https?://[^\s)\]>'\"]+", text):
                if "corp.kuaishou.com" in url and url not in ALLOWED_INTERNAL_URLS:
                    violations.append(f"internal URL in {relative}: {url}")
            if re.search(r"(?:/Users|/home)/[^/<\s'\"]+", text):
                violations.append(f"absolute user path in {relative}")
            if re.search(r"\bfcA[A-Za-z0-9_-]{10,}\b", text):
                violations.append(f"possible real Docs ID in {relative}")
            if re.search(r"\bmeeting_\d{6,}_\d+\b", text):
                violations.append(f"possible real meeting ID in {relative}")
            for field, value in re.findall(
                r"[\"'](docId|folderId|viewId|meetingId)[\"']\s*:\s*[\"']([^\"']+)[\"']",
                text,
            ):
                if value not in SYNTHETIC_ID_VALUES:
                    violations.append(
                        f"non-synthetic {field} value in {relative}: {value}"
                    )

        self.assertEqual([], violations)

    def test_fast_workflow_uses_the_publishing_markdown_verified_contract(self) -> None:
        milestone = next(
            line
            for line in self.fast_workflow_text.splitlines()
            if line.startswith("- `markdown_verified`")
        )
        for phrase in (
            "frozen canonical Markdown",
            "complete local image set when images are referenced",
            "exact Docs source",
            "fresh passing style validation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, milestone)
        self.assertNotIn("DOCX", milestone)
        self.assertNotIn("Word", milestone)

    def test_readme_explains_onepoint_is_optional_and_internal_only(self) -> None:
        self.assertIn("Onepoint（仅限快手内部）", self.readme_text)
        self.assertIn("Skill 的通用写作能力不依赖 Onepoint", self.readme_text)

    def test_publication_timezone_is_not_rendered_in_visible_date_text(self) -> None:
        self.assertIn("must not appear in the visible masthead", self.skill_text)
        self.assertIn("Render only the date", self.skill_text)
        self.assertIn("timezone suffix", self.skill_text)

    def test_formal_masthead_separates_title_subtitle_and_date(self) -> None:
        self.assertIn("# Main title", self.skill_text)
        self.assertIn("> Subtitle", self.skill_text)
        self.assertIn("The H1 must not contain the subtitle, date, or `｜`", self.skill_text)
        self.assertIn("three separate visual lines", self.skill_text)


if __name__ == "__main__":
    unittest.main()

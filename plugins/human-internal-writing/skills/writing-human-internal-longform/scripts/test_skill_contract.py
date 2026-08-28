from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
PLUGIN_DIR = SKILL_DIR.parents[1]
REPO_ROOT = PLUGIN_DIR.parents[1]
ONEPOINT_REFERENCE = SKILL_DIR / "references" / "onepoint-kuaishou.md"


class OnePointBoundaryContractTests(unittest.TestCase):
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

    def test_plugin_version_is_0_2_0(self) -> None:
        self.assertEqual("0.2.0", self.plugin["version"])

    def test_skill_loads_onepoint_reference_only_conditionally(self) -> None:
        self.assertTrue(ONEPOINT_REFERENCE.is_file(), "missing OnePoint reference")
        self.assertIn("references/onepoint-kuaishou.md", self.skill_text)
        self.assertRegex(self.skill_text, r"OnePoint.*(?:only|仅|明确)")

    def test_reference_states_internal_and_general_boundaries(self) -> None:
        self.assertIn("快手内部产品", self.reference_text)
        self.assertIn("仅适用于快手公司内部", self.reference_text)
        self.assertIn("通用 Skill", self.reference_text)
        self.assertIn("不依赖 OnePoint", self.reference_text)

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

    def test_readme_explains_onepoint_is_optional_and_internal_only(self) -> None:
        self.assertIn("OnePoint（仅限快手内部）", self.readme_text)
        self.assertIn("Skill 的通用写作能力不依赖 OnePoint", self.readme_text)

    def test_publication_timezone_is_not_rendered_in_visible_date_text(self) -> None:
        self.assertIn("must not appear in the visible title", self.skill_text)
        self.assertIn("Render only the date", self.skill_text)
        self.assertIn("timezone suffix", self.skill_text)


if __name__ == "__main__":
    unittest.main()

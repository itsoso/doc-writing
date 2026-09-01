from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[3]


class DocWritingEntrypointContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        cls.architecture_text = (
            REPO_ROOT / "docs" / "guides" / "doc-writing-github-architecture.md"
        ).read_text(encoding="utf-8")

    def test_skill_name_matches_directory_and_user_entrypoint(self) -> None:
        self.assertRegex(self.skill_text, r"(?m)^name:\s*doc-writing\s*$")
        self.assertNotRegex(self.skill_text, r"(?m)^name:\s*doc-writing-router\s*$")
        self.assertIn("# Doc-writing", self.skill_text)

    def test_readme_uses_doc_writing_as_the_primary_entrypoint(self) -> None:
        self.assertIn("$doc-writing", self.readme_text)
        self.assertIn("推荐入口", self.readme_text)
        self.assertNotIn("$doc-writing-router", self.readme_text)
        self.assertNotIn("skills/doc-writing-router/", self.readme_text)

    def test_underlying_editorial_skill_remains_explicitly_available(self) -> None:
        self.assertIn("$writing-human-internal-longform", self.readme_text)
        self.assertIn("writing-human-internal-longform", self.skill_text)

    def test_architecture_points_to_the_renamed_directory(self) -> None:
        self.assertIn("├── doc-writing/", self.architecture_text)
        self.assertNotIn("doc-writing-router", self.architecture_text)


if __name__ == "__main__":
    unittest.main()

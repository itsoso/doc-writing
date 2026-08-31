from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
TYPOGRAPHY = SKILL_DIR / "references" / "editorial-and-typography.md"


class FormalTitleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = TYPOGRAPHY.read_text(encoding="utf-8")

    def test_formal_masthead_has_three_semantic_lines(self) -> None:
        self.assertIn("# 主标题", self.text)
        self.assertIn("> 副标题", self.text)
        self.assertIn("2099 年 4 月 5 日", self.text)
        self.assertIn("三层信息不得合并", self.text)

    def test_kstack_article_and_index_alignment_profiles_are_distinct(self) -> None:
        self.assertIn("default formal-article profile", self.text)
        self.assertIn("center the masthead H1, subtitle, and publication date", self.text)
        self.assertIn("index or knowledge-hub profile", self.text)
        self.assertIn("center only H1", self.text)


if __name__ == "__main__":
    unittest.main()

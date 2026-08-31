from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


class SkillRoutingTests(unittest.TestCase):
    def test_focused_edits_route_to_baseline_regression_check(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("--baseline", text)

    def test_real_article_comparisons_route_to_pairwise_evaluation(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/pairwise-article-evaluation.md", text)

    def test_entrypoint_declares_non_trigger_cases(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Do not use the full workflow", text)


if __name__ == "__main__":
    unittest.main()

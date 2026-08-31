from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
INDEX_HUB_REFERENCE = SKILL_DIR / "references" / "index-and-hub-editorial-mode.md"
INDEX_HUB_EVAL = SKILL_DIR / "evals" / "index-hub-global-coherence.md"


class IndexHubEditorialContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.frontmatter = cls.skill_text.split("---", 2)[1].lower()
        cls.rubric_text = (
            SKILL_DIR / "references" / "quality-rubric.md"
        ).read_text(encoding="utf-8")
        cls.pairwise_text = (
            SKILL_DIR / "references" / "pairwise-article-evaluation.md"
        ).read_text(encoding="utf-8")
        cls.reference_text = (
            INDEX_HUB_REFERENCE.read_text(encoding="utf-8")
            if INDEX_HUB_REFERENCE.is_file()
            else ""
        )
        cls.eval_text = (
            INDEX_HUB_EVAL.read_text(encoding="utf-8")
            if INDEX_HUB_EVAL.is_file()
            else ""
        )

    def test_discovery_description_names_all_index_hub_artifacts(self) -> None:
        for phrase in ("article index", "column homepage", "knowledge hub"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.frontmatter)

    def test_entrypoint_routes_index_hub_work_to_dedicated_reference(self) -> None:
        self.assertIn("references/index-and-hub-editorial-mode.md", self.skill_text)
        for phrase in ("article index", "column homepage", "knowledge hub"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.skill_text.lower())

    def test_reference_requires_first_screen_system_explanation(self) -> None:
        self.assertTrue(INDEX_HUB_REFERENCE.is_file(), "missing Index/Hub reference")
        for phrase in (
            "system boundary",
            "first-screen contract",
            "global coherence pass",
            "why these entries belong to one system",
            "entry clarity",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.reference_text.lower())

    def test_quality_rubric_has_index_hub_gate(self) -> None:
        self.assertIn("## 9. Index/Hub global coherence", self.rubric_text)
        for phrase in ("first screen", "system boundary", "entry clarity"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.rubric_text.lower())

    def test_pairwise_evaluation_scores_system_and_entry_quality(self) -> None:
        self.assertIn("| System coherence |", self.pairwise_text)
        self.assertIn("| Entry clarity |", self.pairwise_text)

    def test_eval_records_pressure_case_and_global_failure(self) -> None:
        self.assertTrue(INDEX_HUB_EVAL.is_file(), "missing Index/Hub evaluation")
        for phrase in (
            "five minutes",
            "structure and links already pass",
            "red baseline",
            "global coherence",
            "entry clarity",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.eval_text.lower())


if __name__ == "__main__":
    unittest.main()

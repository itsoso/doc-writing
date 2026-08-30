from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from check_draft import analyze  # noqa: E402


WEAK_DRAFT = """# AI 转型共识

> 从口号转向可验证行动

2026 年 8 月 27 日

一句话带走｜我们必须全面拥抱变化。

一句话带走｜我们必须全面拥抱变化。

首先，我们要统一认知。其次，我们要全面赋能。再次，我们要强化协同。最后，我们要形成闭环。首先要建设体系，其次要打造生态，最后实现价值跃迁。

我们要以体系赋能体系，以能力促进协同，以生态形成闭环，以抓手实现价值，以战略推动落地。
"""


STRONG_DRAFT = """# 从一次售后失败开始改进购物助手

> 从推荐答案走向履约闭环

2026 年 8 月 27 日

上周三，五名试用同学让购物助手寻找两百元以内、周五前送达的通勤鞋。助手推荐了商品，却没有检查配送时间，其中两人到结算页才发现无法按时送达。

这说明当前问题不是回答不够流畅，而是任务完成链路缺少履约信息。下一轮先接入预计送达时间，只面向内部试用；负责人每天复盘失败记录，一周后决定是否扩大范围。

风险也很具体：库存和物流信息可能延迟。信息不确定时，助手必须说明来源与更新时间，不替用户做最终承诺，并保留人工反馈入口。
"""


class AnalyzeDraftTests(unittest.TestCase):
    def test_month_only_article_title_is_blocked(self) -> None:
        month_only = """# 耐心的物理学

> 从 276 毫秒到 1.7 万 DAU

2026 年 8 月

下一步从真实用户链路开始，明确风险、边界和回滚条件。
"""

        finding = next(
            item
            for item in analyze(month_only)
            if item.rule == "missing-exact-publication-date"
        )

        self.assertEqual("blocker", finding.severity)
        self.assertEqual(5, finding.line)

    def test_three_line_masthead_passes_date_rule(self) -> None:
        exact_date = """# 耐心的物理学

> 从 276 毫秒到 1.7 万 DAU

2026 年 8 月 27 日

下一步从真实用户链路开始，明确风险、边界和回滚条件。
"""

        rules = {finding.rule for finding in analyze(exact_date)}

        self.assertNotIn("missing-exact-publication-date", rules)

    def test_visible_timezone_label_in_title_is_blocked(self) -> None:
        labeled_date = """# 突击之后

> 把性能变成日常能力

2026 年 8 月 28 日 · 北京时间

下一步从真实用户链路开始，明确风险、边界和回滚条件。
"""

        finding = next(
            item
            for item in analyze(labeled_date)
            if item.rule == "visible-publication-timezone"
        )

        self.assertEqual("blocker", finding.severity)
        self.assertEqual(5, finding.line)

    def test_combined_title_subtitle_and_date_is_blocked(self) -> None:
        combined = """# 耐心的物理学：从 276 毫秒到 1.7 万 DAU｜2026 年 8 月 27 日

下一步从真实用户链路开始，明确风险、边界和回滚条件。
"""

        rules = {finding.rule for finding in analyze(combined)}

        self.assertIn("combined-formal-masthead", rules)

    def test_template_heavy_draft_produces_named_findings(self) -> None:
        rules = {finding.rule for finding in analyze(WEAK_DRAFT)}

        self.assertIn("repeated-stock-label", rules)
        self.assertIn("mechanical-sequencing", rules)
        self.assertIn("abstract-cluster", rules)

    def test_concrete_draft_stays_under_blocking_threshold(self) -> None:
        findings = analyze(STRONG_DRAFT)

        blockers = [finding for finding in findings if finding.severity == "blocker"]
        self.assertEqual([], blockers)
        self.assertLessEqual(len(findings), 2)

    def test_findings_include_one_based_line_numbers(self) -> None:
        findings = analyze(WEAK_DRAFT)

        repeated = next(item for item in findings if item.rule == "repeated-stock-label")
        self.assertGreaterEqual(repeated.line, 1)

    def test_sequence_finding_points_to_a_matching_paragraph(self) -> None:
        diffuse_sequence_draft = """开场先说明背景。

首先，要理解用户。其次，要查看数据。再次，要构建原型。最后，要上线验证。

首先，要复盘失败。其次，要补齐知识。再次，要调整方案。最后，要回到用户。
"""
        findings = analyze(diffuse_sequence_draft)

        sequence = next(item for item in findings if item.rule == "mechanical-sequencing")
        self.assertEqual(3, sequence.line)
        self.assertNotIn("本段 0 处", sequence.evidence)


class DraftCheckerCliTests(unittest.TestCase):
    def test_json_output_is_machine_readable(self) -> None:
        script = SCRIPT_DIR / "check_draft.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "draft.md"
            draft.write_text(WEAK_DRAFT, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script), str(draft), "--json", "--max-findings", "99"],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(str(draft), payload["path"])
        self.assertGreaterEqual(payload["summary"]["findings"], 3)
        self.assertTrue(all("rule" in item and "line" in item for item in payload["findings"]))

    def test_missing_file_returns_nonzero(self) -> None:
        script = SCRIPT_DIR / "check_draft.py"
        result = subprocess.run(
            [sys.executable, str(script), "/path/that/does/not/exist.md"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("not found", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()

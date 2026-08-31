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


WEAK_DRAFT = """# 合成示例文章 A

> 用于测试模板化表达

2099 年 4 月 5 日

一句话带走｜我们必须全面拥抱变化。

一句话带走｜我们必须全面拥抱变化。

首先，我们要统一认知。其次，我们要全面赋能。再次，我们要强化协同。最后，我们要形成闭环。首先要建设体系，其次要打造生态，最后实现价值跃迁。

我们要以体系赋能体系，以能力促进协同，以生态形成闭环，以抓手实现价值，以战略推动落地。
"""


STRONG_DRAFT = """# 合成示例文章 B

> 从模拟推荐结果走向履约闭环

2099 年 4 月 5 日

上周三，五名试用同学让购物助手寻找两百元以内、周五前送达的通勤鞋。助手推荐了商品，却没有检查配送时间，其中两人到结算页才发现无法按时送达。

这说明当前问题不是回答不够流畅，而是任务完成链路缺少履约信息。下一轮先接入预计送达时间，只面向内部试用；负责人每天复盘失败记录，一周后决定是否扩大范围。

风险也很具体：库存和物流信息可能延迟。信息不确定时，助手必须说明来源与更新时间，不替用户做最终承诺，并保留人工反馈入口。
"""


class AnalyzeDraftTests(unittest.TestCase):
    def test_date_without_canonical_spaces_is_blocked(self) -> None:
        compact_date = """# 合成示例文章 C0

> 用于验证日期格式

2099年1月2日
"""

        rules = {finding.rule for finding in analyze(compact_date, formal=True)}

        self.assertIn("missing-exact-publication-date", rules)

    def test_zero_padded_date_is_blocked(self) -> None:
        zero_padded = """# 合成示例文章 C1

> 用于验证日期格式

2099 年 01 月 02 日
"""

        rules = {finding.rule for finding in analyze(zero_padded, formal=True)}

        self.assertIn("missing-exact-publication-date", rules)

    def test_month_only_masthead_is_blocked(self) -> None:
        month_only = """# 合成示例文章 C

> 用于验证日期精度

2099 年 4 月

下一步从合成用户链路开始，明确风险、边界和回滚条件。
"""

        finding = next(
            item
            for item in analyze(month_only, formal=True)
            if item.rule == "missing-exact-publication-date"
        )

        self.assertEqual("blocker", finding.severity)
        self.assertEqual(5, finding.line)

    def test_impossible_calendar_date_is_blocked(self) -> None:
        impossible = """# 合成示例文章 D

> 用于验证真实日历日

2099 年 2 月 30 日
"""

        rules = {finding.rule for finding in analyze(impossible, formal=True)}

        self.assertIn("missing-exact-publication-date", rules)

    def test_visible_timezone_label_is_blocked(self) -> None:
        labeled_date = """# 合成示例文章 E

> 用于验证题头时区隐藏

2099 年 4 月 5 日 · 北京时间
"""

        finding = next(
            item
            for item in analyze(labeled_date, formal=True)
            if item.rule == "visible-publication-timezone"
        )

        self.assertEqual("blocker", finding.severity)
        self.assertEqual(5, finding.line)

    def test_combined_title_subtitle_and_date_is_blocked(self) -> None:
        combined = """# 合成示例文章 F：副标题｜2099 年 4 月 5 日

下一步从真实用户链路开始，明确风险、边界和回滚条件。
"""

        rules = {finding.rule for finding in analyze(combined, formal=True)}

        self.assertIn("combined-formal-masthead", rules)

    def test_three_line_masthead_is_not_flagged_as_combined(self) -> None:
        separated = """# 合成示例文章 G

> 用于验证三行题头

2099 年 4 月 5 日

下一步从真实用户链路开始，明确风险、边界和回滚条件。
"""

        rules = {finding.rule for finding in analyze(separated, formal=True)}

        self.assertNotIn("combined-formal-masthead", rules)
        self.assertNotIn("missing-exact-publication-date", rules)
        self.assertNotIn("visible-publication-timezone", rules)

    def test_repeated_subtitle_after_h1_colon_is_blocked(self) -> None:
        repeated_subtitle = """# 代码变便宜之后：真正稀缺的是什么？

> 真正稀缺的是什么？

2099 年 4 月 5 日
"""

        rules = {finding.rule for finding in analyze(repeated_subtitle, formal=True)}

        self.assertIn("combined-formal-masthead", rules)

    def test_repeated_plain_subtitle_after_h1_colon_is_blocked(self) -> None:
        repeated_subtitle = """# 代码变便宜之后：真正稀缺的是什么？

真正稀缺的是什么？

2099 年 4 月 5 日
"""

        rules = {finding.rule for finding in analyze(repeated_subtitle, formal=True)}

        self.assertIn("combined-formal-masthead", rules)

    def test_legitimate_colon_in_h1_is_not_blindly_blocked(self) -> None:
        legitimate_colon = """# 模型评测：为什么 P99 仍然重要

> 从一次合成压测理解长尾体验

2099 年 4 月 5 日
"""

        rules = {finding.rule for finding in analyze(legitimate_colon, formal=True)}

        self.assertNotIn("combined-formal-masthead", rules)

    def test_non_formal_draft_does_not_require_a_publication_masthead(self) -> None:
        informal = """一次内部讨论记录

先保留问题和未知项，等证据齐备后再整理成正式文章。
"""

        rules = {finding.rule for finding in analyze(informal)}

        self.assertNotIn("missing-formal-title", rules)
        self.assertNotIn("missing-formal-subtitle", rules)
        self.assertNotIn("missing-exact-publication-date", rules)

    def test_formal_draft_requires_title_subtitle_and_date_together(self) -> None:
        date_only = """2099 年 4 月 5 日

正文只有日期，不能算完整正式题头。
"""

        rules = {finding.rule for finding in analyze(date_only, formal=True)}

        self.assertIn("missing-formal-title", rules)
        self.assertIn("missing-formal-subtitle", rules)
        self.assertNotIn("missing-exact-publication-date", rules)

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

    def test_repeated_binary_contrasts_are_flagged_as_rhetorical_template(self) -> None:
        contrast_heavy_draft = """# 合成测试：对比修辞

问题不是大家不努力，而是每次都靠专家救火。

关键不是再做一次突击，而是建立日常机制。

目标不是让某项指标短期下降，而是让退化及时暴露。

治理不是增加审批，而是让改动团队看到后果。

复盘不是重复总结，而是决定下一次改什么。
"""

        findings = analyze(contrast_heavy_draft)
        contrast = next(item for item in findings if item.rule == "repeated-binary-contrast")

        self.assertEqual(3, contrast.line)
        self.assertIn("5", contrast.evidence)

    def test_one_decisive_binary_contrast_is_not_flagged(self) -> None:
        restrained_draft = """# 合成测试：单次对比

问题不是大家不努力，而是每次都靠专家救火。

两周后的反弹说明团队仍缺少稳定的防退化机制。下一步先统一首页 P95 的口径，再观察变更与指标波动的关系。
"""

        rules = {finding.rule for finding in analyze(restrained_draft)}

        self.assertNotIn("repeated-binary-contrast", rules)

    def test_technical_mode_flags_unqualified_claims_and_unverified_commands(self) -> None:
        technical_draft = """# 合成测试：技术主张

新架构彻底消除了级联故障。

合成测试主张：页面每慢 731ms，示例转化率就下降 3.7%，因此会损失 4321 万元 GMV。

```
curl https://service.example/api/perf/check
```
"""

        rules = {finding.rule for finding in analyze(technical_draft, technical=True)}

        self.assertIn("absolute-technical-claim", rules)
        self.assertIn("unqualified-business-impact", rules)
        self.assertIn("untyped-code-fence", rules)
        self.assertIn("unverified-command-block", rules)

    def test_technical_mode_accepts_bounded_claims_and_explicit_verification_state(self) -> None:
        bounded_draft = """# 合成测试：有边界的技术主张

现有代码只证明调用关系发生变化；是否降低级联故障概率，仍需压测、故障注入和灰度数据验证。

合成测试中的“731ms 对应 3.7%”只作为敏感性场景，来源口径尚未确认，不作为内部转化系数或已发生损失。

```bash
curl https://service.example/api/perf/check
```

这条命令尚未在当前环境执行，发布前状态为“未验证”。
"""

        rules = {finding.rule for finding in analyze(bounded_draft, technical=True)}

        self.assertNotIn("absolute-technical-claim", rules)
        self.assertNotIn("unqualified-business-impact", rules)
        self.assertNotIn("untyped-code-fence", rules)
        self.assertNotIn("unverified-command-block", rules)

    def test_technical_mode_does_not_flag_a_negated_absolute_claim(self) -> None:
        bounded_claim = "现有证据不能证明新架构彻底消除了级联故障。"

        rules = {finding.rule for finding in analyze(bounded_claim, technical=True)}

        self.assertNotIn("absolute-technical-claim", rules)

    def test_technical_mode_detects_chinese_latency_unit_without_word_boundary(self) -> None:
        claim = "合成测试主张：页面慢731毫秒时示例转化率下降3.7%，因此损失4321万元GMV。"

        rules = {finding.rule for finding in analyze(claim, technical=True)}

        self.assertIn("unqualified-business-impact", rules)

    def test_technical_mode_detects_common_build_commands(self) -> None:
        draft = """# 构建验证

```bash
go test ./...
```
"""

        rules = {finding.rule for finding in analyze(draft, technical=True)}

        self.assertIn("unverified-command-block", rules)

    def test_technical_mode_understands_tilde_and_long_backtick_fences(self) -> None:
        draft = """# 构建验证

~~~bash
go test ./...
~~~

````markdown
```bash
curl https://example.test/health
```
````
"""

        rules = [finding.rule for finding in analyze(draft, technical=True)]

        self.assertEqual(2, rules.count("unverified-command-block"))
        self.assertNotIn("untyped-code-fence", rules)

    def test_technical_mode_excludes_code_content_from_prose_claim_checks(self) -> None:
        draft = """# 示例

```python
message = "彻底消除了级联故障"
```

以上代码未执行，仅展示字符串格式。
"""

        rules = {finding.rule for finding in analyze(draft, technical=True)}

        self.assertNotIn("absolute-technical-claim", rules)

    def test_code_content_is_excluded_from_general_prose_checks(self) -> None:
        draft = """# 示例

```text
不是速度问题，而是质量问题。
不是代码问题，而是流程问题。
不是工具问题，而是能力问题。
不是执行问题，而是认知问题。
不是局部问题，而是系统问题。
```

正文只说明代码块是待审材料。
"""

        rules = {finding.rule for finding in analyze(draft, technical=True)}

        self.assertNotIn("repeated-binary-contrast", rules)

    def test_technical_mode_flags_unclosed_fence(self) -> None:
        draft = """# 示例

```bash
go test ./...
"""

        rules = {finding.rule for finding in analyze(draft, technical=True)}

        self.assertIn("unclosed-code-fence", rules)

    def test_technical_mode_flags_standalone_unqualified_metrics(self) -> None:
        draft = """# 合成测试：指标主张

合成测试主张：接口 P99 为 731ms。

合成测试主张：示例转化率提升 3.7%。

合成测试主张：全年增加 4321 万元利润。
"""

        rules = [finding.rule for finding in analyze(draft, technical=True)]

        self.assertIn("unqualified-technical-metric", rules)
        self.assertEqual(2, rules.count("unqualified-business-impact"))

    def test_source_unknown_does_not_qualify_a_business_claim(self) -> None:
        for claim in (
            "合成测试主张：来源未知；页面每慢731ms时示例转化率下降3.7%，因此损失4321万元GMV。",
            "合成测试主张：来源：未知。页面每慢731ms时示例转化率下降3.7%，因此损失4321万元GMV。",
            "合成测试主张：来源为未知。页面每慢731ms时示例转化率下降3.7%，因此损失4321万元GMV。",
        ):
            with self.subTest(claim=claim):
                rules = {finding.rule for finding in analyze(claim, technical=True)}

                self.assertIn("unqualified-business-impact", rules)

    def test_order_api_latency_is_still_a_technical_metric(self) -> None:
        claim = "合成测试主张：示例订单接口 P99 为 731ms。"

        rules = {finding.rule for finding in analyze(claim, technical=True)}

        self.assertIn("unqualified-technical-metric", rules)

    def test_observed_metric_with_scope_marker_is_not_flagged(self) -> None:
        claim = "合成测试记录：监控截图显示，模拟流量在 2099 年 4 月 5 日的接口 P99 为 731ms。"

        rules = {finding.rule for finding in analyze(claim, technical=True)}

        self.assertNotIn("unqualified-technical-metric", rules)

    def test_common_negations_do_not_trigger_absolute_claim_warning(self) -> None:
        for claim in (
            "新架构并非完全解决了级联故障。",
            "调用关系改变不代表彻底消除了级联故障。",
            "现有材料不足以说明新架构完全避免了故障传播。",
        ):
            with self.subTest(claim=claim):
                rules = {finding.rule for finding in analyze(claim, technical=True)}

                self.assertNotIn("absolute-technical-claim", rules)

    def test_unrelated_negation_does_not_hide_an_absolute_claim(self) -> None:
        claim = "不能忽略这个事实：新架构彻底消除了级联故障。"

        rules = {finding.rule for finding in analyze(claim, technical=True)}

        self.assertIn("absolute-technical-claim", rules)


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
        self.assertEqual(draft.name, payload["path"])
        self.assertNotIn(str(draft.parent), result.stdout)
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

    def test_cli_technical_mode_reports_mode_in_json(self) -> None:
        script = SCRIPT_DIR / "check_draft.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "technical.md"
            draft.write_text(
                "# 合成示例架构\n\n> 用于测试技术规则\n\n"
                "2099 年 4 月 5 日\n\n新方案彻底消除了级联故障。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(draft),
                    "--technical",
                    "--json",
                    "--max-findings",
                    "99",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("technical", payload["mode"])
        self.assertIn(
            "absolute-technical-claim",
            {item["rule"] for item in payload["findings"]},
        )

    def test_cli_formal_mode_requires_the_complete_masthead(self) -> None:
        script = SCRIPT_DIR / "check_draft.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "formal.md"
            draft.write_text("2099 年 4 月 5 日\n\n正文。\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script), str(draft), "--formal", "--json"],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(1, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("formal", payload["form"])
        rules = {item["rule"] for item in payload["findings"]}
        self.assertIn("missing-formal-title", rules)
        self.assertIn("missing-formal-subtitle", rules)

    def test_baseline_separates_pre_existing_findings_from_regressions(self) -> None:
        script = SCRIPT_DIR / "check_draft.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline.md"
            current = root / "current.md"
            baseline.write_text(WEAK_DRAFT, encoding="utf-8")
            current.write_text(WEAK_DRAFT, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script), str(current), "--baseline", str(baseline), "--json", "--max-findings", "0"],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["summary"]["pre_existing"], 0)
        self.assertEqual(0, payload["summary"]["new_findings"])

    def test_baseline_still_blocks_a_new_regression(self) -> None:
        script = SCRIPT_DIR / "check_draft.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline.md"
            current = root / "current.md"
            baseline.write_text(STRONG_DRAFT, encoding="utf-8")
            current.write_text(STRONG_DRAFT + "\n核心结论：继续推进。\n\n核心结论：继续推进。\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script), str(current), "--baseline", str(baseline), "--json", "--max-findings", "0"],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertGreaterEqual(payload["summary"]["new_findings"], 1)
        self.assertIn("repeated-stock-label", {item["rule"] for item in payload["new_findings"]})


if __name__ == "__main__":
    unittest.main()

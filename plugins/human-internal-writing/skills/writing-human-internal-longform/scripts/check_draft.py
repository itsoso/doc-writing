#!/usr/bin/env python3
"""Explainable editorial checks for Chinese or bilingual internal long-form drafts.

This is a heuristic writing aid, not an AI-authorship detector. It never rewrites
the source file and every finding names the rule and source line that produced it.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path


STOCK_LABELS = (
    "一句话带走｜",
    "核心结论：",
    "结论先行：",
    "值得注意的是",
    "毋庸置疑",
    "在这个快速变化的时代",
)

SEQUENCE_WORDS = re.compile(
    r"(?:首先|其次|再次|最后|第一|第二|第三|第四)(?=[，、,:：]|要|应|需要)"
)

BINARY_CONTRAST = re.compile(r"不是[^。！？\n]{0,80}?[，,]?而是")

ABSOLUTE_TECHNICAL_CLAIM = re.compile(
    r"(?:彻底|完全|永久)(?:消除|解决|杜绝|避免)|(?:零故障|零风险|百分之百可靠|100%\s*可靠)"
)

LATENCY_VALUE = re.compile(r"\d+(?:\.\d+)?\s*(?:ms\b|s\b|毫秒|秒)", re.IGNORECASE)
PERCENT_VALUE = re.compile(r"\d+(?:\.\d+)?\s*(?:%|％|个百分点)")
MONEY_VALUE = re.compile(r"\d+(?:\.\d+)?\s*(?:万|亿)?\s*元")
EXACT_PUBLICATION_DATE = re.compile(
    r"(?P<year>(?:19|20)\d{2}) 年 "
    r"(?P<month>[1-9]|1[0-2]) 月 "
    r"(?P<day>[1-9]|[12]\d|3[01]) 日"
)
BUSINESS_IMPACT_TERMS = ("转化", "GMV", "利润", "营收", "收入", "订单")
METRIC_BOUNDARY_MARKERS = (
    "场景",
    "假设",
    "风险敞口",
    "尚未确认",
    "未确认",
    "未验证",
    "不作为",
    "不等于",
    "外部参数",
    "监控",
    "截图",
    "日志",
    "压测",
    "实验",
    "追踪",
    "trace",
    "时间窗",
    "样本",
    "流量",
    "环境",
    "基线",
    "口径",
)

SOURCE_BOUNDARY_MARKERS = ("来源：", "来源为", "来自")
SOURCE_UNKNOWN = re.compile(
    r"来源\s*(?:[:：为是]\s*)?(?:未知|不明|缺失|待确认|未确认|不可用)"
)

COMMAND_LINE = re.compile(
    r"^\s*(?:\$\s+)?(?:curl|python(?:3)?|pytest|uv|pip|npm|pnpm|yarn|bun|node|git|gh|go|cargo|rustc|java|mvn|gradle|swift|xcodebuild|kubectl|helm|docker|terraform|make|kcli|brew)\b",
    re.IGNORECASE,
)

ABSOLUTE_NEGATION_CONTEXT = re.compile(
    r"(?:"
    r"不能(?:证明|说明|表明|认为|声称|断言|得出|说)|"
    r"无法(?:证明|说明|表明|得出|断言)|"
    r"尚未(?:证明|说明|表明|达到|实现)|"
    r"未能(?:证明|达到|实现)|"
    r"没有(?:证据)?(?:证明|表明|达到|实现)|"
    r"并未|并非|不是|不等于|不代表|"
    r"不足以(?:证明|说明|表明|得出)|"
    r"不可(?:认为|声称|断言)"
    r")[^。！？\n]{0,24}$"
)

VERIFICATION_MARKERS = (
    "已执行",
    "已运行",
    "已验证",
    "未执行",
    "未运行",
    "未验证",
    "待验证",
    "预期输出",
    "实际输出",
    "执行结果",
    "运行结果",
)

ABSTRACT_TERMS = (
    "赋能",
    "协同",
    "闭环",
    "生态",
    "体系",
    "能力",
    "价值",
    "战略",
    "认知",
    "抓手",
    "落地",
    "跃迁",
)

CONCRETE_ANCHORS = (
    "用户",
    "客户",
    "同学",
    "负责人",
    "直播间",
    "购物",
    "商品",
    "订单",
    "代码",
    "系统",
    "任务",
    "数据",
    "日志",
    "成本",
    "上线",
    "试用",
    "反馈",
)

ACTION_MARKERS = (
    "下一步",
    "从今天",
    "开始",
    "行动",
    "负责人",
    "参与",
    "进入",
    "完成",
    "实践",
    "上线",
)

RISK_MARKERS = (
    "风险",
    "边界",
    "代价",
    "失败",
    "异常",
    "回滚",
    "fallback",
    "限制",
)


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    line: int
    message: str
    evidence: str

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(frozen=True)
class Paragraph:
    line: int
    text: str


@dataclass(frozen=True)
class CodeBlock:
    line: int
    end_line: int
    language: str
    text: str
    fence: str
    closed: bool


def _paragraphs(text: str) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    buffer: list[str] = []
    start_line = 1

    def flush() -> None:
        nonlocal buffer
        if buffer:
            paragraphs.append(Paragraph(start_line, " ".join(part.strip() for part in buffer)))
            buffer = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if not buffer:
            start_line = line_number
        buffer.append(line)
    flush()
    return paragraphs


def _plain_paragraphs(text: str) -> list[Paragraph]:
    return [
        paragraph
        for paragraph in _paragraphs(text)
        if not paragraph.text.startswith(("#", "- ", "*图", "![", ">"))
    ]


def _compact(value: str) -> str:
    return re.sub(r"[\W_]+", "", value, flags=re.UNICODE)


def _is_real_publication_date(value: str) -> bool:
    match = EXACT_PUBLICATION_DATE.fullmatch(value)
    if match is None:
        return False
    try:
        date(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
        )
    except ValueError:
        return False
    return True


def _masthead_date(lines: list[str]) -> tuple[int, str] | None:
    for line_number, raw_line in enumerate(lines[:12], start=1):
        value = raw_line.strip()
        if _is_real_publication_date(value):
            return line_number, value
    return None


def _code_blocks(text: str) -> list[CodeBlock]:
    blocks: list[CodeBlock] = []
    lines = text.splitlines()
    start_line: int | None = None
    language = ""
    buffer: list[str] = []
    opening_fence = ""

    for line_number, raw_line in enumerate(lines, start=1):
        if start_line is None:
            match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", raw_line)
            if match:
                start_line = line_number
                opening_fence = match.group(1)
                language = match.group(2).strip()
                buffer = []
            continue

        closing = re.match(r"^\s*(`+|~+)\s*$", raw_line)
        if (
            closing
            and closing.group(1)[0] == opening_fence[0]
            and len(closing.group(1)) >= len(opening_fence)
        ):
            blocks.append(
                CodeBlock(
                    start_line,
                    line_number,
                    language,
                    "\n".join(buffer),
                    opening_fence,
                    True,
                )
            )
            start_line = None
            language = ""
            buffer = []
            opening_fence = ""
        else:
            buffer.append(raw_line)

    if start_line is not None:
        blocks.append(
            CodeBlock(
                start_line,
                len(lines),
                language,
                "\n".join(buffer),
                opening_fence,
                False,
            )
        )

    return blocks


def _without_code_blocks(text: str, blocks: list[CodeBlock]) -> str:
    lines = text.splitlines()
    for block in blocks:
        for index in range(block.line - 1, min(block.end_line, len(lines))):
            lines[index] = ""
    return "\n".join(lines)


def analyze(
    text: str,
    *,
    technical: bool = False,
    formal: bool = False,
) -> list[Finding]:
    findings: list[Finding] = []
    source_lines = text.splitlines()
    code_blocks = _code_blocks(text)
    prose_text = _without_code_blocks(text, code_blocks)
    lines = prose_text.splitlines()
    paragraphs = _plain_paragraphs(prose_text)

    title = next(
        ((index, line[2:].strip()) for index, line in enumerate(lines, start=1) if line.startswith("# ")),
        None,
    )
    subtitle: tuple[int, str] | None = None
    if title is not None:
        for index, line in enumerate(lines[title[0] : 12], start=title[0] + 1):
            candidate = line.strip()
            if not candidate:
                continue
            if _is_real_publication_date(candidate) or candidate.startswith("#"):
                break
            if candidate.startswith(">"):
                candidate = candidate[1:].strip()
            subtitle = (index, candidate)
            break
    masthead_date = _masthead_date(lines)
    if formal and title is None:
        findings.append(
            Finding(
                rule="missing-formal-title",
                severity="blocker",
                line=1,
                message="正式题头必须以独立 H1 提供主标题。",
                evidence="未发现 H1 主标题",
            )
        )
    if formal and subtitle is None:
        findings.append(
            Finding(
                rule="missing-formal-subtitle",
                severity="blocker",
                line=title[0] if title else 1,
                message="正式题头必须在主标题后提供独立副标题。",
                evidence="题头前 12 行未发现独立副标题",
            )
        )
    if formal and masthead_date is None:
        partial_or_invalid_date = next(
            (
                (index, line.strip())
                for index, line in enumerate(lines[:12], start=1)
                if re.fullmatch(
                    r"(?:19|20)\d{2}\s*年\s*(?:0?[1-9]|1[0-2])\s*月(?:\s*(?:0?[1-9]|[12]\d|3[01])\s*日)?",
                    line.strip(),
                )
            ),
            None,
        )
        findings.append(
            Finding(
                rule="missing-exact-publication-date",
                severity="blocker",
                line=partial_or_invalid_date[0] if partial_or_invalid_date else (title[0] if title else 1),
                message="正式题头必须包含独立且精确到日的真实日历日（YYYY 年 M 月 D 日）。",
                evidence=(
                    partial_or_invalid_date[1]
                    if partial_or_invalid_date
                    else "题头前 12 行未发现独立日期"
                ),
            )
        )

    repeated_colon_subtitle = False
    if title is not None and subtitle is not None:
        colon_parts = re.split(r"[：:]", title[1], maxsplit=1)
        repeated_colon_subtitle = (
            len(colon_parts) == 2
            and bool(_compact(colon_parts[1]))
            and _compact(colon_parts[1]) == _compact(subtitle[1])
        )
    if formal and title is not None and (
        EXACT_PUBLICATION_DATE.search(title[1])
        or "｜" in title[1]
        or repeated_colon_subtitle
    ):
        findings.append(
            Finding(
                rule="combined-formal-masthead",
                severity="blocker",
                line=title[0],
                message="正式文章的主标题、副标题和发布日期必须分成三行，不得合并进 H1。",
                evidence=title[1],
            )
        )

    timezone_line = next(
        (
            (index, line.strip())
            for index, line in enumerate(lines[:12], start=1)
            if re.search(r"北京时间|UTC\s*\+?8|Asia/Shanghai", line, re.IGNORECASE)
        ),
        None,
    )
    if formal and timezone_line is not None:
        findings.append(
            Finding(
                rule="visible-publication-timezone",
                severity="blocker",
                line=timezone_line[0],
                message="发布时区只用于计算日期，不应显示在正式题头中。",
                evidence=timezone_line[1],
            )
        )

    for label in STOCK_LABELS:
        occurrences = [index for index, line in enumerate(lines, start=1) if label in line]
        if len(occurrences) >= 2:
            findings.append(
                Finding(
                    rule="repeated-stock-label",
                    severity="warning",
                    line=occurrences[1],
                    message=f"固定提示语“{label}”重复 {len(occurrences)} 次，容易形成模板感。",
                    evidence=label,
                )
            )

    contrast_occurrences = [
        index
        for index, line in enumerate(lines, start=1)
        for _ in BINARY_CONTRAST.finditer(line)
    ]
    if len(contrast_occurrences) >= 5:
        findings.append(
            Finding(
                rule="repeated-binary-contrast",
                severity="warning",
                line=contrast_occurrences[0],
                message="“不是……而是……”反复承担转折和结论，容易把真实推理压成同一种修辞模板。",
                evidence=f"全文 {len(contrast_occurrences)} 处",
            )
        )

    sequence_hits = [
        (paragraph.line, len(SEQUENCE_WORDS.findall(paragraph.text)))
        for paragraph in paragraphs
    ]
    total_sequence_hits = sum(count for _, count in sequence_hits)
    dense_sequence = next(((line, count) for line, count in sequence_hits if count >= 5), None)
    if dense_sequence or total_sequence_hits >= 8:
        line, count = dense_sequence or max(sequence_hits, key=lambda item: item[1])
        findings.append(
            Finding(
                rule="mechanical-sequencing",
                severity="warning",
                line=line,
                message="顺序连接词过密；检查它们是否真的表达逻辑，而不是制造整齐感。",
                evidence=f"本段 {count} 处，全文 {total_sequence_hits} 处",
            )
        )

    for paragraph in paragraphs:
        abstract_hits = sorted({term for term in ABSTRACT_TERMS if term in paragraph.text})
        anchor_hits = sorted({term for term in CONCRETE_ANCHORS if term in paragraph.text})
        has_number = bool(re.search(r"\d|[一二三四五六七八九十百千万]+(?:天|周|月|年|人|次|项|个)", paragraph.text))
        if len(abstract_hits) >= 5 and len(anchor_hits) + int(has_number) < 2:
            findings.append(
                Finding(
                    rule="abstract-cluster",
                    severity="warning",
                    line=paragraph.line,
                    message="抽象词集中出现，但具体对象、场景、动作或证据不足。",
                    evidence="、".join(abstract_hits),
                )
            )

    for previous, current in zip(paragraphs, paragraphs[1:]):
        left = _compact(previous.text)
        right = _compact(current.text)
        if min(len(left), len(right)) < 24:
            continue
        ratio = SequenceMatcher(None, left, right, autojunk=False).ratio()
        if ratio >= 0.86:
            findings.append(
                Finding(
                    rule="near-duplicate-paragraph",
                    severity="warning",
                    line=current.line,
                    message="相邻段落表达高度相似；考虑保留较强的一段或补充新的证据。",
                    evidence=f"相似度 {ratio:.0%}",
                )
            )

    paragraph_lengths = [len(_compact(paragraph.text)) for paragraph in paragraphs if len(_compact(paragraph.text)) >= 40]
    if len(paragraph_lengths) >= 8:
        mean_length = statistics.mean(paragraph_lengths)
        variation = statistics.pstdev(paragraph_lengths) / mean_length if mean_length else 0
        if variation < 0.12:
            findings.append(
                Finding(
                    rule="uniform-paragraph-rhythm",
                    severity="info",
                    line=paragraphs[0].line,
                    message="长段落长度过度一致；检查是否为了整齐而牺牲了自然节奏。",
                    evidence=f"长度变异系数 {variation:.2f}",
                )
            )

    headings = [(index, line) for index, line in enumerate(lines, start=1) if re.match(r"^#{1,6}\s+", line)]
    compact_length = len(_compact(prose_text))
    if len(headings) >= 6 and compact_length / len(headings) < 180:
        findings.append(
            Finding(
                rule="fragmented-heading-density",
                severity="info",
                line=headings[1][0] if len(headings) > 1 else headings[0][0],
                message="标题密度较高；检查文章是否被切成了幻灯片式碎片。",
                evidence=f"{len(headings)} 个标题 / {compact_length} 个非空白字符",
            )
        )

    if compact_length >= 800 and not any(marker in prose_text for marker in ACTION_MARKERS):
        findings.append(
            Finding(
                rule="missing-action-path",
                severity="blocker",
                line=1,
                message="长文没有清晰的下一步、责任主体或实践入口。",
                evidence="未发现行动表达",
            )
        )

    if compact_length >= 800 and not any(marker in prose_text for marker in RISK_MARKERS):
        findings.append(
            Finding(
                rule="missing-risk-boundary",
                severity="warning",
                line=1,
                message="长文只陈述方向，没有说明风险、边界或失败条件。",
                evidence="未发现风险表达",
            )
        )

    if technical:
        for paragraph in paragraphs:
            absolute_match = ABSOLUTE_TECHNICAL_CLAIM.search(paragraph.text)
            absolute_prefix = (
                paragraph.text[max(0, absolute_match.start() - 36) : absolute_match.start()]
                if absolute_match
                else ""
            )
            if absolute_match and not ABSOLUTE_NEGATION_CONTEXT.search(absolute_prefix):
                findings.append(
                    Finding(
                        rule="absolute-technical-claim",
                        severity="warning",
                        line=paragraph.line,
                        message="技术结论使用了绝对化措辞；核对它是否真的由代码、实验或运行证据支持。",
                        evidence=absolute_match.group(0),
                    )
                )

            has_business_term = any(
                term in paragraph.text for term in BUSINESS_IMPACT_TERMS
            )
            has_non_source_boundary = any(
                marker in paragraph.text for marker in METRIC_BOUNDARY_MARKERS
            )
            has_source_boundary = any(
                marker in paragraph.text for marker in SOURCE_BOUNDARY_MARKERS
            ) and not SOURCE_UNKNOWN.search(paragraph.text)
            has_boundary = has_non_source_boundary or has_source_boundary
            has_business_number = bool(
                PERCENT_VALUE.search(paragraph.text) or MONEY_VALUE.search(paragraph.text)
            )
            if has_business_term and has_business_number and not has_boundary:
                findings.append(
                    Finding(
                        rule="unqualified-business-impact",
                        severity="warning",
                        line=paragraph.line,
                        message="转化、GMV 或利润数字缺少来源、基线、口径或场景边界；不要把外部参数写成内部已证实损失。",
                        evidence="业务指标与百分比或金额缺少边界",
                    )
                )

            if (
                LATENCY_VALUE.search(paragraph.text)
                and not (has_business_term and has_business_number)
                and not has_boundary
            ):
                findings.append(
                    Finding(
                        rule="unqualified-technical-metric",
                        severity="warning",
                        line=paragraph.line,
                        message="技术指标缺少来源、环境、样本、时间窗或场景边界。",
                        evidence=LATENCY_VALUE.search(paragraph.text).group(0),
                    )
                )

        for block in code_blocks:
            if not block.closed:
                findings.append(
                    Finding(
                        rule="unclosed-code-fence",
                        severity="warning",
                        line=block.line,
                        message="代码围栏没有闭合；后续正文可能被错误渲染或跳过检查。",
                        evidence=block.fence,
                    )
                )
            if not block.language:
                findings.append(
                    Finding(
                        rule="untyped-code-fence",
                        severity="info",
                        line=block.line,
                        message="代码块没有语言类型；补充类型以便读者和渲染器正确识别。",
                        evidence=block.fence,
                    )
                )

            if any(COMMAND_LINE.search(line) for line in block.text.splitlines()):
                context_start = max(0, block.line - 4)
                context_end = min(len(source_lines), block.end_line + 3)
                context = "\n".join(source_lines[context_start:context_end])
                if not any(marker in context for marker in VERIFICATION_MARKERS):
                    findings.append(
                        Finding(
                            rule="unverified-command-block",
                            severity="warning",
                            line=block.line,
                            message="命令块没有说明已执行、未验证或预期输出；发布前明确其验证状态。",
                            evidence=next(
                                line.strip()
                                for line in block.text.splitlines()
                                if COMMAND_LINE.search(line)
                            ),
                        )
                    )

    return sorted(findings, key=lambda item: (item.line, item.rule))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run explainable editorial checks on an internal long-form Markdown draft."
    )
    parser.add_argument("path", type=Path, help="Markdown draft to inspect")
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Prior draft used to separate pre-existing findings from new regressions",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--technical",
        action="store_true",
        help="Enable technical-article checks for claims, impact numbers, and command blocks",
    )
    parser.add_argument(
        "--formal",
        action="store_true",
        help="Require the formal three-line masthead: H1, subtitle, and exact publication date",
    )
    parser.add_argument(
        "--max-findings",
        type=int,
        default=8,
        help="Exit 1 when findings exceed this count; blockers always exit 1",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_findings < 0:
        print("--max-findings must be zero or greater", file=sys.stderr)
        return 2
    if not args.path.is_file():
        print(f"Draft not found: {args.path}", file=sys.stderr)
        return 2
    if args.baseline is not None and not args.baseline.is_file():
        print(f"Baseline not found: {args.baseline}", file=sys.stderr)
        return 2

    text = args.path.read_text(encoding="utf-8")
    findings = analyze(text, technical=args.technical, formal=args.formal)
    baseline_findings = (
        analyze(
            args.baseline.read_text(encoding="utf-8"),
            technical=args.technical,
            formal=args.formal,
        )
        if args.baseline is not None
        else []
    )
    baseline_keys = {(item.rule, item.severity, item.evidence.strip()) for item in baseline_findings}
    pre_existing = [
        item for item in findings if (item.rule, item.severity, item.evidence.strip()) in baseline_keys
    ]
    new_findings = [
        item for item in findings if (item.rule, item.severity, item.evidence.strip()) not in baseline_keys
    ]
    blocker_count = sum(item.severity == "blocker" for item in new_findings)
    should_fail = blocker_count > 0 or len(new_findings) > args.max_findings

    if args.json:
        payload = {
            "path": args.path.name,
            "mode": "technical" if args.technical else "longform",
            "form": "formal" if args.formal else "draft",
            "summary": {
                "findings": len(findings),
                "pre_existing": len(pre_existing),
                "new_findings": len(new_findings),
                "blockers": blocker_count,
                "max_findings": args.max_findings,
                "status": "fail" if should_fail else "pass",
            },
            "findings": [item.to_dict() for item in findings],
            "pre_existing_findings": [item.to_dict() for item in pre_existing],
            "new_findings": [item.to_dict() for item in new_findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"Draft check: {len(new_findings)} new finding(s), "
            f"{len(pre_existing)} pre-existing, {blocker_count} new blocker(s)"
        )
        for finding in new_findings:
            print(
                f"[{finding.severity}] line {finding.line} {finding.rule}: "
                f"{finding.message} ({finding.evidence})"
            )
        if not new_findings:
            print("No heuristic issues found. Human editorial judgment is still required.")

    return 1 if should_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

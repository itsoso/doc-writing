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

EXACT_PUBLICATION_DATE = re.compile(
    r"(?P<year>(?:19|20)\d{2})\s*年\s*"
    r"(?P<month>0?[1-9]|1[0-2])\s*月\s*"
    r"(?P<day>0?[1-9]|[12]\d|3[01])\s*日"
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


def _has_valid_exact_publication_date(title: str) -> bool:
    for match in EXACT_PUBLICATION_DATE.finditer(title):
        try:
            date(
                int(match.group("year")),
                int(match.group("month")),
                int(match.group("day")),
            )
        except ValueError:
            continue
        return True
    return False


def _masthead_date(lines: list[str]) -> tuple[int, str] | None:
    for line_number, raw_line in enumerate(lines[:12], start=1):
        value = raw_line.strip()
        match = EXACT_PUBLICATION_DATE.fullmatch(value)
        if match and _has_valid_exact_publication_date(value):
            return line_number, value
    return None


def analyze(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    paragraphs = _plain_paragraphs(text)

    title = next(
        ((index, line[2:].strip()) for index, line in enumerate(lines, start=1) if line.startswith("# ")),
        None,
    )
    masthead_date = _masthead_date(lines)
    if masthead_date is None:
        partial_date = next(
            (
                (index, line.strip())
                for index, line in enumerate(lines[:12], start=1)
                if re.fullmatch(r"(?:19|20)\d{2}\s*年\s*(?:0?[1-9]|1[0-2])\s*月", line.strip())
            ),
            None,
        )
        findings.append(
            Finding(
                rule="missing-exact-publication-date",
                severity="blocker",
                line=partial_date[0] if partial_date else (title[0] if title else 1),
                message="正式题头必须包含独立且精确到日的发布日期（YYYY 年 M 月 D 日）。",
                evidence=partial_date[1] if partial_date else "题头前 12 行未发现独立日期",
            )
        )

    if title is not None and (EXACT_PUBLICATION_DATE.search(title[1]) or "｜" in title[1]):
        findings.append(
            Finding(
                rule="combined-formal-masthead",
                severity="blocker",
                line=title[0],
                message="主标题、副标题和发布日期必须分成三行，不得合并进 H1。",
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
    if timezone_line is not None:
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
    compact_length = len(_compact(text))
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

    if compact_length >= 800 and not any(marker in text for marker in ACTION_MARKERS):
        findings.append(
            Finding(
                rule="missing-action-path",
                severity="blocker",
                line=1,
                message="长文没有清晰的下一步、责任主体或实践入口。",
                evidence="未发现行动表达",
            )
        )

    if compact_length >= 800 and not any(marker in text for marker in RISK_MARKERS):
        findings.append(
            Finding(
                rule="missing-risk-boundary",
                severity="warning",
                line=1,
                message="长文只陈述方向，没有说明风险、边界或失败条件。",
                evidence="未发现风险表达",
            )
        )

    return sorted(findings, key=lambda item: (item.line, item.rule))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run explainable editorial checks on an internal long-form Markdown draft."
    )
    parser.add_argument("path", type=Path, help="Markdown draft to inspect")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
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

    text = args.path.read_text(encoding="utf-8")
    findings = analyze(text)
    blocker_count = sum(item.severity == "blocker" for item in findings)
    should_fail = blocker_count > 0 or len(findings) > args.max_findings

    if args.json:
        payload = {
            "path": str(args.path),
            "summary": {
                "findings": len(findings),
                "blockers": blocker_count,
                "max_findings": args.max_findings,
                "status": "fail" if should_fail else "pass",
            },
            "findings": [item.to_dict() for item in findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Draft check: {len(findings)} finding(s), {blocker_count} blocker(s)")
        for finding in findings:
            print(
                f"[{finding.severity}] line {finding.line} {finding.rule}: "
                f"{finding.message} ({finding.evidence})"
            )
        if not findings:
            print("No heuristic issues found. Human editorial judgment is still required.")

    return 1 if should_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

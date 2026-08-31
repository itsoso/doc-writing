from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("repair_docs_jsonml_style.py")
SPEC = importlib.util.spec_from_file_location("repair_docs_jsonml_style", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


FIXTURE = {
    "body": [
        ["root", {"layout": "LOOSE", "paper": "A3"}],
        ["h1", {"id": "h.title", "jc": "left"}, ["text", {}, "示例标题"]],
        ["p", {"id": "p.subtitle", "jc": "left"}, ["text", {}, "示例副标题"]],
        ["p", {"id": "p.date", "jc": "left"}, ["text", {}, "2099 年 1 月 2 日"]],
        ["p", {"id": "p.lead", "jc": "center"}, ["text", {}, "示例导语"]],
        ["h2", {"id": "h.section", "jc": "center"}, ["text", {}, "示例章节"]],
        ["h3", {"id": "h.subsection", "jc": "center"}, ["text", {}, "示例小节"]],
        [
            "p",
            {
                "id": "p.item",
                "list": {"level": 0, "listId": "list-1", "type": "unordered"},
                "jc": "center",
            },
            ["text", {"bold": True}, "示例项目"],
            ["text", {}, "：示例说明"],
        ],
    ],
    "docId": "doc-1",
    "version": 7,
}


def text_leaves(value: object) -> list[str]:
    if isinstance(value, list):
        if len(value) >= 3 and value[0] == "text":
            return [str(value[2])]
        output: list[str] = []
        for child in value:
            output.extend(text_leaves(child))
        return output
    if isinstance(value, dict):
        output = []
        for child in value.values():
            output.extend(text_leaves(child))
        return output
    return []


class RepairDocsJsonmlStyleTests(unittest.TestCase):
    def test_style_ops_preserve_text_and_apply_kstack_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.json"
            output_path = Path(temp_dir) / "ops.json"
            input_path.write_text(json.dumps(FIXTURE, ensure_ascii=False), encoding="utf-8")
            MODULE.build_ops(input_path, output_path)
            ops = json.loads(output_path.read_text(encoding="utf-8"))

        replacement_by_anchor = {item["anchor"]: item["content"][0] for item in ops}
        self.assertEqual(len(ops), 7)
        self.assertEqual(
            text_leaves(FIXTURE["body"]),
            text_leaves([replacement_by_anchor[item[1]["id"]] for item in FIXTURE["body"][1:]]),
        )
        self.assertEqual("center", replacement_by_anchor["h.title"][1]["jc"])
        self.assertEqual("center", replacement_by_anchor["p.subtitle"][1]["jc"])
        self.assertEqual("center", replacement_by_anchor["p.date"][1]["jc"])
        self.assertEqual("left", replacement_by_anchor["h.section"][1]["jc"])
        self.assertEqual(
            "#2e74b5",
            replacement_by_anchor["h.subsection"][2][1]["color"],
        )
        self.assertEqual("left", replacement_by_anchor["p.item"][1]["jc"])
        self.assertEqual(
            FIXTURE["body"][7][1]["list"],
            replacement_by_anchor["p.item"][1]["list"],
        )

    def test_index_profile_repairs_subtitle_date_and_h3_with_index_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.json"
            output_path = Path(temp_dir) / "ops.json"
            input_path.write_text(json.dumps(FIXTURE, ensure_ascii=False), encoding="utf-8")
            MODULE.build_ops(input_path, output_path, profile="index")
            ops = json.loads(output_path.read_text(encoding="utf-8"))

        replacement_by_anchor = {item["anchor"]: item["content"][0] for item in ops}
        self.assertEqual("left", replacement_by_anchor["p.subtitle"][1]["jc"])
        self.assertEqual("left", replacement_by_anchor["p.date"][1]["jc"])
        h3_text_attrs = replacement_by_anchor["h.subsection"][2][1]
        self.assertEqual("#17344b", h3_text_attrs["color"])

    def test_cli_accepts_explicit_index_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.json"
            output_path = Path(temp_dir) / "ops.json"
            input_path.write_text(json.dumps(FIXTURE, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--profile",
                    "index",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
            ops = json.loads(output_path.read_text(encoding="utf-8"))

        replacement_by_anchor = {item["anchor"]: item["content"][0] for item in ops}
        self.assertEqual("left", replacement_by_anchor["p.subtitle"][1]["jc"])
        self.assertEqual("#17344b", replacement_by_anchor["h.subsection"][2][1]["color"])


if __name__ == "__main__":
    unittest.main()

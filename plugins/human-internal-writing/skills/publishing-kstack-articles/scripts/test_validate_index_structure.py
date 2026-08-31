from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_index_structure.py")
SPEC = importlib.util.spec_from_file_location("validate_index_structure", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


SOURCE = """# 示例知识入口

## 全局介绍

这些主线共同构成一个反馈系统。

## 01｜主线甲

[进入甲](https://example.com/a)

![甲图](images/a.png)

## 02｜主线乙

[进入乙](https://example.com/b)

![乙图](images/b.png)
"""


class IndexStructureContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = MODULE.capture_contract(SOURCE.encode("utf-8"))

    def codes(self, remote: str, *, source: str = SOURCE) -> set[str]:
        result = MODULE.compare_contract(
            source.encode("utf-8"),
            self.contract,
            remote.encode("utf-8"),
        )
        return {finding["code"] for finding in result["findings"]}

    def test_matching_exported_markdown_passes(self) -> None:
        result = MODULE.compare_contract(
            SOURCE.encode("utf-8"),
            self.contract,
            SOURCE.encode("utf-8"),
        )

        self.assertTrue(result["ok"])
        self.assertEqual([], result["findings"])

    def test_contract_binds_source_plugin_and_validator_versions(self) -> None:
        self.assertEqual("kstack.index-structure.v1", self.contract["schema_version"])
        self.assertEqual(64, len(self.contract["source_sha256"]))
        self.assertEqual(64, len(self.contract["validator_sha256"]))
        self.assertEqual(64, len(self.contract["style_validator_sha256"]))
        self.assertRegex(self.contract["plugin_version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(2, self.contract["structure"]["image_count"])

    def test_changed_heading_order_is_rejected(self) -> None:
        remote = SOURCE.replace("## 01｜主线甲", "## __SWAP__", 1).replace(
            "## 02｜主线乙",
            "## 01｜主线甲",
            1,
        ).replace("## __SWAP__", "## 02｜主线乙", 1)
        self.assertIn("index_remote_headings_mismatch", self.codes(remote))

    def test_changed_link_target_is_rejected(self) -> None:
        remote = SOURCE.replace("https://example.com/b", "https://example.com/changed")
        self.assertIn("index_remote_links_mismatch", self.codes(remote))

    def test_changed_image_order_is_rejected(self) -> None:
        remote = SOURCE.replace("![甲图](images/a.png)", "![占位](images/swap.png)", 1).replace(
            "![乙图](images/b.png)",
            "![甲图](images/a.png)",
            1,
        ).replace("![占位](images/swap.png)", "![乙图](images/b.png)", 1)
        self.assertIn("index_remote_images_mismatch", self.codes(remote))

    def test_changed_image_count_is_rejected(self) -> None:
        remote = SOURCE.replace("\n![乙图](images/b.png)\n", "\n")
        self.assertIn("index_remote_images_mismatch", self.codes(remote))

    def test_changed_local_source_cannot_reuse_the_contract(self) -> None:
        changed = SOURCE.replace("这些主线共同构成一个反馈系统。", "本地源已经改变。")
        self.assertIn(
            "index_source_hash_mismatch",
            self.codes(SOURCE, source=changed),
        )

    def test_html_readback_compares_by_semantics_not_markup(self) -> None:
        remote = """
        <h1><span>示例知识入口</span></h1>
        <h2>全局介绍</h2>
        <h2>01｜主线甲</h2>
        <p><a href="https://example.com/a">进入甲</a></p>
        <p><img src="images/a.png" alt="甲图"></p>
        <h2>02｜主线乙</h2>
        <p><a href="https://example.com/b">进入乙</a></p>
        <p><img src="images/b.png" alt="乙图"></p>
        """
        result = MODULE.compare_contract(
            SOURCE.encode("utf-8"),
            self.contract,
            remote.encode("utf-8"),
        )
        self.assertTrue(result["ok"], result)

    def test_cli_capture_and_compare_avoid_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "index.md"
            remote = root / "remote.md"
            contract = root / "index-structure.json"
            source.write_text(SOURCE, encoding="utf-8")
            remote.write_text(SOURCE, encoding="utf-8")

            captured = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "capture",
                    "--source",
                    str(source),
                    "--output",
                    str(contract),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            compared = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "compare",
                    "--source",
                    str(source),
                    "--contract",
                    str(contract),
                    "--remote",
                    str(remote),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            saved = json.loads(contract.read_text(encoding="utf-8"))

        self.assertEqual(0, captured.returncode, captured.stderr or captured.stdout)
        self.assertEqual(0, compared.returncode, compared.stderr or compared.stdout)
        self.assertNotIn(temp_dir, captured.stdout)
        self.assertNotIn(temp_dir, compared.stdout)
        self.assertEqual("index.md", saved["source_path"])


if __name__ == "__main__":
    unittest.main()

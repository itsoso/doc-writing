from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RESOLVER = SCRIPT_DIR / "resolve_docs_target.py"


def envelope(items: list[dict[str, object]], *, has_next: object = False) -> str:
    return json.dumps(
        {
            "ok": True,
            "data": {
                "result": {
                    "hasNext": has_next,
                    "items": items,
                }
            },
        }
    )


class DocsTargetResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        if self._testMethodName != "test_resolver_script_exists" and not RESOLVER.is_file():
            self.skipTest("Docs target resolver is not implemented yet")

    def run_resolver(self, payload: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(RESOLVER), "--title", "我的个人主页"],
            input=payload,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_resolver_script_exists(self) -> None:
        self.assertTrue(RESOLVER.is_file(), "Docs target resolver has not been implemented")

    def test_unique_exact_match_returns_folder_target(self) -> None:
        result = self.run_resolver(
            envelope(
                [
                    {"title": "其他空间", "docId": "folder_other", "docTypeEn": "group"},
                    {
                        "title": "我的个人主页",
                        "docId": "folder_target",
                        "viewId": "view_target",
                        "docTypeEn": "group",
                    },
                ]
            )
        )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual("folder_target", payload["target"]["id"])
        self.assertEqual("drive", payload["target"]["kind"])

    def test_zero_match_fails_closed(self) -> None:
        result = self.run_resolver(envelope([]))

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("target_not_found", payload["reason_code"])

    def test_duplicate_match_fails_closed(self) -> None:
        result = self.run_resolver(
            envelope(
                [
                    {"title": "我的个人主页", "docId": "folder_one", "docTypeEn": "group"},
                    {"title": "我的个人主页", "docId": "folder_two", "docTypeEn": "group"},
                ]
            )
        )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("target_ambiguous", payload["reason_code"])

    def test_incomplete_pagination_fails_closed(self) -> None:
        result = self.run_resolver(
            envelope(
                [{"title": "我的个人主页", "docId": "folder_target", "docTypeEn": "group"}],
                has_next=True,
            )
        )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("pagination_incomplete", payload["reason_code"])

    def test_only_literal_false_proves_pagination_is_complete(self) -> None:
        for label, value in (
            ("missing", object()),
            ("null", None),
            ("string_false", "false"),
            ("zero", 0),
        ):
            with self.subTest(label=label):
                raw = json.loads(
                    envelope(
                        [
                            {
                                "title": "我的个人主页",
                                "docId": "folder_target",
                                "docTypeEn": "group",
                            }
                        ]
                    )
                )
                if label == "missing":
                    del raw["data"]["result"]["hasNext"]
                else:
                    raw["data"]["result"]["hasNext"] = value

                result = self.run_resolver(json.dumps(raw))

                self.assertNotEqual(0, result.returncode)
                payload = json.loads(result.stdout)
                self.assertEqual("pagination_incomplete", payload["reason_code"])

    def test_same_title_with_wrong_doc_type_fails_closed(self) -> None:
        result = self.run_resolver(
            envelope(
                [
                    {
                        "title": "我的个人主页",
                        "docId": "ordinary_document",
                        "docTypeEn": "word",
                    }
                ]
            )
        )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("target_wrong_type", payload["reason_code"])


if __name__ == "__main__":
    unittest.main()

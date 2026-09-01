from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_public_repo import scan


class PublicRepoScanTests(unittest.TestCase):
    def test_clean_export_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("Evidence-led writing with public sources.", encoding="utf-8")
            self.assertEqual(scan(root), [])

    def test_internal_links_and_credentials_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            internal_host = "docs." + "corp.kuaishou.com"
            internal_doc_id = "fcABC" + "123456789"
            (root / "article.md").write_text(
                "See https://" + internal_host + "/d/home/" + internal_doc_id + " and Bearer " + "abcdefghijklmnop.",
                encoding="utf-8",
            )
            rules = {finding["rule"] for finding in scan(root)}
            self.assertIn("internal_url", rules)
            self.assertIn("internal_doc_id", rules)
            self.assertIn("credential", rules)


if __name__ == "__main__":
    unittest.main()

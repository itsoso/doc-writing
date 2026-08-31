from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CONTRACT = SKILL_DIR / "assets" / "kstack-style.v1.json"


class StyleContractTests(unittest.TestCase):
    def test_machine_readable_contract_is_the_single_token_source(self) -> None:
        self.assertTrue(CONTRACT.is_file(), "machine-readable style contract is missing")
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))

        self.assertEqual("kstack.style.v1", payload["schema_version"])
        self.assertEqual("A3", payload["docs"]["view_model"])
        self.assertEqual(11, payload["docs"]["roles"]["body"]["size"])
        self.assertEqual("center", payload["docs"]["roles"]["h1"]["alignment"])
        self.assertEqual("center", payload["docs"]["roles"]["subtitle"]["alignment"])
        self.assertEqual("center", payload["docs"]["roles"]["date"]["alignment"])
        self.assertEqual("left", payload["docs"]["roles"]["h2"]["alignment"])
        self.assertEqual("left", payload["docs"]["roles"]["h3"]["alignment"])
        index_overrides = payload["docs"]["profiles"]["index"]["role_overrides"]
        self.assertEqual("left", index_overrides["h2"]["alignment"])
        self.assertEqual("left", index_overrides["h3"]["alignment"])
        self.assertEqual("#17344B", index_overrides["h3"]["color"])
        for role in ("kicker", "lead", "body", "list", "caption", "source"):
            self.assertEqual("left", payload["docs"]["roles"][role]["alignment"], role)
        self.assertEqual(210, payload["docx"]["page"]["width_mm"])
        self.assertEqual(297, payload["docx"]["page"]["height_mm"])
        self.assertEqual(21, payload["docx"]["page"]["margin_mm"])
        self.assertEqual(11, payload["docx"]["roles"]["body"]["size_pt"])
        self.assertEqual("center", payload["docx"]["roles"]["title"]["alignment"])
        self.assertEqual("center", payload["docx"]["roles"]["subtitle"]["alignment"])
        self.assertEqual("center", payload["docx"]["roles"]["date"]["alignment"])
        self.assertEqual("left", payload["docx"]["roles"]["h2"]["alignment"])
        self.assertEqual("left", payload["docx"]["roles"]["h3"]["alignment"])
        for role in ("kicker", "lead", "body", "list", "caption", "source"):
            self.assertEqual("left", payload["docx"]["roles"][role]["alignment"], role)


if __name__ == "__main__":
    unittest.main()

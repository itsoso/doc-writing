from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_dependencies import install_plan, resolve


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "skill-dependencies.json"


def _skill(root: Path, name: str) -> None:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"---\nname: {name}\ndescription: Use when testing.\n---\n",
        encoding="utf-8",
    )


class DependencyResolverTests(unittest.TestCase):
    def test_generic_profile_is_ready_from_bundled_skills(self) -> None:
        result = resolve(MANIFEST, "generic", [])
        self.assertEqual("ready", result["status"])
        self.assertTrue(all(item["status"] == "ready" for item in result["required"]))

    def test_internal_profile_blocks_without_enterprise_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = resolve(MANIFEST, "kuaishou-internal", [Path(directory)])
        self.assertEqual("blocked", result["status"])
        missing = {
            item["capability"]
            for item in result["required"]
            if item["status"] == "missing"
        }
        self.assertEqual(
            {"internal-docs-read-write", "kim-message-read", "onepoint-meeting-read"},
            missing,
        )

    def test_internal_profile_accepts_all_declared_runtime_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                "docs-cli",
                "docs-word",
                "docs-search",
                "docs-view",
                "docs-docs",
                "docs-meeting-record",
                "kim-sender-context",
                "kim-cli",
                "kim-im",
                "onepoint",
            ):
                _skill(root, name)
            result = resolve(MANIFEST, "kuaishou-internal", [root])
        self.assertEqual("ready", result["status"])

    def test_plan_never_contains_credentials_or_private_data(self) -> None:
        result = {
            "required": [
                {
                    "capability": "onepoint-meeting-read",
                    "source": "enterprise-runtime",
                    "status": "missing",
                    "skill_names": ["onepoint"],
                    "missing": ["onepoint"],
                }
            ],
            "optional": [],
        }
        plan = "\n".join(install_plan(result, "approved-enterprise-marketplace"))
        self.assertIn("approved-enterprise-marketplace", plan)
        self.assertNotIn("Bearer", plan)
        self.assertNotIn("fcA", plan)


if __name__ == "__main__":
    unittest.main()

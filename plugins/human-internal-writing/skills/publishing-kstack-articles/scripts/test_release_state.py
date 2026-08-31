from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("release_state.py")


class ReleaseStateTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)

    def mark(self, state: Path, source: Path, stage: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "mark",
            "--state",
            str(state),
            "--source",
            str(source),
            "--stage",
            stage,
            "--json",
        )

    def test_source_change_invalidates_all_dependent_stages(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "release state tool is missing")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            state = root / "release-state.json"
            source.write_text("# 标题\n", encoding="utf-8")

            first = self.run_cli("init", "--state", str(state), "--source", str(source), "--json")
            self.assertEqual(0, first.returncode, first.stderr)
            for stage in ("source_ready", "docx_generated", "docx_structurally_valid"):
                marked = self.mark(state, source, stage)
                self.assertEqual(0, marked.returncode, marked.stderr)

            source.write_text("# 新标题\n", encoding="utf-8")
            inspected = self.run_cli("inspect", "--state", str(state), "--source", str(source), "--json")
            self.assertEqual(0, inspected.returncode, inspected.stderr)
            payload = json.loads(inspected.stdout)

        self.assertTrue(payload["source_changed"])
        self.assertEqual("source_ready", payload["next_stage"])
        self.assertFalse(payload["stages"]["docx_structurally_valid"]["complete"])

    def test_next_stage_resumes_after_last_proven_checkpoint(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "release state tool is missing")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            state = root / "release-state.json"
            source.write_text("# 标题\n", encoding="utf-8")
            self.run_cli("init", "--state", str(state), "--source", str(source), "--json")
            for stage in ("source_ready", "docx_generated", "docx_structurally_valid"):
                result = self.mark(state, source, stage)
                self.assertEqual(0, result.returncode, result.stderr)
            inspected = self.run_cli("inspect", "--state", str(state), "--source", str(source), "--json")
            payload = json.loads(inspected.stdout)

        self.assertEqual("wps_visually_verified", payload["next_stage"])

    def test_cannot_skip_required_stage(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "release state tool is missing")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            state = root / "release-state.json"
            source.write_text("# 标题\n", encoding="utf-8")
            self.run_cli("init", "--state", str(state), "--source", str(source), "--json")
            result = self.mark(state, source, "docs_created")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("stage_not_requested", result.stderr)

    def test_word_terminal_state_stops_before_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            state = root / "release-state.json"
            source.write_text("# 示例标题\n", encoding="utf-8")
            initialized = self.run_cli(
                "init",
                "--state",
                str(state),
                "--source",
                str(source),
                "--terminal-state",
                "word_verified",
                "--json",
            )
            self.assertEqual(0, initialized.returncode, initialized.stderr)
            for stage in (
                "source_ready",
                "docx_generated",
                "docx_structurally_valid",
                "wps_visually_verified",
                "word_verified",
            ):
                marked = self.mark(state, source, stage)
                self.assertEqual(0, marked.returncode, marked.stderr)
            payload = json.loads(marked.stdout)

        self.assertEqual("word_verified", payload["requested_terminal_state"])
        self.assertIsNone(payload["next_stage"])
        self.assertNotIn("docs_created", payload["stages"])

    def test_legacy_local_verified_migrates_to_word_only_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state = root / "release-state.json"
            completed = {"complete": True, "at": "2099-01-02T00:00:00+00:00"}
            state.write_text(
                json.dumps(
                    {
                        "schema_version": "kstack.release-state.v1",
                        "created_at": "2099-01-02T00:00:00+00:00",
                        "source": {"path": "article.md", "sha256": "legacy-hash"},
                        "stages": {
                            "source_ready": completed,
                            "docx_generated": completed,
                            "docx_structurally_valid": completed,
                            "wps_visually_verified": completed,
                            "local_verified": completed,
                            "docs_created": completed,
                            "docs_readback_verified": completed,
                        },
                    }
                ),
                encoding="utf-8",
            )
            inspected = self.run_cli("inspect", "--state", str(state), "--json")

        self.assertEqual(0, inspected.returncode, inspected.stderr)
        payload = json.loads(inspected.stdout)
        self.assertEqual("word_verified", payload["requested_terminal_state"])
        self.assertTrue(payload["stages"]["word_verified"]["complete"])
        self.assertNotIn("local_verified", payload["stages"])
        self.assertNotIn("docs_created", payload["stages"])
        self.assertIsNone(payload["next_stage"])

    def test_docs_terminal_state_requires_target_and_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            state = root / "release-state.json"
            source.write_text("# 示例标题\n", encoding="utf-8")
            missing_authority = self.run_cli(
                "init",
                "--state",
                str(state),
                "--source",
                str(source),
                "--terminal-state",
                "docs_verified",
                "--json",
            )
            authorized = self.run_cli(
                "init",
                "--state",
                str(state),
                "--source",
                str(source),
                "--terminal-state",
                "docs_verified",
                "--docs-target-label",
                "示例发布区",
                "--docs-authorized",
                "--json",
            )

        self.assertNotEqual(0, missing_authority.returncode)
        self.assertIn("docs_target_and_authorization_required", missing_authority.stderr)
        self.assertEqual(0, authorized.returncode, authorized.stderr)
        payload = json.loads(authorized.stdout)
        self.assertEqual("docs_verified", payload["requested_terminal_state"])
        self.assertIn("docs_created", payload["stages"])
        self.assertTrue(payload["docs_request"]["authorization_confirmed"])

    def test_every_mark_rehashes_source_and_fails_closed_on_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            state = root / "release-state.json"
            source.write_text("# 示例标题\n", encoding="utf-8")
            self.run_cli("init", "--state", str(state), "--source", str(source), "--json")
            first = self.mark(state, source, "source_ready")
            self.assertEqual(0, first.returncode, first.stderr)
            source.write_text("# 已漂移标题\n", encoding="utf-8")
            drifted = self.mark(state, source, "docx_generated")
            persisted = json.loads(state.read_text(encoding="utf-8"))

        self.assertNotEqual(0, drifted.returncode)
        self.assertIn("source_changed", drifted.stderr)
        self.assertFalse(persisted["stages"]["source_ready"]["complete"])
        self.assertFalse(persisted["stages"]["docx_generated"]["complete"])

    def test_state_uses_safe_source_locator_not_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            state = root / "release-state.json"
            source.write_text("# 示例标题\n", encoding="utf-8")
            result = self.run_cli(
                "init", "--state", str(state), "--source", str(source), "--json"
            )
            serialized = state.read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn(str(root), serialized)
        self.assertEqual("article.md", json.loads(serialized)["source"]["path"])

    def test_inspect_redacts_legacy_absolute_source_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            state = root / "release-state.json"
            source.write_text("# 示例标题\n", encoding="utf-8")
            self.run_cli("init", "--state", str(state), "--source", str(source), "--json")
            legacy = json.loads(state.read_text(encoding="utf-8"))
            legacy["source"]["path"] = str(source.resolve())
            state.write_text(json.dumps(legacy), encoding="utf-8")
            inspected = self.run_cli("inspect", "--state", str(state), "--json")

        self.assertEqual(0, inspected.returncode, inspected.stderr)
        self.assertNotIn(str(root), inspected.stdout)
        self.assertEqual("article.md", json.loads(inspected.stdout)["source"]["path"])


if __name__ == "__main__":
    unittest.main()

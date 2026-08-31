from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("track_writing_timing.py")


class WritingTimingTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)

    def test_records_ordered_milestones_and_rework(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "writing timing tool is missing")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "writing-timing.json"
            for event in ("started", "first_complete_draft", "editorially_ready"):
                result = self.run_cli("mark", "--file", str(path), "--event", event, "--json")
                self.assertEqual(0, result.returncode, result.stderr)
            result = self.run_cli("mark", "--file", str(path), "--event", "rework", "--reason", "evidence_gap", "--json")
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)

        self.assertEqual("kstack.writing-timing.v1", payload["schema_version"])
        self.assertEqual(1, payload["rework_count"])
        self.assertEqual("editorially_ready", payload["highest_milestone"])
        self.assertEqual(4, len(payload["events"]))

    def test_rejects_out_of_order_terminal_milestone(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "writing timing tool is missing")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "writing-timing.json"
            result = self.run_cli("mark", "--file", str(path), "--event", "docs_verified", "--json")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing_prior_milestone", result.stderr)

    def test_default_docs_path_does_not_require_word_verification(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "writing timing tool is missing")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "writing-timing.json"
            for event in (
                "started",
                "first_complete_draft",
                "editorially_ready",
                "markdown_verified",
                "docs_verified",
            ):
                result = self.run_cli("mark", "--file", str(path), "--event", event, "--json")
                self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)

        self.assertEqual("docs_verified", payload["highest_milestone"])
        self.assertNotIn("word_verified", [item["event"] for item in payload["events"]])

    def test_word_verification_is_optional_after_markdown(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "writing timing tool is missing")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "writing-timing.json"
            for event in (
                "started",
                "first_complete_draft",
                "editorially_ready",
                "markdown_verified",
                "word_verified",
            ):
                result = self.run_cli("mark", "--file", str(path), "--event", event, "--json")
                self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)

        self.assertEqual("word_verified", payload["highest_milestone"])

    def test_calculates_wall_clock_stage_durations(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "writing timing tool is missing")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "writing-timing.json"
            events = (
                ("started", "2099-04-05T12:00:00+00:00"),
                ("first_complete_draft", "2099-04-05T12:10:00+00:00"),
                ("editorially_ready", "2099-04-05T12:15:30+00:00"),
            )
            for event, at in events:
                result = self.run_cli("mark", "--file", str(path), "--event", event, "--at", at, "--json")
                self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)

        self.assertEqual(600, payload["durations_seconds"]["started_to_first_complete_draft"])
        self.assertEqual(330, payload["durations_seconds"]["first_complete_draft_to_editorially_ready"])
        self.assertEqual(930, payload["elapsed_seconds"])


if __name__ == "__main__":
    unittest.main()

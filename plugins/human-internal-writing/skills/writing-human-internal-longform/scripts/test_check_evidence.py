from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "check_evidence.py"
FIELDS = [
    "claim_id",
    "section",
    "claim",
    "state",
    "risk",
    "source_locator",
    "source_version",
    "verification_status",
    "freshness_status",
    "depends_on",
    "notes",
]


class EvidenceCheckerCliTests(unittest.TestCase):
    def _row(self, **overrides: str) -> dict[str, str]:
        row = {
            "claim_id": "C001",
            "section": "Current state",
            "claim": "The verified sample contains twelve service nodes",
            "state": "observed",
            "risk": "high",
            "source_locator": "trace://example/snapshot#nodes",
            "source_version": "sha256:abc123",
            "verification_status": "verified",
            "freshness_status": "current",
            "depends_on": "",
            "notes": "synthetic fixture",
        }
        row.update(overrides)
        return row

    def _write_ledger(self, rows: list[dict[str, str]], fields: list[str] = FIELDS) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        ledger = Path(temp_dir.name) / "evidence.csv"
        with ledger.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return ledger

    def _run(self, ledger: Path, require_ready: bool = True) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(CHECKER), str(ledger), "--json"]
        if require_ready:
            command.append("--require-ready")
        return subprocess.run(command, check=False, capture_output=True, text=True)

    def _rules(self, result: subprocess.CompletedProcess[str]) -> set[str]:
        return {item["rule"] for item in json.loads(result.stdout)["findings"]}

    def test_ready_ledger_passes_with_machine_readable_summary(self) -> None:
        result = self._run(self._write_ledger([self._row()]))
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ready"])
        self.assertEqual({"claims": 1, "blockers": 0, "warnings": 0}, payload["summary"])

    def test_unverified_high_risk_source_blocks_readiness(self) -> None:
        result = self._run(self._write_ledger([self._row(verification_status="unverified")]))
        self.assertEqual(1, result.returncode)
        self.assertIn("unverified-high-risk-claim", self._rules(result))

    def test_sourced_claim_without_locator_is_blocked(self) -> None:
        result = self._run(self._write_ledger([self._row(risk="medium", source_locator="")]))
        self.assertEqual(1, result.returncode)
        self.assertIn("missing-source-locator", self._rules(result))

    def test_stale_high_risk_source_blocks_readiness(self) -> None:
        result = self._run(self._write_ledger([self._row(freshness_status="stale")]))
        self.assertEqual(1, result.returncode)
        self.assertIn("stale-high-risk-source", self._rules(result))

    def test_high_risk_inference_requires_claim_dependencies(self) -> None:
        result = self._run(
            self._write_ledger(
                [self._row(state="inference", source_locator="", verification_status="not_required", freshness_status="not_applicable")]
            )
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("unbound-high-risk-reasoning", self._rules(result))

    def test_high_risk_unknown_blocks_readiness(self) -> None:
        result = self._run(
            self._write_ledger(
                [self._row(state="unknown", risk="critical", source_locator="", verification_status="unverified", freshness_status="unknown")]
            )
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("material-unknown", self._rules(result))

    def test_dependency_must_reference_existing_claim(self) -> None:
        inference = self._row(
            claim_id="C002",
            state="inference",
            source_locator="",
            verification_status="not_required",
            freshness_status="not_applicable",
            depends_on="C999",
        )
        result = self._run(self._write_ledger([self._row(), inference]))
        self.assertEqual(1, result.returncode)
        self.assertIn("unknown-claim-dependency", self._rules(result))

    def test_missing_required_columns_is_schema_error(self) -> None:
        result = self._run(self._write_ledger([{"claim_id": "C001", "claim": "two columns"}], ["claim_id", "claim"]), require_ready=False)
        self.assertEqual(2, result.returncode)
        self.assertEqual("invalid-schema", json.loads(result.stdout)["error"])

    def test_duplicate_claim_ids_are_blocked(self) -> None:
        result = self._run(self._write_ledger([self._row(), self._row(claim="A second claim")]))
        self.assertEqual(1, result.returncode)
        self.assertIn("duplicate-claim-id", self._rules(result))

    def test_unknown_evidence_state_is_blocked(self) -> None:
        result = self._run(self._write_ledger([self._row(state="source", risk="medium")]))
        self.assertEqual(1, result.returncode)
        self.assertIn("invalid-state", self._rules(result))

    def test_claim_id_must_use_stable_c_number_format(self) -> None:
        result = self._run(self._write_ledger([self._row(claim_id="claim-one", risk="medium")]))
        self.assertEqual(1, result.returncode)
        self.assertIn("invalid-claim-id", self._rules(result))


if __name__ == "__main__":
    unittest.main()

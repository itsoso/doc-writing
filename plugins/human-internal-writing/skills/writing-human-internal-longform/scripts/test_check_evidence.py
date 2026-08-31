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


class EvidenceCheckerCliTests(unittest.TestCase):
    def _write_ledger(self, rows: list[dict[str, str]]) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        ledger = Path(temp_dir.name) / "evidence.csv"
        with ledger.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        return ledger

    def test_ready_ledger_passes_with_machine_readable_summary(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C001",
                    "section": "现状",
                    "claim": "合成测试主张：样本接口 P99 为 731ms",
                    "state": "observed",
                    "risk": "high",
                    "source_locator": "example://fixture/trace-2099-04-05#p99",
                    "source_version": "sha256:abc123",
                    "verification_status": "verified",
                    "freshness_status": "current",
                    "depends_on": "",
                    "notes": "同一批灰度请求",
                }
            ]
        )

        self.assertTrue(CHECKER.exists(), "evidence checker must exist")
        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ready"])
        self.assertEqual(1, payload["summary"]["claims"])
        self.assertEqual(0, payload["summary"]["blockers"])
        self.assertEqual(ledger.name, payload["path"])
        self.assertNotIn(str(ledger.parent), result.stdout)

    def test_misspelled_risk_is_blocked_and_cannot_skip_high_risk_checks(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C008",
                    "section": "影响",
                    "claim": "风险拼写错误不能降级证据要求",
                    "state": "sourced",
                    "risk": "critcal",
                    "source_locator": "example://fixture/high-risk",
                    "source_version": "fixture-v1",
                    "verification_status": "unverified",
                    "freshness_status": "stale",
                    "depends_on": "",
                    "notes": "",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        rules = {finding["rule"] for finding in json.loads(result.stdout)["findings"]}
        self.assertTrue(
            {
                "invalid-risk",
                "stale-high-risk-source",
                "unverified-high-risk-claim",
            }.issubset(rules)
        )

    def test_empty_risk_is_blocked_and_cannot_skip_high_risk_checks(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C009",
                    "section": "影响",
                    "claim": "空风险字段不能降级证据要求",
                    "state": "observed",
                    "risk": "",
                    "source_locator": "example://fixture/high-risk",
                    "source_version": "fixture-v1",
                    "verification_status": "unverified",
                    "freshness_status": "unknown",
                    "depends_on": "",
                    "notes": "",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        rules = {finding["rule"] for finding in json.loads(result.stdout)["findings"]}
        self.assertTrue(
            {
                "invalid-risk",
                "stale-high-risk-source",
                "unverified-high-risk-claim",
            }.issubset(rules)
        )

    def test_unverified_high_risk_source_blocks_editorial_readiness(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C001",
                    "section": "影响",
                    "claim": "合成测试主张：示例指标提升 3.7%",
                    "state": "sourced",
                    "risk": "high",
                    "source_locator": "dashboard://conversion/latest",
                    "source_version": "",
                    "verification_status": "unverified",
                    "freshness_status": "current",
                    "depends_on": "",
                    "notes": "待回读原始实验",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ready"])
        self.assertIn(
            "unverified-high-risk-claim",
            {finding["rule"] for finding in payload["findings"]},
        )

    def test_sourced_claim_without_locator_is_a_blocker(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C002",
                    "section": "背景",
                    "claim": "行业已经普遍转向该架构",
                    "state": "sourced",
                    "risk": "medium",
                    "source_locator": "",
                    "source_version": "",
                    "verification_status": "verified",
                    "freshness_status": "current",
                    "depends_on": "",
                    "notes": "",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn(
            "missing-source-locator",
            {finding["rule"] for finding in payload["findings"]},
        )

    def test_stale_high_risk_source_blocks_editorial_readiness(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C003",
                    "section": "组织现状",
                    "claim": "合成测试主张：虚构 A 组有 37 个席位",
                    "state": "sourced",
                    "risk": "high",
                    "source_locator": "example://fixture/org-snapshot",
                    "source_version": "fixture-stale-v1",
                    "verification_status": "verified",
                    "freshness_status": "stale",
                    "depends_on": "",
                    "notes": "发布前需要刷新",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn(
            "stale-high-risk-source",
            {finding["rule"] for finding in payload["findings"]},
        )

    def test_high_risk_inference_requires_claim_dependencies(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C004",
                    "section": "判断",
                    "claim": "因此该机制会降低全链路故障概率",
                    "state": "inference",
                    "risk": "high",
                    "source_locator": "",
                    "source_version": "",
                    "verification_status": "not_required",
                    "freshness_status": "not_applicable",
                    "depends_on": "",
                    "notes": "需要绑定支撑事实",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn(
            "unbound-high-risk-reasoning",
            {finding["rule"] for finding in payload["findings"]},
        )

    def test_high_risk_unknown_blocks_editorial_readiness(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C005",
                    "section": "结论",
                    "claim": "真实用户转化是否改善",
                    "state": "unknown",
                    "risk": "critical",
                    "source_locator": "",
                    "source_version": "",
                    "verification_status": "unverified",
                    "freshness_status": "unknown",
                    "depends_on": "",
                    "notes": "会改变核心判断",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn(
            "material-unknown",
            {finding["rule"] for finding in payload["findings"]},
        )

    def test_dependency_must_reference_an_existing_claim(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C001",
                    "section": "事实",
                    "claim": "合成测试主张：样本接口 P99 为 731ms",
                    "state": "observed",
                    "risk": "high",
                    "source_locator": "example://fixture/trace-2099-04-05#p99",
                    "source_version": "sha256:abc123",
                    "verification_status": "verified",
                    "freshness_status": "current",
                    "depends_on": "",
                    "notes": "",
                },
                {
                    "claim_id": "C006",
                    "section": "判断",
                    "claim": "因此用户流失风险上升",
                    "state": "inference",
                    "risk": "high",
                    "source_locator": "",
                    "source_version": "",
                    "verification_status": "not_required",
                    "freshness_status": "not_applicable",
                    "depends_on": "C999",
                    "notes": "",
                },
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn(
            "unknown-claim-dependency",
            {finding["rule"] for finding in payload["findings"]},
        )

    def test_missing_required_columns_is_a_schema_error(self) -> None:
        ledger = self._write_ledger([{"claim_id": "C001", "claim": "只有两列"}])

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(2, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("invalid-schema", payload["error"])
        self.assertIn("state", payload["missing_columns"])
        self.assertEqual(ledger.name, payload["path"])
        self.assertNotIn(str(ledger.parent), result.stdout)

    def test_duplicate_claim_ids_are_blocked(self) -> None:
        base = {
            "claim_id": "C001",
            "section": "事实",
            "claim": "合成测试主张：样本接口 P99 为 731ms",
            "state": "observed",
            "risk": "high",
            "source_locator": "example://fixture/trace-2099-04-05#p99",
            "source_version": "sha256:abc123",
            "verification_status": "verified",
            "freshness_status": "current",
            "depends_on": "",
            "notes": "",
        }
        ledger = self._write_ledger([base, {**base, "claim": "重复编号的另一条结论"}])

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn(
            "duplicate-claim-id",
            {finding["rule"] for finding in payload["findings"]},
        )

    def test_unknown_evidence_state_is_blocked(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "C007",
                    "section": "事实",
                    "claim": "状态拼写错误不能被当作有效证据",
                    "state": "source",
                    "risk": "medium",
                    "source_locator": "doc://example#1",
                    "source_version": "v1",
                    "verification_status": "verified",
                    "freshness_status": "immutable",
                    "depends_on": "",
                    "notes": "",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn(
            "invalid-state",
            {finding["rule"] for finding in payload["findings"]},
        )

    def test_claim_id_must_use_stable_c_number_format(self) -> None:
        ledger = self._write_ledger(
            [
                {
                    "claim_id": "claim-one",
                    "section": "事实",
                    "claim": "Claim ID 需要稳定格式",
                    "state": "observed",
                    "risk": "medium",
                    "source_locator": "doc://example#1",
                    "source_version": "v1",
                    "verification_status": "verified",
                    "freshness_status": "immutable",
                    "depends_on": "",
                    "notes": "",
                }
            ]
        )

        result = subprocess.run(
            [sys.executable, str(CHECKER), str(ledger), "--require-ready", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn(
            "invalid-claim-id",
            {finding["rule"] for finding in payload["findings"]},
        )


if __name__ == "__main__":
    unittest.main()

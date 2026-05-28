import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_verified_route_completion_ledger import (
    build_auto_mode_formal_package_verified_route_completion_ledger,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageVerifiedRouteCompletionLedgerTests(unittest.TestCase):
    """BDD: P7-AD records a read-only ledger only after P7-AC verifies one route."""

    def test_bdd_p7ad_verified_pdf_route_records_completion_ledger_without_writeback(self) -> None:
        """行为 1：已验证 PDF route 会登记完成账本，但不写正式层。"""
        verification = self._verified_route("pdf_export")

        report = build_auto_mode_formal_package_verified_route_completion_ledger(
            verification,
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_package_verified_route_completion_ledger.v1")
        self.assertEqual(report["status"], "verified_route_completion_ledger_recorded")
        self.assertTrue(report["route_completion_ledger_recorded"])
        self.assertTrue(report["can_enter_next_auto_mode_gate"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(len(report["route_completion_records"]), 1)
        completion = report["route_completion_records"][0]
        self.assertEqual(completion["completion_id"], "verified_route_completion::pdf_export")
        self.assertEqual(completion["completion_status"], "verified_route_completion_recorded")
        self.assertEqual(completion["artifact_ids"], ["paper_pdf"])
        self.assertEqual(completion["verified_artifacts"][0]["sha256"], "abc123")

    def test_bdd_p7ad_current_blocked_verification_blocks_ledger(self) -> None:
        """行为 2：当前 P7-AC blocked 时不会登记完成账本。"""
        report = build_auto_mode_formal_package_verified_route_completion_ledger(self._blocked_verification())

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_verification")
        self.assertFalse(report["route_completion_ledger_recorded"])
        self.assertFalse(report["can_enter_next_auto_mode_gate"])
        self.assertEqual(report["route_completion_records"], [])
        self.assertIn("route_specific_artifact_verification_not_verified", report["blocking_reasons"])
        self.assertIn("source_verification_has_blocking_reasons", report["blocking_reasons"])

    def test_bdd_p7ad_missing_or_invalid_verification_report_blocks_ledger(self) -> None:
        """行为 3：P7-AC 报告缺失、schema 错误或状态未 verified 时阻断。"""
        missing = build_auto_mode_formal_package_verified_route_completion_ledger({})
        wrong_schema = build_auto_mode_formal_package_verified_route_completion_ledger(
            {"schema_version": "wrong.schema", "status": "route_specific_artifact_verified_for_review"}
        )
        wrong_status = build_auto_mode_formal_package_verified_route_completion_ledger(
            {
                **self._verified_route("pdf_export"),
                "status": "blocked_by_route_specific_artifact_executor",
            }
        )

        self.assertEqual(missing["status"], "blocked_by_route_specific_artifact_verification")
        self.assertIn("route_specific_artifact_verification_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(wrong_schema["status"], "blocked_by_route_specific_artifact_verification")
        self.assertIn("route_specific_artifact_verification_missing_or_invalid_schema", wrong_schema["blocking_reasons"])
        self.assertEqual(wrong_status["status"], "blocked_by_route_specific_artifact_verification")
        self.assertIn("route_specific_artifact_verification_not_verified", wrong_status["blocking_reasons"])

    def test_bdd_p7ad_verified_report_must_be_internally_consistent(self) -> None:
        """行为 4：verified 报告仍有缺口或未验证 artifact 时不能登记。"""
        missing_records = self._verified_route("pdf_export")
        missing_records["artifact_verification_records"] = []
        unverified_record = self._verified_route("pdf_export")
        unverified_record["artifact_verification_records"][0]["verification_status"] = "blocked"
        with_blocker = self._verified_route("pdf_export")
        with_blocker["blocking_reasons"] = ["late_integrity_blocker"]

        reports = [
            build_auto_mode_formal_package_verified_route_completion_ledger(source)
            for source in [missing_records, unverified_record, with_blocker]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_verified_route_completion_contract" for report in reports)
        )
        self.assertIn("artifact_verification_records_missing", reports[0]["blocking_reasons"])
        self.assertIn("artifact_verification_record_not_verified:paper_pdf", reports[1]["blocking_reasons"])
        self.assertIn("source_verification_has_blocking_reasons", reports[2]["blocking_reasons"])
        self.assertTrue(all(report["route_completion_records"] == [] for report in reports))

    def test_bdd_p7ad_route_flags_must_match_verified_route(self) -> None:
        """行为 5：路线类型和路线 flags 必须一致。"""
        mismatched = self._verified_route("pdf_export")
        mismatched["rendered_pdf"] = False
        mismatched["rendered_docx"] = True

        report = build_auto_mode_formal_package_verified_route_completion_ledger(mismatched)

        self.assertEqual(report["status"], "blocked_by_verified_route_completion_contract")
        self.assertFalse(report["route_completion_ledger_recorded"])
        self.assertIn("verified_route_flag_mismatch:pdf_export", report["blocking_reasons"])

    def test_bdd_p7ad_package_route_preserves_all_artifact_evidence(self) -> None:
        """行为 6：package manifest route 会保留 manifest/PDF/DOCX 证据。"""
        verification = self._verified_route(
            "package_manifest",
            [
                self._artifact("package_manifest", "Submissions/formal_package/manifest.json", 200, "manifest-sha"),
                self._artifact("paper_pdf", "Submissions/formal_package/paper.pdf", 300, "pdf-sha"),
                self._artifact("paper_docx", "Submissions/formal_package/paper.docx", 400, "docx-sha"),
            ],
        )

        report = build_auto_mode_formal_package_verified_route_completion_ledger(verification)

        self.assertEqual(report["status"], "verified_route_completion_ledger_recorded")
        completion = report["route_completion_records"][0]
        self.assertEqual(completion["artifact_count"], 3)
        self.assertEqual(completion["artifact_ids"], ["package_manifest", "paper_pdf", "paper_docx"])
        self.assertEqual(
            [(artifact["path"], artifact["bytes"], artifact["sha256"]) for artifact in completion["verified_artifacts"]],
            [
                ("Submissions/formal_package/manifest.json", 200, "manifest-sha"),
                ("Submissions/formal_package/paper.pdf", 300, "pdf-sha"),
                ("Submissions/formal_package/paper.docx", 400, "docx-sha"),
            ],
        )

    def test_bdd_p7ad_boundary_violations_block_completion_ledger(self) -> None:
        """行为 7：源报告出现正式写回或边界越界时阻断。"""
        source = self._verified_route("pdf_export")
        source["formal_writeback_executed"] = True
        source["this_command_wrote_formal_state"] = True
        source["can_write_product_state"] = True
        source["boundary_flags"]["modified_product_state"] = True

        report = build_auto_mode_formal_package_verified_route_completion_ledger(source)

        self.assertEqual(report["status"], "blocked_by_verified_route_completion_boundary")
        self.assertFalse(report["route_completion_ledger_recorded"])
        self.assertIn("source_verification_formal_writeback_executed", report["blocking_reasons"])
        self.assertIn("source_verification_wrote_formal_state", report["blocking_reasons"])
        self.assertIn("source_verification_allows_product_state_write", report["blocking_reasons"])
        self.assertIn("source_verification_boundary_violation:modified_product_state", report["blocking_reasons"])

    def test_bdd_p7ad_cli_defaults_to_current_blocked_verification(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AC，写 blocked ledger report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json",
                self._blocked_verification(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_verified_route_completion_ledger.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_route_specific_artifact_verification", result.stdout)
            self.assertIn("route_completion_ledger_recorded=false", result.stdout)
            self.assertIn("can_enter_next_auto_mode_gate=false", result.stdout)
            self.assertTrue(
                (
                    project_root / "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json"
                ).exists()
            )
            self.assertTrue(
                (project_root / "Reviews/auto_mode_formal_package_verified_route_completion_ledger.md").exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_verified_route_completion_ledger.json"
                ).exists()
            )

    def _verified_route(self, route_type: str, records: list[dict] | None = None) -> dict:
        flags = {
            "rendered_pdf": route_type == "pdf_export",
            "rendered_docx": route_type == "docx_export",
            "package_manifest_generated": route_type == "package_manifest",
            "manual_acceptance_performed": route_type == "manual_acceptance",
        }
        return {
            "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_verification.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "route_specific_artifact_verified_for_review",
            "route_type": route_type,
            "verified_route_type": route_type,
            "delegated_status": {
                "pdf_export": "final_pdf_written",
                "docx_export": "docx_exported",
                "package_manifest": "formal_submission_package_ready",
                "manual_acceptance": "formal_submission_package_accepted",
            }[route_type],
            "route_specific_artifact_verified": True,
            "source_product_state_verified": route_type == "manual_acceptance",
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "source_paths": self._source_paths(),
            "source_executor": {"status": "route_specific_artifact_executed", "route_type": route_type},
            "source_delegated_report": {"status": "delegated_success"},
            "artifact_verification_records": records or [self._artifact("paper_pdf", "Submissions/formal_package/paper.pdf")],
            "boundary_flags": self._clean_boundary_flags(),
            "next_action": {"id": "record_verified_route_completion"},
            **flags,
        }

    def _blocked_verification(self) -> dict:
        report = self._verified_route("pdf_export")
        report["status"] = "blocked_by_route_specific_artifact_executor"
        report["route_type"] = ""
        report["verified_route_type"] = ""
        report["delegated_status"] = ""
        report["route_specific_artifact_verified"] = False
        report["selected_route_executed"] = False
        report["export_or_acceptance_executed"] = False
        report["rendered_pdf"] = False
        report["artifact_verification_records"] = []
        report["blocking_reasons"] = ["route_specific_artifact_executor_not_completed"]
        return report

    def _artifact(
        self,
        artifact_id: str,
        path: str,
        bytes_value: int = 100,
        sha256: str = "abc123",
    ) -> dict:
        return {
            "artifact_id": artifact_id,
            "path": path,
            "exists": True,
            "bytes": bytes_value,
            "delegated_bytes": bytes_value,
            "sha256": sha256,
            "delegated_sha256": sha256,
            "verification_status": "verified",
        }

    def _clean_boundary_flags(self) -> dict:
        return {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "reran_models": False,
            "modified_statistical_execution_artifacts": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "generated_package_manifest": False,
            "performed_manual_acceptance": False,
        }

    def _source_paths(self) -> dict:
        return {
            "route_specific_artifact_verification": (
                "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

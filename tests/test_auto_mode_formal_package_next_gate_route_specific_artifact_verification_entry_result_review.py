import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review import (
    build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateRouteSpecificArtifactVerificationEntryResultReviewTests(
    unittest.TestCase
):
    """BDD: P7-AU reviews verification entry results before the completion ledger."""

    def test_bdd_p7au_entered_verification_is_ready_for_completion_ledger(self) -> None:
        """行为 1：P7-AT 已进入 verification 且验证输出干净时，可继续到 completion ledger。"""
        verification = self._verified_route("package_manifest")
        entry = self._verification_entry("package_manifest", verification)

        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review(
            Path("."),
            entry,
            verification,
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.v1",
        )
        self.assertEqual(report["status"], "route_specific_artifact_verification_entry_result_review_ready")
        self.assertTrue(report["artifact_verification_entry_result_reviewed"])
        self.assertTrue(report["can_continue_to_verified_route_completion_ledger"])
        self.assertEqual(report["verified_route_type"], "package_manifest")
        self.assertEqual(
            report["route_specific_artifact_verification_status"],
            "route_specific_artifact_verified_for_review",
        )
        self.assertTrue(report["route_specific_artifact_verified"])
        self.assertEqual(report["artifact_verification_record_count"], 3)
        self.assertEqual(len(report["verified_route_completion_ledger_input_records"]), 1)
        record = report["verified_route_completion_ledger_input_records"][0]
        self.assertEqual(record["record_id"], "route_specific_artifact_verification_result::package_manifest")
        self.assertEqual(
            record["route_specific_artifact_verification_report_path"],
            "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json",
        )
        self.assertEqual(
            record["review_status"],
            "route_specific_artifact_verification_accepted_for_verified_route_completion_ledger",
        )
        self.assertTrue(record["can_continue_to_verified_route_completion_ledger"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7au_current_blocked_entry_blocks_result_review(self) -> None:
        """行为 2：当前 P7-AT blocked 时，不输出 ledger 输入记录。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review(
            Path("."),
            {},
            {},
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_verification_entry")
        self.assertFalse(report["artifact_verification_entry_result_reviewed"])
        self.assertFalse(report["can_continue_to_verified_route_completion_ledger"])
        self.assertEqual(report["verified_route_completion_ledger_input_records"], [])
        self.assertIn(
            "route_specific_artifact_verification_entry_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7au_missing_invalid_or_not_entered_entry_blocks_review(self) -> None:
        """行为 3：P7-AT 缺失、schema 错、未 entered 或有 blockers 时阻断。"""
        verification = self._verified_route("package_manifest")
        wrong_schema = self._verification_entry("package_manifest", verification)
        wrong_schema["schema_version"] = "wrong.schema"
        not_entered = self._verification_entry("package_manifest", verification)
        not_entered["status"] = "blocked_by_route_specific_artifact_execution_result_review"
        blocked = self._verification_entry("package_manifest", verification)
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review(
                Path("."),
                entry,
                verification,
            )
            for entry in [wrong_schema, not_entered, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_verification_entry" for report in reports)
        )
        self.assertIn(
            "route_specific_artifact_verification_entry_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn("route_specific_artifact_verification_entry_not_completed", reports[1]["blocking_reasons"])
        self.assertIn("source_entry_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7au_entry_and_verification_result_contract_must_match(self) -> None:
        """行为 4：entry 记录的路径、状态、route type 和 summary 必须与 verification 输出一致。"""
        verification = self._verified_route("package_manifest")
        wrong_path = self._verification_entry("package_manifest", verification)
        wrong_path["route_specific_artifact_verification_report_path"] = "Results/json/wrong.json"
        status_mismatch = self._verification_entry("package_manifest", verification)
        status_mismatch["route_specific_artifact_verification_status"] = "blocked_by_route_specific_artifact_integrity"
        summary_mismatch = self._verification_entry("package_manifest", verification)
        summary_mismatch["route_specific_artifact_verification_result"][
            "route_specific_artifact_verification_report_summary"
        ]["verified_route_type"] = "pdf_export"

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review(
                Path("."),
                entry,
                verification,
            )
            for entry in [wrong_path, status_mismatch, summary_mismatch]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_route_specific_artifact_verification_entry_result_contract"
                for report in reports
            )
        )
        self.assertIn("artifact_verification_report_path_mismatch:package_manifest", reports[0]["blocking_reasons"])
        self.assertIn("artifact_verification_status_mismatch:package_manifest", reports[1]["blocking_reasons"])
        self.assertIn(
            "artifact_verification_summary_verified_route_type_mismatch:package_manifest",
            reports[2]["blocking_reasons"],
        )

    def test_bdd_p7au_verification_output_must_be_ledger_acceptable(self) -> None:
        """行为 5：verification 输出未 verified、缺 artifact 记录或边界越界时阻断。"""
        verified = self._verified_route("package_manifest")
        not_verified = self._verified_route("package_manifest")
        not_verified["status"] = "blocked_by_route_specific_artifact_integrity"
        not_verified["route_specific_artifact_verified"] = False
        not_verified["blocking_reasons"] = ["artifact_missing"]
        missing_records = self._verified_route("package_manifest")
        missing_records["artifact_verification_records"] = []
        boundary_violation = self._verified_route("package_manifest")
        boundary_violation["boundary_flags"]["modified_product_state"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review(
                Path("."),
                self._verification_entry("package_manifest", verified),
                source,
            )
            for source in [not_verified, missing_records, boundary_violation]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_verification_output" for report in reports)
        )
        self.assertIn("route_specific_artifact_verification_not_verified", reports[0]["blocking_reasons"])
        self.assertIn("artifact_verification_records_missing", reports[1]["blocking_reasons"])
        self.assertIn("source_verification_boundary_violation:modified_product_state", reports[2]["blocking_reasons"])

    def test_bdd_p7au_writes_result_review_only(self) -> None:
        """行为 6：只写 P7-AU result review，不运行 ledger、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            verification = self._verified_route("package_manifest")
            report = build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review(
                project_root,
                self._verification_entry("package_manifest", verification),
                verification,
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(
                written["status"],
                "route_specific_artifact_verification_entry_result_review_ready",
            )
            self.assertFalse(
                (
                    project_root / "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.json"
                ).exists()
            )

    def test_bdd_p7au_cli_defaults_to_current_blocked_entry(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AT entry，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            entry_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.json"
            )
            entry_path.parent.mkdir(parents=True, exist_ok=True)
            entry_path.write_text(
                json.dumps({"status": "blocked_by_route_specific_artifact_execution_result_review"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_route_specific_artifact_verification_entry", result.stdout)
            self.assertIn("can_continue_to_verified_route_completion_ledger=false", result.stdout)
            self.assertIn("verified_route_completion_ledger_input_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.json"
                ).exists()
            )

    def _verification_entry(self, route_type: str, verification: dict) -> dict:
        flags = self._route_flags(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "route_specific_artifact_execution_result_review_ready",
            "status": "next_gate_route_specific_artifact_verification_entered",
            "verified_route_type": route_type,
            "can_enter_route_specific_artifact_verification": True,
            "route_specific_artifact_verification_entry_command": [
                "python3",
                "Program/auto_mode_formal_package_route_specific_artifact_verification.py",
            ],
            "route_specific_artifact_verification_entry_command_executed": True,
            "this_command_ran_route_specific_artifact_verification": True,
            "route_specific_artifact_verification_report_path": (
                "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json"
            ),
            "route_specific_artifact_verification_review_path": (
                "Reviews/auto_mode_formal_package_route_specific_artifact_verification.md"
            ),
            "route_specific_artifact_verification_returncode": 0,
            "route_specific_artifact_verification_status": "route_specific_artifact_verified_for_review",
            "route_specific_artifact_verification_result": {
                "stdout": "",
                "stderr": "",
                "returncode": 0,
                "status": "route_specific_artifact_verified_for_review",
                "report_path": "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json",
                "review_path": "Reviews/auto_mode_formal_package_route_specific_artifact_verification.md",
                "route_specific_artifact_verification_report_summary": {
                    "schema_version": verification["schema_version"],
                    "status": verification["status"],
                    "route_type": verification["route_type"],
                    "verified_route_type": verification["verified_route_type"],
                    "delegated_status": verification["delegated_status"],
                    "route_specific_artifact_verified": verification["route_specific_artifact_verified"],
                    "artifact_verification_record_count": len(verification["artifact_verification_records"]),
                    "blocking_reasons": verification["blocking_reasons"],
                },
            },
            "route_specific_artifact_verified": True,
            "verification_artifact_record_count": len(verification["artifact_verification_records"]),
            "artifact_verification_records": verification["artifact_verification_records"],
            "delegated_status": verification["delegated_status"],
            "route_specific_command_executed": True,
            "route_specific_artifact_executed": True,
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_entry_boundary_flags(),
            **flags,
        }

    def _verified_route(self, route_type: str) -> dict:
        records = {
            "package_manifest": [
                self._artifact("package_manifest", "Submissions/formal_package/manifest.json", 200, "manifest-sha"),
                self._artifact("paper_pdf", "Submissions/formal_package/paper.pdf", 300, "pdf-sha"),
                self._artifact("paper_docx", "Submissions/formal_package/paper.docx", 400, "docx-sha"),
            ],
            "pdf_export": [self._artifact("paper_pdf", "Submissions/formal_package/paper.pdf", 300, "pdf-sha")],
            "docx_export": [self._artifact("paper_docx", "Submissions/formal_package/paper.docx", 400, "docx-sha")],
            "manual_acceptance": [
                self._artifact(
                    "manual_acceptance_state",
                    "state/product/formal_submission_package_manual_acceptance.json",
                    500,
                    "state-sha",
                )
            ],
        }[route_type]
        return {
            "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_verification.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "route_specific_artifact_verified_for_review",
            "route_type": route_type,
            "verified_route_type": route_type,
            "delegated_status": self._delegated_status(route_type),
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
            "source_delegated_report": {"status": self._delegated_status(route_type)},
            "artifact_verification_records": records,
            "boundary_flags": self._clean_verification_boundary_flags(),
            "next_action": {"id": "record_verified_route_completion"},
            **self._route_flags(route_type),
        }

    def _artifact(self, artifact_id: str, path: str, bytes_value: int, sha256: str) -> dict:
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

    def _delegated_status(self, route_type: str) -> str:
        return {
            "pdf_export": "final_pdf_written",
            "docx_export": "docx_exported",
            "package_manifest": "formal_submission_package_ready",
            "manual_acceptance": "formal_submission_package_accepted",
        }[route_type]

    def _route_flags(self, route_type: str) -> dict:
        return {
            "rendered_pdf": route_type == "pdf_export",
            "rendered_docx": route_type == "docx_export",
            "package_manifest_generated": route_type == "package_manifest",
            "manual_acceptance_performed": route_type == "manual_acceptance",
        }

    def _clean_entry_boundary_flags(self) -> dict:
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
            "entered_next_gate": False,
            "ran_next_gate_command": False,
            "wrote_formal_state": False,
            "executed_selected_route": False,
            "exported_or_accepted_formal_package": False,
            "verified_route_specific_artifact": False,
        }

    def _clean_verification_boundary_flags(self) -> dict:
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
            "route_specific_artifact_verification_entry": (
                "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.json"
            ),
            "route_specific_artifact_verification": (
                "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

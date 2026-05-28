import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review import (
    build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateRouteSpecificArtifactExecutorEntryResultReviewTests(
    unittest.TestCase
):
    """BDD: P7-AQ reviews artifact executor dry-run output after P7-AP entry."""

    def test_bdd_p7aq_entered_artifact_executor_dry_run_is_review_ready(self) -> None:
        """行为 1：P7-AP 已进入 executor 且 dry-run 干净时，可继续到显式 artifact execution。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
            Path("."),
            self._entry_report("pdf_export"),
            self._artifact_executor_report("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.v1",
        )
        self.assertEqual(
            report["status"],
            "route_specific_artifact_executor_entry_result_review_ready",
        )
        self.assertTrue(report["artifact_executor_entry_result_reviewed"])
        self.assertTrue(report["can_continue_to_route_specific_artifact_execution"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(
            report["route_specific_artifact_executor_status"],
            "route_specific_artifact_executor_dry_run_ready",
        )
        self.assertEqual(len(report["route_specific_artifact_execution_records"]), 1)
        record = report["route_specific_artifact_execution_records"][0]
        self.assertEqual(
            record["review_status"],
            "artifact_executor_dry_run_accepted_for_explicit_artifact_execution",
        )
        self.assertEqual(record["route_type"], "pdf_export")
        self.assertEqual(
            record["artifact_executor_report_path"],
            "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
        )
        self.assertEqual(record["route_specific_command"][0], "python3")
        self.assertFalse(report["route_specific_command_executed"])
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7aq_current_blocked_entry_blocks_dry_run_review(self) -> None:
        """行为 2：当前 P7-AP blocked 时没有 artifact executor dry-run 可审阅。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
            Path("."),
            {},
            {},
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_executor_entry")
        self.assertFalse(report["artifact_executor_entry_result_reviewed"])
        self.assertFalse(report["can_continue_to_route_specific_artifact_execution"])
        self.assertEqual(report["route_specific_artifact_execution_records"], [])
        self.assertIn(
            "route_specific_artifact_executor_entry_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7aq_missing_invalid_or_not_entered_entry_blocks_review(self) -> None:
        """行为 3：P7-AP 缺失、schema 错、未进入 executor 或有 blockers 时阻断。"""
        wrong_schema = self._entry_report("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_entered = self._entry_report("pdf_export")
        not_entered["status"] = "blocked_by_next_gate_selected_route_execute_result_review"
        blocked = self._entry_report("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
                Path("."),
                source,
                self._artifact_executor_report("pdf_export"),
            )
            for source in [wrong_schema, not_entered, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_executor_entry" for report in reports)
        )
        self.assertIn(
            "route_specific_artifact_executor_entry_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "route_specific_artifact_executor_entry_not_completed",
            reports[1]["blocking_reasons"],
        )
        self.assertIn("source_entry_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7aq_entry_and_artifact_executor_result_contract_must_match(self) -> None:
        """行为 4：entry 的 report path、status、result summary 必须与 executor report 一致。"""
        wrong_path = self._entry_report("pdf_export")
        wrong_path["route_specific_artifact_executor_report_path"] = "Results/json/wrong.json"
        status_mismatch = self._artifact_executor_report("pdf_export")
        status_mismatch["status"] = "blocked_by_selected_route_execute"
        summary_mismatch = self._entry_report("pdf_export")
        summary_mismatch["route_specific_artifact_executor_result"]["status"] = (
            "blocked_by_selected_route_execute"
        )

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
                Path("."),
                wrong_path,
                self._artifact_executor_report("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
                Path("."),
                self._entry_report("pdf_export"),
                status_mismatch,
            ),
            build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
                Path("."),
                summary_mismatch,
                self._artifact_executor_report("pdf_export"),
            ),
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_route_specific_artifact_executor_entry_result_contract"
                for report in reports
            )
        )
        self.assertIn("artifact_executor_report_path_mismatch:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("artifact_executor_status_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("artifact_executor_result_status_mismatch:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7aq_artifact_executor_dry_run_report_must_be_clean(self) -> None:
        """行为 5：artifact executor dry-run 缺失、schema 错或已执行产物时阻断。"""
        missing = {}
        wrong_schema = self._artifact_executor_report("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        boundary_violation = self._artifact_executor_report("pdf_export")
        boundary_violation["boundary_flags"]["modified_formal_manuscript"] = True
        execution_violation = self._artifact_executor_report("pdf_export")
        execution_violation["route_specific_command_executed"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
                Path("."),
                self._entry_report("pdf_export"),
                executor_report,
            )
            for executor_report in [missing, wrong_schema, boundary_violation, execution_violation]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_route_specific_artifact_executor_dry_run_report"
                for report in reports
            )
        )
        self.assertIn("artifact_executor_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("artifact_executor_missing_or_invalid_schema", reports[1]["blocking_reasons"])
        self.assertIn(
            "artifact_executor_boundary_violation:modified_formal_manuscript",
            reports[2]["blocking_reasons"],
        )
        self.assertIn("artifact_executor_route_specific_command_executed", reports[3]["blocking_reasons"])

    def test_bdd_p7aq_writes_result_review_only(self) -> None:
        """行为 6：只写 result review report/review，不运行正式 artifact execution。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
                project_root,
                self._entry_report("pdf_export"),
                self._artifact_executor_report("pdf_export"),
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(
                written["status"],
                "route_specific_artifact_executor_entry_result_review_ready",
            )
            self.assertFalse(written["route_specific_artifact_executed"])
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.json"
                ).exists()
            )

    def test_bdd_p7aq_cli_defaults_to_current_blocked_entry(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AP entry，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            entry_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
            )
            entry_path.parent.mkdir(parents=True, exist_ok=True)
            entry_path.write_text(
                json.dumps({"status": "blocked_by_next_gate_selected_route_execute_result_review"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_route_specific_artifact_executor_entry", result.stdout)
            self.assertIn("can_continue_to_route_specific_artifact_execution=false", result.stdout)
            self.assertIn("route_specific_artifact_execution_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.json"
                ).exists()
            )

    def _entry_report(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_selected_route_execute_result_review_ready",
            "status": "next_gate_route_specific_artifact_executor_entered",
            "mode": "execute",
            "confirm_artifact_executor_entry": True,
            "verified_route_type": route_type,
            "can_enter_route_specific_artifact_executor_with_confirmation": True,
            "requires_explicit_artifact_executor_entry_command": True,
            "route_specific_artifact_executor_entry_command_executed": True,
            "this_command_ran_route_specific_artifact_executor": True,
            "route_specific_artifact_executor_entered": True,
            "route_specific_artifact_executor_report_path": (
                "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
            ),
            "route_specific_artifact_executor_review_path": (
                "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md"
            ),
            "route_specific_artifact_executor_returncode": 0,
            "route_specific_artifact_executor_status": "route_specific_artifact_executor_dry_run_ready",
            "route_specific_artifact_executor_result": {
                "returncode": 0,
                "status": "route_specific_artifact_executor_dry_run_ready",
                "report_path": "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
                "review_path": "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md",
                "route_specific_artifact_executor_report_summary": {
                    "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_executor.v1",
                    "status": "route_specific_artifact_executor_dry_run_ready",
                    "route_type": route_type,
                    "route_specific_command_executed": False,
                    "route_specific_artifact_executed": False,
                    "blocking_reasons": [],
                },
            },
            "route_specific_command_executed": False,
            "route_specific_artifact_executed": False,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _artifact_executor_report(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_executor.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "route_specific_artifact_executor_dry_run_ready",
            "mode": "dry-run",
            "confirm_artifact_execution": False,
            "can_execute_route_specific_artifact_with_confirmation": True,
            "route_type": route_type,
            "route_specific_artifact_executed": False,
            "route_specific_command_executed": False,
            "route_specific_command": self._route_specific_command(route_type),
            "delegated_report_path": "Results/json/formal_pdf_final_writeback.json",
            "delegated_review_path": "Reviews/formal_pdf_final_writeback.md",
            "delegated_returncode": None,
            "delegated_status": "",
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "artifact_execution_request": {
                "mode": "dry-run",
                "confirm_artifact_execution": False,
                "metadata_complete": False,
            },
            "selected_route_operation": self._operation(route_type),
            "route_specific_result": {},
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _operation(self, route_type: str) -> dict:
        routed_action, next_command, planned_outputs = self._route_mapping(route_type)
        return {
            "operation_id": f"selected_route_execute::{route_type}",
            "route_execution_id": f"selected_formal_package_route_execution::{routed_action}",
            "routed_action": routed_action,
            "route_type": route_type,
            "next_command": next_command,
            "planned_outputs": planned_outputs,
            "operation_status": "planned_not_executed",
            "will_execute_selected_route": False,
            "will_render_pdf": False,
            "will_render_docx": False,
            "will_generate_package_manifest": False,
            "will_perform_manual_acceptance": False,
            "will_write_product_state": False,
        }

    def _route_specific_command(self, route_type: str) -> list[str]:
        if route_type == "docx_export":
            return ["python3", "Program/formal_docx_export.py"]
        if route_type == "package_manifest":
            return ["python3", "Program/formal_submission_package_manifest.py"]
        return ["python3", "Program/formal_pdf_final_writeback.py"]

    def _route_mapping(self, route_type: str) -> tuple[str, str, list[str]]:
        if route_type == "docx_export":
            return "formal_docx_export_preflight", "formal_docx_export_execute", [
                "Submissions/formal_package/paper.docx"
            ]
        if route_type == "package_manifest":
            return "formal_submission_package_manifest_preflight", "formal_submission_package_manifest_execute", [
                "Submissions/formal_package/manifest.json"
            ]
        return "formal_pdf_export_preflight", "formal_pdf_export_execute", [
            "Submissions/formal_package/paper.pdf"
        ]

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
            "entered_next_gate": False,
            "ran_next_gate_command": False,
            "wrote_formal_state": False,
            "executed_selected_route": False,
            "exported_or_accepted_formal_package": False,
        }

    def _source_paths(self) -> dict:
        return {
            "route_specific_artifact_executor_entry": (
                "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
            ),
            "route_specific_artifact_executor": (
                "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_selected_route_execute_result_review import (
    build_auto_mode_formal_package_next_gate_selected_route_execute_result_review,
    write_auto_mode_formal_package_next_gate_selected_route_execute_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateSelectedRouteExecuteResultReviewTests(unittest.TestCase):
    """BDD: P7-AO reviews P7-AN selected route execute output before artifact execution."""

    def test_bdd_p7ao_confirmed_selected_route_execute_with_clean_manifest_is_review_ready(self) -> None:
        """行为 1：P7-AN 已执行且 manifest 干净时，才允许进入 route-specific artifact executor。"""
        report = build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
            Path("."),
            self._next_gate_selected_route_execute("pdf_export"),
            self._selected_route_execute("pdf_export"),
            self._selected_route_execute_manifest("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_selected_route_execute_result_review.v1",
        )
        self.assertEqual(report["status"], "next_gate_selected_route_execute_result_review_ready")
        self.assertTrue(report["selected_route_execute_result_reviewed"])
        self.assertTrue(report["can_continue_to_route_specific_artifact_executor"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["selected_route_execute_status"], "selected_route_execute_manifest_recorded")
        self.assertTrue(report["selected_route_execute_manifest_recorded"])
        self.assertEqual(len(report["route_specific_artifact_executor_input_records"]), 1)
        record = report["route_specific_artifact_executor_input_records"][0]
        self.assertEqual(
            record["review_status"],
            "selected_route_execute_manifest_accepted_for_route_specific_artifact_executor",
        )
        self.assertEqual(
            record["selected_route_execute_report_path"],
            "Results/json/auto_mode_formal_package_selected_route_execute.json",
        )
        self.assertEqual(
            record["selected_route_execute_manifest_path"],
            "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json",
        )
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ao_current_blocked_next_gate_execute_blocks_manifest_review(self) -> None:
        """行为 2：当前 P7-AN blocked 时没有 selected route manifest 可审阅。"""
        report = build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
            Path("."),
            {},
            {},
            {},
        )

        self.assertEqual(report["status"], "blocked_by_next_gate_selected_route_execute")
        self.assertFalse(report["selected_route_execute_result_reviewed"])
        self.assertFalse(report["can_continue_to_route_specific_artifact_executor"])
        self.assertEqual(report["route_specific_artifact_executor_input_records"], [])
        self.assertIn(
            "next_gate_selected_route_execute_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7ao_missing_invalid_or_not_completed_next_gate_execute_blocks_review(self) -> None:
        """行为 3：P7-AN 缺失、schema 错、未完成或有 blockers 时阻断。"""
        wrong_schema = self._next_gate_selected_route_execute("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_completed = self._next_gate_selected_route_execute("pdf_export")
        not_completed["status"] = "blocked_by_workflow_continuation_result_review"
        blocked = self._next_gate_selected_route_execute("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
                Path("."),
                source,
                self._selected_route_execute("pdf_export"),
                self._selected_route_execute_manifest("pdf_export"),
            )
            for source in [wrong_schema, not_completed, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_next_gate_selected_route_execute" for report in reports)
        )
        self.assertIn("next_gate_selected_route_execute_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("next_gate_selected_route_execute_not_completed", reports[1]["blocking_reasons"])
        self.assertIn("source_next_gate_selected_route_execute_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7ao_selected_route_execute_report_contract_must_match_p7an(self) -> None:
        """行为 4：selected route execute report 的路径、状态和摘要必须与 P7-AN 一致。"""
        wrong_path = self._next_gate_selected_route_execute("pdf_export")
        wrong_path["selected_route_execute_report_path"] = "Results/json/wrong.json"
        status_mismatch = self._selected_route_execute("pdf_export")
        status_mismatch["status"] = "selected_route_execute_dry_run_ready"
        summary_mismatch = self._next_gate_selected_route_execute("pdf_export")
        summary_mismatch["selected_route_execute_result"]["status"] = "selected_route_execute_dry_run_ready"

        reports = [
            build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
                Path("."),
                wrong_path,
                self._selected_route_execute("pdf_export"),
                self._selected_route_execute_manifest("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
                Path("."),
                self._next_gate_selected_route_execute("pdf_export"),
                status_mismatch,
                self._selected_route_execute_manifest("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
                Path("."),
                summary_mismatch,
                self._selected_route_execute("pdf_export"),
                self._selected_route_execute_manifest("pdf_export"),
            ),
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_next_gate_selected_route_execute_result_contract"
                for report in reports
            )
        )
        self.assertIn("selected_route_execute_report_path_mismatch:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("selected_route_execute_status_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("selected_route_execute_result_status_mismatch:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7ao_selected_route_execute_manifest_must_be_clean(self) -> None:
        """行为 5：manifest 缺失、schema 错、操作不干净或越权标志时阻断。"""
        missing = {}
        wrong_schema = self._selected_route_execute_manifest("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        boundary_violation = self._selected_route_execute_manifest("pdf_export")
        boundary_violation["boundary_flags"]["rendered_pdf"] = True
        operation_violation = self._selected_route_execute_manifest("pdf_export")
        operation_violation["selected_route_execute_operations"][0]["will_render_pdf"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
                Path("."),
                self._next_gate_selected_route_execute("pdf_export"),
                self._selected_route_execute("pdf_export"),
                manifest,
            )
            for manifest in [missing, wrong_schema, boundary_violation, operation_violation]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_selected_route_execute_manifest_review" for report in reports)
        )
        self.assertIn("selected_route_execute_manifest_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("selected_route_execute_manifest_missing_or_invalid_schema", reports[1]["blocking_reasons"])
        self.assertIn("selected_route_execute_manifest_boundary_violation:rendered_pdf", reports[2]["blocking_reasons"])
        self.assertIn("route_operation_marked_render_pdf:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7ao_writes_result_review_only(self) -> None:
        """行为 6：只写 result review report/review，不运行 artifact executor、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
                project_root,
                self._next_gate_selected_route_execute("pdf_export"),
                self._selected_route_execute("pdf_export"),
                self._selected_route_execute_manifest("pdf_export"),
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_selected_route_execute_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "next_gate_selected_route_execute_result_review_ready")
            self.assertFalse(written["route_specific_artifact_executed"])
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_selected_route_execute_result_review.json"
                ).exists()
            )

    def test_bdd_p7ao_cli_defaults_to_current_blocked_next_gate_execute(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AN report，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            execute_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_selected_route_execute.json"
            )
            execute_path.parent.mkdir(parents=True, exist_ok=True)
            execute_path.write_text(
                json.dumps({"status": "blocked_by_workflow_continuation_result_review"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_selected_route_execute_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_next_gate_selected_route_execute", result.stdout)
            self.assertIn("can_continue_to_route_specific_artifact_executor=false", result.stdout)
            self.assertIn("route_specific_artifact_executor_input_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_selected_route_execute_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_selected_route_execute_result_review.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_selected_route_execute_result_review.json"
                ).exists()
            )

    def _next_gate_selected_route_execute(self, route_type: str) -> dict:
        operation = self._operation(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_selected_route_execute.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_workflow_continuation_result_review_ready",
            "status": "next_gate_selected_route_execute_command_executed",
            "mode": "execute",
            "confirm_selected_route_execute": True,
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "can_execute_selected_route_with_confirmation": True,
            "requires_explicit_selected_route_execute_command": True,
            "selected_route_execute_command_executed": True,
            "this_command_ran_selected_route_execute_command": True,
            "selected_route_execute_report_path": (
                "Results/json/auto_mode_formal_package_selected_route_execute.json"
            ),
            "selected_route_execute_review_path": "Reviews/auto_mode_formal_package_selected_route_execute.md",
            "selected_route_execute_manifest_path": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
            "selected_route_execute_returncode": 0,
            "selected_route_execute_status": "selected_route_execute_manifest_recorded",
            "selected_route_execute_result": {
                "returncode": 0,
                "status": "selected_route_execute_manifest_recorded",
                "report_path": "Results/json/auto_mode_formal_package_selected_route_execute.json",
                "review_path": "Reviews/auto_mode_formal_package_selected_route_execute.md",
                "manifest_path": (
                    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
                ),
                "selected_route_execute_report_summary": {
                    "schema_version": "p7.auto_mode_formal_package_selected_route_execute.v1",
                    "status": "selected_route_execute_manifest_recorded",
                    "selected_route_execute_manifest_recorded": True,
                    "selected_route_execute_operations_count": 1,
                    "blocking_reasons": [],
                },
            },
            "selected_route_execute_manifest_recorded": True,
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
            "selected_route_preflight_record": {
                "verified_route_type": route_type,
                "routed_next_gate": "formal_package_export_acceptance_router",
                "routed_action": operation["routed_action"],
                "next_command": operation["next_command"],
                "planned_outputs": operation["planned_outputs"],
            },
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _selected_route_execute(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "selected_route_execute_manifest_recorded",
            "mode": "execute",
            "confirm_execute": True,
            "can_execute_selected_route_with_confirmation": True,
            "selected_route_execute_manifest_recorded": True,
            "selected_route_execute_manifest_path": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
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
            "selected_route_execute_operations": [self._operation(route_type)],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _selected_route_execute_manifest(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute_manifest.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_execute_report": "Results/json/auto_mode_formal_package_selected_route_execute.json",
            "manifest_path": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "selected_route_execute_operations": [self._operation(route_type)],
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
            "next_gate_selected_route_execute": (
                "Results/json/auto_mode_formal_package_next_gate_selected_route_execute.json"
            ),
            "selected_route_execute": "Results/json/auto_mode_formal_package_selected_route_execute.json",
            "selected_route_execute_manifest": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

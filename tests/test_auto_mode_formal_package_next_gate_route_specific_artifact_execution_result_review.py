import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review import (
    build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateRouteSpecificArtifactExecutionResultReviewTests(unittest.TestCase):
    """BDD: P7-AS reviews executed route-specific artifacts before verification."""

    def test_bdd_p7as_completed_artifact_execution_is_ready_for_verification(self) -> None:
        """行为 1：P7-AR 执行完成且 executor 输出干净时，放行进入 artifact verification。"""
        execution = self._execution("package_manifest")
        executor = self._executor("package_manifest")

        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
            Path("."),
            execution,
            executor,
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.v1",
        )
        self.assertEqual(report["status"], "route_specific_artifact_execution_result_review_ready")
        self.assertTrue(report["artifact_execution_result_reviewed"])
        self.assertTrue(report["can_continue_to_route_specific_artifact_verification"])
        self.assertEqual(report["verified_route_type"], "package_manifest")
        self.assertEqual(report["artifact_executor_status"], "route_specific_artifact_executed")
        self.assertTrue(report["route_specific_artifact_executed"])
        self.assertTrue(report["selected_route_executed"])
        self.assertTrue(report["export_or_acceptance_executed"])
        self.assertTrue(report["package_manifest_generated"])
        self.assertFalse(report["rendered_pdf"])
        self.assertFalse(report["rendered_docx"])
        self.assertFalse(report["manual_acceptance_performed"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(len(report["route_specific_artifact_verification_input_records"]), 1)
        record = report["route_specific_artifact_verification_input_records"][0]
        self.assertEqual(record["record_id"], "artifact_execution_result::package_manifest")
        self.assertEqual(
            record["artifact_executor_report_path"],
            "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
        )
        self.assertEqual(
            record["delegated_report_path"],
            "Results/json/formal_submission_package_manifest.json",
        )
        self.assertEqual(
            record["review_status"],
            "artifact_execution_accepted_for_route_specific_artifact_verification",
        )

    def test_bdd_p7as_current_blocked_execution_blocks_result_review(self) -> None:
        """行为 2：当前 P7-AR blocked 时，不输出 verification 输入记录。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
            Path("."),
            {},
            {},
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_execution")
        self.assertFalse(report["artifact_execution_result_reviewed"])
        self.assertFalse(report["can_continue_to_route_specific_artifact_verification"])
        self.assertEqual(report["route_specific_artifact_verification_input_records"], [])
        self.assertIn(
            "route_specific_artifact_execution_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7as_missing_invalid_or_not_completed_execution_blocks_review(self) -> None:
        """行为 3：P7-AR 缺失、schema 错、未完成或有 blockers 时阻断。"""
        wrong_schema = self._execution("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_completed = self._execution("package_manifest")
        not_completed["status"] = "blocked_by_route_specific_artifact_execution_result_review"
        blocked = self._execution("package_manifest")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
                Path("."),
                source,
                self._executor("package_manifest"),
            )
            for source in [wrong_schema, not_completed, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_execution" for report in reports)
        )
        self.assertIn("route_specific_artifact_execution_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("route_specific_artifact_execution_not_completed", reports[1]["blocking_reasons"])
        self.assertIn("source_artifact_execution_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7as_execution_and_executor_contract_must_match(self) -> None:
        """行为 4：P7-AR 记录的路径、状态、returncode 和摘要必须与 executor 输出一致。"""
        wrong_path = self._execution("package_manifest")
        wrong_path["route_specific_artifact_executor_report_path"] = "Results/json/wrong.json"
        status_mismatch = self._execution("package_manifest")
        status_mismatch["route_specific_artifact_executor_result"]["status"] = "route_specific_artifact_executor_dry_run_ready"
        route_mismatch = self._executor("package_manifest")
        route_mismatch["route_type"] = "pdf_export"

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
                Path("."),
                wrong_path,
                self._executor("package_manifest"),
            ),
            build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
                Path("."),
                status_mismatch,
                self._executor("package_manifest"),
            ),
            build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
                Path("."),
                self._execution("package_manifest"),
                route_mismatch,
            ),
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_route_specific_artifact_execution_result_contract"
                for report in reports
            )
        )
        self.assertIn("artifact_executor_report_path_mismatch:package_manifest", reports[0]["blocking_reasons"])
        self.assertIn("artifact_executor_result_status_mismatch:package_manifest", reports[1]["blocking_reasons"])
        self.assertIn("artifact_executor_route_type_mismatch:package_manifest", reports[2]["blocking_reasons"])

    def test_bdd_p7as_artifact_executor_output_must_be_completed_and_clean(self) -> None:
        """行为 5：executor output 缺失、未执行、路线 flags 错或越界时阻断。"""
        missing = {}
        not_executed = self._executor("package_manifest")
        not_executed["route_specific_command_executed"] = False
        mismatched_flags = self._executor("package_manifest")
        mismatched_flags["rendered_pdf"] = True
        boundary_violation = self._executor("package_manifest")
        boundary_violation["boundary_flags"]["modified_run_plan"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
                Path("."),
                self._execution("package_manifest"),
                executor,
            )
            for executor in [missing, not_executed, mismatched_flags, boundary_violation]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_executor_output" for report in reports)
        )
        self.assertIn("artifact_executor_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("artifact_executor_route_specific_command_not_executed", reports[1]["blocking_reasons"])
        self.assertIn("artifact_executor_route_flag_mismatch:package_manifest", reports[2]["blocking_reasons"])
        self.assertIn("artifact_executor_boundary_violation:modified_run_plan", reports[3]["blocking_reasons"])

    def test_bdd_p7as_writes_result_review_only(self) -> None:
        """行为 6：只写 P7-AS result review，不运行 verification、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
                project_root,
                self._execution("package_manifest"),
                self._executor("package_manifest"),
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "route_specific_artifact_execution_result_review_ready")
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json"
                ).exists()
            )

    def test_bdd_p7as_cli_defaults_to_current_blocked_execution(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AR report，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            execution_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
            )
            execution_path.parent.mkdir(parents=True, exist_ok=True)
            execution_path.write_text(
                json.dumps({"status": "blocked_by_route_specific_artifact_execution_result_review"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_route_specific_artifact_execution", result.stdout)
            self.assertIn("can_continue_to_route_specific_artifact_verification=false", result.stdout)
            self.assertIn("route_specific_artifact_verification_input_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.json"
                ).exists()
            )

    def _execution(self, route_type: str) -> dict:
        delegated_status = self._delegated_status(route_type)
        flags = self._route_flags(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution.v1",
            "generated_at": "2026-05-29T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "route_specific_artifact_executor_entry_result_review_ready",
            "status": "next_gate_route_specific_artifact_executed",
            "mode": "execute",
            "confirm_artifact_execution": True,
            "verified_route_type": route_type,
            "can_execute_route_specific_artifact_with_confirmation": True,
            "requires_explicit_route_specific_artifact_execution_command": True,
            "route_specific_artifact_execution_command": ["python3", "Program/auto_mode_formal_package_route_specific_artifact_executor.py"],
            "route_specific_artifact_execution_command_executed": True,
            "this_command_ran_route_specific_artifact_executor": True,
            "route_specific_artifact_executor_report_path": (
                "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
            ),
            "route_specific_artifact_executor_review_path": (
                "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md"
            ),
            "route_specific_artifact_executor_returncode": 0,
            "route_specific_artifact_executor_status": "route_specific_artifact_executed",
            "route_specific_artifact_executor_result": {
                "stdout": "",
                "stderr": "",
                "returncode": 0,
                "status": "route_specific_artifact_executed",
                "report_path": "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
                "review_path": "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md",
                "route_specific_artifact_executor_report_summary": {
                    "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_executor.v1",
                    "status": "route_specific_artifact_executed",
                    "mode": "execute",
                    "route_type": route_type,
                    "route_specific_artifact_executed": True,
                    "route_specific_command_executed": True,
                    "delegated_status": delegated_status,
                    "blocking_reasons": [],
                },
            },
            "route_specific_artifact_executed": True,
            "route_specific_command_executed": True,
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": route_type == "manual_acceptance",
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
            **flags,
        }

    def _executor(self, route_type: str) -> dict:
        delegated_status = self._delegated_status(route_type)
        flags = self._route_flags(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_executor.v1",
            "generated_at": "2026-05-29T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "route_specific_artifact_executed",
            "mode": "execute",
            "confirm_artifact_execution": True,
            "can_execute_route_specific_artifact_with_confirmation": True,
            "route_type": route_type,
            "route_specific_artifact_executed": True,
            "route_specific_command_executed": True,
            "route_specific_command": ["python3", self._route_command(route_type)],
            "delegated_report_path": self._delegated_report_path(route_type),
            "delegated_review_path": self._delegated_review_path(route_type),
            "delegated_returncode": 0,
            "delegated_status": delegated_status,
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": route_type == "manual_acceptance",
            "blocking_reasons": [],
            "selected_route_operation": {
                "operation_id": f"selected_route_execute::{route_type}",
                "route_type": route_type,
                "planned_outputs": self._planned_outputs(route_type),
            },
            "route_specific_result": {
                "stdout": "",
                "stderr": "",
                "returncode": 0,
                "status": delegated_status,
                "report_path": self._delegated_report_path(route_type),
                "review_path": self._delegated_review_path(route_type),
            },
            "boundary_flags": self._clean_boundary_flags(),
            **flags,
        }

    def _delegated_status(self, route_type: str) -> str:
        return {
            "pdf_export": "final_pdf_written",
            "docx_export": "docx_exported",
            "package_manifest": "formal_submission_package_ready",
            "manual_acceptance": "formal_submission_package_accepted",
        }[route_type]

    def _delegated_report_path(self, route_type: str) -> str:
        return {
            "pdf_export": "Results/json/formal_pdf_final_writeback.json",
            "docx_export": "Results/json/formal_docx_export.json",
            "package_manifest": "Results/json/formal_submission_package_manifest.json",
            "manual_acceptance": "Results/json/formal_submission_package_manual_acceptance.json",
        }[route_type]

    def _delegated_review_path(self, route_type: str) -> str:
        return {
            "pdf_export": "Reviews/formal_pdf_final_writeback.md",
            "docx_export": "Reviews/formal_docx_export.md",
            "package_manifest": "Reviews/formal_submission_package_acceptance.md",
            "manual_acceptance": "Reviews/formal_submission_package_manual_acceptance.md",
        }[route_type]

    def _route_command(self, route_type: str) -> str:
        return {
            "pdf_export": "Program/formal_pdf_final_writeback.py",
            "docx_export": "Program/formal_docx_export.py",
            "package_manifest": "Program/formal_submission_package_manifest.py",
            "manual_acceptance": "Program/formal_submission_package_manual_acceptance.py",
        }[route_type]

    def _planned_outputs(self, route_type: str) -> list[str]:
        return {
            "pdf_export": ["Submissions/formal_package/paper.pdf"],
            "docx_export": ["Submissions/formal_package/paper.docx"],
            "package_manifest": ["Submissions/formal_package/manifest.json"],
            "manual_acceptance": ["state/product/formal_submission_package_manual_acceptance.json"],
        }[route_type]

    def _route_flags(self, route_type: str) -> dict:
        return {
            "rendered_pdf": route_type == "pdf_export",
            "rendered_docx": route_type == "docx_export",
            "package_manifest_generated": route_type == "package_manifest",
            "manual_acceptance_performed": route_type == "manual_acceptance",
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
            "entered_next_gate": False,
            "ran_next_gate_command": False,
            "wrote_formal_state": False,
            "executed_selected_route": False,
            "exported_or_accepted_formal_package": False,
        }

    def _source_paths(self) -> dict:
        return {
            "route_specific_artifact_execution": (
                "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
            ),
            "route_specific_artifact_executor": (
                "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

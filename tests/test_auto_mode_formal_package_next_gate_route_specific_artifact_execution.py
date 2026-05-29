import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_execution import (
    build_auto_mode_formal_package_next_gate_route_specific_artifact_execution,
    run_auto_mode_formal_package_next_gate_route_specific_artifact_execution,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_execution_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateRouteSpecificArtifactExecutionTests(unittest.TestCase):
    """BDD: P7-AR executes route-specific artifacts only after P7-AQ approves."""

    def test_bdd_p7ar_ready_result_review_creates_execution_command_without_running_it(self) -> None:
        """行为 1：ready P7-AQ 可 dry-run 预览 artifact execution command，但不执行。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
                project_root,
                self._result_review("package_manifest"),
                mode="dry-run",
                source_paths=self._source_paths(),
                repo_root=REPO_ROOT,
            )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution.v1",
        )
        self.assertEqual(report["status"], "route_specific_artifact_execution_dry_run_ready")
        self.assertTrue(report["can_execute_route_specific_artifact_with_confirmation"])
        self.assertEqual(report["verified_route_type"], "package_manifest")
        self.assertEqual(report["route_specific_artifact_execution_command"][0], "python3")
        self.assertEqual(
            report["route_specific_artifact_execution_command"][1],
            "Program/auto_mode_formal_package_route_specific_artifact_executor.py",
        )
        self.assertIn("--mode", report["route_specific_artifact_execution_command"])
        self.assertIn("execute", report["route_specific_artifact_execution_command"])
        self.assertFalse(report["route_specific_artifact_execution_command_executed"])
        self.assertFalse(report["this_command_ran_route_specific_artifact_executor"])
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ar_current_blocked_result_review_blocks_artifact_execution(self) -> None:
        """行为 2：当前 P7-AQ blocked 时不运行 artifact execution。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
            Path("."),
            {},
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_execution_result_review")
        self.assertFalse(report["can_execute_route_specific_artifact_with_confirmation"])
        self.assertEqual(report["route_specific_artifact_execution_command"], [])
        self.assertFalse(report["route_specific_artifact_execution_command_executed"])
        self.assertIn(
            "route_specific_artifact_executor_entry_result_review_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7ar_missing_invalid_or_not_ready_result_review_blocks_execution(self) -> None:
        """行为 3：P7-AQ 缺失、schema 错误、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._result_review("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._result_review("package_manifest")
        not_ready["status"] = "blocked_by_route_specific_artifact_executor_entry"
        blocked = self._result_review("package_manifest")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_execution_result_review" for report in reports)
        )
        self.assertIn(
            "route_specific_artifact_executor_entry_result_review_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn("route_specific_artifact_executor_entry_result_review_not_ready", reports[1]["blocking_reasons"])
        self.assertIn("source_result_review_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7ar_artifact_execution_record_contract_must_be_clean(self) -> None:
        """行为 4：artifact execution record 缺失、重复、错配或未批准时阻断。"""
        missing_record = self._result_review("package_manifest")
        missing_record["route_specific_artifact_execution_records"] = []
        duplicated = self._result_review("package_manifest")
        duplicated["route_specific_artifact_execution_records"].append(
            dict(duplicated["route_specific_artifact_execution_records"][0])
        )
        wrong_route = self._result_review("package_manifest")
        wrong_route["route_specific_artifact_execution_records"][0]["route_type"] = "pdf_export"
        wrong_status = self._result_review("package_manifest")
        wrong_status["route_specific_artifact_execution_records"][0]["review_status"] = "wrong_status"

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_record, duplicated, wrong_route, wrong_status]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_execution_contract" for report in reports)
        )
        self.assertIn("route_specific_artifact_execution_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("route_specific_artifact_execution_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("route_specific_artifact_execution_record_route_type_mismatch:package_manifest", reports[2]["blocking_reasons"])
        self.assertIn("route_specific_artifact_execution_record_review_status_mismatch:package_manifest", reports[3]["blocking_reasons"])

    def test_bdd_p7ar_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 5：execute 模式必须有确认、reviewer 和 note。"""
        no_confirm = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
            Path("."),
            self._result_review("package_manifest"),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_metadata = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
            Path("."),
            self._result_review("package_manifest"),
            mode="execute",
            confirm_artifact_execution=True,
            repo_root=REPO_ROOT,
        )

        self.assertEqual(no_confirm["status"], "blocked_by_missing_route_specific_artifact_execution_confirmation")
        self.assertIn("confirm_artifact_execution_required", no_confirm["blocking_reasons"])
        self.assertEqual(no_metadata["status"], "blocked_by_route_specific_artifact_execution_metadata")
        self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
        self.assertIn("artifact_execution_note_required", no_metadata["blocking_reasons"])
        self.assertFalse(no_confirm["route_specific_artifact_execution_command_executed"])
        self.assertFalse(no_metadata["route_specific_artifact_execution_command_executed"])

    def test_bdd_p7ar_confirmed_execution_runs_route_specific_artifact_executor(self) -> None:
        """行为 6：confirmed execute 会运行 artifact executor execute 并记录路线产物结果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_route_inputs(project_root, "package_manifest")
            self._write_package_manifest_inputs(project_root)

            report, exit_code = run_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
                project_root,
                self._result_review("package_manifest"),
                mode="execute",
                confirm_artifact_execution=True,
                reviewer="unit_test_reviewer",
                note="Run route-specific artifact execution.",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = write_auto_mode_formal_package_next_gate_route_specific_artifact_execution_outputs(
                project_root,
                report,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(report["status"], "next_gate_route_specific_artifact_executed")
            self.assertTrue(report["route_specific_artifact_execution_command_executed"])
            self.assertTrue(report["this_command_ran_route_specific_artifact_executor"])
            self.assertEqual(report["route_specific_artifact_executor_returncode"], 0)
            self.assertEqual(report["route_specific_artifact_executor_status"], "route_specific_artifact_executed")
            self.assertTrue(report["route_specific_artifact_executed"])
            self.assertTrue(report["selected_route_executed"])
            self.assertTrue(report["export_or_acceptance_executed"])
            self.assertTrue(report["package_manifest_generated"])
            self.assertFalse(report["rendered_pdf"])
            self.assertFalse(report["rendered_docx"])
            self.assertFalse(report["manual_acceptance_performed"])
            self.assertFalse(report["can_write_product_state"])
            self.assertTrue((project_root / "Submissions/formal_package/manifest.json").exists())
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
                ).exists()
            )

    def test_bdd_p7ar_missing_artifact_executor_command_file_blocks_execution(self) -> None:
        """行为 7：artifact executor command 文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
            Path("."),
            self._result_review("package_manifest"),
            mode="execute",
            confirm_artifact_execution=True,
            reviewer="unit_test_reviewer",
            note="Try artifact execution.",
            repo_root=Path("/tmp/nonexistent-repo-for-p7ar"),
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_executor_command_unavailable")
        self.assertIn(
            "route_specific_artifact_executor_command_file_missing:Program/auto_mode_formal_package_route_specific_artifact_executor.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["route_specific_artifact_execution_command_executed"])
        self.assertFalse(report["this_command_ran_route_specific_artifact_executor"])

    def test_bdd_p7ar_cli_defaults_to_current_blocked_result_review(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AQ report，写 blocked execution gate。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_review_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.json"
            )
            result_review_path.parent.mkdir(parents=True, exist_ok=True)
            result_review_path.write_text(
                json.dumps({"status": "blocked_by_route_specific_artifact_executor_entry"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_route_specific_artifact_execution.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_route_specific_artifact_execution_result_review", result.stdout)
            self.assertIn("route_specific_artifact_execution_command=0", result.stdout)
            self.assertIn("route_specific_artifact_execution_command_executed=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_execution.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
                ).exists()
            )

    def _result_review(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.v1",
            "generated_at": "2026-05-29T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_route_specific_artifact_executor_entered",
            "status": "route_specific_artifact_executor_entry_result_review_ready",
            "verified_route_type": route_type,
            "route_specific_artifact_executor_status": "route_specific_artifact_executor_dry_run_ready",
            "artifact_executor_entry_result_reviewed": True,
            "can_continue_to_route_specific_artifact_execution": True,
            "route_specific_artifact_execution_records": [
                {
                    "record_id": f"artifact_executor_dry_run::{route_type}",
                    "route_type": route_type,
                    "artifact_executor_report_path": (
                        "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
                    ),
                    "artifact_executor_review_path": (
                        "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md"
                    ),
                    "route_specific_command": self._route_specific_command(route_type),
                    "delegated_report_path": self._delegated_report_path(route_type),
                    "delegated_review_path": self._delegated_review_path(route_type),
                    "review_status": "artifact_executor_dry_run_accepted_for_explicit_artifact_execution",
                    "can_continue_to_route_specific_artifact_execution": True,
                }
            ],
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

    def _write_route_inputs(self, project_root: Path, route_type: str) -> None:
        selected_route_execute = {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute.v1",
            "status": "selected_route_execute_manifest_recorded",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "selected_route_execute_manifest_recorded": True,
            "can_execute_selected_route_with_confirmation": True,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": {},
        }
        manifest = {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute_manifest.v1",
            "topic": selected_route_execute["topic"],
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "boundary_flags": {},
            "selected_route_execute_operations": [self._operation(route_type)],
        }
        self._write_json(
            project_root / "Results/json/auto_mode_formal_package_selected_route_execute.json",
            selected_route_execute,
        )
        self._write_json(
            project_root
            / "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json",
            manifest,
        )

    def _write_package_manifest_inputs(self, project_root: Path) -> None:
        pdf = project_root / "Submissions/formal_package/paper.pdf"
        docx = project_root / "Submissions/formal_package/paper.docx"
        pdf.parent.mkdir(parents=True, exist_ok=True)
        pdf.write_bytes(b"%PDF-1.4\nunit-test\n")
        docx.write_bytes(b"unit-test-docx")
        p6a = {
            "status": "final_pdf_written",
            "final_pdf": "Submissions/formal_package/paper.pdf",
            "final_pdf_sha256": self._sha256(pdf),
            "final_pdf_bytes": pdf.stat().st_size,
            "source_candidate_qmd": "Submissions/formal_package/paper.qmd",
            "formal_state_guard": {"changed": False},
        }
        p6b = {
            "status": "ready_for_docx_export",
            "can_export_docx": True,
            "expected_docx": "Submissions/formal_package/paper.docx",
            "formal_state_guard": {"changed": False},
        }
        p6c = {
            "status": "docx_exported",
            "docx": "Submissions/formal_package/paper.docx",
            "docx_sha256": self._sha256(docx),
            "docx_bytes": docx.stat().st_size,
            "final_pdf": "Submissions/formal_package/paper.pdf",
            "source_candidate_qmd": "Submissions/formal_package/paper.qmd",
            "this_command_wrote_pdf": False,
            "this_command_wrote_docx": True,
            "formal_state_guard": {"changed": False},
        }
        self._write_json(project_root / "Results/json/formal_pdf_final_writeback.json", p6a)
        self._write_json(project_root / "Results/json/formal_docx_export_preflight.json", p6b)
        self._write_json(project_root / "Results/json/formal_docx_export.json", p6c)

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
        if route_type == "manual_acceptance":
            return ["python3", "Program/formal_submission_package_manual_acceptance.py"]
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
        if route_type == "manual_acceptance":
            return "formal_submission_package_manual_acceptance_preflight", "formal_submission_package_manual_acceptance_execute", [
                "Submissions/formal_package/manual_acceptance.json"
            ]
        return "formal_pdf_export_preflight", "formal_pdf_export_execute", [
            "Submissions/formal_package/paper.pdf"
        ]

    def _delegated_report_path(self, route_type: str) -> str:
        if route_type == "docx_export":
            return "Results/json/formal_docx_export.json"
        if route_type == "package_manifest":
            return "Results/json/formal_submission_package_manifest.json"
        if route_type == "manual_acceptance":
            return "Results/json/formal_submission_package_manual_acceptance.json"
        return "Results/json/formal_pdf_final_writeback.json"

    def _delegated_review_path(self, route_type: str) -> str:
        if route_type == "docx_export":
            return "Reviews/formal_docx_export.md"
        if route_type == "package_manifest":
            return "Reviews/formal_submission_package_acceptance.md"
        if route_type == "manual_acceptance":
            return "Reviews/formal_submission_package_manual_acceptance.md"
        return "Reviews/formal_pdf_final_writeback.md"

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
            "route_specific_artifact_executor_entry_result_review": (
                "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.json"
            )
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        digest.update(path.read_bytes())
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()

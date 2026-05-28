import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry import (
    build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry,
    run_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateRouteSpecificArtifactExecutorEntryTests(unittest.TestCase):
    """BDD: P7-AP enters the route-specific artifact executor only after P7-AO is ready."""

    def test_bdd_p7ap_ready_result_review_creates_executor_dry_run_command_without_running_it(self) -> None:
        """行为 1：ready P7-AO 可预览进入 artifact executor 的 dry-run command，但不执行。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
                Path(tmpdir),
                self._result_review("pdf_export"),
                mode="dry-run",
                source_paths=self._source_paths(),
                repo_root=REPO_ROOT,
            )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.v1",
        )
        self.assertEqual(report["status"], "next_gate_route_specific_artifact_executor_entry_dry_run_ready")
        self.assertTrue(report["can_enter_route_specific_artifact_executor_with_confirmation"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["route_specific_artifact_executor_entry_command"][0], "python3")
        self.assertEqual(
            report["route_specific_artifact_executor_entry_command"][1],
            "Program/auto_mode_formal_package_route_specific_artifact_executor.py",
        )
        self.assertIn("--mode", report["route_specific_artifact_executor_entry_command"])
        self.assertIn("dry-run", report["route_specific_artifact_executor_entry_command"])
        self.assertFalse(report["route_specific_artifact_executor_entry_command_executed"])
        self.assertFalse(report["this_command_ran_route_specific_artifact_executor"])
        self.assertFalse(report["route_specific_artifact_executor_entered"])
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ap_current_blocked_result_review_blocks_executor_entry(self) -> None:
        """行为 2：当前 P7-AO blocked 时不进入 artifact executor。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
            Path("."),
            {},
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_next_gate_selected_route_execute_result_review")
        self.assertFalse(report["can_enter_route_specific_artifact_executor_with_confirmation"])
        self.assertEqual(report["route_specific_artifact_executor_entry_command"], [])
        self.assertFalse(report["route_specific_artifact_executor_entry_command_executed"])
        self.assertIn(
            "next_gate_selected_route_execute_result_review_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7ap_missing_invalid_or_not_ready_result_review_blocks_entry(self) -> None:
        """行为 3：P7-AO 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._result_review("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._result_review("pdf_export")
        not_ready["status"] = "blocked_by_next_gate_selected_route_execute"
        blocked = self._result_review("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_next_gate_selected_route_execute_result_review" for report in reports)
        )
        self.assertIn(
            "next_gate_selected_route_execute_result_review_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "next_gate_selected_route_execute_result_review_not_ready",
            reports[1]["blocking_reasons"],
        )
        self.assertIn("source_result_review_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7ap_artifact_executor_input_record_contract_must_be_clean(self) -> None:
        """行为 4：executor input record 缺失、重复、未知路线或路径错配时阻断。"""
        missing_record = self._result_review("pdf_export")
        missing_record["route_specific_artifact_executor_input_records"] = []
        duplicated = self._result_review("pdf_export")
        duplicated["route_specific_artifact_executor_input_records"].append(
            dict(duplicated["route_specific_artifact_executor_input_records"][0])
        )
        unknown_route = self._result_review("pdf_export")
        unknown_route["route_specific_artifact_executor_input_records"][0]["verified_route_type"] = "unknown_route"
        wrong_manifest_path = self._result_review("pdf_export")
        wrong_manifest_path["route_specific_artifact_executor_input_records"][0][
            "selected_route_execute_manifest_path"
        ] = "workspace/wrong.json"

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_record, duplicated, unknown_route, wrong_manifest_path]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_executor_entry_contract" for report in reports)
        )
        self.assertIn("artifact_executor_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("artifact_executor_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("artifact_executor_route_type_unknown:unknown_route", reports[2]["blocking_reasons"])
        self.assertIn("artifact_executor_manifest_path_mismatch:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7ap_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 5：execute 模式必须有确认、reviewer 和 note。"""
        no_confirm = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
            Path("."),
            self._result_review("pdf_export"),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_metadata = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
            Path("."),
            self._result_review("pdf_export"),
            mode="execute",
            confirm_artifact_executor_entry=True,
            repo_root=REPO_ROOT,
        )

        self.assertEqual(no_confirm["status"], "blocked_by_missing_route_specific_artifact_executor_entry_confirmation")
        self.assertIn("confirm_artifact_executor_entry_required", no_confirm["blocking_reasons"])
        self.assertEqual(no_metadata["status"], "blocked_by_route_specific_artifact_executor_entry_metadata")
        self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
        self.assertIn("artifact_executor_entry_note_required", no_metadata["blocking_reasons"])
        self.assertFalse(no_confirm["route_specific_artifact_executor_entry_command_executed"])
        self.assertFalse(no_metadata["route_specific_artifact_executor_entry_command_executed"])

    def test_bdd_p7ap_confirmed_entry_runs_artifact_executor_dry_run_only(self) -> None:
        """行为 6：confirmed entry 只运行既有 artifact executor 的 dry-run，不产出正式包。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_selected_route_execute.json",
                self._selected_route_execute("pdf_export"),
            )
            self._write_json(
                project_root
                / "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json",
                self._selected_route_execute_manifest("pdf_export"),
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
                project_root,
                self._result_review("pdf_export"),
                mode="execute",
                confirm_artifact_executor_entry=True,
                reviewer="unit_test_reviewer",
                note="Enter route-specific artifact executor dry-run.",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_outputs(
                    project_root,
                    report,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(report["status"], "next_gate_route_specific_artifact_executor_entered")
            self.assertTrue(report["route_specific_artifact_executor_entry_command_executed"])
            self.assertTrue(report["this_command_ran_route_specific_artifact_executor"])
            self.assertTrue(report["route_specific_artifact_executor_entered"])
            self.assertEqual(report["route_specific_artifact_executor_returncode"], 0)
            self.assertEqual(report["route_specific_artifact_executor_status"], "route_specific_artifact_executor_dry_run_ready")
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
                ).exists()
            )
            self.assertFalse(report["route_specific_command_executed"])
            self.assertFalse(report["route_specific_artifact_executed"])
            self.assertFalse(report["selected_route_executed"])
            self.assertFalse(report["export_or_acceptance_executed"])
            self.assertFalse(report["rendered_pdf"])
            self.assertFalse(report["rendered_docx"])
            self.assertFalse(report["package_manifest_generated"])
            self.assertFalse(report["manual_acceptance_performed"])
            self.assertFalse(report["can_write_product_state"])
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
                ).exists()
            )

    def test_bdd_p7ap_missing_artifact_executor_command_file_blocks_entry(self) -> None:
        """行为 7：artifact executor command 文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
            Path("."),
            self._result_review("pdf_export"),
            mode="execute",
            confirm_artifact_executor_entry=True,
            reviewer="unit_test_reviewer",
            note="Try artifact executor entry.",
            repo_root=Path("/tmp/nonexistent-repo-for-p7ap"),
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_executor_command_unavailable")
        self.assertIn(
            "route_specific_artifact_executor_command_file_missing:Program/auto_mode_formal_package_route_specific_artifact_executor.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["route_specific_artifact_executor_entry_command_executed"])
        self.assertFalse(report["this_command_ran_route_specific_artifact_executor"])

    def test_bdd_p7ap_cli_defaults_to_current_blocked_result_review(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AO report，写 blocked entry gate。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_review_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_selected_route_execute_result_review.json"
            )
            result_review_path.parent.mkdir(parents=True, exist_ok=True)
            result_review_path.write_text(
                json.dumps({"status": "blocked_by_next_gate_selected_route_execute"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_next_gate_selected_route_execute_result_review", result.stdout)
            self.assertIn("route_specific_artifact_executor_entry_command=0", result.stdout)
            self.assertIn("route_specific_artifact_executor_entered=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
                ).exists()
            )

    def _result_review(self, route_type: str) -> dict:
        operation = self._operation(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_selected_route_execute_result_review.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_selected_route_execute_command_executed",
            "status": "next_gate_selected_route_execute_result_review_ready",
            "verified_route_type": route_type,
            "selected_route_execute_status": "selected_route_execute_manifest_recorded",
            "selected_route_execute_result_reviewed": True,
            "can_continue_to_route_specific_artifact_executor": True,
            "selected_route_execute_command_executed": True,
            "this_command_ran_selected_route_execute_command": False,
            "selected_route_execute_manifest_recorded": True,
            "route_specific_artifact_executed": False,
            "route_specific_command_executed": False,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "route_specific_artifact_executor_input_records": [
                {
                    "record_id": f"selected_route_execute_result::{route_type}",
                    "verified_route_type": route_type,
                    "selected_route_execute_status": "selected_route_execute_manifest_recorded",
                    "selected_route_execute_report_path": (
                        "Results/json/auto_mode_formal_package_selected_route_execute.json"
                    ),
                    "selected_route_execute_manifest_path": (
                        "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
                    ),
                    "operation_id": operation["operation_id"],
                    "route_execution_id": operation["route_execution_id"],
                    "routed_action": operation["routed_action"],
                    "next_command": operation["next_command"],
                    "planned_outputs": operation["planned_outputs"],
                    "review_status": "selected_route_execute_manifest_accepted_for_route_specific_artifact_executor",
                    "can_continue_to_route_specific_artifact_executor": True,
                }
            ],
            "blocking_reasons": [],
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
            "next_gate_selected_route_execute_result_review": (
                "Results/json/auto_mode_formal_package_next_gate_selected_route_execute_result_review.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

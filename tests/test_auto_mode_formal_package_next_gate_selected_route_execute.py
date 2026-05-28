import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_selected_route_execute import (
    build_auto_mode_formal_package_next_gate_selected_route_execute,
    run_auto_mode_formal_package_next_gate_selected_route_execute,
    write_auto_mode_formal_package_next_gate_selected_route_execute_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateSelectedRouteExecuteTests(unittest.TestCase):
    """BDD: P7-AN runs selected route execute only after P7-AM is ready."""

    def test_bdd_p7an_ready_result_review_creates_dry_run_command_without_running_it(self) -> None:
        """行为 1：ready P7-AM 可 dry-run 预览 selected route execute command，但不执行。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_selected_route_execute(
                project_root,
                self._result_review("pdf_export"),
                mode="dry-run",
                source_paths=self._source_paths(),
                repo_root=REPO_ROOT,
            )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_selected_route_execute.v1",
        )
        self.assertEqual(report["status"], "next_gate_selected_route_execute_dry_run_ready")
        self.assertTrue(report["can_execute_selected_route_with_confirmation"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(report["selected_route_execute_command"][0], "python3")
        self.assertEqual(
            report["selected_route_execute_command"][1],
            "Program/auto_mode_formal_package_selected_route_execute.py",
        )
        self.assertIn("--selected-route-preflight", report["selected_route_execute_command"])
        self.assertFalse(report["selected_route_execute_command_executed"])
        self.assertFalse(report["this_command_ran_selected_route_execute_command"])
        self.assertFalse(report["selected_route_execute_manifest_recorded"])
        self.assertFalse(report["selected_route_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7an_current_blocked_result_review_blocks_selected_route_execute(self) -> None:
        """行为 2：当前 P7-AM blocked 时不运行 selected route execute。"""
        report = build_auto_mode_formal_package_next_gate_selected_route_execute(
            Path("."),
            {},
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_workflow_continuation_result_review")
        self.assertFalse(report["can_execute_selected_route_with_confirmation"])
        self.assertEqual(report["selected_route_execute_command"], [])
        self.assertFalse(report["selected_route_execute_command_executed"])
        self.assertIn(
            "workflow_continuation_result_review_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7an_missing_invalid_or_not_ready_result_review_blocks_execution(self) -> None:
        """行为 3：P7-AM 缺失、schema 错误、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._result_review("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._result_review("pdf_export")
        not_ready["status"] = "blocked_by_next_gate_workflow_continuation_execute"
        blocked = self._result_review("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_selected_route_execute(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_workflow_continuation_result_review" for report in reports))
        self.assertIn("workflow_continuation_result_review_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("workflow_continuation_result_review_not_ready", reports[1]["blocking_reasons"])
        self.assertIn("source_result_review_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7an_selected_route_execute_contract_must_be_clean(self) -> None:
        """行为 4：selected route preflight record 缺失、重复、未知或错配时阻断。"""
        missing_record = self._result_review("pdf_export")
        missing_record["selected_route_execution_preflight_records"] = []
        duplicated = self._result_review("pdf_export")
        duplicated["selected_route_execution_preflight_records"].append(
            dict(duplicated["selected_route_execution_preflight_records"][0])
        )
        unknown_route = self._result_review("pdf_export")
        unknown_route["selected_route_execution_preflight_records"][0]["verified_route_type"] = "unknown_route"
        wrong_path = self._result_review("pdf_export")
        wrong_path["selected_route_execution_preflight_records"][0][
            "selected_route_preflight_report_path"
        ] = "Results/json/wrong.json"

        reports = [
            build_auto_mode_formal_package_next_gate_selected_route_execute(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_record, duplicated, unknown_route, wrong_path]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_next_gate_selected_route_execute_contract" for report in reports))
        self.assertIn("selected_route_preflight_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("selected_route_preflight_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("selected_route_type_unknown:unknown_route", reports[2]["blocking_reasons"])
        self.assertIn("selected_route_preflight_report_path_mismatch:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7an_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 5：execute 模式必须有确认、reviewer 和 note。"""
        no_confirm = build_auto_mode_formal_package_next_gate_selected_route_execute(
            Path("."),
            self._result_review("pdf_export"),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_metadata = build_auto_mode_formal_package_next_gate_selected_route_execute(
            Path("."),
            self._result_review("pdf_export"),
            mode="execute",
            confirm_selected_route_execute=True,
            repo_root=REPO_ROOT,
        )

        self.assertEqual(no_confirm["status"], "blocked_by_missing_next_gate_selected_route_execute_confirmation")
        self.assertIn("confirm_selected_route_execute_required", no_confirm["blocking_reasons"])
        self.assertEqual(no_metadata["status"], "blocked_by_next_gate_selected_route_execute_metadata")
        self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
        self.assertIn("selected_route_execute_note_required", no_metadata["blocking_reasons"])
        self.assertFalse(no_confirm["selected_route_execute_command_executed"])
        self.assertFalse(no_metadata["selected_route_execute_command_executed"])

    def test_bdd_p7an_confirmed_execution_runs_selected_route_execute_command(self) -> None:
        """行为 6：confirmed execute 会运行 selected route execute gate 并记录结果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
                self._selected_route_preflight("pdf_export"),
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_selected_route_execute(
                project_root,
                self._result_review("pdf_export"),
                mode="execute",
                confirm_selected_route_execute=True,
                reviewer="unit_test_reviewer",
                note="Run selected route execute gate.",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = write_auto_mode_formal_package_next_gate_selected_route_execute_outputs(
                project_root,
                report,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(report["status"], "next_gate_selected_route_execute_command_executed")
            self.assertTrue(report["selected_route_execute_command_executed"])
            self.assertTrue(report["this_command_ran_selected_route_execute_command"])
            self.assertEqual(report["selected_route_execute_returncode"], 0)
            self.assertEqual(report["selected_route_execute_status"], "selected_route_execute_manifest_recorded")
            self.assertTrue(report["selected_route_execute_manifest_recorded"])
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_selected_route_execute.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
                ).exists()
            )
            self.assertFalse(report["selected_route_executed"])
            self.assertFalse(report["export_or_acceptance_executed"])
            self.assertFalse(report["rendered_pdf"])
            self.assertFalse(report["rendered_docx"])
            self.assertFalse(report["package_manifest_generated"])
            self.assertFalse(report["manual_acceptance_performed"])
            self.assertFalse(report["can_write_product_state"])
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_selected_route_execute.json"
                ).exists()
            )

    def test_bdd_p7an_missing_selected_route_execute_command_file_blocks_execution(self) -> None:
        """行为 7：selected route execute command 文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_next_gate_selected_route_execute(
            Path("."),
            self._result_review("pdf_export"),
            mode="execute",
            confirm_selected_route_execute=True,
            reviewer="unit_test_reviewer",
            note="Try selected route execute.",
            repo_root=Path("/tmp/nonexistent-repo-for-p7an"),
        )

        self.assertEqual(report["status"], "blocked_by_next_gate_selected_route_command_unavailable")
        self.assertIn(
            "selected_route_execute_command_file_missing:Program/auto_mode_formal_package_selected_route_execute.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["selected_route_execute_command_executed"])
        self.assertFalse(report["this_command_ran_selected_route_execute_command"])

    def test_bdd_p7an_cli_defaults_to_current_blocked_result_review(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AM report，写 blocked execute gate。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_review_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json"
            )
            result_review_path.parent.mkdir(parents=True, exist_ok=True)
            result_review_path.write_text(
                json.dumps({"status": "blocked_by_next_gate_workflow_continuation_execute"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_selected_route_execute.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_workflow_continuation_result_review", result.stdout)
            self.assertIn("selected_route_execute_command=0", result.stdout)
            self.assertIn("selected_route_execute_command_executed=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_selected_route_execute.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_selected_route_execute.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_selected_route_execute.json"
                ).exists()
            )

    def _result_review(self, route_type: str) -> dict:
        routed_action, next_command, planned_outputs = self._route_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_workflow_continuation_result_review.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_workflow_continuation_executed",
            "status": "next_gate_workflow_continuation_result_review_ready",
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "continuation_status": "ready_for_selected_formal_package_route_execution_review",
            "selected_route_preflight_status": "ready_for_selected_formal_package_route_execution_review",
            "workflow_continuation_result_reviewed": True,
            "can_continue_to_selected_route_execution": True,
            "workflow_continuation_executed": True,
            "this_command_ran_continuation": False,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "selected_route_execution_preflight_records": [
                {
                    "record_id": (
                        "workflow_continuation_result::formal_package_export_acceptance_router::"
                        f"{route_type}"
                    ),
                    "verified_route_type": route_type,
                    "routed_next_gate": "formal_package_export_acceptance_router",
                    "selected_route_preflight_status": (
                        "ready_for_selected_formal_package_route_execution_review"
                    ),
                    "selected_route_preflight_schema_version": (
                        "p7.auto_mode_formal_package_selected_route_execution_preflight.v1"
                    ),
                    "selected_route_preflight_report_path": (
                        "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
                    ),
                    "selected_route_preflight_review_path": (
                        "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md"
                    ),
                    "routed_action": routed_action,
                    "next_command": next_command,
                    "planned_outputs": planned_outputs,
                    "review_status": "selected_route_preflight_accepted_for_explicit_route_execution",
                    "can_continue_to_selected_route_execution": True,
                }
            ],
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _selected_route_preflight(self, route_type: str) -> dict:
        routed_action, next_command, planned_outputs = self._route_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execution_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "formal_package_export_acceptance_route_recorded",
            "status": "ready_for_selected_formal_package_route_execution_review",
            "can_request_selected_route_execution": True,
            "requires_explicit_route_execute_command": True,
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
            "selected_route_execution_plan": [
                {
                    "route_execution_id": f"selected_formal_package_route_execution::{routed_action}",
                    "routed_action": routed_action,
                    "route_type": route_type,
                    "next_command": next_command,
                    "source_formal_targets": [
                        "Submissions/formal_package/manuscript/paper.md",
                    ],
                    "planned_outputs": planned_outputs,
                    "execution_status": "pending_explicit_route_execute_command",
                    "requires_explicit_route_execute_command": True,
                    "will_execute_by_this_command": False,
                    "will_render_pdf_by_this_command": False,
                    "will_render_docx_by_this_command": False,
                    "will_generate_manifest_by_this_command": False,
                    "will_perform_manual_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
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
        }

    def _source_paths(self) -> dict:
        return {
            "next_gate_workflow_continuation_result_review": (
                "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_workflow_continuation_execute import (
    build_auto_mode_formal_package_next_gate_workflow_continuation_execute,
    run_auto_mode_formal_package_next_gate_workflow_continuation_execute,
    write_auto_mode_formal_package_next_gate_workflow_continuation_execute_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateWorkflowContinuationExecuteTests(unittest.TestCase):
    """BDD: P7-AL executes a reviewed workflow continuation only with confirmation."""

    def test_bdd_p7al_ready_preflight_creates_dry_run_command_without_running_it(self) -> None:
        """行为 1：ready P7-AK 可 dry-run 预览 continuation command，但不执行。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
                project_root,
                self._continuation_preflight("pdf_export"),
                mode="dry-run",
                source_paths=self._source_paths(),
                repo_root=REPO_ROOT,
            )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_workflow_continuation_execute.v1",
        )
        self.assertEqual(report["status"], "next_gate_workflow_continuation_execute_dry_run_ready")
        self.assertTrue(report["can_execute_next_gate_workflow_continuation_with_confirmation"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(report["continuation_command"][0], "python3")
        self.assertEqual(
            report["continuation_command"][1],
            "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
        )
        self.assertIn("--export-acceptance-router", report["continuation_command"])
        self.assertFalse(report["workflow_continuation_executed"])
        self.assertFalse(report["this_command_ran_continuation"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7al_current_blocked_preflight_blocks_continuation_execution(self) -> None:
        """行为 2：当前 P7-AK blocked 时不运行 continuation。"""
        report = build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
            Path("."),
            {},
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_next_gate_workflow_continuation_preflight")
        self.assertFalse(report["can_execute_next_gate_workflow_continuation_with_confirmation"])
        self.assertEqual(report["continuation_command"], [])
        self.assertFalse(report["workflow_continuation_executed"])
        self.assertIn(
            "next_gate_workflow_continuation_preflight_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7al_missing_invalid_or_not_ready_preflight_blocks_execution(self) -> None:
        """行为 3：P7-AK 缺失、schema 错误、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._continuation_preflight("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._continuation_preflight("pdf_export")
        not_ready["status"] = "blocked_by_manifested_next_gate_command_result_review"
        blocked = self._continuation_preflight("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_next_gate_workflow_continuation_preflight" for report in reports)
        )
        self.assertIn("next_gate_workflow_continuation_preflight_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("next_gate_workflow_continuation_preflight_not_ready", reports[1]["blocking_reasons"])
        self.assertIn("source_preflight_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7al_continuation_plan_contract_must_be_clean(self) -> None:
        """行为 4：continuation plan 缺失、重复、错配或标记自执行时阻断。"""
        missing_plan = self._continuation_preflight("pdf_export")
        missing_plan["workflow_continuation_plan"] = []
        duplicated = self._continuation_preflight("pdf_export")
        duplicated["workflow_continuation_plan"].append(dict(duplicated["workflow_continuation_plan"][0]))
        wrong_path = self._continuation_preflight("pdf_export")
        wrong_path["workflow_continuation_plan"][0]["command_path"] = "Program/wrong.py"
        marked_run = self._continuation_preflight("pdf_export")
        marked_run["workflow_continuation_plan"][0]["will_run_continuation_by_this_command"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_plan, duplicated, wrong_path, marked_run]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_next_gate_workflow_continuation_execute_contract" for report in reports)
        )
        self.assertIn("workflow_continuation_plan_missing", reports[0]["blocking_reasons"])
        self.assertIn("workflow_continuation_plan_not_single", reports[1]["blocking_reasons"])
        self.assertIn("workflow_continuation_command_path_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("workflow_continuation_plan_marked_run_continuation:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7al_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 5：execute 模式必须有确认、reviewer 和 note。"""
        no_confirm = build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
            Path("."),
            self._continuation_preflight("pdf_export"),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_metadata = build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
            Path("."),
            self._continuation_preflight("pdf_export"),
            mode="execute",
            confirm_continuation_execute=True,
            repo_root=REPO_ROOT,
        )

        self.assertEqual(no_confirm["status"], "blocked_by_missing_next_gate_workflow_continuation_execute_confirmation")
        self.assertIn("confirm_continuation_execute_required", no_confirm["blocking_reasons"])
        self.assertEqual(no_metadata["status"], "blocked_by_next_gate_workflow_continuation_execute_metadata")
        self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
        self.assertIn("continuation_execute_note_required", no_metadata["blocking_reasons"])
        self.assertFalse(no_confirm["workflow_continuation_executed"])
        self.assertFalse(no_metadata["workflow_continuation_executed"])

    def test_bdd_p7al_confirmed_execution_runs_continuation_preflight_command(self) -> None:
        """行为 6：confirmed execute 会运行 selected route execution preflight 并记录结果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_export_acceptance_router.json",
                self._ready_export_acceptance_router("formal_pdf_export_preflight"),
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_workflow_continuation_execute(
                project_root,
                self._continuation_preflight("pdf_export"),
                mode="execute",
                confirm_continuation_execute=True,
                reviewer="unit_test_reviewer",
                note="Run continuation preflight.",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = write_auto_mode_formal_package_next_gate_workflow_continuation_execute_outputs(
                project_root,
                report,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(report["status"], "next_gate_workflow_continuation_executed")
            self.assertTrue(report["workflow_continuation_executed"])
            self.assertTrue(report["this_command_ran_continuation"])
            self.assertEqual(report["continuation_returncode"], 0)
            self.assertEqual(
                report["continuation_status"],
                "ready_for_selected_formal_package_route_execution_review",
            )
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
                ).exists()
            )
            self.assertFalse(report["selected_route_executed"])
            self.assertFalse(report["export_or_acceptance_executed"])
            self.assertFalse(report["can_write_product_state"])
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_workflow_continuation_execute.json"
                ).exists()
            )

    def test_bdd_p7al_missing_continuation_command_file_blocks_execution(self) -> None:
        """行为 7：continuation command 文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
            Path("."),
            self._continuation_preflight("pdf_export"),
            mode="execute",
            confirm_continuation_execute=True,
            reviewer="unit_test_reviewer",
            note="Try continuation.",
            repo_root=Path("/tmp/nonexistent-repo-for-p7al"),
        )

        self.assertEqual(report["status"], "blocked_by_next_gate_workflow_continuation_command_unavailable")
        self.assertIn(
            "workflow_continuation_command_file_missing:Program/auto_mode_formal_package_selected_route_execution_preflight.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["workflow_continuation_executed"])
        self.assertFalse(report["this_command_ran_continuation"])

    def test_bdd_p7al_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AK report，写 blocked execute report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            preflight_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json"
            )
            preflight_path.parent.mkdir(parents=True, exist_ok=True)
            preflight_path.write_text(
                json.dumps({"status": "blocked_by_manifested_next_gate_command_result_review"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_workflow_continuation_execute.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_next_gate_workflow_continuation_preflight", result.stdout)
            self.assertIn("workflow_continuation_executed=false", result.stdout)
            self.assertIn("continuation_command=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_workflow_continuation_execute.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_workflow_continuation_execute.json"
                ).exists()
            )

    def _continuation_preflight(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_workflow_continuation_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_next_gate_command_result_review_ready",
            "status": "ready_for_next_gate_workflow_continuation_review",
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "can_request_next_gate_workflow_continuation": True,
            "requires_explicit_workflow_continuation_command": True,
            "workflow_continuation_executed": False,
            "this_command_ran_continuation": False,
            "next_gate_command_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "workflow_continuation_plan": [
                {
                    "continuation_id": (
                        "next_gate_workflow_continuation::formal_package_export_acceptance_router::"
                        f"{route_type}"
                    ),
                    "source_delegated_result_record_id": (
                        "manifested_next_gate_result::formal_package_export_acceptance_router::"
                        f"{route_type}"
                    ),
                    "verified_route_type": route_type,
                    "routed_next_gate": "formal_package_export_acceptance_router",
                    "delegated_status": "formal_package_export_acceptance_route_recorded",
                    "continuation_kind": "selected_route_execution_preflight",
                    "next_command": "auto_mode_formal_package_selected_route_execution_preflight",
                    "command_path": "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
                    "source_report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
                    "next_report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
                    "next_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
                    "continuation_status": "pending_explicit_workflow_continuation_command",
                    "requires_explicit_workflow_continuation_command": True,
                    "will_run_continuation_by_this_command": False,
                    "will_execute_export_or_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _ready_export_acceptance_router(self, routed_action: str) -> dict:
        selected_plan_item = {
            "action_id": routed_action,
            "label": "Formal PDF Export Preflight",
            "description": "Later explicit command.",
            "source_formal_targets": [
                "Submissions/formal_package/manuscript/paper.md",
                "Submissions/formal_package/bibliography/literature_review_packet.json",
            ],
            "execution_status": "pending_explicit_export_or_acceptance_command",
            "requires_explicit_export_or_acceptance_command": True,
            "this_command_rendered_or_accepted": False,
            "this_command_wrote_product_state": False,
        }
        return {
            "schema_version": "p7.auto_mode_formal_package_export_acceptance_router.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "ready_for_formal_package_export_acceptance_review",
            "status": "formal_package_export_acceptance_route_recorded",
            "decision": "pdf_export",
            "route_request": {
                "decision": "pdf_export",
                "confirm_route": True,
                "reviewer": "reviewer-a",
                "note": "Route selected for later explicit execution.",
                "metadata_complete": True,
            },
            "can_route_export_or_acceptance": True,
            "route_recorded": True,
            "routed_action": routed_action,
            "selected_plan_item": selected_plan_item,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
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
        }

    def _source_paths(self) -> dict:
        return {
            "next_gate_workflow_continuation_preflight": (
                "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

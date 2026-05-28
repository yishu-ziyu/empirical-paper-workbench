import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_manifested_routed_next_gate_command_execute import (
    build_auto_mode_formal_package_manifested_routed_next_gate_command_execute,
    run_auto_mode_formal_package_manifested_routed_next_gate_command_execute,
    write_auto_mode_formal_package_manifested_routed_next_gate_command_execute_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageManifestedRoutedNextGateCommandExecuteTests(unittest.TestCase):
    """BDD: P7-AI executes a reviewed manifested next-gate command only with confirmation."""

    def test_bdd_p7ai_ready_pdf_preflight_creates_dry_run_command_without_running_it(self) -> None:
        """行为 1：ready PDF command preflight 可 dry-run 预览命令，但不执行。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
                project_root,
                self._command_preflight("pdf_export"),
                mode="dry-run",
                source_paths=self._source_paths(),
                repo_root=REPO_ROOT,
            )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_manifested_routed_next_gate_command_execute.v1",
        )
        self.assertEqual(report["status"], "manifested_next_gate_command_execute_dry_run_ready")
        self.assertTrue(report["can_execute_manifested_next_gate_command_with_confirmation"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(report["delegated_command"][0], "python3")
        self.assertEqual(report["delegated_command"][1], "Program/auto_mode_formal_package_export_acceptance_router.py")
        self.assertFalse(report["next_gate_command_executed"])
        self.assertFalse(report["this_command_ran_next_gate_command"])
        self.assertFalse(report["next_gate_entered"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ai_current_blocked_preflight_blocks_command_execution(self) -> None:
        """行为 2：当前 P7-AH blocked 时不运行下一关命令。"""
        report = build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
            Path("."),
            {},
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_command_preflight")
        self.assertFalse(report["can_execute_manifested_next_gate_command_with_confirmation"])
        self.assertEqual(report["delegated_command"], [])
        self.assertFalse(report["next_gate_command_executed"])
        self.assertIn("manifested_routed_next_gate_command_preflight_missing_or_invalid_schema", report["blocking_reasons"])

    def test_bdd_p7ai_missing_invalid_or_not_ready_preflight_blocks_execution(self) -> None:
        """行为 3：preflight 缺失、schema 错误、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._command_preflight("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._command_preflight("pdf_export")
        not_ready["status"] = "blocked_by_routed_next_gate_entry_manifest"
        blocked = self._command_preflight("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_command_preflight" for report in reports)
        )
        self.assertIn(
            "manifested_routed_next_gate_command_preflight_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn("manifested_routed_next_gate_command_preflight_not_ready", reports[1]["blocking_reasons"])
        self.assertIn("source_preflight_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7ai_command_plan_contract_must_be_clean(self) -> None:
        """行为 4：命令计划缺失、重复、错配或已执行标记都会阻断。"""
        missing_plan = self._command_preflight("pdf_export")
        missing_plan["next_gate_command_call_plan"] = []
        duplicated = self._command_preflight("pdf_export")
        duplicated["next_gate_command_call_plan"].append(dict(duplicated["next_gate_command_call_plan"][0]))
        missing_command = self._command_preflight("pdf_export")
        missing_command["next_gate_command_call_plan"][0]["next_command"] = ""
        wrong_path = self._command_preflight("pdf_export")
        wrong_path["next_gate_command_call_plan"][0]["command_path"] = "Program/wrong.py"
        marked_run = self._command_preflight("pdf_export")
        marked_run["next_gate_command_call_plan"][0]["will_run_next_gate_command_by_this_command"] = True

        reports = [
            build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_plan, duplicated, missing_command, wrong_path, marked_run]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_command_execute_contract" for report in reports)
        )
        self.assertIn("next_gate_command_call_plan_missing", reports[0]["blocking_reasons"])
        self.assertIn("next_gate_command_call_plan_not_single", reports[1]["blocking_reasons"])
        self.assertIn("next_gate_command_missing:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("next_gate_command_path_mismatch:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("next_gate_command_plan_marked_run_command:pdf_export", reports[4]["blocking_reasons"])

    def test_bdd_p7ai_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 5：execute 模式必须有确认、reviewer 和 note。"""
        no_confirm = build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
            Path("."),
            self._command_preflight("pdf_export"),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_metadata = build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
            Path("."),
            self._command_preflight("pdf_export"),
            mode="execute",
            confirm_command_execute=True,
            repo_root=REPO_ROOT,
        )

        self.assertEqual(no_confirm["status"], "blocked_by_missing_manifested_next_gate_command_execute_confirmation")
        self.assertIn("confirm_command_execute_required", no_confirm["blocking_reasons"])
        self.assertEqual(no_metadata["status"], "blocked_by_manifested_next_gate_command_execute_metadata")
        self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
        self.assertIn("command_execute_note_required", no_metadata["blocking_reasons"])
        self.assertFalse(no_confirm["next_gate_command_executed"])
        self.assertFalse(no_metadata["next_gate_command_executed"])

    def test_bdd_p7ai_confirmed_pdf_execution_runs_delegated_next_gate_command(self) -> None:
        """行为 6：confirmed execute 会调用 export/acceptance router 并记录结果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report, exit_code = run_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
                project_root,
                self._command_preflight("pdf_export"),
                mode="execute",
                confirm_command_execute=True,
                reviewer="unit_test_reviewer",
                note="Run delegated next gate command.",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = write_auto_mode_formal_package_manifested_routed_next_gate_command_execute_outputs(
                project_root,
                report,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(report["status"], "manifested_next_gate_command_executed")
            self.assertTrue(report["next_gate_command_executed"])
            self.assertTrue(report["this_command_ran_next_gate_command"])
            self.assertEqual(report["delegated_returncode"], 0)
            self.assertEqual(report["delegated_command"][1], "Program/auto_mode_formal_package_export_acceptance_router.py")
            self.assertTrue((project_root / "Results/json/auto_mode_formal_package_export_acceptance_router.json").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json").exists())

    def test_bdd_p7ai_missing_downstream_command_file_blocks_execution(self) -> None:
        """行为 7：下游命令文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
            Path("."),
            self._command_preflight("manual_acceptance"),
            mode="execute",
            confirm_command_execute=True,
            reviewer="unit_test_reviewer",
            note="Try delivery completion.",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_manifested_next_gate_command_unavailable")
        self.assertIn(
            "next_gate_command_file_missing:Program/auto_mode_formal_package_delivery_completion_gate.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["next_gate_command_executed"])
        self.assertFalse(report["this_command_ran_next_gate_command"])

    def test_bdd_p7ai_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AH report，写 blocked execute report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            preflight_path = (
                project_root
                / "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json"
            )
            preflight_path.parent.mkdir(parents=True, exist_ok=True)
            preflight_path.write_text(json.dumps({"status": "blocked_by_routed_next_gate_entry_manifest"}), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_manifested_routed_next_gate_command_execute.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_manifested_routed_next_gate_command_preflight", result.stdout)
            self.assertIn("next_gate_command_executed=false", result.stdout)
            self.assertIn("delegated_command=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_execute.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json"
                ).exists()
            )

    def _command_preflight(self, route_type: str) -> dict:
        gate_id, action, next_command, command_path, command_kind = self._command_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_manifested_routed_next_gate_command_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_paths": {
                "routed_next_gate_entry_manifest": (
                    "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
                )
            },
            "source_status": "manifested",
            "status": "ready_for_manifested_routed_next_gate_command_review",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "can_request_manifested_next_gate_command_execution": True,
            "requires_explicit_next_gate_command_execute": True,
            "next_gate_command_executed": False,
            "this_command_ran_next_gate_command": False,
            "next_gate_entered": False,
            "this_command_entered_next_gate": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "next_gate_command_call_plan": [
                {
                    "command_plan_id": f"manifested_routed_next_gate_command::{gate_id}::{route_type}",
                    "source_operation_id": f"routed_next_gate_entry_execute::{gate_id}::{route_type}",
                    "source_entry_id": f"routed_next_gate_entry::{gate_id}::{route_type}",
                    "verified_route_type": route_type,
                    "gate_id": gate_id,
                    "next_gate_action": action,
                    "next_command": next_command,
                    "command_path": command_path,
                    "command_args": ["--project-root", "."],
                    "command_kind": command_kind,
                    "command_status": "pending_explicit_next_gate_command_execute",
                    "requires_explicit_next_gate_command_execute": True,
                    "will_run_next_gate_command_by_this_command": False,
                    "will_enter_next_gate_by_this_command": False,
                    "will_execute_export_or_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _command_mapping(self, route_type: str) -> tuple[str, str, str, str, str]:
        if route_type == "manual_acceptance":
            return (
                "formal_package_delivery_completion_gate",
                "finalize_formal_package_delivery_review",
                "auto_mode_formal_package_delivery_completion_gate",
                "Program/auto_mode_formal_package_delivery_completion_gate.py",
                "delivery_completion",
            )
        return (
            "formal_package_export_acceptance_router",
            "continue_formal_package_export_acceptance_cycle",
            "auto_mode_formal_package_export_acceptance_router",
            "Program/auto_mode_formal_package_export_acceptance_router.py",
            "continue_export_acceptance_cycle",
        )

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
            "manifested_routed_next_gate_command_preflight": (
                "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json"
            ),
        }

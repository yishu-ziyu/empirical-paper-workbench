import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry import (
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry,
    run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateCommandExecuteGateEntryTests(unittest.TestCase):
    """BDD: P7-BD consumes P7-BC and gates manifested next-gate command execution."""

    def test_bdd_p7bd_ready_run_preflight_with_confirmation_delegates_existing_execute(self) -> None:
        """行为 1：ready P7-BC + 显式确认才委托 existing command execute。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
                project_root,
                self._ready_run_preflight("pdf_export"),
                confirm_command_execute=True,
                reviewer="unit_test_reviewer",
                note="Run manifested next gate command.",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_outputs(
                project_root,
                report,
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(report["status"], "manifested_routed_next_gate_command_execute_gate_entry_executed")
            self.assertTrue(report["command_execute_gate_entry_executed"])
            self.assertEqual(report["manifested_command_execute_status"], "manifested_next_gate_command_executed")
            self.assertTrue(report["next_gate_command_executed"])
            self.assertTrue(report["this_command_ran_next_gate_command"])
            self.assertTrue(report["next_gate_entered"])
            self.assertEqual(report["verified_route_type"], "pdf_export")
            self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertTrue((project_root / "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json").exists())
            self.assertTrue((project_root / "Results/json/auto_mode_formal_package_export_acceptance_router.json").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.json").exists())

    def test_bdd_p7bd_current_blocked_run_preflight_blocks_execution(self) -> None:
        """行为 2：当前 blocked P7-BC 不能生成 delegated command。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
            self._blocked_run_preflight(),
            confirm_command_execute=True,
            reviewer="unit_test_reviewer",
            note="Attempt command execute.",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_run_preflight")
        self.assertFalse(report["command_execute_gate_entry_executed"])
        self.assertEqual(report["delegated_command"], [])
        self.assertFalse(report["next_gate_command_executed"])
        self.assertIn("manifested_routed_next_gate_run_preflight_not_ready", report["blocking_reasons"])

    def test_bdd_p7bd_missing_invalid_or_not_ready_run_preflight_blocks_execution(self) -> None:
        """行为 3：P7-BC 缺失、schema 错、未 ready 或不能请求执行时阻断。"""
        wrong_schema = self._ready_run_preflight("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._ready_run_preflight("pdf_export")
        not_ready["status"] = "blocked_by_explicit_routed_next_gate_entry_gate"
        cannot_request = self._ready_run_preflight("pdf_export")
        cannot_request["can_request_manifested_next_gate_command_execution"] = False

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
                source,
                repo_root=REPO_ROOT,
            )
            for source in [{}, wrong_schema, not_ready, cannot_request]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_run_preflight" for report in reports)
        )
        self.assertIn("manifested_routed_next_gate_run_preflight_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_preflight_missing_or_invalid_schema", reports[1]["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_preflight_not_ready", reports[2]["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_preflight_cannot_request_execution", reports[3]["blocking_reasons"])

    def test_bdd_p7bd_run_input_record_must_match_command_plan(self) -> None:
        """行为 4：P7-BC run input record 必须与 command plan 完全匹配。"""
        missing_record = self._ready_run_preflight("pdf_export")
        missing_record["manifested_routed_next_gate_run_input_records"] = []
        duplicated = self._ready_run_preflight("pdf_export")
        duplicated["manifested_routed_next_gate_run_input_records"].append(
            dict(duplicated["manifested_routed_next_gate_run_input_records"][0])
        )
        command_mismatch = self._ready_run_preflight("pdf_export")
        command_mismatch["manifested_routed_next_gate_run_input_records"][0]["next_command"] = "wrong_command"
        plan_mismatch = self._ready_run_preflight("pdf_export")
        plan_mismatch["manifested_routed_next_gate_run_input_records"][0]["command_plan_id"] = "wrong"

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_record, duplicated, command_mismatch, plan_mismatch]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_input_contract" for report in reports)
        )
        self.assertIn("manifested_routed_next_gate_run_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_input_record_next_command_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_input_record_command_plan_id_mismatch:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7bd_execute_requires_explicit_confirmation_before_delegation(self) -> None:
        """行为 5：ready P7-BC 但缺确认时不委托 execute。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
            self._ready_run_preflight("pdf_export"),
            confirm_command_execute=False,
            reviewer="unit_test_reviewer",
            note="Attempt command execute.",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_missing_manifested_routed_next_gate_command_execute_confirmation")
        self.assertFalse(report["command_execute_gate_entry_executed"])
        self.assertEqual(report["delegated_command"], [])
        self.assertIn("confirm_command_execute_required", report["blocking_reasons"])

    def test_bdd_p7bd_execute_requires_reviewer_and_note_before_delegation(self) -> None:
        """行为 6：ready 且确认但缺 reviewer/note 时不委托 execute。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
            self._ready_run_preflight("pdf_export"),
            confirm_command_execute=True,
            reviewer="",
            note="",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_metadata")
        self.assertFalse(report["command_execute_gate_entry_executed"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("command_execute_note_required", report["blocking_reasons"])

    def test_bdd_p7bd_boundary_violations_block_execution(self) -> None:
        """行为 7：P7-BC 出现已运行、已进入或写回信号时阻断。"""
        source = self._ready_run_preflight("pdf_export")
        source["next_gate_command_executed"] = True
        source["next_gate_entered"] = True
        source["can_write_product_state"] = True
        source["boundary_flags"]["ran_next_gate_command"] = True

        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
            source,
            confirm_command_execute=True,
            reviewer="unit_test_reviewer",
            note="Attempt command execute.",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_boundary")
        self.assertIn("manifested_routed_next_gate_run_preflight_already_executed_command", report["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_preflight_already_entered_next_gate", report["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_preflight_allows_product_state_write", report["blocking_reasons"])
        self.assertIn("manifested_routed_next_gate_run_preflight_boundary_violation:ran_next_gate_command", report["blocking_reasons"])

    def test_bdd_p7bd_cli_defaults_to_current_blocked_run_preflight(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-BC，只写 blocked report/review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            preflight_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.json"
            )
            preflight_path.parent.mkdir(parents=True, exist_ok=True)
            preflight_path.write_text(json.dumps(self._blocked_run_preflight()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_manifested_routed_next_gate_run_preflight", result.stdout)
            self.assertIn("command_execute_gate_entry_executed=false", result.stdout)
            self.assertIn("delegated_command=0", result.stdout)
            self.assertIn("next_gate_command_executed=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.md"
                ).exists()
            )
            self.assertFalse((project_root / "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json").exists())

    def _ready_run_preflight(self, route_type: str) -> dict:
        gate_id, action, next_command, command_path, command_kind = self._command_mapping(route_type)
        command_plan_id = f"manifested_routed_next_gate_command::{gate_id}::{route_type}"
        source_operation_id = f"routed_next_gate_entry_execute::{gate_id}::{route_type}"
        source_entry_id = f"routed_next_gate_entry::{gate_id}::{route_type}"
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "explicit_routed_next_gate_entry_manifest_recorded",
            "status": "ready_for_manifested_routed_next_gate_run_preflight",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "manifested_routed_next_gate_run_preflight_reviewed": True,
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
                    "command_plan_id": command_plan_id,
                    "source_operation_id": source_operation_id,
                    "source_entry_id": source_entry_id,
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
            "next_gate_command_call_plan_count": 1,
            "manifested_routed_next_gate_run_input_records": [
                {
                    "record_id": f"manifested_routed_next_gate_run_input::{gate_id}::{route_type}",
                    "verified_route_type": route_type,
                    "routed_next_gate": gate_id,
                    "manifested_command_preflight_status": "ready_for_manifested_routed_next_gate_command_review",
                    "command_plan_id": command_plan_id,
                    "source_operation_id": source_operation_id,
                    "source_entry_id": source_entry_id,
                    "next_command": next_command,
                    "command_path": command_path,
                    "command_kind": command_kind,
                    "requires_explicit_next_gate_command_execute": True,
                    "review_status": "manifested_routed_next_gate_run_preflight_ready_for_command_execute_gate",
                    "manifest_operation_count": 1,
                }
            ],
            "manifested_routed_next_gate_run_input_record_count": 1,
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_run_preflight(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.v1",
            "status": "blocked_by_explicit_routed_next_gate_entry_gate",
            "manifested_routed_next_gate_run_preflight_reviewed": False,
            "can_request_manifested_next_gate_command_execution": False,
            "requires_explicit_next_gate_command_execute": False,
            "next_gate_command_call_plan": [],
            "next_gate_command_call_plan_count": 0,
            "manifested_routed_next_gate_run_input_records": [],
            "manifested_routed_next_gate_run_input_record_count": 0,
            "next_gate_command_executed": False,
            "this_command_ran_next_gate_command": False,
            "next_gate_entered": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": ["explicit_routed_next_gate_entry_gate_not_manifest_recorded"],
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
            "executed_selected_route": False,
            "exported_or_accepted_formal_package": False,
            "entered_explicit_routed_next_gate_entry": False,
            "ran_manifested_routed_next_gate_command": False,
        }


if __name__ == "__main__":
    unittest.main()

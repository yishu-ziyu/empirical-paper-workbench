import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate import (
    run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateCommandResultContinuationExecuteResultDownstreamGateEntryExecuteGateTests(
    unittest.TestCase
):
    """BDD: P7-BJ executes or records the downstream action authorized by P7-BI."""

    def test_bdd_p7bj_export_dry_run_builds_selected_route_execute_command(self) -> None:
        """行为 1：export ready input 只预览 selected-route execution 命令。"""
        report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
            Path("/tmp/project"),
            self._ready_export_gate_entry(),
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            report["status"],
            "manifested_routed_next_gate_downstream_execute_dry_run_ready",
        )
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["downstream_kind"], "selected_route_execution")
        self.assertTrue(report["can_execute_downstream_with_confirmation"])
        self.assertTrue(report["requires_explicit_downstream_command"])
        self.assertEqual(report["downstream_execute_command"][1], "Program/auto_mode_formal_package_selected_route_execute.py")
        self.assertIn("--selected-route-preflight", report["downstream_execute_command"])
        self.assertIn("Results/json/auto_mode_formal_package_selected_route_execution_preflight.json", report["downstream_execute_command"])
        self.assertFalse(report["downstream_execute_command_executed"])
        self.assertFalse(report["selected_route_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bj_manual_terminal_dry_run_prepares_product_review_without_command(self) -> None:
        """行为 2：manual terminal ready input 只预览产品审阅准备。"""
        report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
            Path("/tmp/project"),
            self._ready_manual_gate_entry(),
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            report["status"],
            "manifested_routed_next_gate_downstream_product_review_preparation_dry_run_ready",
        )
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["downstream_kind"], "product_review_preparation")
        self.assertTrue(report["can_execute_downstream_with_confirmation"])
        self.assertFalse(report["requires_explicit_downstream_command"])
        self.assertEqual(report["downstream_execute_command"], [])
        self.assertFalse(report["downstream_execute_command_executed"])
        self.assertFalse(report["product_review_preparation_recorded"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bj_current_blocked_gate_entry_blocks_execute(self) -> None:
        """行为 3：当前 P7-BI blocked 时不生成执行动作。"""
        report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
            Path("/tmp/project"),
            self._blocked_gate_entry(),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(
            report["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry",
        )
        self.assertFalse(report["can_execute_downstream_with_confirmation"])
        self.assertEqual(report["downstream_execute_command"], [])
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_not_ready",
            report["blocking_reasons"],
        )

    def test_bdd_p7bj_missing_invalid_or_not_ready_gate_entry_blocks_execute(self) -> None:
        """行为 4：P7-BI 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._ready_export_gate_entry()
        wrong_schema["schema_version"] = "wrong.schema"
        no_request = self._ready_export_gate_entry()
        no_request["can_request_manifested_routed_next_gate_result_continuation_downstream"] = False
        blocked = self._ready_export_gate_entry()
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
                Path("/tmp/project"),
                source,
                repo_root=REPO_ROOT,
            )[0]
            for source in [{}, wrong_schema, no_request, blocked]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry"
                for report in reports
            )
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_missing_or_invalid_schema",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_cannot_request_downstream",
            reports[2]["blocking_reasons"],
        )
        self.assertIn("source_downstream_gate_entry_has_blocking_reasons", reports[3]["blocking_reasons"])

    def test_bdd_p7bj_downstream_input_record_contract_must_be_single_and_matching(self) -> None:
        """行为 5：downstream input 缺失、重复、错配或路径不干净时阻断。"""
        missing = self._ready_export_gate_entry()
        missing["downstream_input_records"] = []
        duplicated = self._ready_export_gate_entry()
        duplicated["downstream_input_records"].append(dict(duplicated["downstream_input_records"][0]))
        wrong_kind = self._ready_export_gate_entry()
        wrong_kind["downstream_input_records"][0]["downstream_kind"] = "product_review_preparation"
        wrong_route = self._ready_export_gate_entry()
        wrong_route["downstream_input_records"][0]["verified_route_type"] = "docx_export"
        wrong_path = self._ready_export_gate_entry()
        wrong_path["downstream_input_records"][0]["source_report_path"] = "../outside.json"

        reports = [
            run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
                Path("/tmp/project"),
                source,
                repo_root=REPO_ROOT,
            )[0]
            for source in [missing, duplicated, wrong_kind, wrong_route, wrong_path]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_downstream_execute_contract"
                for report in reports
            )
        )
        self.assertIn("downstream_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("downstream_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("downstream_record_kind_mismatch:selected_route_execution", reports[2]["blocking_reasons"])
        self.assertIn("downstream_record_route_type_mismatch:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("downstream_record_source_report_path_unsafe:../outside.json", reports[4]["blocking_reasons"])

    def test_bdd_p7bj_execute_requires_confirmation_reviewer_and_note(self) -> None:
        """行为 6：execute 模式必须有显式确认、reviewer 和 note。"""
        no_confirm, _ = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
            Path("/tmp/project"),
            self._ready_export_gate_entry(),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_reviewer, _ = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
            Path("/tmp/project"),
            self._ready_export_gate_entry(),
            mode="execute",
            confirm_downstream_execute=True,
            note="approved",
            repo_root=REPO_ROOT,
        )
        no_note, _ = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
            Path("/tmp/project"),
            self._ready_manual_gate_entry(),
            mode="execute",
            confirm_downstream_execute=True,
            reviewer="human",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(no_confirm["status"], "blocked_by_missing_downstream_execute_confirmation")
        self.assertIn("confirm_downstream_execute_required", no_confirm["blocking_reasons"])
        self.assertEqual(no_reviewer["status"], "blocked_by_downstream_execute_metadata")
        self.assertIn("downstream_execute_reviewer_required", no_reviewer["blocking_reasons"])
        self.assertEqual(no_note["status"], "blocked_by_downstream_execute_metadata")
        self.assertIn("downstream_execute_note_required", no_note["blocking_reasons"])

    def test_bdd_p7bj_confirmed_export_execute_delegates_selected_route_execute(self) -> None:
        """行为 7：confirmed export execute 调用 selected-route execute 并记录结果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            preflight_path = project_root / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
            preflight_path.parent.mkdir(parents=True, exist_ok=True)
            preflight_path.write_text(json.dumps(self._selected_route_preflight()), encoding="utf-8")

            report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
                project_root,
                self._ready_export_gate_entry(),
                mode="execute",
                confirm_downstream_execute=True,
                reviewer="human",
                note="approved",
                repo_root=REPO_ROOT,
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                report["status"],
                "manifested_routed_next_gate_downstream_selected_route_execute_command_executed",
            )
            self.assertTrue(report["downstream_execute_command_executed"])
            self.assertTrue(report["this_command_ran_downstream_command"])
            self.assertEqual(report["downstream_execute_returncode"], 0)
            self.assertEqual(report["downstream_execute_status"], "selected_route_execute_manifest_recorded")
            self.assertTrue(report["selected_route_execute_manifest_recorded"])
            self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bj_confirmed_manual_terminal_records_product_review_preparation_only(self) -> None:
        """行为 8：confirmed manual terminal 只记录产品审阅准备。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
                project_root,
                self._ready_manual_gate_entry(),
                mode="execute",
                confirm_downstream_execute=True,
                reviewer="human",
                note="approved",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_outputs(
                    project_root,
                    report,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                report["status"],
                "manifested_routed_next_gate_downstream_product_review_preparation_recorded",
            )
            self.assertTrue(report["product_review_preparation_recorded"])
            self.assertFalse(report["downstream_execute_command_executed"])
            self.assertFalse(report["this_command_ran_downstream_command"])
            self.assertEqual(report["downstream_execute_command"], [])
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_product_review_preparation.json").exists())

    def _ready_export_gate_entry(self) -> dict:
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_downstream_gate_entry.v1"
            ),
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_routed_next_gate_result_continuation_execute_result_review_ready",
            "status": "ready_for_manifested_routed_next_gate_result_continuation_execute_downstream_gate_entry",
            "verified_route_type": "pdf_export",
            "routed_next_gate": "formal_package_export_acceptance_router",
            "downstream_kind": "selected_route_execution",
            "downstream_status": "pending_explicit_selected_route_execution",
            "downstream_gate_entry_recorded": True,
            "can_request_manifested_routed_next_gate_result_continuation_downstream": True,
            "requires_explicit_downstream_command": True,
            "downstream_command_executed": False,
            "this_command_ran_downstream_command": False,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "downstream_input_records": [
                {
                    "record_id": (
                        "manifested_routed_continuation_execute_result_downstream::"
                        "formal_package_export_acceptance_router::pdf_export"
                    ),
                    "verified_route_type": "pdf_export",
                    "routed_next_gate": "formal_package_export_acceptance_router",
                    "downstream_kind": "selected_route_execution",
                    "downstream_command": "auto_mode_formal_package_next_gate_selected_route_execute",
                    "command_path": "Program/auto_mode_formal_package_next_gate_selected_route_execute.py",
                    "route_specific_next_command": "formal_pdf_export_execute",
                    "source_report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
                    "source_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
                    "next_report_path": "Results/json/auto_mode_formal_package_next_gate_selected_route_execute.json",
                    "next_review_path": "Reviews/auto_mode_formal_package_next_gate_selected_route_execute.md",
                    "downstream_status": "pending_explicit_selected_route_execution",
                    "planned_outputs": ["Submissions/formal_package/paper.pdf"],
                    "requires_explicit_downstream_command": True,
                    "terminal_completion": False,
                    "will_run_downstream_command_by_this_command": False,
                    "will_execute_selected_route_by_this_command": False,
                    "will_execute_export_or_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _ready_manual_gate_entry(self) -> dict:
        report = self._ready_export_gate_entry()
        report["verified_route_type"] = "manual_acceptance"
        report["routed_next_gate"] = "formal_package_delivery_completion_gate"
        report["downstream_kind"] = "product_review_preparation"
        report["downstream_status"] = "pending_product_review_preparation"
        report["requires_explicit_downstream_command"] = False
        report["downstream_input_records"] = [
            {
                "record_id": (
                    "manifested_routed_continuation_execute_result_downstream::"
                    "formal_package_delivery_completion_gate::manual_acceptance"
                ),
                "verified_route_type": "manual_acceptance",
                "routed_next_gate": "formal_package_delivery_completion_gate",
                "downstream_kind": "product_review_preparation",
                "downstream_command": "product_review_preparation",
                "command_path": "",
                "route_specific_next_command": "",
                "source_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
                "source_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
                "next_report_path": "Results/json/auto_mode_formal_package_product_review_preparation.json",
                "next_review_path": "Reviews/auto_mode_formal_package_product_review_preparation.md",
                "downstream_status": "pending_product_review_preparation",
                "terminal_status": "terminal_delivery_completion_ready_for_product_review",
                "planned_outputs": [],
                "requires_explicit_downstream_command": False,
                "terminal_completion": True,
                "will_run_downstream_command_by_this_command": False,
                "will_execute_selected_route_by_this_command": False,
                "will_execute_export_or_acceptance_by_this_command": False,
                "will_write_product_state_by_this_command": False,
            }
        ]
        return report

    def _blocked_gate_entry(self) -> dict:
        report = self._ready_export_gate_entry()
        report["source_status"] = "blocked_by_manifested_routed_next_gate_result_continuation_execute_gate"
        report["status"] = "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_review"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["downstream_kind"] = ""
        report["downstream_status"] = ""
        report["downstream_gate_entry_recorded"] = False
        report["can_request_manifested_routed_next_gate_result_continuation_downstream"] = False
        report["requires_explicit_downstream_command"] = False
        report["downstream_input_records"] = []
        report["blocking_reasons"] = [
            "manifested_routed_next_gate_result_continuation_execute_result_review_not_ready"
        ]
        return report

    def _selected_route_preflight(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execution_preflight.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
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
                    "route_execution_id": "selected_route::pdf_export",
                    "route_type": "pdf_export",
                    "routed_action": "formal_pdf_export_preflight",
                    "next_command": "formal_pdf_export_execute",
                    "planned_outputs": ["Submissions/formal_package/paper.pdf"],
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
            "entered_continuation_execute_result_downstream_gate": False,
        }


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate import (
    build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate,
    run_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate,
    write_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateExplicitRoutedNextGateEntryGateTests(unittest.TestCase):
    """BDD: P7-BB consumes P7-BA and gates explicit routed next-gate entry."""

    def test_bdd_p7bb_ready_review_with_confirmation_records_manifest_via_existing_execute(self) -> None:
        """行为 1：ready P7-BA + 显式确认才调用 existing execute 并记录 manifest。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report, exit_code = run_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
                project_root,
                self._ready_result_review("package_manifest"),
                mode="execute",
                confirm_entry=True,
                reviewer="unit_test_reviewer",
                note="Record explicit routed next gate entry.",
            )

            report_path, review_path = write_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate_outputs(
                project_root,
                report,
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(report["status"], "explicit_routed_next_gate_entry_manifest_recorded")
            self.assertTrue(report["explicit_routed_next_gate_entry_gate_executed"])
            self.assertEqual(report["explicit_routed_next_gate_entry_execute_status"], "routed_next_gate_entry_manifest_recorded")
            self.assertTrue(report["routed_next_gate_entry_manifest_recorded"])
            self.assertEqual(report["verified_route_type"], "package_manifest")
            self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertTrue((project_root / "Results/json/auto_mode_formal_package_routed_next_gate_entry_execute.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_package_routed_next_gate_entry_execute.md").exists())
            self.assertTrue(
                (
                    project_root
                    / "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
                ).exists()
            )
            self.assertFalse(report["next_gate_entered"])
            self.assertFalse(report["next_gate_command_executed"])
            self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bb_current_blocked_result_review_blocks_gate(self) -> None:
        """行为 2：当前 blocked P7-BA 必须继续阻断，不调用 execute。"""
        report = build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
            self._blocked_result_review(),
            mode="execute",
            confirm_entry=True,
            reviewer="unit_test_reviewer",
            note="Attempt entry.",
        )

        self.assertEqual(report["status"], "blocked_by_routed_next_gate_entry_preflight_entry_result_review")
        self.assertFalse(report["explicit_routed_next_gate_entry_gate_executed"])
        self.assertFalse(report["routed_next_gate_entry_manifest_recorded"])
        self.assertEqual(report["explicit_routed_next_gate_entry_operations"], [])
        self.assertIn("routed_next_gate_entry_preflight_entry_result_review_not_ready", report["blocking_reasons"])

    def test_bdd_p7bb_missing_invalid_or_unready_result_review_blocks_gate(self) -> None:
        """行为 3：P7-BA 缺失、schema 错或未 ready 都阻断。"""
        wrong_schema = self._ready_result_review("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._ready_result_review("package_manifest")
        not_ready["status"] = "blocked_by_routed_next_gate_entry_preflight_entry"
        cannot_continue = self._ready_result_review("package_manifest")
        cannot_continue["can_continue_to_explicit_routed_next_gate_entry"] = False

        reports = [
            build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(source)
            for source in [{}, wrong_schema, not_ready, cannot_continue]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_routed_next_gate_entry_preflight_entry_result_review" for report in reports)
        )
        self.assertIn("routed_next_gate_entry_preflight_entry_result_review_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_preflight_entry_result_review_missing_or_invalid_schema", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_preflight_entry_result_review_not_ready", reports[2]["blocking_reasons"])
        self.assertIn("result_review_cannot_continue_to_explicit_routed_next_gate_entry", reports[3]["blocking_reasons"])

    def test_bdd_p7bb_input_record_must_match_entry_plan(self) -> None:
        """行为 4：P7-BA input record 必须与 entry plan 匹配。"""
        missing_record = self._ready_result_review("package_manifest")
        missing_record["explicit_routed_next_gate_entry_input_records"] = []
        duplicated_record = self._ready_result_review("package_manifest")
        duplicated_record["explicit_routed_next_gate_entry_input_records"].append(
            dict(duplicated_record["explicit_routed_next_gate_entry_input_records"][0])
        )
        path_mismatch = self._ready_result_review("package_manifest")
        path_mismatch["explicit_routed_next_gate_entry_input_records"][0][
            "routed_next_gate_entry_preflight_report_path"
        ] = "Results/json/wrong.json"
        entry_id_mismatch = self._ready_result_review("package_manifest")
        entry_id_mismatch["explicit_routed_next_gate_entry_input_records"][0]["entry_ids"] = ["wrong"]

        reports = [
            build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(source)
            for source in [missing_record, duplicated_record, path_mismatch, entry_id_mismatch]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_explicit_routed_next_gate_entry_input_contract" for report in reports)
        )
        self.assertIn("explicit_routed_next_gate_entry_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("explicit_routed_next_gate_entry_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_preflight_report_path_mismatch:package_manifest", reports[2]["blocking_reasons"])
        self.assertIn("explicit_routed_next_gate_entry_input_record_entry_ids_mismatch:package_manifest", reports[3]["blocking_reasons"])

    def test_bdd_p7bb_execute_requires_explicit_confirmation_before_calling_execute(self) -> None:
        """行为 5：ready 但缺显式确认时不调用 execute。"""
        report = build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
            self._ready_result_review("package_manifest"),
            mode="execute",
            confirm_entry=False,
            reviewer="unit_test_reviewer",
            note="Record entry.",
        )

        self.assertEqual(report["status"], "blocked_by_missing_explicit_routed_next_gate_entry_confirmation")
        self.assertFalse(report["explicit_routed_next_gate_entry_gate_executed"])
        self.assertFalse(report["routed_next_gate_entry_manifest_recorded"])
        self.assertIn("confirm_entry_required", report["blocking_reasons"])

    def test_bdd_p7bb_execute_requires_reviewer_and_note_before_calling_execute(self) -> None:
        """行为 6：ready 且确认但缺 reviewer/note 时不调用 execute。"""
        report = build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
            self._ready_result_review("package_manifest"),
            mode="execute",
            confirm_entry=True,
            reviewer="",
            note="",
        )

        self.assertEqual(report["status"], "blocked_by_explicit_routed_next_gate_entry_metadata")
        self.assertFalse(report["explicit_routed_next_gate_entry_gate_executed"])
        self.assertFalse(report["routed_next_gate_entry_manifest_recorded"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("entry_note_required", report["blocking_reasons"])

    def test_bdd_p7bb_boundary_violations_block_gate(self) -> None:
        """行为 7：P7-BB 不能接受越界或副作用信号。"""
        source = self._ready_result_review("package_manifest")
        source["explicit_routed_next_gate_entry_executed"] = True
        source["this_command_entered_next_gate"] = True
        source["can_write_product_state"] = True
        source["boundary_flags"]["modified_product_state"] = True

        report = build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
            source,
            mode="execute",
            confirm_entry=True,
            reviewer="unit_test_reviewer",
            note="Attempt entry.",
        )

        self.assertEqual(report["status"], "blocked_by_explicit_routed_next_gate_entry_boundary")
        self.assertIn("result_review_already_executed_explicit_routed_next_gate_entry", report["blocking_reasons"])
        self.assertIn("result_review_entered_next_gate", report["blocking_reasons"])
        self.assertIn("result_review_allows_product_state_write", report["blocking_reasons"])
        self.assertIn("result_review_boundary_violation:modified_product_state", report["blocking_reasons"])

    def test_bdd_p7bb_cli_defaults_to_current_blocked_result_review(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-BA，写 blocked gate report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_review_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.json"
            )
            result_review_path.parent.mkdir(parents=True, exist_ok=True)
            result_review_path.write_text(json.dumps(self._blocked_result_review()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_routed_next_gate_entry_preflight_entry_result_review", result.stdout)
            self.assertIn("explicit_routed_next_gate_entry_gate_executed=false", result.stdout)
            self.assertIn("routed_next_gate_entry_manifest_recorded=false", result.stdout)
            self.assertIn("explicit_routed_next_gate_entry_operations=0", result.stdout)
            self.assertIn("next_gate_entered=false", result.stdout)
            self.assertIn("next_gate_command_executed=false", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
                ).exists()
            )

    def _ready_result_review(self, route_type: str) -> dict:
        gate_id = (
            "formal_package_delivery_completion_gate"
            if route_type == "manual_acceptance"
            else "formal_package_export_acceptance_router"
        )
        action = (
            "finalize_formal_package_delivery_review"
            if route_type == "manual_acceptance"
            else "continue_formal_package_export_acceptance_cycle"
        )
        next_command = (
            "auto_mode_formal_package_delivery_completion_gate"
            if route_type == "manual_acceptance"
            else "auto_mode_formal_package_export_acceptance_router"
        )
        entry_kind = "delivery_completion" if route_type == "manual_acceptance" else "continue_export_acceptance_cycle"
        entry_id = f"routed_next_gate_entry::{gate_id}::{route_type}"
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_routed_next_gate_entry_preflight_entered",
            "status": "routed_next_gate_entry_preflight_entry_result_review_ready",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "routed_next_gate_entry_preflight_status": "ready_for_routed_next_gate_entry_review",
            "routed_next_gate_entry_preflight_entry_result_reviewed": True,
            "can_continue_to_explicit_routed_next_gate_entry": True,
            "can_request_routed_next_gate_entry": True,
            "requires_explicit_next_gate_entry_command": True,
            "next_gate_entry_plan_count": 1,
            "next_gate_entry_plan": [
                {
                    "entry_id": entry_id,
                    "source_route_id": f"verified_route_next_gate::{route_type}",
                    "verified_route_type": route_type,
                    "gate_id": gate_id,
                    "entry_kind": entry_kind,
                    "next_gate_action": action,
                    "next_command": next_command,
                    "entry_status": "pending_explicit_next_gate_entry_command",
                    "requires_explicit_next_gate_entry_command": True,
                    "will_enter_next_gate_by_this_command": False,
                    "will_execute_export_or_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                    "handoff_summary": "Ready for explicit next gate entry.",
                }
            ],
            "explicit_routed_next_gate_entry_input_records": [
                {
                    "record_id": f"explicit_routed_next_gate_entry_input::{gate_id}::{route_type}",
                    "verified_route_type": route_type,
                    "routed_next_gate": gate_id,
                    "routed_next_gate_entry_preflight_status": "ready_for_routed_next_gate_entry_review",
                    "routed_next_gate_entry_preflight_report_path": (
                        "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json"
                    ),
                    "routed_next_gate_entry_preflight_review_path": (
                        "Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md"
                    ),
                    "next_gate_entry_plan_count": 1,
                    "entry_ids": [entry_id],
                    "review_status": "routed_next_gate_entry_preflight_accepted_for_explicit_entry_gate",
                    "can_continue_to_explicit_routed_next_gate_entry": True,
                }
            ],
            "explicit_routed_next_gate_entry_executed": False,
            "next_gate_entered": False,
            "this_command_entered_next_gate": False,
            "next_gate_command_executed": False,
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

    def _blocked_result_review(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.v1",
            "status": "blocked_by_routed_next_gate_entry_preflight_entry",
            "can_continue_to_explicit_routed_next_gate_entry": False,
            "explicit_routed_next_gate_entry_input_records": [],
            "next_gate_entry_plan": [],
            "blocking_reasons": ["routed_next_gate_entry_preflight_entry_not_entered"],
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
            "ran_routed_next_gate_entry_preflight": False,
            "entered_explicit_routed_next_gate_entry": False,
        }


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight import (
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateRunPreflightTests(unittest.TestCase):
    """BDD: P7-BC consumes P7-BB and an entry manifest before exposing a run preflight."""

    def test_bdd_p7bc_ready_gate_and_manifest_create_run_preflight_without_running_command(self) -> None:
        """行为 1：P7-BB 已记录 manifest 时，P7-BC 只生成下一关运行预检。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
            self._ready_gate("pdf_export"),
            self._entry_manifest("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.v1",
        )
        self.assertEqual(report["status"], "ready_for_manifested_routed_next_gate_run_preflight")
        self.assertTrue(report["manifested_routed_next_gate_run_preflight_reviewed"])
        self.assertTrue(report["can_request_manifested_next_gate_command_execution"])
        self.assertTrue(report["requires_explicit_next_gate_command_execute"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(len(report["next_gate_command_call_plan"]), 1)
        self.assertEqual(report["next_gate_command_call_plan_count"], 1)
        self.assertEqual(len(report["manifested_routed_next_gate_run_input_records"]), 1)
        input_record = report["manifested_routed_next_gate_run_input_records"][0]
        self.assertEqual(
            input_record["record_id"],
            "manifested_routed_next_gate_run_input::formal_package_export_acceptance_router::pdf_export",
        )
        self.assertEqual(input_record["next_command"], "auto_mode_formal_package_export_acceptance_router")
        self.assertFalse(report["next_gate_command_executed"])
        self.assertFalse(report["this_command_ran_next_gate_command"])
        self.assertFalse(report["next_gate_entered"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bc_current_blocked_gate_blocks_run_preflight(self) -> None:
        """行为 2：当前 blocked P7-BB 不能生成 manifested run preflight。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
            self._blocked_gate(),
            {},
        )

        self.assertEqual(report["status"], "blocked_by_explicit_routed_next_gate_entry_gate")
        self.assertFalse(report["manifested_routed_next_gate_run_preflight_reviewed"])
        self.assertFalse(report["can_request_manifested_next_gate_command_execution"])
        self.assertFalse(report["requires_explicit_next_gate_command_execute"])
        self.assertEqual(report["next_gate_command_call_plan"], [])
        self.assertEqual(report["manifested_routed_next_gate_run_input_records"], [])
        self.assertIn("explicit_routed_next_gate_entry_gate_not_manifest_recorded", report["blocking_reasons"])

    def test_bdd_p7bc_missing_invalid_or_unrecorded_gate_blocks_preflight(self) -> None:
        """行为 3：P7-BB 缺失、schema 错或未真实记录 manifest 都阻断。"""
        wrong_schema = self._ready_gate("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_recorded = self._ready_gate("pdf_export")
        not_recorded["status"] = "ready_to_execute_explicit_routed_next_gate_entry"
        not_recorded["routed_next_gate_entry_manifest_recorded"] = False
        not_executed = self._ready_gate("pdf_export")
        not_executed["explicit_routed_next_gate_entry_gate_executed"] = False

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(source, {})
            for source in [{}, wrong_schema, not_recorded, not_executed]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_explicit_routed_next_gate_entry_gate" for report in reports)
        )
        self.assertIn("explicit_routed_next_gate_entry_gate_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("explicit_routed_next_gate_entry_gate_missing_or_invalid_schema", reports[1]["blocking_reasons"])
        self.assertIn("explicit_routed_next_gate_entry_gate_not_manifest_recorded", reports[2]["blocking_reasons"])
        self.assertIn("explicit_routed_next_gate_entry_gate_not_executed", reports[3]["blocking_reasons"])

    def test_bdd_p7bc_gate_and_manifest_must_match(self) -> None:
        """行为 4：P7-BB 与 manifest 的 route、gate、path、operation 数必须一致。"""
        route_mismatch = self._entry_manifest("docx_export")
        gate_mismatch = self._entry_manifest("pdf_export")
        gate_mismatch["routed_next_gate"] = "formal_package_delivery_completion_gate"
        path_mismatch_gate = self._ready_gate("pdf_export")
        path_mismatch_gate["routed_next_gate_entry_manifest_path"] = "workspace/wrong/manifest.json"
        operation_mismatch_gate = self._ready_gate("pdf_export")
        operation_mismatch_gate["explicit_routed_next_gate_entry_operations"].append(
            dict(operation_mismatch_gate["explicit_routed_next_gate_entry_operations"][0])
        )

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
                self._ready_gate("pdf_export"),
                route_mismatch,
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
                self._ready_gate("pdf_export"),
                gate_mismatch,
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
                path_mismatch_gate,
                self._entry_manifest("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
                operation_mismatch_gate,
                self._entry_manifest("pdf_export"),
            ),
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_run_contract" for report in reports)
        )
        self.assertIn("gate_manifest_route_type_mismatch:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("gate_manifest_routed_next_gate_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_manifest_path_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("gate_manifest_operation_count_mismatch:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7bc_missing_invalid_or_unmanifested_manifest_blocks_preflight(self) -> None:
        """行为 5：manifest 缺失、schema 错或未 manifested 时阻断。"""
        wrong_schema = self._entry_manifest("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        unmanifested = self._entry_manifest("pdf_export")
        unmanifested["next_gate_entry_manifested"] = False

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
                self._ready_gate("pdf_export"),
                source,
            )
            for source in [{}, wrong_schema, unmanifested]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_routed_next_gate_entry_manifest" for report in reports))
        self.assertIn("routed_next_gate_entry_manifest_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_manifest_missing_or_invalid_schema", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_not_manifested", reports[2]["blocking_reasons"])

    def test_bdd_p7bc_manifest_boundary_violations_block_preflight(self) -> None:
        """行为 6：manifest 出现已运行、已进入或写回信号时阻断。"""
        entered = self._entry_manifest("pdf_export")
        entered["next_gate_entered"] = True
        ran = self._entry_manifest("pdf_export")
        ran["next_gate_command_executed"] = True
        boundary = self._entry_manifest("pdf_export")
        boundary["boundary_flags"]["ran_next_gate_command"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
                self._ready_gate("pdf_export"),
                source,
            )
            for source in [entered, ran, boundary]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_run_boundary" for report in reports)
        )
        self.assertIn("routed_next_gate_entry_manifest_entered_next_gate", reports[0]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_manifest_ran_next_gate_command", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_manifest_boundary_violation:ran_next_gate_command", reports[2]["blocking_reasons"])

    def test_bdd_p7bc_manifest_operation_contract_must_be_clean(self) -> None:
        """行为 7：manifest operation 缺失、重复、未知或已标记运行都阻断。"""
        missing_operation = self._entry_manifest("pdf_export")
        missing_operation["routed_next_gate_entry_operations"] = []
        duplicated = self._entry_manifest("pdf_export")
        duplicated["routed_next_gate_entry_operations"].append(dict(duplicated["routed_next_gate_entry_operations"][0]))
        unknown_gate = self._entry_manifest("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        unknown_gate["routed_next_gate_entry_operations"][0]["gate_id"] = "unknown_gate"
        marked_run = self._entry_manifest("pdf_export")
        marked_run["routed_next_gate_entry_operations"][0]["will_run_next_gate_command"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
                self._ready_gate("pdf_export"),
                source,
            )
            for source in [missing_operation, duplicated, unknown_gate, marked_run]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_run_contract" for report in reports)
        )
        self.assertIn("routed_next_gate_entry_operations_missing", reports[0]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_operations_not_single", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_unknown:unknown_gate", reports[2]["blocking_reasons"])
        self.assertIn("next_gate_command_operation_marked_run_command:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7bc_cli_defaults_to_current_blocked_gate_and_writes_report_only(self) -> None:
        """行为 8：CLI 默认当前 blocked P7-BB，只写 blocked report/review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            gate_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.json"
            )
            gate_path.parent.mkdir(parents=True, exist_ok=True)
            gate_path.write_text(json.dumps(self._blocked_gate()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_explicit_routed_next_gate_entry_gate", result.stdout)
            self.assertIn("can_request_manifested_next_gate_command_execution=false", result.stdout)
            self.assertIn("next_gate_command_call_plan=0", result.stdout)
            self.assertIn("manifested_routed_next_gate_run_input_records=0", result.stdout)
            self.assertIn("next_gate_command_executed=false", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.md"
                ).exists()
            )
            self.assertFalse((project_root / "workspace/formal_package_routed_next_gate_command").exists())
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.json"
                ).exists()
            )

    def _ready_gate(self, route_type: str) -> dict:
        gate_id, action, next_command, entry_kind = self._entry_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "routed_next_gate_entry_preflight_entry_result_review_ready",
            "status": "explicit_routed_next_gate_entry_manifest_recorded",
            "mode": "execute",
            "confirm_entry": True,
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "can_execute_explicit_routed_next_gate_entry": True,
            "explicit_routed_next_gate_entry_gate_executed": True,
            "explicit_routed_next_gate_entry_execute_status": "routed_next_gate_entry_manifest_recorded",
            "explicit_routed_next_gate_entry_execute_report_path": (
                "Results/json/auto_mode_formal_package_routed_next_gate_entry_execute.json"
            ),
            "explicit_routed_next_gate_entry_execute_review_path": (
                "Reviews/auto_mode_formal_package_routed_next_gate_entry_execute.md"
            ),
            "explicit_routed_next_gate_entry_execute_written_paths": {
                "report": "Results/json/auto_mode_formal_package_routed_next_gate_entry_execute.json",
                "review": "Reviews/auto_mode_formal_package_routed_next_gate_entry_execute.md",
                "manifest": (
                    "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
                ),
            },
            "routed_next_gate_entry_manifest_recorded": True,
            "routed_next_gate_entry_manifest_path": (
                "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
            ),
            "explicit_routed_next_gate_entry_operations": [
                {
                    "operation_id": f"routed_next_gate_entry_execute::{gate_id}::{route_type}",
                    "entry_id": f"routed_next_gate_entry::{gate_id}::{route_type}",
                    "verified_route_type": route_type,
                    "gate_id": gate_id,
                    "entry_kind": entry_kind,
                    "next_gate_action": action,
                    "next_command": next_command,
                    "operation_status": "planned_not_entered",
                    "will_enter_next_gate": False,
                    "will_run_next_gate_command": False,
                    "will_execute_export_or_acceptance": False,
                    "will_write_product_state": False,
                }
            ],
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

    def _blocked_gate(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "status": "blocked_by_routed_next_gate_entry_preflight_entry_result_review",
            "can_execute_explicit_routed_next_gate_entry": False,
            "explicit_routed_next_gate_entry_gate_executed": False,
            "explicit_routed_next_gate_entry_execute_status": "",
            "routed_next_gate_entry_manifest_recorded": False,
            "routed_next_gate_entry_manifest_path": "",
            "explicit_routed_next_gate_entry_operations": [],
            "next_gate_entered": False,
            "this_command_entered_next_gate": False,
            "next_gate_command_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": ["routed_next_gate_entry_preflight_entry_result_review_not_ready"],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _entry_manifest(self, route_type: str) -> dict:
        gate_id, action, next_command, entry_kind = self._entry_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_routed_next_gate_entry_manifest.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_execute_report": "Results/json/auto_mode_formal_package_routed_next_gate_entry_execute.json",
            "manifest_path": "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json",
            "reviewer": "unit_test_reviewer",
            "note": "Record next gate entry manifest.",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "next_gate_entry_manifested": True,
            "next_gate_entered": False,
            "this_command_entered_next_gate": False,
            "next_gate_command_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "routed_next_gate_entry_operations": [
                {
                    "operation_id": f"routed_next_gate_entry_execute::{gate_id}::{route_type}",
                    "entry_id": f"routed_next_gate_entry::{gate_id}::{route_type}",
                    "source_route_id": f"verified_route_next_gate::{route_type}",
                    "verified_route_type": route_type,
                    "gate_id": gate_id,
                    "entry_kind": entry_kind,
                    "next_gate_action": action,
                    "next_command": next_command,
                    "operation_status": "planned_not_entered",
                    "will_record_entry_manifest_on_confirm": True,
                    "will_enter_next_gate": False,
                    "will_run_next_gate_command": False,
                    "will_execute_export_or_acceptance": False,
                    "will_write_product_state": False,
                    "handoff_summary": "Ready for command preflight.",
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _entry_mapping(self, route_type: str) -> tuple[str, str, str, str]:
        if route_type == "manual_acceptance":
            return (
                "formal_package_delivery_completion_gate",
                "finalize_formal_package_delivery_review",
                "auto_mode_formal_package_delivery_completion_gate",
                "delivery_completion",
            )
        return (
            "formal_package_export_acceptance_router",
            "continue_formal_package_export_acceptance_cycle",
            "auto_mode_formal_package_export_acceptance_router",
            "continue_export_acceptance_cycle",
        )

    def _source_paths(self) -> dict:
        return {
            "explicit_routed_next_gate_entry_gate": (
                "Results/json/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.json"
            ),
            "routed_next_gate_entry_manifest": (
                "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
            ),
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
            "entered_explicit_routed_next_gate_entry": False,
        }


if __name__ == "__main__":
    unittest.main()

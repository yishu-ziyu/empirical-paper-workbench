import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_manifested_routed_next_gate_command_preflight import (
    build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight,
    write_auto_mode_formal_package_manifested_routed_next_gate_command_preflight_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageManifestedRoutedNextGateCommandPreflightTests(unittest.TestCase):
    """BDD: P7-AH prepares a command call from a manifested next-gate entry."""

    def test_bdd_p7ah_ready_pdf_entry_manifest_creates_command_plan_without_running_it(self) -> None:
        """行为 1：PDF entry manifest 生成下一关命令计划，但不运行命令。"""
        report = build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(
            self._entry_manifest("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_manifested_routed_next_gate_command_preflight.v1",
        )
        self.assertEqual(report["status"], "ready_for_manifested_routed_next_gate_command_review")
        self.assertTrue(report["can_request_manifested_next_gate_command_execution"])
        self.assertTrue(report["requires_explicit_next_gate_command_execute"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(len(report["next_gate_command_call_plan"]), 1)
        plan = report["next_gate_command_call_plan"][0]
        self.assertEqual(plan["next_command"], "auto_mode_formal_package_export_acceptance_router")
        self.assertEqual(plan["command_path"], "Program/auto_mode_formal_package_export_acceptance_router.py")
        self.assertEqual(plan["command_status"], "pending_explicit_next_gate_command_execute")
        self.assertFalse(report["next_gate_command_executed"])
        self.assertFalse(report["this_command_ran_next_gate_command"])
        self.assertFalse(report["next_gate_entered"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ah_current_missing_manifest_blocks_command_preflight(self) -> None:
        """行为 2：当前无 P7-AG manifest 时不能生成下一关命令计划。"""
        report = build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight({})

        self.assertEqual(report["status"], "blocked_by_routed_next_gate_entry_manifest")
        self.assertFalse(report["can_request_manifested_next_gate_command_execution"])
        self.assertFalse(report["requires_explicit_next_gate_command_execute"])
        self.assertEqual(report["next_gate_command_call_plan"], [])
        self.assertIn("routed_next_gate_entry_manifest_missing_or_invalid_schema", report["blocking_reasons"])

    def test_bdd_p7ah_missing_invalid_or_unmanifested_entry_manifest_blocks_preflight(self) -> None:
        """行为 3：manifest 缺失、schema 错误或未 manifested 时阻断。"""
        missing = build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight({})
        wrong_schema_source = self._entry_manifest("pdf_export")
        wrong_schema_source["schema_version"] = "wrong.schema"
        unmanifested_source = self._entry_manifest("pdf_export")
        unmanifested_source["next_gate_entry_manifested"] = False

        wrong_schema = build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(
            wrong_schema_source
        )
        unmanifested = build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(
            unmanifested_source
        )

        self.assertEqual(missing["status"], "blocked_by_routed_next_gate_entry_manifest")
        self.assertEqual(wrong_schema["status"], "blocked_by_routed_next_gate_entry_manifest")
        self.assertIn("routed_next_gate_entry_manifest_missing_or_invalid_schema", wrong_schema["blocking_reasons"])
        self.assertEqual(unmanifested["status"], "blocked_by_routed_next_gate_entry_manifest")
        self.assertIn("routed_next_gate_entry_not_manifested", unmanifested["blocking_reasons"])

    def test_bdd_p7ah_entry_manifest_boundary_violations_block_preflight(self) -> None:
        """行为 4：manifest 带已进入、已运行命令、写回或边界越界信号时阻断。"""
        entered = self._entry_manifest("pdf_export")
        entered["next_gate_entered"] = True
        ran = self._entry_manifest("pdf_export")
        ran["next_gate_command_executed"] = True
        product = self._entry_manifest("pdf_export")
        product["can_write_product_state"] = True
        boundary = self._entry_manifest("pdf_export")
        boundary["boundary_flags"]["ran_next_gate_command"] = True

        reports = [
            build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(source)
            for source in [entered, ran, product, boundary]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_command_boundary" for report in reports)
        )
        self.assertIn("routed_next_gate_entry_manifest_entered_next_gate", reports[0]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_manifest_ran_next_gate_command", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_manifest_allows_product_state_write", reports[2]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_manifest_boundary_violation:ran_next_gate_command", reports[3]["blocking_reasons"])

    def test_bdd_p7ah_entry_operation_contract_must_be_clean(self) -> None:
        """行为 5：entry operation 缺失、重复、未知或不干净时阻断。"""
        missing_operation = self._entry_manifest("pdf_export")
        missing_operation["routed_next_gate_entry_operations"] = []
        duplicated = self._entry_manifest("pdf_export")
        duplicated["routed_next_gate_entry_operations"].append(dict(duplicated["routed_next_gate_entry_operations"][0]))
        unknown_gate = self._entry_manifest("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        unknown_gate["routed_next_gate_entry_operations"][0]["gate_id"] = "unknown_gate"
        marked_run = self._entry_manifest("pdf_export")
        marked_run["routed_next_gate_entry_operations"][0]["will_run_next_gate_command"] = True
        no_command = self._entry_manifest("pdf_export")
        no_command["routed_next_gate_entry_operations"][0]["next_command"] = ""

        reports = [
            build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(source)
            for source in [missing_operation, duplicated, unknown_gate, marked_run, no_command]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_manifested_routed_next_gate_command_contract"
                for report in reports
            )
        )
        self.assertIn("routed_next_gate_entry_operations_missing", reports[0]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_operations_not_single", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_unknown:unknown_gate", reports[2]["blocking_reasons"])
        self.assertIn("next_gate_command_operation_marked_run_command:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("next_gate_command_missing:pdf_export", reports[4]["blocking_reasons"])

    def test_bdd_p7ah_manual_acceptance_entry_creates_delivery_completion_command_plan(self) -> None:
        """行为 6：manual acceptance entry 生成交付完成门命令计划。"""
        report = build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(
            self._entry_manifest("manual_acceptance")
        )

        self.assertEqual(report["status"], "ready_for_manifested_routed_next_gate_command_review")
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["routed_next_gate"], "formal_package_delivery_completion_gate")
        self.assertEqual(
            report["next_gate_command_call_plan"][0]["next_command"],
            "auto_mode_formal_package_delivery_completion_gate",
        )
        self.assertEqual(
            report["next_gate_command_call_plan"][0]["command_path"],
            "Program/auto_mode_formal_package_delivery_completion_gate.py",
        )
        self.assertFalse(report["next_gate_command_executed"])

    def test_bdd_p7ah_writes_report_and_review_only(self) -> None:
        """行为 7：只写 command preflight report/review，不运行命令、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(
                self._entry_manifest("docx_export")
            )
            report_path, review_path = (
                write_auto_mode_formal_package_manifested_routed_next_gate_command_preflight_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "ready_for_manifested_routed_next_gate_command_review")
            self.assertEqual(
                written["next_gate_command_call_plan"][0]["next_command"],
                "auto_mode_formal_package_export_acceptance_router",
            )
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json").exists())
            self.assertFalse((project_root / "workspace/formal_package_routed_next_gate_command").exists())
            self.assertFalse(written["next_gate_command_executed"])

    def test_bdd_p7ah_cli_defaults_to_current_missing_manifest(self) -> None:
        """行为 8：CLI 默认读取当前缺失 P7-AG manifest，写 blocked preflight report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_routed_next_gate_entry_manifest", result.stdout)
            self.assertIn("can_request_manifested_next_gate_command_execution=false", result.stdout)
            self.assertIn("next_gate_command_call_plan=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json"
                ).exists()
            )

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
            "routed_next_gate_entry_manifest": (
                "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
            ),
        }

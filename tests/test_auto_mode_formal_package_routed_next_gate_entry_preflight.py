import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_routed_next_gate_entry_preflight import (
    build_auto_mode_formal_package_routed_next_gate_entry_preflight,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageRoutedNextGateEntryPreflightTests(unittest.TestCase):
    """BDD: P7-AF prepares P7-AE routed next-gate entry without entering it."""

    def test_bdd_p7af_ready_pdf_route_creates_entry_preflight_without_entering_gate(self) -> None:
        """行为 1：PDF 下一关路由生成进入预检计划，但不进入下一关。"""
        report = build_auto_mode_formal_package_routed_next_gate_entry_preflight(
            self._ready_router("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_routed_next_gate_entry_preflight.v1",
        )
        self.assertEqual(report["status"], "ready_for_routed_next_gate_entry_review")
        self.assertTrue(report["can_request_routed_next_gate_entry"])
        self.assertTrue(report["requires_explicit_next_gate_entry_command"])
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(len(report["next_gate_entry_plan"]), 1)
        plan_item = report["next_gate_entry_plan"][0]
        self.assertEqual(plan_item["verified_route_type"], "pdf_export")
        self.assertEqual(plan_item["gate_id"], "formal_package_export_acceptance_router")
        self.assertEqual(plan_item["next_gate_action"], "continue_formal_package_export_acceptance_cycle")
        self.assertEqual(plan_item["next_command"], "auto_mode_formal_package_export_acceptance_router")
        self.assertFalse(report["next_gate_entered"])
        self.assertFalse(report["this_command_entered_next_gate"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7af_current_blocked_router_blocks_entry_preflight(self) -> None:
        """行为 2：当前 P7-AE blocked 时不能生成下一关进入计划。"""
        report = build_auto_mode_formal_package_routed_next_gate_entry_preflight(self._blocked_router())

        self.assertEqual(report["status"], "blocked_by_verified_route_next_gate_router")
        self.assertFalse(report["can_request_routed_next_gate_entry"])
        self.assertFalse(report["requires_explicit_next_gate_entry_command"])
        self.assertEqual(report["routed_next_gate"], "")
        self.assertEqual(report["next_gate_entry_plan"], [])
        self.assertIn("verified_route_next_gate_router_not_route_recorded", report["blocking_reasons"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7af_missing_invalid_or_unrecorded_router_blocks_entry_preflight(self) -> None:
        """行为 3：router 缺失、schema 错误或未 route-recorded 时阻断。"""
        missing = build_auto_mode_formal_package_routed_next_gate_entry_preflight({})
        wrong_schema_source = self._ready_router("pdf_export")
        wrong_schema_source["schema_version"] = "wrong.schema"
        wrong_status_source = self._ready_router("pdf_export")
        wrong_status_source["status"] = "blocked_by_verified_route_completion_ledger"

        wrong_schema = build_auto_mode_formal_package_routed_next_gate_entry_preflight(wrong_schema_source)
        wrong_status = build_auto_mode_formal_package_routed_next_gate_entry_preflight(wrong_status_source)

        self.assertEqual(missing["status"], "blocked_by_verified_route_next_gate_router")
        self.assertIn("verified_route_next_gate_router_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(wrong_schema["status"], "blocked_by_verified_route_next_gate_router")
        self.assertIn("verified_route_next_gate_router_missing_or_invalid_schema", wrong_schema["blocking_reasons"])
        self.assertEqual(wrong_status["status"], "blocked_by_verified_route_next_gate_router")
        self.assertIn("verified_route_next_gate_router_not_route_recorded", wrong_status["blocking_reasons"])

    def test_bdd_p7af_next_gate_route_contract_must_be_clean(self) -> None:
        """行为 4：next gate route 缺失、不匹配、不 pending 或不要求显式命令时阻断。"""
        missing_route = self._ready_router("pdf_export")
        missing_route["next_gate_route"] = {}
        mismatch = self._ready_router("pdf_export")
        mismatch["next_gate_route"]["route_type"] = "docx_export"
        not_pending = self._ready_router("pdf_export")
        not_pending["next_gate_route"]["routing_status"] = "entered"
        no_explicit_command = self._ready_router("pdf_export")
        no_explicit_command["next_gate_route"]["requires_explicit_next_gate_command"] = False

        reports = [
            build_auto_mode_formal_package_routed_next_gate_entry_preflight(source)
            for source in [missing_route, mismatch, not_pending, no_explicit_command]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_routed_next_gate_entry_contract" for report in reports)
        )
        self.assertIn("next_gate_route_missing", reports[0]["blocking_reasons"])
        self.assertIn("next_gate_route_type_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("next_gate_route_not_pending:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("next_gate_route_missing_explicit_command_requirement:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7af_unknown_or_mismatched_next_gate_blocks_entry_preflight(self) -> None:
        """行为 5：未知下一关或 gate/action 不匹配时阻断。"""
        unknown_gate = self._ready_router("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        unknown_gate["next_gate_route"]["gate_id"] = "unknown_gate"
        action_mismatch = self._ready_router("pdf_export")
        action_mismatch["next_gate_route"]["next_gate_action"] = "finalize_formal_package_delivery_review"
        gate_mismatch = self._ready_router("pdf_export")
        gate_mismatch["next_gate_route"]["gate_id"] = "formal_package_delivery_completion_gate"

        unknown_report = build_auto_mode_formal_package_routed_next_gate_entry_preflight(unknown_gate)
        action_report = build_auto_mode_formal_package_routed_next_gate_entry_preflight(action_mismatch)
        gate_report = build_auto_mode_formal_package_routed_next_gate_entry_preflight(gate_mismatch)

        self.assertEqual(unknown_report["status"], "blocked_by_routed_next_gate_entry_contract")
        self.assertIn("routed_next_gate_unknown:unknown_gate", unknown_report["blocking_reasons"])
        self.assertEqual(action_report["status"], "blocked_by_routed_next_gate_entry_contract")
        self.assertIn(
            "next_gate_action_not_allowed:formal_package_export_acceptance_router",
            action_report["blocking_reasons"],
        )
        self.assertEqual(gate_report["status"], "blocked_by_routed_next_gate_entry_contract")
        self.assertIn("next_gate_route_gate_mismatch:formal_package_export_acceptance_router", gate_report["blocking_reasons"])

    def test_bdd_p7af_manual_acceptance_route_creates_delivery_completion_entry_plan(self) -> None:
        """行为 6：manual acceptance 路由准备进入交付完成门。"""
        report = build_auto_mode_formal_package_routed_next_gate_entry_preflight(
            self._ready_router("manual_acceptance")
        )

        self.assertEqual(report["status"], "ready_for_routed_next_gate_entry_review")
        self.assertEqual(report["routed_next_gate"], "formal_package_delivery_completion_gate")
        self.assertEqual(report["next_gate_entry_plan"][0]["next_gate_action"], "finalize_formal_package_delivery_review")
        self.assertEqual(report["next_gate_entry_plan"][0]["next_command"], "auto_mode_formal_package_delivery_completion_gate")
        self.assertFalse(report["this_command_entered_next_gate"])

    def test_bdd_p7af_boundary_violations_block_entry_preflight(self) -> None:
        """行为 7：P7-AE 带进入下一关、执行、写回或边界越界信号时阻断。"""
        entered = self._ready_router("pdf_export")
        entered["this_command_entered_next_gate"] = True
        executed = self._ready_router("pdf_export")
        executed["export_or_acceptance_executed"] = True
        product = self._ready_router("pdf_export")
        product["can_write_product_state"] = True
        boundary = self._ready_router("pdf_export")
        boundary["boundary_flags"]["entered_next_gate"] = True

        reports = [
            build_auto_mode_formal_package_routed_next_gate_entry_preflight(source)
            for source in [entered, executed, product, boundary]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_routed_next_gate_entry_boundary" for report in reports))
        self.assertIn("verified_route_next_gate_router_entered_next_gate", reports[0]["blocking_reasons"])
        self.assertIn("verified_route_next_gate_router_executed_export_or_acceptance", reports[1]["blocking_reasons"])
        self.assertIn("verified_route_next_gate_router_allows_product_state_write", reports[2]["blocking_reasons"])
        self.assertIn("verified_route_next_gate_router_boundary_violation:entered_next_gate", reports[3]["blocking_reasons"])

    def test_bdd_p7af_cli_defaults_to_current_blocked_router(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AE，写 blocked preflight report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json",
                self._blocked_router(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_routed_next_gate_entry_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_verified_route_next_gate_router", result.stdout)
            self.assertIn("can_request_routed_next_gate_entry=false", result.stdout)
            self.assertIn("next_gate_entry_plan=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_routed_next_gate_entry_preflight.json"
                ).exists()
            )

    def _ready_router(self, route_type: str) -> dict:
        gate_id, action, description = self._gate_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_verified_route_next_gate_router.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "verified_route_completion_ledger_recorded",
            "status": "verified_route_next_gate_route_recorded",
            "verified_route_type": route_type,
            "next_gate_route_recorded": True,
            "can_enter_routed_next_gate": True,
            "routed_next_gate": gate_id,
            "next_gate_route": {
                "route_id": f"verified_route_next_gate::{route_type}",
                "route_type": route_type,
                "gate_id": gate_id,
                "next_gate_action": action,
                "routing_status": "pending_next_auto_mode_gate",
                "requires_explicit_next_gate_command": True,
                "this_command_entered_next_gate": False,
                "description": description,
            },
            "route_completion_records_count": 1,
            "route_completion_ledger_recorded": True,
            "can_enter_next_auto_mode_gate": True,
            "export_or_acceptance_executed": False,
            "this_command_entered_next_gate": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "source_ledger": {"status": "verified_route_completion_ledger_recorded"},
            "route_completion_records": [{"route_type": route_type}],
            "boundary_flags": self._clean_boundary_flags(),
            "next_action": {"id": gate_id},
        }

    def _blocked_router(self) -> dict:
        router = self._ready_router("pdf_export")
        router["source_status"] = "blocked_by_route_specific_artifact_verification"
        router["status"] = "blocked_by_verified_route_completion_ledger"
        router["verified_route_type"] = ""
        router["next_gate_route_recorded"] = False
        router["can_enter_routed_next_gate"] = False
        router["routed_next_gate"] = ""
        router["next_gate_route"] = {}
        router["route_completion_records_count"] = 0
        router["route_completion_ledger_recorded"] = False
        router["can_enter_next_auto_mode_gate"] = False
        router["blocking_reasons"] = ["verified_route_completion_ledger_not_recorded"]
        router["route_completion_records"] = []
        return router

    def _gate_mapping(self, route_type: str) -> tuple[str, str, str]:
        if route_type == "manual_acceptance":
            return (
                "formal_package_delivery_completion_gate",
                "finalize_formal_package_delivery_review",
                "Manual acceptance completion is verified; enter delivery completion.",
            )
        return (
            "formal_package_export_acceptance_router",
            "continue_formal_package_export_acceptance_cycle",
            "Route completion is verified; choose the next export or acceptance route.",
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
        }

    def _source_paths(self) -> dict:
        return {
            "verified_route_next_gate_router": (
                "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json"
            )
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_selected_route_execution_preflight import (
    build_auto_mode_formal_package_selected_route_execution_preflight,
    write_auto_mode_formal_package_selected_route_execution_preflight_outputs,
)


class AutoModeFormalPackageSelectedRouteExecutionPreflightTests(unittest.TestCase):
    """BDD: P7-Z prepares one selected P7-Y route without executing it."""

    def test_bdd_p7z_pdf_route_creates_execution_preflight_without_export(self) -> None:
        """行为 1：PDF 路由生成执行预检计划，但不导出。"""
        report = build_auto_mode_formal_package_selected_route_execution_preflight(
            self._ready_router("formal_pdf_export_preflight"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_selected_route_execution_preflight.v1",
        )
        self.assertEqual(report["status"], "ready_for_selected_formal_package_route_execution_review")
        self.assertTrue(report["can_request_selected_route_execution"])
        self.assertTrue(report["requires_explicit_route_execute_command"])
        self.assertEqual(len(report["selected_route_execution_plan"]), 1)
        self.assertEqual(report["selected_route_execution_plan"][0]["route_type"], "pdf_export")
        self.assertEqual(report["selected_route_execution_plan"][0]["planned_outputs"], ["Submissions/formal_package/paper.pdf"])
        self.assertFalse(report["selected_route_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["rendered_pdf"])
        self.assertFalse(report["rendered_docx"])
        self.assertFalse(report["package_manifest_generated"])
        self.assertFalse(report["manual_acceptance_performed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7z_maps_docx_package_and_manual_routes(self) -> None:
        """行为 2：DOCX、package manifest、manual acceptance 路线分流到对应预检。"""
        expectations = {
            "formal_docx_export_preflight": ("docx_export", ["Submissions/formal_package/paper.docx"]),
            "formal_submission_package_manifest_preflight": ("package_manifest", ["Submissions/formal_package/manifest.json"]),
            "manual_acceptance_packet_preflight": ("manual_acceptance", ["Reviews/formal_package_manual_acceptance.md"]),
        }

        for routed_action, (route_type, planned_outputs) in expectations.items():
            with self.subTest(routed_action=routed_action):
                report = build_auto_mode_formal_package_selected_route_execution_preflight(
                    self._ready_router(routed_action),
                )

                self.assertEqual(report["status"], "ready_for_selected_formal_package_route_execution_review")
                self.assertEqual(report["selected_route_execution_plan"][0]["routed_action"], routed_action)
                self.assertEqual(report["selected_route_execution_plan"][0]["route_type"], route_type)
                self.assertEqual(report["selected_route_execution_plan"][0]["planned_outputs"], planned_outputs)

    def test_bdd_p7z_current_blocked_router_blocks_preflight(self) -> None:
        """行为 3：当前 P7-Y blocked 时不能生成执行预检。"""
        report = build_auto_mode_formal_package_selected_route_execution_preflight(
            self._blocked_router(),
        )

        self.assertEqual(report["status"], "blocked_by_export_acceptance_router")
        self.assertFalse(report["can_request_selected_route_execution"])
        self.assertFalse(report["requires_explicit_route_execute_command"])
        self.assertEqual(report["selected_route_execution_plan"], [])
        self.assertIn("export_acceptance_router_not_route_recorded", report["blocking_reasons"])

    def test_bdd_p7z_missing_invalid_or_unrecorded_router_blocks_preflight(self) -> None:
        """行为 4：router 缺失、schema 错误或未 route-recorded 时阻断。"""
        missing = build_auto_mode_formal_package_selected_route_execution_preflight({})
        invalid = self._ready_router("formal_pdf_export_preflight")
        invalid["schema_version"] = "wrong.schema"
        unrecorded = self._ready_router("formal_pdf_export_preflight")
        unrecorded["status"] = "waiting_for_formal_package_export_acceptance_decision"
        unrecorded["route_recorded"] = False

        invalid_report = build_auto_mode_formal_package_selected_route_execution_preflight(invalid)
        unrecorded_report = build_auto_mode_formal_package_selected_route_execution_preflight(unrecorded)

        self.assertEqual(missing["status"], "blocked_by_export_acceptance_router")
        self.assertIn("export_acceptance_router_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(invalid_report["status"], "blocked_by_export_acceptance_router")
        self.assertIn("export_acceptance_router_missing_or_invalid_schema", invalid_report["blocking_reasons"])
        self.assertEqual(unrecorded_report["status"], "blocked_by_export_acceptance_router")
        self.assertIn("export_acceptance_router_not_route_recorded", unrecorded_report["blocking_reasons"])

    def test_bdd_p7z_unknown_mismatched_or_missing_selected_route_blocks_contract(self) -> None:
        """行为 5：未知路线、route mismatch 或缺 selected plan item 时阻断。"""
        unknown = self._ready_router("formal_pdf_export_preflight")
        unknown["routed_action"] = "unknown_route"
        mismatch = self._ready_router("formal_pdf_export_preflight")
        mismatch["selected_plan_item"]["action_id"] = "formal_docx_export_preflight"
        missing = self._ready_router("formal_pdf_export_preflight")
        missing["selected_plan_item"] = {}

        unknown_report = build_auto_mode_formal_package_selected_route_execution_preflight(unknown)
        mismatch_report = build_auto_mode_formal_package_selected_route_execution_preflight(mismatch)
        missing_report = build_auto_mode_formal_package_selected_route_execution_preflight(missing)

        self.assertEqual(unknown_report["status"], "blocked_by_selected_route_contract")
        self.assertIn("selected_route_unknown:unknown_route", unknown_report["blocking_reasons"])
        self.assertEqual(mismatch_report["status"], "blocked_by_selected_route_contract")
        self.assertIn("selected_route_action_mismatch", mismatch_report["blocking_reasons"])
        self.assertEqual(missing_report["status"], "blocked_by_selected_route_contract")
        self.assertIn("selected_plan_item_missing", missing_report["blocking_reasons"])

    def test_bdd_p7z_bad_selected_plan_contract_blocks_preflight(self) -> None:
        """行为 6：selected plan 不干净或 source target 越界时阻断。"""
        not_pending = self._ready_router("formal_pdf_export_preflight")
        not_pending["selected_plan_item"]["execution_status"] = "completed"
        rendered = self._ready_router("formal_pdf_export_preflight")
        rendered["selected_plan_item"]["this_command_rendered_or_accepted"] = True
        outside = self._ready_router("formal_pdf_export_preflight")
        outside["selected_plan_item"]["source_formal_targets"] = ["workspace/not-formal/paper.md"]

        not_pending_report = build_auto_mode_formal_package_selected_route_execution_preflight(not_pending)
        rendered_report = build_auto_mode_formal_package_selected_route_execution_preflight(rendered)
        outside_report = build_auto_mode_formal_package_selected_route_execution_preflight(outside)

        self.assertEqual(not_pending_report["status"], "blocked_by_selected_route_contract")
        self.assertIn("selected_route_not_pending:formal_pdf_export_preflight", not_pending_report["blocking_reasons"])
        self.assertEqual(rendered_report["status"], "blocked_by_selected_route_contract")
        self.assertIn("selected_route_already_rendered_or_accepted:formal_pdf_export_preflight", rendered_report["blocking_reasons"])
        self.assertEqual(outside_report["status"], "blocked_by_selected_route_contract")
        self.assertIn("selected_route_source_target_outside_formal_package:workspace/not-formal/paper.md", outside_report["blocking_reasons"])

    def test_bdd_p7z_boundary_violations_block_preflight(self) -> None:
        """行为 7：P7-Y 带导出、渲染、正式层或产品层副作用时阻断。"""
        executed = self._ready_router("formal_pdf_export_preflight")
        executed["export_or_acceptance_executed"] = True
        product_state = self._ready_router("formal_pdf_export_preflight")
        product_state["can_write_product_state"] = True
        boundary = self._ready_router("formal_pdf_export_preflight")
        boundary["boundary_flags"]["rendered_pdf"] = True

        executed_report = build_auto_mode_formal_package_selected_route_execution_preflight(executed)
        product_report = build_auto_mode_formal_package_selected_route_execution_preflight(product_state)
        boundary_report = build_auto_mode_formal_package_selected_route_execution_preflight(boundary)

        self.assertEqual(executed_report["status"], "blocked_by_export_acceptance_router")
        self.assertIn("export_acceptance_router_already_executed_export_or_acceptance", executed_report["blocking_reasons"])
        self.assertEqual(product_report["status"], "blocked_by_export_acceptance_router")
        self.assertIn("export_acceptance_router_allows_product_state_write", product_report["blocking_reasons"])
        self.assertEqual(boundary_report["status"], "blocked_by_export_acceptance_router")
        self.assertIn("export_acceptance_router_boundary_violation:rendered_pdf", boundary_report["blocking_reasons"])

    def test_bdd_p7z_cli_defaults_to_current_blocked_router(self) -> None:
        """行为 3：CLI 默认读取当前 blocked P7-Y，继续不生成执行计划。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_export_acceptance_router.json",
                self._blocked_router(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_export_acceptance_router", result.stdout)
            self.assertIn("can_request_selected_route_execution=false", result.stdout)
            self.assertIn("selected_route_execution_plan=0", result.stdout)
            self.assertTrue(
                (project_root / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json").exists()
            )
            self.assertTrue((project_root / "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.docx").exists())
            self.assertFalse((project_root / "Submissions/formal_package/manifest.json").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_selected_route_execution_preflight.json").exists())

    def test_bdd_p7z_writes_report_and_review_only(self) -> None:
        """行为 8：只写 selected route preflight report/review，不导出不验收。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_selected_route_execution_preflight(
                self._ready_router("manual_acceptance_packet_preflight"),
            )
            report_path, review_path = write_auto_mode_formal_package_selected_route_execution_preflight_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "ready_for_selected_formal_package_route_execution_review")
            self.assertEqual(written["selected_route_execution_plan"][0]["route_type"], "manual_acceptance")
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.docx").exists())
            self.assertFalse((project_root / "Submissions/formal_package/manifest.json").exists())
            self.assertFalse((project_root / "Reviews/formal_package_manual_acceptance.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_selected_route_execution_preflight.json").exists())

    def _ready_router(self, routed_action: str) -> dict:
        selected_plan_item = {
            "action_id": routed_action,
            "label": routed_action.replace("_", " ").title(),
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
            "decision": self._decision_for_action(routed_action),
            "route_request": {
                "decision": self._decision_for_action(routed_action),
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

    def _blocked_router(self) -> dict:
        report = self._ready_router("formal_pdf_export_preflight")
        report["source_status"] = "blocked_by_promoted_package_verification"
        report["status"] = "blocked_by_export_acceptance_preflight"
        report["decision"] = "defer"
        report["route_request"] = {
            "decision": "defer",
            "confirm_route": False,
            "reviewer": "",
            "note": "",
            "metadata_complete": False,
        }
        report["can_route_export_or_acceptance"] = False
        report["route_recorded"] = False
        report["routed_action"] = ""
        report["selected_plan_item"] = {}
        report["blocking_reasons"] = ["export_acceptance_preflight_not_ready"]
        return report

    def _decision_for_action(self, action: str) -> str:
        return {
            "formal_pdf_export_preflight": "pdf_export",
            "formal_docx_export_preflight": "docx_export",
            "formal_submission_package_manifest_preflight": "package_manifest",
            "manual_acceptance_packet_preflight": "manual_acceptance",
        }.get(action, "unknown")

    def _clean_boundary_flags(self) -> dict:
        return {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "reran_models": False,
            "modified_statistical_execution_artifacts": False,
            "executed_target_adapters": False,
            "wrote_formal_state": False,
            "created_or_repaired_candidate_targets": False,
            "promoted_candidate_targets": False,
            "exported_or_accepted_formal_package": False,
            "generated_package_manifest": False,
            "performed_manual_acceptance": False,
        }

    def _source_paths(self) -> dict:
        return {
            "export_acceptance_router": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

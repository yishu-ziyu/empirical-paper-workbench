import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_verified_route_next_gate_router import (
    build_auto_mode_formal_package_verified_route_next_gate_router,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageVerifiedRouteNextGateRouterTests(unittest.TestCase):
    """BDD: P7-AE routes a verified route completion ledger to the next gate."""

    def test_bdd_p7ae_ready_pdf_completion_ledger_records_next_gate_route(self) -> None:
        """行为 1：已完成 PDF route 时，只记录下一关路由。"""
        report = build_auto_mode_formal_package_verified_route_next_gate_router(
            self._ready_ledger("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_package_verified_route_next_gate_router.v1")
        self.assertEqual(report["status"], "verified_route_next_gate_route_recorded")
        self.assertTrue(report["next_gate_route_recorded"])
        self.assertTrue(report["can_enter_routed_next_gate"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(report["next_gate_route"]["next_gate_action"], "continue_formal_package_export_acceptance_cycle")
        self.assertFalse(report["this_command_entered_next_gate"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ae_current_blocked_ledger_blocks_routing(self) -> None:
        """行为 2：当前 P7-AD blocked 时不会记录下一关路由。"""
        report = build_auto_mode_formal_package_verified_route_next_gate_router(self._blocked_ledger())

        self.assertEqual(report["status"], "blocked_by_verified_route_completion_ledger")
        self.assertFalse(report["next_gate_route_recorded"])
        self.assertFalse(report["can_enter_routed_next_gate"])
        self.assertEqual(report["routed_next_gate"], "")
        self.assertIn("verified_route_completion_ledger_not_recorded", report["blocking_reasons"])

    def test_bdd_p7ae_missing_or_invalid_ledger_blocks_routing(self) -> None:
        """行为 3：P7-AD ledger 缺失、schema 错误或状态未 recorded 时阻断。"""
        missing = build_auto_mode_formal_package_verified_route_next_gate_router({})
        wrong_schema = build_auto_mode_formal_package_verified_route_next_gate_router(
            {"schema_version": "wrong.schema", "status": "verified_route_completion_ledger_recorded"}
        )
        wrong_status = build_auto_mode_formal_package_verified_route_next_gate_router(
            {
                **self._ready_ledger("pdf_export"),
                "status": "blocked_by_route_specific_artifact_verification",
            }
        )

        self.assertEqual(missing["status"], "blocked_by_verified_route_completion_ledger")
        self.assertIn("verified_route_completion_ledger_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(wrong_schema["status"], "blocked_by_verified_route_completion_ledger")
        self.assertIn("verified_route_completion_ledger_missing_or_invalid_schema", wrong_schema["blocking_reasons"])
        self.assertEqual(wrong_status["status"], "blocked_by_verified_route_completion_ledger")
        self.assertIn("verified_route_completion_ledger_status_not_recorded", wrong_status["blocking_reasons"])

    def test_bdd_p7ae_completion_record_must_match_verified_route(self) -> None:
        """行为 4：completion record 必须和 verified route 一致。"""
        missing_records = self._ready_ledger("pdf_export")
        missing_records["route_completion_records"] = []
        mismatched = self._ready_ledger("pdf_export")
        mismatched["route_completion_records"][0]["route_type"] = "docx_export"
        bad_status = self._ready_ledger("pdf_export")
        bad_status["route_completion_records"][0]["completion_status"] = "pending"

        reports = [
            build_auto_mode_formal_package_verified_route_next_gate_router(source)
            for source in [missing_records, mismatched, bad_status]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_verified_route_next_gate_contract" for report in reports))
        self.assertIn("route_completion_records_missing", reports[0]["blocking_reasons"])
        self.assertIn("route_completion_record_route_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("route_completion_record_not_recorded:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7ae_unknown_route_type_blocks_routing(self) -> None:
        """行为 5：未知 route type 不能猜下一关。"""
        ledger = self._ready_ledger("pdf_export")
        ledger["verified_route_type"] = "spreadsheet_export"
        ledger["route_completion_records"][0]["route_type"] = "spreadsheet_export"
        ledger["route_completion_records"][0]["completion_id"] = "verified_route_completion::spreadsheet_export"

        report = build_auto_mode_formal_package_verified_route_next_gate_router(ledger)

        self.assertEqual(report["status"], "blocked_by_verified_route_next_gate_contract")
        self.assertFalse(report["next_gate_route_recorded"])
        self.assertIn("verified_route_type_unknown:spreadsheet_export", report["blocking_reasons"])

    def test_bdd_p7ae_manual_acceptance_routes_to_delivery_completion_gate(self) -> None:
        """行为 6：manual acceptance 完成后进入交付完成门，不回到导出循环。"""
        report = build_auto_mode_formal_package_verified_route_next_gate_router(self._ready_ledger("manual_acceptance"))

        self.assertEqual(report["status"], "verified_route_next_gate_route_recorded")
        self.assertTrue(report["next_gate_route_recorded"])
        self.assertEqual(report["routed_next_gate"], "formal_package_delivery_completion_gate")
        self.assertEqual(report["next_gate_route"]["next_gate_action"], "finalize_formal_package_delivery_review")
        self.assertEqual(report["next_gate_route"]["route_type"], "manual_acceptance")

    def test_bdd_p7ae_boundary_violations_block_routing(self) -> None:
        """行为 7：账本出现正式写回或边界越界时阻断。"""
        ledger = self._ready_ledger("pdf_export")
        ledger["formal_writeback_executed"] = True
        ledger["this_command_wrote_formal_state"] = True
        ledger["can_write_product_state"] = True
        ledger["boundary_flags"]["modified_product_state"] = True

        report = build_auto_mode_formal_package_verified_route_next_gate_router(ledger)

        self.assertEqual(report["status"], "blocked_by_verified_route_next_gate_boundary")
        self.assertFalse(report["next_gate_route_recorded"])
        self.assertIn("source_ledger_formal_writeback_executed", report["blocking_reasons"])
        self.assertIn("source_ledger_wrote_formal_state", report["blocking_reasons"])
        self.assertIn("source_ledger_allows_product_state_write", report["blocking_reasons"])
        self.assertIn("source_ledger_boundary_violation:modified_product_state", report["blocking_reasons"])

    def test_bdd_p7ae_cli_defaults_to_current_blocked_ledger(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AD，写 blocked router report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json",
                self._blocked_ledger(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_verified_route_next_gate_router.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_verified_route_completion_ledger", result.stdout)
            self.assertIn("next_gate_route_recorded=false", result.stdout)
            self.assertIn("can_enter_routed_next_gate=false", result.stdout)
            self.assertTrue(
                (
                    project_root / "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json"
                ).exists()
            )
            self.assertTrue(
                (project_root / "Reviews/auto_mode_formal_package_verified_route_next_gate_router.md").exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_verified_route_next_gate_router.json"
                ).exists()
            )

    def _ready_ledger(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_verified_route_completion_ledger.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "verified_route_completion_ledger_recorded",
            "route_completion_ledger_recorded": True,
            "can_enter_next_auto_mode_gate": True,
            "route_type": route_type,
            "verified_route_type": route_type,
            "delegated_status": "route_done",
            "route_specific_artifact_verified": True,
            "source_product_state_verified": route_type == "manual_acceptance",
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "rendered_pdf": route_type == "pdf_export",
            "rendered_docx": route_type == "docx_export",
            "package_manifest_generated": route_type == "package_manifest",
            "manual_acceptance_performed": route_type == "manual_acceptance",
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "artifact_verification_records_count": 1,
            "blocking_reasons": [],
            "source_verification": {"status": "route_specific_artifact_verified_for_review"},
            "route_completion_records": [self._completion_record(route_type)],
            "boundary_flags": self._clean_boundary_flags(),
            "next_action": {"id": "run_next_auto_mode_gate_for_verified_route"},
        }

    def _blocked_ledger(self) -> dict:
        ledger = self._ready_ledger("pdf_export")
        ledger["status"] = "blocked_by_route_specific_artifact_verification"
        ledger["route_completion_ledger_recorded"] = False
        ledger["can_enter_next_auto_mode_gate"] = False
        ledger["route_type"] = ""
        ledger["verified_route_type"] = ""
        ledger["route_completion_records"] = []
        ledger["blocking_reasons"] = ["route_specific_artifact_verification_not_verified"]
        return ledger

    def _completion_record(self, route_type: str) -> dict:
        artifact_id = {
            "pdf_export": "paper_pdf",
            "docx_export": "paper_docx",
            "package_manifest": "package_manifest",
            "manual_acceptance": "manual_acceptance_state",
        }[route_type]
        return {
            "completion_id": f"verified_route_completion::{route_type}",
            "completion_status": "verified_route_completion_recorded",
            "route_type": route_type,
            "delegated_status": "route_done",
            "source_verification_status": "route_specific_artifact_verified_for_review",
            "source_product_state_verified": route_type == "manual_acceptance",
            "artifact_count": 1,
            "artifact_ids": [artifact_id],
            "verified_artifacts": [
                {
                    "artifact_id": artifact_id,
                    "path": f"Submissions/formal_package/{artifact_id}",
                    "exists": True,
                    "bytes": 100,
                    "delegated_bytes": 100,
                    "sha256": "abc123",
                    "delegated_sha256": "abc123",
                    "verification_status": "verified",
                }
            ],
            "can_enter_next_auto_mode_gate": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
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
        }

    def _source_paths(self) -> dict:
        return {
            "verified_route_completion_ledger": (
                "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

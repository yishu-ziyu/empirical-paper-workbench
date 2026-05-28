import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_workflow_continuation_preflight import (
    build_auto_mode_formal_package_next_gate_workflow_continuation_preflight,
    write_auto_mode_formal_package_next_gate_workflow_continuation_preflight_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateWorkflowContinuationPreflightTests(unittest.TestCase):
    """BDD: P7-AK prepares next-gate workflow continuation after P7-AJ review."""

    def test_bdd_p7ak_reviewed_export_router_output_creates_continuation_plan(self) -> None:
        """行为 1：已审阅 export router 输出后，只生成下一工作流预检计划。"""
        report = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(
            self._ready_result_review("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_workflow_continuation_preflight.v1",
        )
        self.assertEqual(report["status"], "ready_for_next_gate_workflow_continuation_review")
        self.assertTrue(report["can_request_next_gate_workflow_continuation"])
        self.assertTrue(report["requires_explicit_workflow_continuation_command"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(len(report["workflow_continuation_plan"]), 1)
        item = report["workflow_continuation_plan"][0]
        self.assertEqual(item["next_command"], "auto_mode_formal_package_selected_route_execution_preflight")
        self.assertEqual(item["command_path"], "Program/auto_mode_formal_package_selected_route_execution_preflight.py")
        self.assertEqual(item["source_report_path"], "Results/json/auto_mode_formal_package_export_acceptance_router.json")
        self.assertEqual(item["next_report_path"], "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json")
        self.assertEqual(item["continuation_status"], "pending_explicit_workflow_continuation_command")
        self.assertFalse(report["workflow_continuation_executed"])
        self.assertFalse(report["this_command_ran_continuation"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ak_current_blocked_result_review_blocks_continuation(self) -> None:
        """行为 2：当前 P7-AJ blocked 时不生成 continuation plan。"""
        report = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(
            self._blocked_result_review(),
        )

        self.assertEqual(report["status"], "blocked_by_manifested_next_gate_command_result_review")
        self.assertFalse(report["can_request_next_gate_workflow_continuation"])
        self.assertFalse(report["requires_explicit_workflow_continuation_command"])
        self.assertEqual(report["workflow_continuation_plan"], [])
        self.assertIn("manifested_next_gate_command_result_review_not_ready", report["blocking_reasons"])

    def test_bdd_p7ak_missing_invalid_or_not_ready_result_review_blocks_continuation(self) -> None:
        """行为 3：P7-AJ 缺失、schema 错误或未 ready 时阻断。"""
        missing = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight({})
        wrong_schema = self._ready_result_review("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        no_continue = self._ready_result_review("pdf_export")
        no_continue["can_continue_after_delegated_next_gate"] = False

        wrong_report = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(wrong_schema)
        no_continue_report = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(no_continue)

        self.assertEqual(missing["status"], "blocked_by_manifested_next_gate_command_result_review")
        self.assertIn("manifested_next_gate_command_result_review_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(wrong_report["status"], "blocked_by_manifested_next_gate_command_result_review")
        self.assertIn("manifested_next_gate_command_result_review_missing_or_invalid_schema", wrong_report["blocking_reasons"])
        self.assertEqual(no_continue_report["status"], "blocked_by_manifested_next_gate_command_result_review")
        self.assertIn("manifested_next_gate_result_review_cannot_continue", no_continue_report["blocking_reasons"])

    def test_bdd_p7ak_result_record_must_match_top_level_contract(self) -> None:
        """行为 4：delegated result record 必须和顶层 route/gate/status/path 一致。"""
        record_mismatch = self._ready_result_review("pdf_export")
        record_mismatch["delegated_result_records"][0]["verified_route_type"] = "docx_export"
        path_mismatch = self._ready_result_review("pdf_export")
        path_mismatch["delegated_result_records"][0]["delegated_report_path"] = "Results/json/wrong.json"
        status_mismatch = self._ready_result_review("pdf_export")
        status_mismatch["delegated_result_records"][0]["delegated_status"] = "waiting"

        reports = [
            build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(source)
            for source in [record_mismatch, path_mismatch, status_mismatch]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_next_gate_workflow_continuation_contract" for report in reports)
        )
        self.assertIn("delegated_result_record_route_type_mismatch:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("delegated_result_record_report_path_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("delegated_result_record_status_mismatch:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7ak_unknown_gate_or_route_blocks_continuation_contract(self) -> None:
        """行为 5：未知 gate 或不支持 route type 时阻断。"""
        unknown_gate = self._ready_result_review("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        unknown_gate["delegated_result_records"][0]["routed_next_gate"] = "unknown_gate"
        unsupported_route = self._ready_result_review("manual_acceptance")

        unknown_report = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(unknown_gate)
        unsupported_report = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(unsupported_route)

        self.assertEqual(unknown_report["status"], "blocked_by_next_gate_workflow_continuation_contract")
        self.assertIn("routed_next_gate_unknown:unknown_gate", unknown_report["blocking_reasons"])
        self.assertEqual(unsupported_report["status"], "blocked_by_next_gate_workflow_continuation_contract")
        self.assertIn(
            "workflow_continuation_route_type_not_allowed:manual_acceptance",
            unsupported_report["blocking_reasons"],
        )

    def test_bdd_p7ak_writes_continuation_preflight_only(self) -> None:
        """行为 6：只写 continuation preflight report/review，不运行下一步。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(
                self._ready_result_review("pdf_export"),
            )
            report_path, review_path = write_auto_mode_formal_package_next_gate_workflow_continuation_preflight_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "ready_for_next_gate_workflow_continuation_review")
            self.assertEqual(len(written["workflow_continuation_plan"]), 1)
            self.assertFalse((project_root / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json").exists())

    def test_bdd_p7ak_cli_defaults_to_current_blocked_result_review(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AJ，写 blocked continuation preflight。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_manifested_next_gate_command_result_review.json",
                self._blocked_result_review(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_workflow_continuation_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_manifested_next_gate_command_result_review", result.stdout)
            self.assertIn("can_request_next_gate_workflow_continuation=false", result.stdout)
            self.assertIn("workflow_continuation_plan=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_workflow_continuation_preflight.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json"
                ).exists()
            )

    def _ready_result_review(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_manifested_next_gate_command_result_review.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_next_gate_command_executed",
            "status": "manifested_next_gate_command_result_review_ready",
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "delegated_status": "formal_package_export_acceptance_route_recorded",
            "delegated_next_gate_result_reviewed": True,
            "can_continue_after_delegated_next_gate": True,
            "next_gate_command_executed": True,
            "this_command_ran_next_gate_command": False,
            "next_gate_entered": True,
            "this_command_entered_next_gate": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "delegated_result_records": [
                {
                    "record_id": f"manifested_next_gate_result::formal_package_export_acceptance_router::{route_type}",
                    "verified_route_type": route_type,
                    "routed_next_gate": "formal_package_export_acceptance_router",
                    "delegated_status": "formal_package_export_acceptance_route_recorded",
                    "delegated_schema_version": "p7.auto_mode_formal_package_export_acceptance_router.v1",
                    "delegated_report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
                    "delegated_review_path": "Reviews/auto_mode_formal_package_export_acceptance_router.md",
                    "review_status": "delegated_next_gate_result_accepted_for_continuation",
                    "can_continue_after_delegated_next_gate": True,
                }
            ],
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_result_review(self) -> dict:
        report = self._ready_result_review("pdf_export")
        report["source_status"] = "blocked_by_manifested_routed_next_gate_command_preflight"
        report["status"] = "blocked_by_manifested_next_gate_command_execute"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["delegated_status"] = ""
        report["delegated_next_gate_result_reviewed"] = False
        report["can_continue_after_delegated_next_gate"] = False
        report["next_gate_command_executed"] = False
        report["next_gate_entered"] = False
        report["delegated_result_records"] = []
        report["blocking_reasons"] = ["manifested_next_gate_command_execute_not_completed"]
        return report

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
            "manifested_next_gate_command_result_review": (
                "Results/json/auto_mode_formal_package_manifested_next_gate_command_result_review.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

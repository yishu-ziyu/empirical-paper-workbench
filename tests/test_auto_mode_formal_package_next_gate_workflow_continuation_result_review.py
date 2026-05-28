import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_workflow_continuation_result_review import (
    build_auto_mode_formal_package_next_gate_workflow_continuation_result_review,
    write_auto_mode_formal_package_next_gate_workflow_continuation_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateWorkflowContinuationResultReviewTests(unittest.TestCase):
    """BDD: P7-AM reviews the selected route preflight produced by P7-AL."""

    def test_bdd_p7am_completed_continuation_with_ready_selected_route_preflight_can_continue(self) -> None:
        """行为 1：P7-AL completed 且 selected route preflight ready 时可继续。"""
        report = build_auto_mode_formal_package_next_gate_workflow_continuation_result_review(
            Path("."),
            self._execute_report("pdf_export"),
            self._selected_route_preflight("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_workflow_continuation_result_review.v1",
        )
        self.assertEqual(report["status"], "next_gate_workflow_continuation_result_review_ready")
        self.assertTrue(report["workflow_continuation_result_reviewed"])
        self.assertTrue(report["can_continue_to_selected_route_execution"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(
            report["selected_route_preflight_status"],
            "ready_for_selected_formal_package_route_execution_review",
        )
        self.assertEqual(len(report["selected_route_execution_preflight_records"]), 1)
        record = report["selected_route_execution_preflight_records"][0]
        self.assertEqual(record["review_status"], "selected_route_preflight_accepted_for_explicit_route_execution")
        self.assertEqual(record["next_command"], "formal_pdf_export_execute")
        self.assertTrue(report["workflow_continuation_executed"])
        self.assertFalse(report["this_command_ran_continuation"])
        self.assertFalse(report["selected_route_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7am_current_blocked_execute_report_blocks_result_review(self) -> None:
        """行为 2：当前 P7-AL blocked 时没有 selected route preflight 结果可审阅。"""
        report = build_auto_mode_formal_package_next_gate_workflow_continuation_result_review(
            Path("."),
            {},
            {},
        )

        self.assertEqual(report["status"], "blocked_by_next_gate_workflow_continuation_execute")
        self.assertFalse(report["workflow_continuation_result_reviewed"])
        self.assertFalse(report["can_continue_to_selected_route_execution"])
        self.assertEqual(report["selected_route_execution_preflight_records"], [])
        self.assertIn(
            "next_gate_workflow_continuation_execute_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7am_missing_invalid_or_not_completed_execute_report_blocks_review(self) -> None:
        """行为 3：P7-AL 缺失、schema 错误、未完成、失败或有 blockers 时阻断。"""
        wrong_schema = self._execute_report("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_completed = self._execute_report("pdf_export")
        not_completed["status"] = "blocked_by_next_gate_workflow_continuation_preflight"
        not_executed = self._execute_report("pdf_export")
        not_executed["workflow_continuation_executed"] = False
        failed = self._execute_report("pdf_export")
        failed["continuation_returncode"] = 1
        blocked = self._execute_report("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_workflow_continuation_result_review(
                Path("."),
                source,
                self._selected_route_preflight("pdf_export"),
            )
            for source in [wrong_schema, not_completed, not_executed, failed, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_next_gate_workflow_continuation_execute" for report in reports)
        )
        self.assertIn("next_gate_workflow_continuation_execute_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("next_gate_workflow_continuation_execute_not_completed", reports[1]["blocking_reasons"])
        self.assertIn("workflow_continuation_not_executed", reports[2]["blocking_reasons"])
        self.assertIn("continuation_returncode_not_zero", reports[3]["blocking_reasons"])
        self.assertIn("source_execute_has_blocking_reasons", reports[4]["blocking_reasons"])

    def test_bdd_p7am_execute_report_contract_must_match_selected_route_preflight(self) -> None:
        """行为 4：route、path、review path 或 continuation status 错配时阻断。"""
        unknown_gate = self._execute_report("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        wrong_path = self._execute_report("pdf_export")
        wrong_path["continuation_report_path"] = "Results/json/wrong.json"
        wrong_review_path = self._execute_report("pdf_export")
        wrong_review_path["continuation_review_path"] = "Reviews/wrong.md"
        status_mismatch = self._execute_report("pdf_export")
        status_mismatch["continuation_status"] = "blocked_by_export_acceptance_router"

        reports = [
            build_auto_mode_formal_package_next_gate_workflow_continuation_result_review(
                Path("."),
                source,
                self._selected_route_preflight("pdf_export"),
            )
            for source in [unknown_gate, wrong_path, wrong_review_path, status_mismatch]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_next_gate_workflow_continuation_result_contract"
                for report in reports
            )
        )
        self.assertIn("routed_next_gate_unknown:unknown_gate", reports[0]["blocking_reasons"])
        self.assertIn("continuation_report_path_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("continuation_review_path_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("continuation_status_mismatch:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7am_selected_route_preflight_report_must_be_clean(self) -> None:
        """行为 5：selected route preflight 缺失、无效、未 ready 或计划错配时阻断。"""
        missing = {}
        wrong_schema = self._selected_route_preflight("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_success = self._selected_route_preflight("pdf_export")
        not_success["status"] = "blocked_by_export_acceptance_router"
        blocked_report = self._selected_route_preflight("pdf_export")
        blocked_report["blocking_reasons"] = ["selected_route_blocked"]
        wrong_plan = self._selected_route_preflight("pdf_export")
        wrong_plan["selected_route_execution_plan"][0]["route_type"] = "docx_export"

        reports = [
            build_auto_mode_formal_package_next_gate_workflow_continuation_result_review(
                Path("."),
                self._execute_report("pdf_export"),
                selected_route_preflight,
            )
            for selected_route_preflight in [missing, wrong_schema, not_success, blocked_report, wrong_plan]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_selected_route_execution_preflight_report" for report in reports)
        )
        self.assertIn("selected_route_preflight_missing_or_invalid_schema:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("selected_route_preflight_missing_or_invalid_schema:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("selected_route_preflight_status_not_ready:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("selected_route_preflight_has_blocking_reasons:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("selected_route_plan_route_type_mismatch:pdf_export", reports[4]["blocking_reasons"])

    def test_bdd_p7am_writes_result_review_only(self) -> None:
        """行为 6：只写 P7-AM result review，不运行命令、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_workflow_continuation_result_review(
                project_root,
                self._execute_report("pdf_export"),
                self._selected_route_preflight("pdf_export"),
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_workflow_continuation_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "next_gate_workflow_continuation_result_review_ready")
            self.assertTrue(written["can_continue_to_selected_route_execution"])
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json"
                ).exists()
            )

    def test_bdd_p7am_cli_defaults_to_current_blocked_execute_report(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AL report，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            execute_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json"
            )
            execute_path.parent.mkdir(parents=True, exist_ok=True)
            execute_path.write_text(
                json.dumps({"status": "blocked_by_next_gate_workflow_continuation_preflight"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_workflow_continuation_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_next_gate_workflow_continuation_execute", result.stdout)
            self.assertIn("can_continue_to_selected_route_execution=false", result.stdout)
            self.assertIn("selected_route_execution_preflight_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_workflow_continuation_result_review.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json"
                ).exists()
            )

    def _execute_report(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_workflow_continuation_execute.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "ready_for_next_gate_workflow_continuation_review",
            "status": "next_gate_workflow_continuation_executed",
            "mode": "execute",
            "confirm_continuation_execute": True,
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "can_execute_next_gate_workflow_continuation_with_confirmation": True,
            "requires_explicit_workflow_continuation_command": True,
            "workflow_continuation_executed": True,
            "this_command_ran_continuation": True,
            "continuation_command": [
                "python3",
                "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
            ],
            "continuation_report_path": (
                "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
            ),
            "continuation_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
            "continuation_returncode": 0,
            "continuation_status": "ready_for_selected_formal_package_route_execution_review",
            "continuation_result": {
                "returncode": 0,
                "status": "ready_for_selected_formal_package_route_execution_review",
                "report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
                "review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
            },
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "workflow_continuation_plan_item": {
                "verified_route_type": route_type,
                "routed_next_gate": "formal_package_export_acceptance_router",
                "continuation_kind": "selected_route_execution_preflight",
                "next_command": "auto_mode_formal_package_selected_route_execution_preflight",
                "next_report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
                "next_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
            },
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _selected_route_preflight(self, route_type: str) -> dict:
        routed_action, next_command, planned_outputs = self._route_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execution_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "formal_package_export_acceptance_route_recorded",
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
                    "route_execution_id": f"selected_formal_package_route_execution::{routed_action}",
                    "routed_action": routed_action,
                    "route_type": route_type,
                    "next_command": next_command,
                    "source_formal_targets": [
                        "Submissions/formal_package/manuscript/paper.md",
                        "Submissions/formal_package/bibliography/literature_review_packet.json",
                    ],
                    "planned_outputs": planned_outputs,
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

    def _route_mapping(self, route_type: str) -> tuple[str, str, list[str]]:
        if route_type == "docx_export":
            return "formal_docx_export_preflight", "formal_docx_export_execute", [
                "Submissions/formal_package/paper.docx"
            ]
        if route_type == "package_manifest":
            return "formal_submission_package_manifest_preflight", "formal_submission_package_manifest_execute", [
                "Submissions/formal_package/manifest.json"
            ]
        return "formal_pdf_export_preflight", "formal_pdf_export_execute", [
            "Submissions/formal_package/paper.pdf"
        ]

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
            "next_gate_workflow_continuation_execute": (
                "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json"
            ),
            "selected_route_execution_preflight": (
                "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

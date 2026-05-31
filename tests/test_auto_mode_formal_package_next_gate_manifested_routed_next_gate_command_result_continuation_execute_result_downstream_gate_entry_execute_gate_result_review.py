import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review import (
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateCommandResultContinuationExecuteResultDownstreamGateEntryExecuteGateResultReviewTests(
    unittest.TestCase
):
    """BDD: P7-BK reviews P7-BJ downstream execution or product-review preparation."""

    def test_bdd_p7bk_export_execute_result_with_clean_manifest_is_review_ready(self) -> None:
        """行为 1：export downstream execute 完成且 manifest 干净时放行 artifact executor 输入。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
            Path("."),
            self._export_execute_gate(),
            self._selected_route_execute("pdf_export"),
            self._selected_route_execute_manifest("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.v1"
            ),
        )
        self.assertEqual(
            report["status"],
            "manifested_routed_next_gate_downstream_execute_result_review_ready",
        )
        self.assertTrue(report["downstream_execute_result_reviewed"])
        self.assertTrue(report["can_continue_after_downstream_execute"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["downstream_kind"], "selected_route_execution")
        self.assertTrue(report["selected_route_execute_manifest_recorded"])
        self.assertEqual(len(report["route_specific_artifact_executor_input_records"]), 1)
        record = report["route_specific_artifact_executor_input_records"][0]
        self.assertEqual(
            record["review_status"],
            "selected_route_execute_manifest_accepted_for_route_specific_artifact_executor",
        )
        self.assertEqual(
            record["selected_route_execute_report_path"],
            "Results/json/auto_mode_formal_package_selected_route_execute.json",
        )
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bk_manual_terminal_product_review_preparation_is_review_ready(self) -> None:
        """行为 2：manual terminal 产品审阅准备记录完成时放行 product-review 结果记录。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
            Path("."),
            self._manual_product_review_execute_gate(),
            {},
            {},
        )

        self.assertEqual(
            report["status"],
            "manifested_routed_next_gate_product_review_preparation_result_review_ready",
        )
        self.assertTrue(report["downstream_execute_result_reviewed"])
        self.assertTrue(report["can_continue_after_downstream_execute"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["downstream_kind"], "product_review_preparation")
        self.assertFalse(report["selected_route_execute_manifest_recorded"])
        self.assertEqual(report["route_specific_artifact_executor_input_records"], [])
        self.assertEqual(len(report["product_review_preparation_result_records"]), 1)
        self.assertEqual(
            report["product_review_preparation_result_records"][0]["review_status"],
            "product_review_preparation_accepted_for_product_review_packet",
        )
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bk_current_blocked_execute_gate_blocks_result_review(self) -> None:
        """行为 3：当前 P7-BJ blocked 时不生成 continuation record。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
            Path("."),
            self._blocked_execute_gate(),
            {},
            {},
        )

        self.assertEqual(
            report["status"],
            "blocked_by_manifested_routed_next_gate_downstream_execute_gate",
        )
        self.assertFalse(report["downstream_execute_result_reviewed"])
        self.assertFalse(report["can_continue_after_downstream_execute"])
        self.assertEqual(report["route_specific_artifact_executor_input_records"], [])
        self.assertEqual(report["product_review_preparation_result_records"], [])
        self.assertIn(
            "manifested_routed_next_gate_downstream_execute_gate_not_completed",
            report["blocking_reasons"],
        )

    def test_bdd_p7bk_missing_invalid_or_not_completed_execute_gate_blocks_review(self) -> None:
        """行为 4：P7-BJ 缺失、schema 错、未完成或有 blockers 时阻断。"""
        wrong_schema = self._export_execute_gate()
        wrong_schema["schema_version"] = "wrong.schema"
        not_completed = self._export_execute_gate()
        not_completed["status"] = "manifested_routed_next_gate_downstream_execute_dry_run_ready"
        blocked = self._export_execute_gate()
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                Path("."),
                source,
                self._selected_route_execute("pdf_export"),
                self._selected_route_execute_manifest("pdf_export"),
            )
            for source in [{}, wrong_schema, not_completed, blocked]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_downstream_execute_gate"
                for report in reports
            )
        )
        self.assertIn(
            "manifested_routed_next_gate_downstream_execute_gate_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_downstream_execute_gate_missing_or_invalid_schema",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_downstream_execute_gate_not_completed",
            reports[2]["blocking_reasons"],
        )
        self.assertIn("source_downstream_execute_gate_has_blocking_reasons", reports[3]["blocking_reasons"])

    def test_bdd_p7bk_export_delegated_report_and_manifest_must_match(self) -> None:
        """行为 5：export 分支必须核对 selected-route execute report 与 manifest。"""
        wrong_path = self._export_execute_gate()
        wrong_path["downstream_execute_result"]["report_path"] = "Results/json/wrong.json"
        status_mismatch = self._selected_route_execute("pdf_export")
        status_mismatch["status"] = "selected_route_execute_dry_run_ready"
        manifest_violation = self._selected_route_execute_manifest("pdf_export")
        manifest_violation["selected_route_execute_operations"][0]["will_render_pdf"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                Path("."),
                wrong_path,
                self._selected_route_execute("pdf_export"),
                self._selected_route_execute_manifest("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                Path("."),
                self._export_execute_gate(),
                status_mismatch,
                self._selected_route_execute_manifest("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                Path("."),
                self._export_execute_gate(),
                self._selected_route_execute("pdf_export"),
                manifest_violation,
            ),
        ]

        self.assertEqual(
            reports[0]["status"],
            "blocked_by_manifested_routed_next_gate_downstream_selected_route_execute_contract",
        )
        self.assertEqual(
            reports[1]["status"],
            "blocked_by_manifested_routed_next_gate_downstream_selected_route_execute_contract",
        )
        self.assertEqual(
            reports[2]["status"],
            "blocked_by_manifested_routed_next_gate_downstream_selected_route_manifest_review",
        )
        self.assertIn("downstream_execute_result_report_path_mismatch:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("selected_route_execute_status_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("route_operation_marked_render_pdf:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7bk_manual_terminal_output_must_be_pure_product_review_preparation(self) -> None:
        """行为 6：manual terminal 不能混入命令执行或错误路线。"""
        command_executed = self._manual_product_review_execute_gate()
        command_executed["downstream_execute_command_executed"] = True
        missing_record = self._manual_product_review_execute_gate()
        missing_record["product_review_preparation_recorded"] = False
        wrong_route = self._manual_product_review_execute_gate()
        wrong_route["verified_route_type"] = "pdf_export"

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                Path("."),
                source,
                {},
                {},
            )
            for source in [command_executed, missing_record, wrong_route]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_product_review_preparation_contract"
                for report in reports
            )
        )
        self.assertIn("product_review_preparation_mixed_with_downstream_command_execution", reports[0]["blocking_reasons"])
        self.assertIn("product_review_preparation_not_recorded", reports[1]["blocking_reasons"])
        self.assertIn("product_review_preparation_route_type_mismatch:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7bk_boundary_violations_block_review(self) -> None:
        """行为 7：P7-BJ 或 selected-route artifacts 出现越权信号时阻断。"""
        source_route_executed = self._export_execute_gate()
        source_route_executed["selected_route_executed"] = True
        source_wrote = self._export_execute_gate()
        source_wrote["can_write_product_state"] = True
        manifest_flag = self._selected_route_execute_manifest("pdf_export")
        manifest_flag["boundary_flags"]["rendered_pdf"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                Path("."),
                source_route_executed,
                self._selected_route_execute("pdf_export"),
                self._selected_route_execute_manifest("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                Path("."),
                source_wrote,
                self._selected_route_execute("pdf_export"),
                self._selected_route_execute_manifest("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                Path("."),
                self._export_execute_gate(),
                self._selected_route_execute("pdf_export"),
                manifest_flag,
            ),
        ]

        self.assertEqual(reports[0]["status"], "blocked_by_manifested_routed_next_gate_downstream_execute_boundary")
        self.assertEqual(reports[1]["status"], "blocked_by_manifested_routed_next_gate_downstream_execute_boundary")
        self.assertEqual(
            reports[2]["status"],
            "blocked_by_manifested_routed_next_gate_downstream_selected_route_manifest_review",
        )
        self.assertIn("downstream_execute_gate_selected_route_executed", reports[0]["blocking_reasons"])
        self.assertIn("downstream_execute_gate_allows_product_state_write", reports[1]["blocking_reasons"])
        self.assertIn("selected_route_execute_manifest_boundary_violation:rendered_pdf", reports[2]["blocking_reasons"])

    def test_bdd_p7bk_writes_result_review_only_and_cli_defaults_blocked(self) -> None:
        """行为 8：只写 P7-BK report/review；CLI 默认读取当前 blocked P7-BJ。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
                project_root,
                self._manual_product_review_execute_gate(),
                {},
                {},
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(
                written["status"],
                "manifested_routed_next_gate_product_review_preparation_result_review_ready",
            )
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_product_review_preparation.json").exists())

            source_path = (
                project_root
                / (
                    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                    "continuation_execute_result_downstream_gate_entry_execute_gate.json"
                )
            )
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(json.dumps(self._blocked_execute_gate()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    (
                        "Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                        "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.py"
                    ),
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_manifested_routed_next_gate_downstream_execute_gate", result.stdout)
            self.assertIn("downstream_execute_result_reviewed=false", result.stdout)
            self.assertIn("can_continue_after_downstream_execute=false", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)

    def _export_execute_gate(self) -> dict:
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_downstream_gate_entry_execute_gate.v1"
            ),
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "ready_for_manifested_routed_next_gate_result_continuation_execute_downstream_gate_entry",
            "status": "manifested_routed_next_gate_downstream_selected_route_execute_command_executed",
            "mode": "execute",
            "confirm_downstream_execute": True,
            "verified_route_type": "pdf_export",
            "routed_next_gate": "formal_package_export_acceptance_router",
            "downstream_kind": "selected_route_execution",
            "downstream_status": "pending_explicit_selected_route_execution",
            "can_execute_downstream_with_confirmation": True,
            "requires_explicit_downstream_command": True,
            "downstream_execute_command_executed": True,
            "this_command_ran_downstream_command": True,
            "downstream_execute_returncode": 0,
            "downstream_execute_status": "selected_route_execute_manifest_recorded",
            "downstream_execute_result": {
                "returncode": 0,
                "status": "selected_route_execute_manifest_recorded",
                "report_path": "Results/json/auto_mode_formal_package_selected_route_execute.json",
                "review_path": "Reviews/auto_mode_formal_package_selected_route_execute.md",
                "manifest_path": (
                    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
                ),
                "selected_route_execute_report_summary": {
                    "schema_version": "p7.auto_mode_formal_package_selected_route_execute.v1",
                    "status": "selected_route_execute_manifest_recorded",
                    "selected_route_execute_manifest_recorded": True,
                    "selected_route_execute_operations_count": 1,
                    "blocking_reasons": [],
                },
            },
            "selected_route_execute_manifest_recorded": True,
            "product_review_preparation_recorded": False,
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
            "downstream_input_record": {
                "verified_route_type": "pdf_export",
                "routed_next_gate": "formal_package_export_acceptance_router",
                "downstream_kind": "selected_route_execution",
                "source_report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
                "planned_outputs": ["Submissions/formal_package/paper.pdf"],
            },
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _manual_product_review_execute_gate(self) -> dict:
        report = self._export_execute_gate()
        report["verified_route_type"] = "manual_acceptance"
        report["routed_next_gate"] = "formal_package_delivery_completion_gate"
        report["downstream_kind"] = "product_review_preparation"
        report["downstream_status"] = "pending_product_review_preparation"
        report["status"] = "manifested_routed_next_gate_downstream_product_review_preparation_recorded"
        report["requires_explicit_downstream_command"] = False
        report["downstream_execute_command_executed"] = False
        report["this_command_ran_downstream_command"] = False
        report["downstream_execute_returncode"] = None
        report["downstream_execute_status"] = ""
        report["downstream_execute_result"] = {}
        report["selected_route_execute_manifest_recorded"] = False
        report["product_review_preparation_recorded"] = True
        report["downstream_input_record"] = {
            "verified_route_type": "manual_acceptance",
            "routed_next_gate": "formal_package_delivery_completion_gate",
            "downstream_kind": "product_review_preparation",
            "terminal_status": "terminal_delivery_completion_ready_for_product_review",
            "next_report_path": "Results/json/auto_mode_formal_package_product_review_preparation.json",
            "next_review_path": "Reviews/auto_mode_formal_package_product_review_preparation.md",
            "terminal_completion": True,
        }
        return report

    def _blocked_execute_gate(self) -> dict:
        report = self._export_execute_gate()
        report["status"] = "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["downstream_kind"] = ""
        report["can_execute_downstream_with_confirmation"] = False
        report["requires_explicit_downstream_command"] = False
        report["downstream_execute_command_executed"] = False
        report["this_command_ran_downstream_command"] = False
        report["downstream_execute_returncode"] = None
        report["downstream_execute_status"] = ""
        report["selected_route_execute_manifest_recorded"] = False
        report["product_review_preparation_recorded"] = False
        report["downstream_input_record"] = {}
        report["blocking_reasons"] = [
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_not_ready"
        ]
        return report

    def _selected_route_execute(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "selected_route_execute_manifest_recorded",
            "mode": "execute",
            "confirm_execute": True,
            "can_execute_selected_route_with_confirmation": True,
            "selected_route_execute_manifest_recorded": True,
            "selected_route_execute_manifest_path": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
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
            "selected_route_execute_operations": [self._operation(route_type)],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _selected_route_execute_manifest(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute_manifest.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_execute_report": "Results/json/auto_mode_formal_package_selected_route_execute.json",
            "manifest_path": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "selected_route_execute_operations": [self._operation(route_type)],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _operation(self, route_type: str) -> dict:
        return {
            "operation_id": f"selected_route_execute::{route_type}",
            "route_execution_id": "selected_formal_package_route_execution::formal_pdf_export_preflight",
            "routed_action": "formal_pdf_export_preflight",
            "route_type": route_type,
            "next_command": "formal_pdf_export_execute",
            "planned_outputs": ["Submissions/formal_package/paper.pdf"],
            "operation_status": "planned_not_executed",
            "will_execute_selected_route": False,
            "will_render_pdf": False,
            "will_render_docx": False,
            "will_generate_package_manifest": False,
            "will_perform_manual_acceptance": False,
            "will_write_product_state": False,
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
        }

    def _source_paths(self) -> dict:
        return {
            "manifested_routed_next_gate_downstream_execute_gate": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate.json"
            ),
            "selected_route_execute": "Results/json/auto_mode_formal_package_selected_route_execute.json",
            "selected_route_execute_manifest": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

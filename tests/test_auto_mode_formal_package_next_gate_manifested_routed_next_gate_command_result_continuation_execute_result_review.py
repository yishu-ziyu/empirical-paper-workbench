import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review import (
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateCommandResultContinuationExecuteResultReviewTests(
    unittest.TestCase
):
    """BDD: P7-BH reviews P7-BG continuation execution results without running the next step."""

    def test_bdd_p7bh_export_continuation_output_ready_can_continue(self) -> None:
        """行为 1：export continuation 执行完成且 selected-route preflight ready 时可继续。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
            Path("."),
            self._execute_gate_export("pdf_export"),
            self._selected_route_preflight("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_review.v1"
            ),
        )
        self.assertEqual(
            report["status"],
            "manifested_routed_next_gate_result_continuation_execute_result_review_ready",
        )
        self.assertTrue(report["continuation_execute_result_reviewed"])
        self.assertTrue(report["can_continue_after_manifested_routed_next_gate_result_continuation"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(
            report["selected_route_preflight_status"],
            "ready_for_selected_formal_package_route_execution_review",
        )
        self.assertEqual(len(report["selected_route_execution_preflight_records"]), 1)
        self.assertEqual(report["terminal_continuation_records"], [])
        record = report["selected_route_execution_preflight_records"][0]
        self.assertEqual(record["next_command"], "formal_pdf_export_execute")
        self.assertTrue(report["continuation_executed"])
        self.assertFalse(report["terminal_continuation_recorded"])
        self.assertFalse(report["this_command_ran_continuation"])
        self.assertFalse(report["selected_route_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bh_manual_terminal_record_can_continue_without_command(self) -> None:
        """行为 2：manual terminal continuation 记录完成时可继续产品审阅准备。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
            Path("."),
            self._execute_gate_manual(),
            {},
        )

        self.assertEqual(
            report["status"],
            "manifested_routed_next_gate_result_continuation_execute_result_review_ready",
        )
        self.assertTrue(report["continuation_execute_result_reviewed"])
        self.assertTrue(report["can_continue_after_manifested_routed_next_gate_result_continuation"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["routed_next_gate"], "formal_package_delivery_completion_gate")
        self.assertEqual(report["selected_route_execution_preflight_records"], [])
        self.assertEqual(len(report["terminal_continuation_records"]), 1)
        record = report["terminal_continuation_records"][0]
        self.assertEqual(record["terminal_status"], "terminal_delivery_completion_ready_for_product_review")
        self.assertEqual(record["next_command"], "product_review_preparation")
        self.assertFalse(report["continuation_executed"])
        self.assertTrue(report["terminal_continuation_recorded"])
        self.assertFalse(report["this_command_ran_continuation"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bh_current_blocked_execute_gate_blocks_result_review(self) -> None:
        """行为 3：当前 P7-BG blocked 时没有 continuation 执行结果可审阅。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
            Path("."),
            self._blocked_execute_gate(),
            {},
        )

        self.assertEqual(
            report["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_execute_gate",
        )
        self.assertFalse(report["continuation_execute_result_reviewed"])
        self.assertFalse(report["can_continue_after_manifested_routed_next_gate_result_continuation"])
        self.assertEqual(report["selected_route_execution_preflight_records"], [])
        self.assertEqual(report["terminal_continuation_records"], [])
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_gate_not_completed",
            report["blocking_reasons"],
        )

    def test_bdd_p7bh_missing_invalid_or_failed_execute_gate_blocks_review(self) -> None:
        """行为 4：P7-BG 缺失、schema 错、未完成、失败或有 blockers 时阻断。"""
        wrong_schema = self._execute_gate_export("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_completed = self._execute_gate_export("pdf_export")
        not_completed["status"] = "blocked_by_manifested_routed_next_gate_result_continuation_failure"
        failed = self._execute_gate_export("pdf_export")
        failed["continuation_returncode"] = 1
        blocked = self._execute_gate_export("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
                Path("."),
                source,
                self._selected_route_preflight("pdf_export"),
            )
            for source in [{}, wrong_schema, not_completed, failed, blocked]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_gate"
                for report in reports
            )
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_gate_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_gate_missing_or_invalid_schema",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_gate_not_completed",
            reports[2]["blocking_reasons"],
        )
        self.assertIn("continuation_returncode_not_zero", reports[3]["blocking_reasons"])
        self.assertIn("source_execute_gate_has_blocking_reasons", reports[4]["blocking_reasons"])

    def test_bdd_p7bh_export_continuation_output_contract_must_be_clean(self) -> None:
        """行为 5：export continuation 的 path、status、schema、summary 或计划错配时阻断。"""
        wrong_path = self._execute_gate_export("pdf_export")
        wrong_path["continuation_report_path"] = "Results/json/wrong.json"
        status_mismatch = self._execute_gate_export("pdf_export")
        status_mismatch["continuation_status"] = "blocked_by_selected_route_preflight"
        summary_mismatch = self._execute_gate_export("pdf_export")
        summary_mismatch["continuation_result"]["continuation_report_summary"]["status"] = "wrong"
        wrong_schema = self._selected_route_preflight("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        wrong_plan = self._selected_route_preflight("pdf_export")
        wrong_plan["selected_route_execution_plan"][0]["route_type"] = "docx_export"

        cases = [
            (wrong_path, self._selected_route_preflight("pdf_export")),
            (status_mismatch, self._selected_route_preflight("pdf_export")),
            (summary_mismatch, self._selected_route_preflight("pdf_export")),
            (self._execute_gate_export("pdf_export"), wrong_schema),
            (self._execute_gate_export("pdf_export"), wrong_plan),
        ]
        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
                Path("."),
                execute_gate,
                selected_route_preflight,
            )
            for execute_gate, selected_route_preflight in cases
        ]

        self.assertEqual(
            reports[0]["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_output",
        )
        self.assertEqual(
            reports[1]["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_output",
        )
        self.assertEqual(
            reports[2]["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_output",
        )
        self.assertEqual(
            reports[3]["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_output",
        )
        self.assertEqual(
            reports[4]["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_output",
        )
        self.assertIn("continuation_report_path_mismatch:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("continuation_status_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("continuation_summary_status_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("selected_route_preflight_missing_or_invalid_schema:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("selected_route_plan_route_type_mismatch:pdf_export", reports[4]["blocking_reasons"])

    def test_bdd_p7bh_manual_terminal_contract_must_be_clean(self) -> None:
        """行为 6：manual terminal 缺少终态标记或混入命令执行时阻断。"""
        missing_terminal = self._execute_gate_manual()
        missing_terminal["terminal_continuation_recorded"] = False
        has_command = self._execute_gate_manual()
        has_command["continuation_command"] = ["python3", "Program/anything.py"]
        has_returncode = self._execute_gate_manual()
        has_returncode["continuation_returncode"] = 0
        ran_continuation = self._execute_gate_manual()
        ran_continuation["this_command_ran_continuation"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
                Path("."),
                source,
                {},
            )
            for source in [missing_terminal, has_command, has_returncode, ran_continuation]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_contract"
                for report in reports
            )
        )
        self.assertIn("terminal_continuation_not_recorded", reports[0]["blocking_reasons"])
        self.assertIn("terminal_continuation_has_external_command", reports[1]["blocking_reasons"])
        self.assertIn("terminal_continuation_has_returncode", reports[2]["blocking_reasons"])
        self.assertIn("terminal_continuation_ran_external_continuation", reports[3]["blocking_reasons"])

    def test_bdd_p7bh_boundary_violations_block_review(self) -> None:
        """行为 7：source 或 continuation output 出现正式层动作时阻断。"""
        executed_source = self._execute_gate_export("pdf_export")
        executed_source["selected_route_executed"] = True
        wrote_source = self._execute_gate_export("pdf_export")
        wrote_source["can_write_product_state"] = True
        source_flag = self._execute_gate_export("pdf_export")
        source_flag["boundary_flags"]["executed_selected_route"] = True
        executed_preflight = self._selected_route_preflight("pdf_export")
        executed_preflight["export_or_acceptance_executed"] = True
        preflight_flag = self._selected_route_preflight("pdf_export")
        preflight_flag["boundary_flags"]["rendered_pdf"] = True

        cases = [
            (executed_source, self._selected_route_preflight("pdf_export")),
            (wrote_source, self._selected_route_preflight("pdf_export")),
            (source_flag, self._selected_route_preflight("pdf_export")),
            (self._execute_gate_export("pdf_export"), executed_preflight),
            (self._execute_gate_export("pdf_export"), preflight_flag),
        ]
        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
                Path("."),
                execute_gate,
                selected_route_preflight,
            )
            for execute_gate, selected_route_preflight in cases
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_boundary"
                for report in reports
            )
        )
        self.assertIn("execute_gate_selected_route_executed", reports[0]["blocking_reasons"])
        self.assertIn("execute_gate_allows_product_state_write", reports[1]["blocking_reasons"])
        self.assertIn("execute_gate_boundary_violation:executed_selected_route", reports[2]["blocking_reasons"])
        self.assertIn("selected_route_preflight_export_or_acceptance_executed:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("selected_route_preflight_boundary_violation:rendered_pdf", reports[4]["blocking_reasons"])

    def test_bdd_p7bh_writes_result_review_only_and_cli_defaults_to_blocked(self) -> None:
        """行为 8：只写 P7-BH result review；CLI 默认读取当前 blocked P7-BG。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
                project_root,
                self._execute_gate_export("pdf_export"),
                self._selected_route_preflight("pdf_export"),
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review.json"
                ).exists()
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            execute_gate_path = (
                project_root
                / (
                    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                    "continuation_execute_gate.json"
                )
            )
            execute_gate_path.parent.mkdir(parents=True, exist_ok=True)
            execute_gate_path.write_text(json.dumps(self._blocked_execute_gate()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    (
                        "Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                        "continuation_execute_result_review.py"
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
            self.assertIn(
                "status=blocked_by_manifested_routed_next_gate_result_continuation_execute_gate",
                result.stdout,
            )
            self.assertIn("continuation_execute_result_reviewed=false", result.stdout)
            self.assertIn("selected_route_execution_preflight_records=0", result.stdout)
            self.assertIn("terminal_continuation_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / (
                        "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                        "continuation_execute_result_review.json"
                    )
                ).exists()
            )

    def _execute_gate_export(self, route_type: str) -> dict:
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_gate.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "ready_for_manifested_routed_next_gate_command_result_continuation_gate_entry",
            "status": "manifested_routed_next_gate_result_continuation_executed",
            "mode": "execute",
            "confirm_continuation_execute": True,
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "completion_terminal": False,
            "terminal_continuation_recorded": False,
            "this_command_recorded_terminal_continuation": False,
            "continuation_executed": True,
            "this_command_ran_continuation": True,
            "continuation_command": [
                "python3",
                "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
            ],
            "continuation_report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
            "continuation_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
            "continuation_returncode": 0,
            "continuation_status": "ready_for_selected_formal_package_route_execution_review",
            "continuation_result": {
                "returncode": 0,
                "status": "ready_for_selected_formal_package_route_execution_review",
                "report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
                "review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
                "continuation_report_summary": {
                    "schema_version": "p7.auto_mode_formal_package_selected_route_execution_preflight.v1",
                    "status": "ready_for_selected_formal_package_route_execution_review",
                    "can_request_selected_route_execution": True,
                    "selected_route_execution_plan_count": 1,
                    "blocking_reasons": [],
                },
            },
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _execute_gate_manual(self) -> dict:
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_gate.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "ready_for_manifested_routed_next_gate_command_result_continuation_gate_entry",
            "status": "manifested_routed_next_gate_terminal_continuation_recorded",
            "mode": "execute",
            "confirm_continuation_execute": True,
            "verified_route_type": "manual_acceptance",
            "routed_next_gate": "formal_package_delivery_completion_gate",
            "completion_terminal": True,
            "terminal_continuation_recorded": True,
            "this_command_recorded_terminal_continuation": True,
            "continuation_executed": False,
            "this_command_ran_continuation": False,
            "continuation_command": [],
            "continuation_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
            "continuation_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
            "continuation_returncode": None,
            "continuation_status": "terminal_delivery_completion_ready_for_product_review",
            "continuation_result": {},
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_execute_gate(self) -> dict:
        report = self._execute_gate_export("pdf_export")
        report["source_status"] = "blocked_by_manifested_routed_next_gate_command_result_review"
        report["status"] = "blocked_by_manifested_routed_next_gate_result_continuation_gate_entry"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["completion_terminal"] = False
        report["continuation_executed"] = False
        report["this_command_ran_continuation"] = False
        report["continuation_command"] = []
        report["continuation_report_path"] = ""
        report["continuation_review_path"] = ""
        report["continuation_returncode"] = None
        report["continuation_status"] = ""
        report["continuation_result"] = {}
        report["blocking_reasons"] = [
            "manifested_routed_next_gate_result_continuation_gate_entry_not_ready"
        ]
        return report

    def _selected_route_preflight(self, route_type: str) -> dict:
        routed_action, next_command, planned_outputs = self._route_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execution_preflight.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
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
            "executed_selected_route": False,
            "exported_or_accepted_formal_package": False,
            "executed_manifested_routed_next_gate_result_continuation": False,
            "recorded_terminal_continuation": False,
        }

    def _source_paths(self) -> dict:
        return {
            "manifested_routed_next_gate_command_result_continuation_execute_gate": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.json"
            ),
            "selected_route_execution_preflight": (
                "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry import (
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateCommandResultContinuationExecuteResultDownstreamGateEntryTests(
    unittest.TestCase
):
    """BDD: P7-BI converts P7-BH result review records into downstream gate entry input."""

    def test_bdd_p7bi_export_review_creates_selected_route_execution_input(self) -> None:
        """行为 1：export ready record 转成 selected-route execution 下游入口。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
            self._ready_result_review_export("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_downstream_gate_entry.v1"
            ),
        )
        self.assertEqual(
            report["status"],
            "ready_for_manifested_routed_next_gate_result_continuation_execute_downstream_gate_entry",
        )
        self.assertTrue(report["downstream_gate_entry_recorded"])
        self.assertTrue(report["can_request_manifested_routed_next_gate_result_continuation_downstream"])
        self.assertTrue(report["requires_explicit_downstream_command"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(report["downstream_kind"], "selected_route_execution")
        self.assertEqual(len(report["downstream_input_records"]), 1)
        record = report["downstream_input_records"][0]
        self.assertEqual(
            record["record_id"],
            (
                "manifested_routed_continuation_execute_result_downstream::"
                "formal_package_export_acceptance_router::pdf_export"
            ),
        )
        self.assertEqual(record["downstream_kind"], "selected_route_execution")
        self.assertEqual(record["downstream_command"], "auto_mode_formal_package_next_gate_selected_route_execute")
        self.assertEqual(record["command_path"], "Program/auto_mode_formal_package_next_gate_selected_route_execute.py")
        self.assertEqual(record["route_specific_next_command"], "formal_pdf_export_execute")
        self.assertEqual(
            record["source_report_path"],
            "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
        )
        self.assertEqual(
            record["next_report_path"],
            "Results/json/auto_mode_formal_package_next_gate_selected_route_execute.json",
        )
        self.assertTrue(record["requires_explicit_downstream_command"])
        self.assertFalse(report["this_command_ran_downstream_command"])
        self.assertFalse(report["selected_route_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bi_manual_terminal_review_creates_product_review_input(self) -> None:
        """行为 2：manual terminal ready record 转成产品审阅准备入口。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
            self._ready_result_review_manual(),
        )

        self.assertEqual(
            report["status"],
            "ready_for_manifested_routed_next_gate_result_continuation_execute_downstream_gate_entry",
        )
        self.assertTrue(report["downstream_gate_entry_recorded"])
        self.assertTrue(report["can_request_manifested_routed_next_gate_result_continuation_downstream"])
        self.assertFalse(report["requires_explicit_downstream_command"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["routed_next_gate"], "formal_package_delivery_completion_gate")
        self.assertEqual(report["downstream_kind"], "product_review_preparation")
        self.assertEqual(len(report["downstream_input_records"]), 1)
        record = report["downstream_input_records"][0]
        self.assertEqual(record["downstream_kind"], "product_review_preparation")
        self.assertEqual(record["downstream_command"], "product_review_preparation")
        self.assertEqual(record["command_path"], "")
        self.assertEqual(record["terminal_status"], "terminal_delivery_completion_ready_for_product_review")
        self.assertFalse(record["requires_explicit_downstream_command"])
        self.assertFalse(report["this_command_ran_downstream_command"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bi_current_blocked_result_review_blocks_downstream_entry(self) -> None:
        """行为 3：当前 P7-BH blocked 时不生成下游入口。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
            self._blocked_result_review(),
        )

        self.assertEqual(
            report["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_review",
        )
        self.assertFalse(report["downstream_gate_entry_recorded"])
        self.assertFalse(report["can_request_manifested_routed_next_gate_result_continuation_downstream"])
        self.assertFalse(report["requires_explicit_downstream_command"])
        self.assertEqual(report["downstream_input_records"], [])
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_result_review_not_ready",
            report["blocking_reasons"],
        )

    def test_bdd_p7bi_missing_invalid_or_not_ready_result_review_blocks_entry(self) -> None:
        """行为 4：P7-BH 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._ready_result_review_export("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        no_continue = self._ready_result_review_export("pdf_export")
        no_continue["can_continue_after_manifested_routed_next_gate_result_continuation"] = False
        blocked = self._ready_result_review_export("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
                source
            )
            for source in [{}, wrong_schema, no_continue, blocked]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_review"
                for report in reports
            )
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_result_review_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_result_review_missing_or_invalid_schema",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_execute_result_review_cannot_continue",
            reports[2]["blocking_reasons"],
        )
        self.assertIn("source_result_review_has_blocking_reasons", reports[3]["blocking_reasons"])

    def test_bdd_p7bi_downstream_record_must_be_single_accepted_and_matching(self) -> None:
        """行为 5：下游 record 缺失、重复、错配、未接受或不可继续时阻断。"""
        missing = self._ready_result_review_export("pdf_export")
        missing["selected_route_execution_preflight_records"] = []
        duplicated = self._ready_result_review_export("pdf_export")
        duplicated["selected_route_execution_preflight_records"].append(
            dict(duplicated["selected_route_execution_preflight_records"][0])
        )
        route_mismatch = self._ready_result_review_export("pdf_export")
        route_mismatch["selected_route_execution_preflight_records"][0]["verified_route_type"] = "docx_export"
        not_accepted = self._ready_result_review_export("pdf_export")
        not_accepted["selected_route_execution_preflight_records"][0]["review_status"] = "waiting"
        cannot_continue = self._ready_result_review_manual()
        cannot_continue["terminal_continuation_records"][0]["can_continue_to_product_review_preparation"] = False

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
                source
            )
            for source in [missing, duplicated, route_mismatch, not_accepted, cannot_continue]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_contract"
                for report in reports
            )
        )
        self.assertIn("selected_route_preflight_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("selected_route_preflight_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("downstream_record_route_type_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("downstream_record_not_accepted:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("terminal_downstream_record_cannot_continue:manual_acceptance", reports[4]["blocking_reasons"])

    def test_bdd_p7bi_unknown_route_or_downstream_mapping_blocks_entry(self) -> None:
        """行为 6：未知路线、未知 gate 或 record 内容不符合下游映射时阻断。"""
        unknown_gate = self._ready_result_review_export("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        unsupported_route = self._ready_result_review_export("pdf_export")
        unsupported_route["verified_route_type"] = "manual_acceptance"
        wrong_command = self._ready_result_review_export("pdf_export")
        wrong_command["selected_route_execution_preflight_records"][0]["next_command"] = "wrong_command"
        wrong_terminal_command = self._ready_result_review_manual()
        wrong_terminal_command["terminal_continuation_records"][0]["next_command"] = "wrong_command"

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
                source
            )
            for source in [unknown_gate, unsupported_route, wrong_command, wrong_terminal_command]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_contract"
                for report in reports
            )
        )
        self.assertIn("routed_next_gate_unknown:unknown_gate", reports[0]["blocking_reasons"])
        self.assertIn("downstream_route_type_not_allowed:manual_acceptance", reports[1]["blocking_reasons"])
        self.assertIn("selected_route_record_next_command_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("terminal_downstream_record_next_command_mismatch:manual_acceptance", reports[3]["blocking_reasons"])

    def test_bdd_p7bi_boundary_violations_block_entry(self) -> None:
        """行为 7：P7-BH 出现执行、导出、写回或边界越权信号时阻断。"""
        source_ran = self._ready_result_review_export("pdf_export")
        source_ran["this_command_ran_continuation"] = True
        source_executed = self._ready_result_review_export("pdf_export")
        source_executed["selected_route_executed"] = True
        source_wrote = self._ready_result_review_export("pdf_export")
        source_wrote["can_write_product_state"] = True
        source_flag = self._ready_result_review_export("pdf_export")
        source_flag["boundary_flags"]["wrote_formal_state"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
                source
            )
            for source in [source_ran, source_executed, source_wrote, source_flag]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_boundary"
                for report in reports
            )
        )
        self.assertIn("result_review_ran_continuation", reports[0]["blocking_reasons"])
        self.assertIn("result_review_selected_route_executed", reports[1]["blocking_reasons"])
        self.assertIn("result_review_allows_product_state_write", reports[2]["blocking_reasons"])
        self.assertIn("result_review_boundary_violation:wrote_formal_state", reports[3]["blocking_reasons"])

    def test_bdd_p7bi_writes_downstream_entry_only_and_cli_defaults_blocked(self) -> None:
        """行为 8：只写 P7-BI report/review；CLI 默认读取当前 blocked P7-BH。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
                self._ready_result_review_export("pdf_export")
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(
                written["status"],
                "ready_for_manifested_routed_next_gate_result_continuation_execute_downstream_gate_entry",
            )
            self.assertEqual(len(written["downstream_input_records"]), 1)
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry.json"
                ).exists()
            )

            source_path = (
                project_root
                / (
                    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                    "continuation_execute_result_review.json"
                )
            )
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(json.dumps(self._blocked_result_review()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    (
                        "Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                        "continuation_execute_result_downstream_gate_entry.py"
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
                "status=blocked_by_manifested_routed_next_gate_result_continuation_execute_result_review",
                result.stdout,
            )
            self.assertIn("downstream_gate_entry_recorded=false", result.stdout)
            self.assertIn("downstream_input_records=0", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)

    def _ready_result_review_export(self, route_type: str) -> dict:
        routed_action, next_command, planned_outputs = self._route_mapping(route_type)
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_review.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_routed_next_gate_result_continuation_executed",
            "status": "manifested_routed_next_gate_result_continuation_execute_result_review_ready",
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "continuation_status": "ready_for_selected_formal_package_route_execution_review",
            "selected_route_preflight_status": "ready_for_selected_formal_package_route_execution_review",
            "terminal_status": "",
            "continuation_execute_result_reviewed": True,
            "can_continue_after_manifested_routed_next_gate_result_continuation": True,
            "continuation_executed": True,
            "terminal_continuation_recorded": False,
            "this_command_ran_continuation": False,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "selected_route_execution_preflight_records": [
                {
                    "record_id": (
                        "manifested_routed_continuation_result::"
                        f"formal_package_export_acceptance_router::{route_type}"
                    ),
                    "verified_route_type": route_type,
                    "routed_next_gate": "formal_package_export_acceptance_router",
                    "continuation_status": "ready_for_selected_formal_package_route_execution_review",
                    "selected_route_preflight_status": "ready_for_selected_formal_package_route_execution_review",
                    "selected_route_preflight_schema_version": (
                        "p7.auto_mode_formal_package_selected_route_execution_preflight.v1"
                    ),
                    "selected_route_preflight_report_path": (
                        "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
                    ),
                    "selected_route_preflight_review_path": (
                        "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md"
                    ),
                    "routed_action": routed_action,
                    "next_command": next_command,
                    "planned_outputs": planned_outputs,
                    "review_status": "selected_route_preflight_accepted_for_explicit_route_execution",
                    "can_continue_to_selected_route_execution": True,
                }
            ],
            "terminal_continuation_records": [],
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _ready_result_review_manual(self) -> dict:
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_review.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_routed_next_gate_terminal_continuation_recorded",
            "status": "manifested_routed_next_gate_result_continuation_execute_result_review_ready",
            "verified_route_type": "manual_acceptance",
            "routed_next_gate": "formal_package_delivery_completion_gate",
            "continuation_status": "terminal_delivery_completion_ready_for_product_review",
            "selected_route_preflight_status": "",
            "terminal_status": "terminal_delivery_completion_ready_for_product_review",
            "continuation_execute_result_reviewed": True,
            "can_continue_after_manifested_routed_next_gate_result_continuation": True,
            "continuation_executed": False,
            "terminal_continuation_recorded": True,
            "this_command_ran_continuation": False,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "selected_route_execution_preflight_records": [],
            "terminal_continuation_records": [
                {
                    "record_id": (
                        "manifested_routed_terminal_continuation::"
                        "formal_package_delivery_completion_gate::manual_acceptance"
                    ),
                    "verified_route_type": "manual_acceptance",
                    "routed_next_gate": "formal_package_delivery_completion_gate",
                    "terminal_status": "terminal_delivery_completion_ready_for_product_review",
                    "terminal_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
                    "terminal_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
                    "next_command": "product_review_preparation",
                    "review_status": "terminal_continuation_accepted_for_product_review_preparation",
                    "can_continue_to_product_review_preparation": True,
                }
            ],
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_result_review(self) -> dict:
        report = self._ready_result_review_export("pdf_export")
        report["source_status"] = "blocked_by_manifested_routed_next_gate_result_continuation_gate_entry"
        report["status"] = "blocked_by_manifested_routed_next_gate_result_continuation_execute_gate"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["continuation_status"] = ""
        report["selected_route_preflight_status"] = ""
        report["continuation_execute_result_reviewed"] = False
        report["can_continue_after_manifested_routed_next_gate_result_continuation"] = False
        report["continuation_executed"] = False
        report["selected_route_execution_preflight_records"] = []
        report["blocking_reasons"] = [
            "manifested_routed_next_gate_result_continuation_execute_gate_not_completed"
        ]
        return report

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
            "reviewed_manifested_routed_next_gate_result_continuation_execute_result": False,
        }

    def _source_paths(self) -> dict:
        return {
            "manifested_routed_next_gate_command_result_continuation_execute_result_review": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

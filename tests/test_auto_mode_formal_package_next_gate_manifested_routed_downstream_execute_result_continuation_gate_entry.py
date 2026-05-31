import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry import (
    build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry,
    write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedDownstreamExecuteResultContinuationGateEntryTests(
    unittest.TestCase
):
    """BDD: P7-BL converts P7-BK result review into the next continuation entry."""

    def test_bdd_p7bl_export_review_creates_artifact_executor_continuation_input(self) -> None:
        """行为 1：export ready result 转成 artifact executor continuation 入口。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
            self._ready_export_review("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry.v1",
        )
        self.assertEqual(
            report["status"],
            "ready_for_manifested_routed_downstream_execute_result_continuation_gate_entry",
        )
        self.assertTrue(report["downstream_execute_result_continuation_gate_entry_recorded"])
        self.assertTrue(report["can_request_downstream_execute_result_continuation"])
        self.assertTrue(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["continuation_kind"], "route_specific_artifact_executor_continuation")
        self.assertEqual(len(report["continuation_input_records"]), 1)
        record = report["continuation_input_records"][0]
        self.assertEqual(
            record["record_id"],
            "manifested_routed_downstream_execute_result_continuation::route_specific_artifact_executor::pdf_export",
        )
        self.assertEqual(record["continuation_kind"], "route_specific_artifact_executor_continuation")
        self.assertEqual(record["next_command"], "auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry")
        self.assertEqual(
            record["next_report_path"],
            "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json",
        )
        self.assertEqual(
            record["selected_route_execute_report_path"],
            "Results/json/auto_mode_formal_package_selected_route_execute.json",
        )
        self.assertTrue(record["requires_explicit_continuation_command"])
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bl_manual_review_creates_product_review_packet_input(self) -> None:
        """行为 2：manual terminal result 转成 product-review packet 入口。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
            self._ready_manual_review(),
        )

        self.assertEqual(
            report["status"],
            "ready_for_manifested_routed_downstream_execute_result_continuation_gate_entry",
        )
        self.assertTrue(report["downstream_execute_result_continuation_gate_entry_recorded"])
        self.assertTrue(report["can_request_downstream_execute_result_continuation"])
        self.assertFalse(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["continuation_kind"], "product_review_packet_continuation")
        self.assertEqual(len(report["continuation_input_records"]), 1)
        record = report["continuation_input_records"][0]
        self.assertEqual(record["continuation_kind"], "product_review_packet_continuation")
        self.assertEqual(record["next_command"], "product_review_packet")
        self.assertEqual(record["command_path"], "")
        self.assertEqual(record["terminal_status"], "terminal_delivery_completion_ready_for_product_review")
        self.assertFalse(record["requires_explicit_continuation_command"])
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bl_current_blocked_result_review_blocks_entry(self) -> None:
        """行为 3：当前 P7-BK blocked 时不生成 continuation input。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
            self._blocked_review(),
        )

        self.assertEqual(
            report["status"],
            "blocked_by_manifested_routed_next_gate_downstream_execute_result_review",
        )
        self.assertFalse(report["downstream_execute_result_continuation_gate_entry_recorded"])
        self.assertFalse(report["can_request_downstream_execute_result_continuation"])
        self.assertEqual(report["continuation_input_records"], [])
        self.assertIn(
            "manifested_routed_next_gate_downstream_execute_result_review_not_ready",
            report["blocking_reasons"],
        )

    def test_bdd_p7bl_missing_invalid_or_not_ready_result_review_blocks_entry(self) -> None:
        """行为 4：P7-BK 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._ready_export_review("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        no_continue = self._ready_export_review("pdf_export")
        no_continue["can_continue_after_downstream_execute"] = False
        blocked = self._ready_export_review("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
                source
            )
            for source in [{}, wrong_schema, no_continue, blocked]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_downstream_execute_result_review"
                for report in reports
            )
        )
        self.assertIn(
            "manifested_routed_next_gate_downstream_execute_result_review_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_downstream_execute_result_review_missing_or_invalid_schema",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_downstream_execute_result_review_cannot_continue",
            reports[2]["blocking_reasons"],
        )
        self.assertIn("source_downstream_execute_result_review_has_blocking_reasons", reports[3]["blocking_reasons"])

    def test_bdd_p7bl_export_record_must_be_single_accepted_and_matching(self) -> None:
        """行为 5：export continuation record 必须单一、匹配、已接受且可继续。"""
        missing = self._ready_export_review("pdf_export")
        missing["route_specific_artifact_executor_input_records"] = []
        duplicated = self._ready_export_review("pdf_export")
        duplicated["route_specific_artifact_executor_input_records"].append(
            dict(duplicated["route_specific_artifact_executor_input_records"][0])
        )
        route_mismatch = self._ready_export_review("pdf_export")
        route_mismatch["route_specific_artifact_executor_input_records"][0]["verified_route_type"] = "docx_export"
        not_accepted = self._ready_export_review("pdf_export")
        not_accepted["route_specific_artifact_executor_input_records"][0]["review_status"] = "waiting"
        cannot_continue = self._ready_export_review("pdf_export")
        cannot_continue["route_specific_artifact_executor_input_records"][0][
            "can_continue_to_route_specific_artifact_executor"
        ] = False

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
                source
            )
            for source in [missing, duplicated, route_mismatch, not_accepted, cannot_continue]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_downstream_execute_result_continuation_contract"
                for report in reports
            )
        )
        self.assertIn("route_specific_artifact_executor_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("route_specific_artifact_executor_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("continuation_record_route_type_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("route_specific_artifact_executor_input_record_not_accepted:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("route_specific_artifact_executor_input_record_cannot_continue:pdf_export", reports[4]["blocking_reasons"])

    def test_bdd_p7bl_manual_record_must_be_single_accepted_and_unmixed(self) -> None:
        """行为 6：manual continuation record 必须单一、匹配、已接受且不能混入 artifact record。"""
        missing = self._ready_manual_review()
        missing["product_review_preparation_result_records"] = []
        duplicated = self._ready_manual_review()
        duplicated["product_review_preparation_result_records"].append(
            dict(duplicated["product_review_preparation_result_records"][0])
        )
        not_accepted = self._ready_manual_review()
        not_accepted["product_review_preparation_result_records"][0]["review_status"] = "waiting"
        mixed = self._ready_manual_review()
        mixed["route_specific_artifact_executor_input_records"] = [
            self._artifact_input_record("manual_acceptance")
        ]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
                source
            )
            for source in [missing, duplicated, not_accepted, mixed]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_downstream_execute_result_continuation_contract"
                for report in reports
            )
        )
        self.assertIn("product_review_preparation_result_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("product_review_preparation_result_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("product_review_preparation_result_record_not_accepted:manual_acceptance", reports[2]["blocking_reasons"])
        self.assertIn("unexpected_continuation_record_set:route_specific_artifact_executor_input_records", reports[3]["blocking_reasons"])

    def test_bdd_p7bl_boundary_violations_block_entry(self) -> None:
        """行为 7：P7-BK 出现执行、导出、写回或边界越权信号时阻断。"""
        source_ran = self._ready_export_review("pdf_export")
        source_ran["this_command_ran_downstream_command"] = True
        source_executed = self._ready_export_review("pdf_export")
        source_executed["route_specific_artifact_executed"] = True
        source_wrote = self._ready_export_review("pdf_export")
        source_wrote["can_write_product_state"] = True
        source_flag = self._ready_export_review("pdf_export")
        source_flag["boundary_flags"]["wrote_formal_state"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
                source
            )
            for source in [source_ran, source_executed, source_wrote, source_flag]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_downstream_execute_result_continuation_boundary"
                for report in reports
            )
        )
        self.assertIn("downstream_execute_result_review_ran_downstream_command", reports[0]["blocking_reasons"])
        self.assertIn("downstream_execute_result_review_executed_route_specific_artifact", reports[1]["blocking_reasons"])
        self.assertIn("downstream_execute_result_review_allows_product_state_write", reports[2]["blocking_reasons"])
        self.assertIn("downstream_execute_result_review_boundary_violation:wrote_formal_state", reports[3]["blocking_reasons"])

    def test_bdd_p7bl_writes_continuation_entry_only_and_cli_defaults_blocked(self) -> None:
        """行为 8：只写 P7-BL report/review；CLI 默认读取当前 blocked P7-BK。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
                self._ready_export_review("pdf_export")
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(
                written["status"],
                "ready_for_manifested_routed_downstream_execute_result_continuation_gate_entry",
            )
            self.assertEqual(len(written["continuation_input_records"]), 1)
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry.json"
                ).exists()
            )

            source_path = (
                project_root
                / (
                    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                    "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.json"
                )
            )
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(json.dumps(self._blocked_review()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_manifested_routed_next_gate_downstream_execute_result_review", result.stdout)
            self.assertIn("downstream_execute_result_continuation_gate_entry_recorded=false", result.stdout)
            self.assertIn("can_request_downstream_execute_result_continuation=false", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)

    def _ready_export_review(self, route_type: str) -> dict:
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.v1"
            ),
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_routed_next_gate_downstream_selected_route_execute_command_executed",
            "status": "manifested_routed_next_gate_downstream_execute_result_review_ready",
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "downstream_kind": "selected_route_execution",
            "downstream_execute_result_reviewed": True,
            "can_continue_after_downstream_execute": True,
            "selected_route_execute_manifest_recorded": True,
            "product_review_preparation_recorded": False,
            "this_command_ran_downstream_command": False,
            "route_specific_artifact_executed": False,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "route_specific_artifact_executor_input_records": [
                self._artifact_input_record(route_type),
            ],
            "product_review_preparation_result_records": [],
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _ready_manual_review(self) -> dict:
        report = self._ready_export_review("manual_acceptance")
        report["source_status"] = "manifested_routed_next_gate_downstream_product_review_preparation_recorded"
        report["status"] = "manifested_routed_next_gate_product_review_preparation_result_review_ready"
        report["routed_next_gate"] = "formal_package_delivery_completion_gate"
        report["downstream_kind"] = "product_review_preparation"
        report["selected_route_execute_manifest_recorded"] = False
        report["product_review_preparation_recorded"] = True
        report["route_specific_artifact_executor_input_records"] = []
        report["product_review_preparation_result_records"] = [
            {
                "record_id": (
                    "manifested_routed_downstream_execute_result_review::"
                    "product_review_preparation::manual_acceptance"
                ),
                "verified_route_type": "manual_acceptance",
                "routed_next_gate": "formal_package_delivery_completion_gate",
                "downstream_kind": "product_review_preparation",
                "terminal_status": "terminal_delivery_completion_ready_for_product_review",
                "next_report_path": "Results/json/auto_mode_formal_package_product_review_preparation.json",
                "next_review_path": "Reviews/auto_mode_formal_package_product_review_preparation.md",
                "terminal_completion": True,
                "review_status": "product_review_preparation_accepted_for_product_review_packet",
                "can_continue_to_product_review_packet": True,
            }
        ]
        return report

    def _blocked_review(self) -> dict:
        report = self._ready_export_review("pdf_export")
        report["source_status"] = "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry"
        report["status"] = "blocked_by_manifested_routed_next_gate_downstream_execute_gate"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["downstream_kind"] = ""
        report["downstream_execute_result_reviewed"] = False
        report["can_continue_after_downstream_execute"] = False
        report["selected_route_execute_manifest_recorded"] = False
        report["route_specific_artifact_executor_input_records"] = []
        report["product_review_preparation_result_records"] = []
        report["blocking_reasons"] = [
            "manifested_routed_next_gate_downstream_execute_gate_not_completed",
        ]
        return report

    def _artifact_input_record(self, route_type: str) -> dict:
        return {
            "record_id": (
                "manifested_routed_downstream_execute_result_review::"
                f"route_specific_artifact_executor::{route_type}"
            ),
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "downstream_kind": "selected_route_execution",
            "selected_route_execute_status": "selected_route_execute_manifest_recorded",
            "selected_route_execute_report_path": "Results/json/auto_mode_formal_package_selected_route_execute.json",
            "selected_route_execute_review_path": "Reviews/auto_mode_formal_package_selected_route_execute.md",
            "selected_route_execute_manifest_path": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
            "operation_id": f"selected_route_execute::{route_type}",
            "route_execution_id": "selected_formal_package_route_execution::formal_pdf_export_preflight",
            "routed_action": "formal_pdf_export_preflight",
            "next_command": "formal_pdf_export_execute",
            "planned_outputs": ["Submissions/formal_package/paper.pdf"],
            "review_status": "selected_route_execute_manifest_accepted_for_route_specific_artifact_executor",
            "can_continue_to_route_specific_artifact_executor": True,
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
            "manifested_routed_downstream_execute_result_review": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

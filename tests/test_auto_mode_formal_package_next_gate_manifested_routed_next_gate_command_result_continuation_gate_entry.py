import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry import (
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateCommandResultContinuationGateEntryTests(unittest.TestCase):
    """BDD: P7-BF converts a reviewed P7-BE delegated result into continuation input."""

    def test_bdd_p7bf_export_router_result_creates_selected_route_continuation_input(self) -> None:
        """行为 1：export router delegated result 变成 selected route execution preflight 输入。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
            self._ready_result_review("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.v1",
        )
        self.assertEqual(
            report["status"],
            "ready_for_manifested_routed_next_gate_command_result_continuation_gate_entry",
        )
        self.assertTrue(report["command_result_continuation_gate_entry_recorded"])
        self.assertTrue(report["can_request_manifested_routed_next_gate_result_continuation"])
        self.assertTrue(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(len(report["continuation_input_records"]), 1)
        record = report["continuation_input_records"][0]
        self.assertEqual(
            record["record_id"],
            "manifested_routed_next_gate_command_result_continuation::"
            "formal_package_export_acceptance_router::pdf_export",
        )
        self.assertEqual(record["continuation_kind"], "selected_route_execution_preflight")
        self.assertEqual(record["next_command"], "auto_mode_formal_package_selected_route_execution_preflight")
        self.assertEqual(record["command_path"], "Program/auto_mode_formal_package_selected_route_execution_preflight.py")
        self.assertEqual(record["source_report_path"], "Results/json/auto_mode_formal_package_export_acceptance_router.json")
        self.assertEqual(record["next_report_path"], "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json")
        self.assertEqual(record["continuation_status"], "pending_explicit_continuation_command")
        self.assertTrue(record["requires_explicit_continuation_command"])
        self.assertFalse(report["continuation_executed"])
        self.assertFalse(report["this_command_ran_continuation"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bf_delivery_completion_result_creates_terminal_continuation_input(self) -> None:
        """行为 2：manual acceptance completion 输出变成终态交付记录输入。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
            self._ready_result_review("manual_acceptance")
        )

        self.assertEqual(
            report["status"],
            "ready_for_manifested_routed_next_gate_command_result_continuation_gate_entry",
        )
        self.assertTrue(report["command_result_continuation_gate_entry_recorded"])
        self.assertTrue(report["can_request_manifested_routed_next_gate_result_continuation"])
        self.assertFalse(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["routed_next_gate"], "formal_package_delivery_completion_gate")
        self.assertEqual(len(report["continuation_input_records"]), 1)
        record = report["continuation_input_records"][0]
        self.assertEqual(record["continuation_kind"], "delivery_completion_terminal_record")
        self.assertEqual(record["next_command"], "none")
        self.assertEqual(record["continuation_status"], "terminal_delivery_completion_ready_for_product_review")
        self.assertTrue(record["completion_terminal"])
        self.assertFalse(record["requires_explicit_continuation_command"])

    def test_bdd_p7bf_current_blocked_result_review_blocks_continuation_input(self) -> None:
        """行为 3：当前 P7-BE blocked 时不生成 continuation input。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
            self._blocked_result_review(),
        )

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_command_result_review")
        self.assertFalse(report["command_result_continuation_gate_entry_recorded"])
        self.assertFalse(report["can_request_manifested_routed_next_gate_result_continuation"])
        self.assertFalse(report["requires_explicit_continuation_command"])
        self.assertEqual(report["continuation_input_records"], [])
        self.assertIn("manifested_routed_next_gate_command_result_review_not_ready", report["blocking_reasons"])

    def test_bdd_p7bf_missing_invalid_or_not_ready_result_review_blocks_gate_entry(self) -> None:
        """行为 4：P7-BE 缺失、schema 错或未 ready 时阻断。"""
        missing = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry({})
        wrong_schema = self._ready_result_review("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        no_continue = self._ready_result_review("pdf_export")
        no_continue["can_continue_after_manifested_routed_next_gate_command"] = False

        wrong_report = (
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
                wrong_schema
            )
        )
        no_continue_report = (
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
                no_continue
            )
        )

        self.assertEqual(missing["status"], "blocked_by_manifested_routed_next_gate_command_result_review")
        self.assertIn("manifested_routed_next_gate_command_result_review_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(wrong_report["status"], "blocked_by_manifested_routed_next_gate_command_result_review")
        self.assertIn("manifested_routed_next_gate_command_result_review_missing_or_invalid_schema", wrong_report["blocking_reasons"])
        self.assertEqual(no_continue_report["status"], "blocked_by_manifested_routed_next_gate_command_result_review")
        self.assertIn("manifested_routed_next_gate_command_result_review_cannot_continue", no_continue_report["blocking_reasons"])

    def test_bdd_p7bf_result_record_must_match_top_level_contract(self) -> None:
        """行为 5：delegated result record 必须和顶层 route/gate/status/path 一致。"""
        route_mismatch = self._ready_result_review("pdf_export")
        route_mismatch["delegated_result_records"][0]["verified_route_type"] = "docx_export"
        path_mismatch = self._ready_result_review("pdf_export")
        path_mismatch["delegated_result_records"][0]["delegated_report_path"] = "Results/json/wrong.json"
        status_mismatch = self._ready_result_review("pdf_export")
        status_mismatch["delegated_result_records"][0]["delegated_status"] = "waiting"

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
                source
            )
            for source in [route_mismatch, path_mismatch, status_mismatch]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_command_result_continuation_contract"
                for report in reports
            )
        )
        self.assertIn("delegated_result_record_route_type_mismatch:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("delegated_result_record_report_path_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("delegated_result_record_status_mismatch:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7bf_unknown_gate_or_route_blocks_continuation_contract(self) -> None:
        """行为 6：未知 gate 或不支持 route type 时阻断。"""
        unknown_gate = self._ready_result_review("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        unknown_gate["delegated_result_records"][0]["routed_next_gate"] = "unknown_gate"
        unsupported_route = self._ready_result_review("manual_acceptance")
        unsupported_route["routed_next_gate"] = "formal_package_export_acceptance_router"
        unsupported_route["delegated_result_records"][0]["routed_next_gate"] = "formal_package_export_acceptance_router"

        unknown_report = (
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
                unknown_gate
            )
        )
        unsupported_report = (
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
                unsupported_route
            )
        )

        self.assertEqual(
            unknown_report["status"],
            "blocked_by_manifested_routed_next_gate_command_result_continuation_contract",
        )
        self.assertIn("routed_next_gate_unknown:unknown_gate", unknown_report["blocking_reasons"])
        self.assertEqual(
            unsupported_report["status"],
            "blocked_by_manifested_routed_next_gate_command_result_continuation_contract",
        )
        self.assertIn(
            "manifested_routed_result_continuation_route_type_not_allowed:manual_acceptance",
            unsupported_report["blocking_reasons"],
        )

    def test_bdd_p7bf_boundary_violations_block_gate_entry(self) -> None:
        """行为 7：P7-BE 出现运行命令、进入下一关或写正式层信号时阻断。"""
        source = self._ready_result_review("pdf_export")
        source["this_command_ran_next_gate_command"] = True
        source["this_command_entered_next_gate"] = True
        source["can_write_product_state"] = True
        source["boundary_flags"]["wrote_formal_state"] = True

        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
            source
        )

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_command_result_continuation_boundary")
        self.assertIn("result_review_ran_next_gate_command", report["blocking_reasons"])
        self.assertIn("result_review_entered_next_gate", report["blocking_reasons"])
        self.assertIn("result_review_allows_product_state_write", report["blocking_reasons"])
        self.assertIn("result_review_boundary_violation:wrote_formal_state", report["blocking_reasons"])

    def test_bdd_p7bf_writes_continuation_gate_entry_only_and_cli_defaults_blocked(self) -> None:
        """行为 8：只写 P7-BF report/review；CLI 默认读取当前 blocked P7-BE。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
                self._ready_result_review("pdf_export")
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(
                written["status"],
                "ready_for_manifested_routed_next_gate_command_result_continuation_gate_entry",
            )
            self.assertEqual(len(written["continuation_input_records"]), 1)
            self.assertFalse(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.json"
                ).exists()
            )

            source_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.json"
            )
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(json.dumps(self._blocked_result_review()), encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    (
                        "Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                        "continuation_gate_entry.py"
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
            self.assertIn("status=blocked_by_manifested_routed_next_gate_command_result_review", result.stdout)
            self.assertIn("can_request_manifested_routed_next_gate_result_continuation=false", result.stdout)
            self.assertIn("continuation_input_records=0", result.stdout)

    def _ready_result_review(self, route_type: str) -> dict:
        gate_id, delegated_status, delegated_schema, report_path, review_path = self._route_mapping(route_type)
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_routed_next_gate_command_execute_gate_entry_executed",
            "status": "manifested_routed_next_gate_command_execute_gate_entry_result_review_ready",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "delegated_status": delegated_status,
            "command_execute_gate_entry_result_reviewed": True,
            "can_continue_after_manifested_routed_next_gate_command": True,
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
                    "record_id": f"manifested_routed_next_gate_command_result::{gate_id}::{route_type}",
                    "verified_route_type": route_type,
                    "routed_next_gate": gate_id,
                    "delegated_status": delegated_status,
                    "delegated_schema_version": delegated_schema,
                    "delegated_report_path": report_path,
                    "delegated_review_path": review_path,
                    "review_status": "delegated_next_gate_result_accepted_for_continuation",
                    "can_continue_after_manifested_routed_next_gate_command": True,
                }
            ],
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_result_review(self) -> dict:
        report = self._ready_result_review("pdf_export")
        report["source_status"] = "blocked_by_manifested_routed_next_gate_run_preflight"
        report["status"] = "blocked_by_manifested_routed_next_gate_command_execute_gate_entry"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["delegated_status"] = ""
        report["command_execute_gate_entry_result_reviewed"] = False
        report["can_continue_after_manifested_routed_next_gate_command"] = False
        report["next_gate_command_executed"] = False
        report["next_gate_entered"] = False
        report["delegated_result_records"] = []
        report["blocking_reasons"] = ["command_execute_gate_entry_not_completed"]
        return report

    def _route_mapping(self, route_type: str) -> tuple[str, str, str, str, str]:
        if route_type == "manual_acceptance":
            return (
                "formal_package_delivery_completion_gate",
                "formal_package_delivery_review_ready",
                "p7.auto_mode_formal_package_delivery_completion_gate.v1",
                "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
                "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
            )
        return (
            "formal_package_export_acceptance_router",
            "formal_package_export_acceptance_route_recorded",
            "p7.auto_mode_formal_package_export_acceptance_router.v1",
            "Results/json/auto_mode_formal_package_export_acceptance_router.json",
            "Reviews/auto_mode_formal_package_export_acceptance_router.md",
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
            "executed_selected_route": False,
            "exported_or_accepted_formal_package": False,
            "entered_explicit_routed_next_gate_entry": False,
            "ran_manifested_routed_next_gate_command": False,
            "reviewed_manifested_routed_next_gate_command_result": False,
        }

    def _source_paths(self) -> dict:
        return {
            "manifested_routed_next_gate_command_execute_gate_entry_result_review": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

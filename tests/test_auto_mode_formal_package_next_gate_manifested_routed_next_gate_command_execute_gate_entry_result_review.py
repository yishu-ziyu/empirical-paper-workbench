import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review import (
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateCommandExecuteGateEntryResultReviewTests(unittest.TestCase):
    """BDD: P7-BE reviews the P7-BD delegated command result without running commands."""

    def test_bdd_p7be_executed_gate_entry_with_successful_delegated_result_is_review_ready(self) -> None:
        """行为 1：P7-BD 已成功委托并记录 delegated success 时可继续。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(
            self._executed_gate_entry("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.v1",
        )
        self.assertEqual(report["status"], "manifested_routed_next_gate_command_execute_gate_entry_result_review_ready")
        self.assertTrue(report["command_execute_gate_entry_result_reviewed"])
        self.assertTrue(report["can_continue_after_manifested_routed_next_gate_command"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(report["delegated_status"], "formal_package_export_acceptance_route_recorded")
        self.assertEqual(len(report["delegated_result_records"]), 1)
        record = report["delegated_result_records"][0]
        self.assertEqual(record["review_status"], "delegated_next_gate_result_accepted_for_continuation")
        self.assertEqual(record["delegated_report_path"], "Results/json/auto_mode_formal_package_export_acceptance_router.json")
        self.assertTrue(report["next_gate_command_executed"])
        self.assertFalse(report["this_command_ran_next_gate_command"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7be_current_blocked_gate_entry_blocks_result_review(self) -> None:
        """行为 2：当前 blocked P7-BD 没有 delegated result 可审阅。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(
            self._blocked_gate_entry()
        )

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_command_execute_gate_entry")
        self.assertFalse(report["command_execute_gate_entry_result_reviewed"])
        self.assertFalse(report["can_continue_after_manifested_routed_next_gate_command"])
        self.assertEqual(report["delegated_result_records"], [])
        self.assertIn("command_execute_gate_entry_not_executed", report["blocking_reasons"])

    def test_bdd_p7be_missing_invalid_or_unexecuted_gate_entry_blocks_review(self) -> None:
        """行为 3：P7-BD 缺失、schema 错、未执行或有 blockers 时阻断。"""
        wrong_schema = self._executed_gate_entry("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        unexecuted = self._executed_gate_entry("pdf_export")
        unexecuted["status"] = "ready_to_execute_manifested_routed_next_gate_command"
        unexecuted["command_execute_gate_entry_executed"] = False
        blocked = self._executed_gate_entry("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(source)
            for source in [{}, wrong_schema, unexecuted, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry" for report in reports)
        )
        self.assertIn("command_execute_gate_entry_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("command_execute_gate_entry_missing_or_invalid_schema", reports[1]["blocking_reasons"])
        self.assertIn("command_execute_gate_entry_not_completed", reports[2]["blocking_reasons"])
        self.assertIn("source_command_execute_gate_entry_has_blocking_reasons", reports[3]["blocking_reasons"])

    def test_bdd_p7be_delegated_contract_must_be_complete_and_matching(self) -> None:
        """行为 4：delegated returncode、status、report path、review path 必须匹配。"""
        bad_return = self._executed_gate_entry("pdf_export")
        bad_return["delegated_returncode"] = 1
        missing_status = self._executed_gate_entry("pdf_export")
        missing_status["delegated_status"] = ""
        wrong_report = self._executed_gate_entry("pdf_export")
        wrong_report["delegated_report_path"] = "Results/json/wrong.json"
        wrong_review = self._executed_gate_entry("pdf_export")
        wrong_review["delegated_review_path"] = "Reviews/wrong.md"

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(source)
            for source in [bad_return, missing_status, wrong_report, wrong_review]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_result_contract" for report in reports)
        )
        self.assertIn("delegated_returncode_not_zero", reports[0]["blocking_reasons"])
        self.assertIn("delegated_status_missing", reports[1]["blocking_reasons"])
        self.assertIn("delegated_report_path_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("delegated_review_path_mismatch:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7be_delegated_result_summary_must_be_successful(self) -> None:
        """行为 5：delegated result summary 缺失、schema 错、有 blockers 或非成功时阻断。"""
        missing_summary = self._executed_gate_entry("pdf_export")
        missing_summary["delegated_result"] = {}
        wrong_schema = self._executed_gate_entry("pdf_export")
        wrong_schema["delegated_result"]["delegated_report_summary"]["schema_version"] = "wrong.schema"
        blocked_summary = self._executed_gate_entry("pdf_export")
        blocked_summary["delegated_result"]["delegated_report_summary"]["blocking_reasons"] = ["delegated_blocked"]
        not_success = self._executed_gate_entry("pdf_export")
        not_success["delegated_result"]["delegated_report_summary"]["status"] = "waiting_for_formal_package_export_acceptance_decision"

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(source)
            for source in [missing_summary, wrong_schema, blocked_summary, not_success]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_delegated_next_gate_result" for report in reports)
        )
        self.assertIn("delegated_result_summary_missing:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("delegated_result_summary_schema_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("delegated_result_summary_has_blocking_reasons:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("delegated_result_summary_status_not_success:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7be_boundary_violations_block_review(self) -> None:
        """行为 6：P7-BD 出现写正式层、写产品状态或边界越权时阻断。"""
        source = self._executed_gate_entry("pdf_export")
        source["this_command_wrote_formal_state"] = True
        source["can_write_product_state"] = True
        source["boundary_flags"]["wrote_formal_state"] = True

        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(source)

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_boundary")
        self.assertIn("command_execute_gate_entry_wrote_formal_state", report["blocking_reasons"])
        self.assertIn("command_execute_gate_entry_allows_product_state_write", report["blocking_reasons"])
        self.assertIn("command_execute_gate_entry_boundary_violation:wrote_formal_state", report["blocking_reasons"])

    def test_bdd_p7be_writes_result_review_only(self) -> None:
        """行为 7：只写 P7-BE result review，不运行命令、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(
                self._executed_gate_entry("pdf_export")
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "manifested_routed_next_gate_command_execute_gate_entry_result_review_ready")
            self.assertTrue(written["can_continue_after_manifested_routed_next_gate_command"])
            self.assertFalse((project_root / "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.json").exists())

    def test_bdd_p7be_cli_defaults_to_current_blocked_gate_entry(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-BD，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            gate_entry_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.json"
            )
            gate_entry_path.parent.mkdir(parents=True, exist_ok=True)
            gate_entry_path.write_text(json.dumps(self._blocked_gate_entry()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_manifested_routed_next_gate_command_execute_gate_entry", result.stdout)
            self.assertIn("can_continue_after_manifested_routed_next_gate_command=false", result.stdout)
            self.assertIn("delegated_result_records=0", result.stdout)
            self.assertIn("next_gate_command_executed=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.md"
                ).exists()
            )

    def _executed_gate_entry(self, route_type: str) -> dict:
        gate_id, delegated_status, delegated_schema = self._route_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "ready_for_manifested_routed_next_gate_run_preflight",
            "status": "manifested_routed_next_gate_command_execute_gate_entry_executed",
            "confirm_command_execute": True,
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "can_execute_manifested_routed_next_gate_command": True,
            "requires_explicit_next_gate_command_execute": True,
            "command_execute_gate_entry_executed": True,
            "manifested_command_execute_status": "manifested_next_gate_command_executed",
            "manifested_command_execute_report_path": (
                "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json"
            ),
            "manifested_command_execute_review_path": (
                "Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_execute.md"
            ),
            "delegated_command": ["python3", "Program/auto_mode_formal_package_export_acceptance_router.py"],
            "delegated_report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
            "delegated_review_path": "Reviews/auto_mode_formal_package_export_acceptance_router.md",
            "delegated_returncode": 0,
            "delegated_status": delegated_status,
            "delegated_result": {
                "returncode": 0,
                "status": delegated_status,
                "report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
                "review_path": "Reviews/auto_mode_formal_package_export_acceptance_router.md",
                "delegated_report_summary": {
                    "schema_version": delegated_schema,
                    "status": delegated_status,
                    "blocking_reasons": [],
                },
            },
            "next_gate_command_executed": True,
            "this_command_ran_next_gate_command": True,
            "next_gate_entered": True,
            "this_command_entered_next_gate": True,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_gate_entry(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.v1",
            "status": "blocked_by_manifested_routed_next_gate_run_preflight",
            "command_execute_gate_entry_executed": False,
            "manifested_command_execute_status": "",
            "delegated_command": [],
            "delegated_returncode": None,
            "delegated_status": "",
            "next_gate_command_executed": False,
            "this_command_ran_next_gate_command": False,
            "next_gate_entered": False,
            "this_command_entered_next_gate": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": ["manifested_routed_next_gate_run_preflight_not_ready"],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _route_mapping(self, route_type: str) -> tuple[str, str, str]:
        if route_type == "manual_acceptance":
            return (
                "formal_package_delivery_completion_gate",
                "formal_package_delivery_review_ready",
                "p7.auto_mode_formal_package_delivery_completion_gate.v1",
            )
        return (
            "formal_package_export_acceptance_router",
            "formal_package_export_acceptance_route_recorded",
            "p7.auto_mode_formal_package_export_acceptance_router.v1",
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
        }

    def _source_paths(self) -> dict:
        return {
            "manifested_routed_next_gate_command_execute_gate_entry": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

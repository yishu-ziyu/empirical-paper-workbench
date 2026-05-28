import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_manifested_next_gate_command_result_review import (
    build_auto_mode_formal_package_manifested_next_gate_command_result_review,
    write_auto_mode_formal_package_manifested_next_gate_command_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageManifestedNextGateCommandResultReviewTests(unittest.TestCase):
    """BDD: P7-AJ reviews delegated next-gate output after P7-AI execution."""

    def test_bdd_p7aj_executed_pdf_next_gate_command_with_route_recorded_output_is_review_ready(self) -> None:
        """行为 1：已执行 PDF 下一关命令且 delegated router route recorded 时可继续。"""
        report = build_auto_mode_formal_package_manifested_next_gate_command_result_review(
            Path("."),
            self._execute_report("pdf_export"),
            self._delegated_router_report("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_manifested_next_gate_command_result_review.v1",
        )
        self.assertEqual(report["status"], "manifested_next_gate_command_result_review_ready")
        self.assertTrue(report["delegated_next_gate_result_reviewed"])
        self.assertTrue(report["can_continue_after_delegated_next_gate"])
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

    def test_bdd_p7aj_current_blocked_execute_report_blocks_result_review(self) -> None:
        """行为 2：当前 P7-AI blocked 时没有 delegated result 可审阅。"""
        report = build_auto_mode_formal_package_manifested_next_gate_command_result_review(
            Path("."),
            {},
            {},
        )

        self.assertEqual(report["status"], "blocked_by_manifested_next_gate_command_execute")
        self.assertFalse(report["delegated_next_gate_result_reviewed"])
        self.assertFalse(report["can_continue_after_delegated_next_gate"])
        self.assertEqual(report["delegated_result_records"], [])
        self.assertIn("manifested_next_gate_command_execute_missing_or_invalid_schema", report["blocking_reasons"])

    def test_bdd_p7aj_missing_invalid_or_not_completed_execute_report_blocks_review(self) -> None:
        """行为 3：execute report 缺失、schema 错误、未完成或有 blockers 时阻断。"""
        wrong_schema = self._execute_report("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_completed = self._execute_report("pdf_export")
        not_completed["status"] = "blocked_by_manifested_routed_next_gate_command_preflight"
        blocked = self._execute_report("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_manifested_next_gate_command_result_review(
                Path("."),
                source,
                self._delegated_router_report("pdf_export"),
            )
            for source in [wrong_schema, not_completed, blocked]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_manifested_next_gate_command_execute" for report in reports))
        self.assertIn("manifested_next_gate_command_execute_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("manifested_next_gate_command_execute_not_completed", reports[1]["blocking_reasons"])
        self.assertIn("source_execute_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7aj_execute_report_contract_must_match_known_next_gate(self) -> None:
        """行为 4：route type、gate、report path 或 delegated status 错配时阻断。"""
        unknown_gate = self._execute_report("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        wrong_path = self._execute_report("pdf_export")
        wrong_path["delegated_report_path"] = "Results/json/wrong.json"
        status_mismatch = self._execute_report("pdf_export")
        status_mismatch["delegated_status"] = "waiting_for_formal_package_export_acceptance_decision"

        reports = [
            build_auto_mode_formal_package_manifested_next_gate_command_result_review(
                Path("."),
                source,
                self._delegated_router_report("pdf_export"),
            )
            for source in [unknown_gate, wrong_path, status_mismatch]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_manifested_next_gate_command_result_contract" for report in reports)
        )
        self.assertIn("routed_next_gate_unknown:unknown_gate", reports[0]["blocking_reasons"])
        self.assertIn("delegated_report_path_mismatch:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("delegated_status_mismatch:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7aj_delegated_report_must_be_valid_and_successful(self) -> None:
        """行为 5：delegated report 缺失、schema 错误、有 blockers 或非成功状态时阻断。"""
        missing = {}
        wrong_schema = self._delegated_router_report("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        blocked_report = self._delegated_router_report("pdf_export")
        blocked_report["blocking_reasons"] = ["delegated_blocked"]
        not_success = self._delegated_router_report("pdf_export")
        not_success["status"] = "waiting_for_formal_package_export_acceptance_decision"

        reports = [
            build_auto_mode_formal_package_manifested_next_gate_command_result_review(
                Path("."),
                self._execute_report("pdf_export"),
                delegated,
            )
            for delegated in [missing, wrong_schema, blocked_report, not_success]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_delegated_next_gate_report" for report in reports))
        self.assertIn("delegated_next_gate_report_missing_or_invalid_schema:pdf_export", reports[0]["blocking_reasons"])
        self.assertIn("delegated_next_gate_report_missing_or_invalid_schema:pdf_export", reports[1]["blocking_reasons"])
        self.assertIn("delegated_next_gate_report_has_blocking_reasons:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("delegated_next_gate_status_not_success:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7aj_writes_result_review_only(self) -> None:
        """行为 6：只写 result review report/review，不运行命令、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_manifested_next_gate_command_result_review(
                project_root,
                self._execute_report("pdf_export"),
                self._delegated_router_report("pdf_export"),
            )
            report_path, review_path = write_auto_mode_formal_package_manifested_next_gate_command_result_review_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "manifested_next_gate_command_result_review_ready")
            self.assertTrue(written["can_continue_after_delegated_next_gate"])
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_manifested_next_gate_command_result_review.json").exists())

    def test_bdd_p7aj_cli_defaults_to_current_blocked_execute_report(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AI report，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            execute_path = (
                project_root
                / "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json"
            )
            execute_path.parent.mkdir(parents=True, exist_ok=True)
            execute_path.write_text(
                json.dumps({"status": "blocked_by_manifested_routed_next_gate_command_preflight"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_manifested_next_gate_command_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_manifested_next_gate_command_execute", result.stdout)
            self.assertIn("can_continue_after_delegated_next_gate=false", result.stdout)
            self.assertIn("delegated_result_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_manifested_next_gate_command_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_manifested_next_gate_command_result_review.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_manifested_next_gate_command_result_review.json"
                ).exists()
            )

    def _execute_report(self, route_type: str) -> dict:
        gate_id, delegated_status = self._route_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_manifested_routed_next_gate_command_execute.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "ready_for_manifested_routed_next_gate_command_review",
            "status": "manifested_next_gate_command_executed",
            "mode": "execute",
            "confirm_command_execute": True,
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "can_execute_manifested_next_gate_command_with_confirmation": True,
            "requires_explicit_next_gate_command_execute": True,
            "next_gate_command_executed": True,
            "this_command_ran_next_gate_command": True,
            "next_gate_entered": True,
            "this_command_entered_next_gate": True,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
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
            },
            "blocking_reasons": [],
            "command_plan_item": {
                "verified_route_type": route_type,
                "gate_id": gate_id,
                "next_command": "auto_mode_formal_package_export_acceptance_router",
                "command_path": "Program/auto_mode_formal_package_export_acceptance_router.py",
            },
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _delegated_router_report(self, route_type: str) -> dict:
        _gate_id, delegated_status = self._route_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_export_acceptance_router.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": delegated_status,
            "decision": route_type,
            "can_route_export_or_acceptance": True,
            "route_recorded": True,
            "routed_action": "formal_pdf_export_preflight",
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _route_mapping(self, route_type: str) -> tuple[str, str]:
        return (
            "formal_package_export_acceptance_router",
            "formal_package_export_acceptance_route_recorded",
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
        }

    def _source_paths(self) -> dict:
        return {
            "manifested_next_gate_command_execute": (
                "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json"
            ),
            "delegated_report": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
        }

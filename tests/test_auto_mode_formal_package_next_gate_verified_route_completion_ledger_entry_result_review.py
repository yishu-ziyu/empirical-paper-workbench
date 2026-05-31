import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review import (
    build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review,
    write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateVerifiedRouteCompletionLedgerEntryResultReviewTests(unittest.TestCase):
    """BDD: P7-AW reviews P7-AV before the verified route next-gate router."""

    def test_bdd_p7aw_ready_entry_and_clean_ledger_are_review_ready(self) -> None:
        """行为 1：ready P7-AV 和干净 ledger 才放行到 next gate router。"""
        report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
            Path("."),
            self._ready_entry("package_manifest"),
            self._ready_ledger("package_manifest"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.v1",
        )
        self.assertEqual(report["status"], "verified_route_completion_ledger_entry_result_review_ready")
        self.assertTrue(report["verified_route_completion_ledger_entry_result_reviewed"])
        self.assertTrue(report["can_continue_to_verified_route_next_gate_router"])
        self.assertEqual(report["verified_route_type"], "package_manifest")
        self.assertEqual(report["verified_route_completion_ledger_status"], "verified_route_completion_ledger_recorded")
        self.assertTrue(report["route_completion_ledger_recorded"])
        self.assertTrue(report["can_enter_next_auto_mode_gate"])
        self.assertEqual(report["route_completion_record_count"], 1)
        self.assertEqual(len(report["verified_route_next_gate_router_input_records"]), 1)
        record = report["verified_route_next_gate_router_input_records"][0]
        self.assertEqual(
            record["review_status"],
            "verified_route_completion_ledger_entry_accepted_for_next_gate_router",
        )
        self.assertEqual(
            record["verified_route_completion_ledger_report_path"],
            "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json",
        )
        self.assertFalse(report["verified_route_next_gate_router_executed"])
        self.assertFalse(report["this_command_ran_verified_route_next_gate_router"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7aw_current_blocked_entry_blocks_router_review(self) -> None:
        """行为 2：当前 P7-AV blocked 时继续阻断，不生成 router input。"""
        report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
            Path("."),
            {},
            {},
        )

        self.assertEqual(report["status"], "blocked_by_verified_route_completion_ledger_entry")
        self.assertFalse(report["verified_route_completion_ledger_entry_result_reviewed"])
        self.assertFalse(report["can_continue_to_verified_route_next_gate_router"])
        self.assertEqual(report["verified_route_next_gate_router_input_records"], [])
        self.assertIn(
            "verified_route_completion_ledger_entry_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7aw_missing_invalid_or_not_completed_entry_blocks_review(self) -> None:
        """行为 3：P7-AV 缺失、schema 错、未完成或有 blockers 时阻断。"""
        wrong_schema = self._ready_entry("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_completed = self._ready_entry("package_manifest")
        not_completed["status"] = "blocked_by_route_specific_artifact_verification_entry_result_review"
        blocked = self._ready_entry("package_manifest")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
                Path("."),
                source,
                self._ready_ledger("package_manifest"),
            )
            for source in [wrong_schema, not_completed, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_verified_route_completion_ledger_entry" for report in reports)
        )
        self.assertIn("verified_route_completion_ledger_entry_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("verified_route_completion_ledger_entry_not_completed", reports[1]["blocking_reasons"])
        self.assertIn("source_ledger_entry_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7aw_entry_result_must_match_existing_ledger(self) -> None:
        """行为 4：P7-AV 记录的 ledger 路径、状态和摘要必须匹配真实 ledger。"""
        wrong_path = self._ready_entry("package_manifest")
        wrong_path["verified_route_completion_ledger_report_path"] = "Results/json/wrong.json"
        wrong_status = self._ready_entry("package_manifest")
        wrong_status["verified_route_completion_ledger_result"]["status"] = "blocked"
        summary_mismatch = self._ready_entry("package_manifest")
        summary_mismatch["verified_route_completion_ledger_result"]["verified_route_completion_ledger_report_summary"][
            "route_completion_record_count"
        ] = 2

        reports = [
            build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
                Path("."),
                source,
                self._ready_ledger("package_manifest"),
            )
            for source in [wrong_path, wrong_status, summary_mismatch]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_verified_route_completion_ledger_entry_result_contract"
                for report in reports
            )
        )
        self.assertIn("verified_route_completion_ledger_report_path_mismatch:package_manifest", reports[0]["blocking_reasons"])
        self.assertIn("verified_route_completion_ledger_result_status_mismatch:package_manifest", reports[1]["blocking_reasons"])
        self.assertIn(
            "verified_route_completion_ledger_summary_record_count_mismatch:package_manifest",
            reports[2]["blocking_reasons"],
        )

    def test_bdd_p7aw_ledger_must_be_clean_for_router(self) -> None:
        """行为 5：ledger schema、状态、record 和 route 必须干净才能交给 router。"""
        wrong_schema = self._ready_ledger("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_recorded = self._ready_ledger("package_manifest")
        not_recorded["status"] = "blocked_by_route_specific_artifact_verification"
        no_records = self._ready_ledger("package_manifest")
        no_records["route_completion_records"] = []
        route_mismatch = self._ready_ledger("package_manifest")
        route_mismatch["route_completion_records"][0]["route_type"] = "pdf_export"

        reports = [
            build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
                Path("."),
                self._ready_entry("package_manifest"),
                source,
            )
            for source in [wrong_schema, not_recorded, no_records, route_mismatch]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_verified_route_completion_ledger_review" for report in reports)
        )
        self.assertIn("verified_route_completion_ledger_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("verified_route_completion_ledger_status_not_recorded", reports[1]["blocking_reasons"])
        self.assertIn("route_completion_records_missing", reports[2]["blocking_reasons"])
        self.assertIn("route_completion_record_route_mismatch:package_manifest", reports[3]["blocking_reasons"])

    def test_bdd_p7aw_boundary_violations_block_review(self) -> None:
        """行为 6：正式层写入或边界越权标志都会阻断。"""
        entry_boundary = self._ready_entry("package_manifest")
        entry_boundary["can_write_product_state"] = True
        ledger_boundary = self._ready_ledger("package_manifest")
        ledger_boundary["formal_writeback_executed"] = True
        ledger_boundary["boundary_flags"]["modified_product_state"] = True

        entry_report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
            Path("."),
            entry_boundary,
            self._ready_ledger("package_manifest"),
        )
        ledger_report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
            Path("."),
            self._ready_entry("package_manifest"),
            ledger_boundary,
        )

        self.assertEqual(entry_report["status"], "blocked_by_verified_route_completion_ledger_entry")
        self.assertIn("ledger_entry_can_write_product_state", entry_report["blocking_reasons"])
        self.assertEqual(
            ledger_report["status"],
            "blocked_by_verified_route_completion_ledger_entry_result_boundary",
        )
        self.assertIn("verified_route_completion_ledger_formal_writeback_executed", ledger_report["blocking_reasons"])
        self.assertIn(
            "verified_route_completion_ledger_boundary_violation:modified_product_state",
            ledger_report["blocking_reasons"],
        )

    def test_bdd_p7aw_writes_result_review_only(self) -> None:
        """行为 7：只写 P7-AW result review，不运行 router、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
                project_root,
                self._ready_entry("package_manifest"),
                self._ready_ledger("package_manifest"),
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "verified_route_completion_ledger_entry_result_review_ready")
            self.assertFalse(written["verified_route_next_gate_router_executed"])
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.json"
                ).exists()
            )

    def test_bdd_p7aw_cli_defaults_to_current_blocked_entry(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AV，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            entry_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.json"
            )
            entry_path.parent.mkdir(parents=True, exist_ok=True)
            entry_path.write_text(
                json.dumps({"status": "blocked_by_route_specific_artifact_verification_entry_result_review"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_verified_route_completion_ledger_entry", result.stdout)
            self.assertIn("can_continue_to_verified_route_next_gate_router=false", result.stdout)
            self.assertIn("verified_route_next_gate_router_input_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.json"
                ).exists()
            )

    def _ready_entry(self, route_type: str) -> dict:
        ledger = self._ready_ledger(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "route_specific_artifact_verification_entry_result_review_ready",
            "status": "next_gate_verified_route_completion_ledger_entered",
            "verified_route_type": route_type,
            "can_enter_verified_route_completion_ledger": True,
            "verified_route_completion_ledger_entry_command": [
                "python3",
                "Program/auto_mode_formal_package_verified_route_completion_ledger.py",
            ],
            "verified_route_completion_ledger_entry_command_executed": True,
            "this_command_ran_verified_route_completion_ledger": True,
            "verified_route_completion_ledger_report_path": (
                "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json"
            ),
            "verified_route_completion_ledger_review_path": (
                "Reviews/auto_mode_formal_package_verified_route_completion_ledger.md"
            ),
            "verified_route_completion_ledger_returncode": 0,
            "verified_route_completion_ledger_status": "verified_route_completion_ledger_recorded",
            "verified_route_completion_ledger_result": {
                "returncode": 0,
                "status": "verified_route_completion_ledger_recorded",
                "report_path": "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json",
                "review_path": "Reviews/auto_mode_formal_package_verified_route_completion_ledger.md",
                "verified_route_completion_ledger_report_summary": {
                    "schema_version": ledger["schema_version"],
                    "status": ledger["status"],
                    "verified_route_type": ledger["verified_route_type"],
                    "route_completion_ledger_recorded": True,
                    "can_enter_next_auto_mode_gate": True,
                    "route_completion_record_count": 1,
                    "blocking_reasons": [],
                },
            },
            "route_completion_ledger_recorded": True,
            "can_enter_next_auto_mode_gate": True,
            "route_completion_record_count": 1,
            "route_completion_records": ledger["route_completion_records"],
            "route_specific_artifact_verified": True,
            "artifact_verification_record_count": 1,
            "delegated_status": "route_done",
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "rendered_pdf": route_type == "pdf_export",
            "rendered_docx": route_type == "docx_export",
            "package_manifest_generated": route_type == "package_manifest",
            "manual_acceptance_performed": route_type == "manual_acceptance",
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
            "next_action": {"id": "route_verified_completion_to_next_auto_mode_gate"},
        }

    def _ready_ledger(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_verified_route_completion_ledger.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
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
            "route_completion_records": [self._completion_record(route_type)],
            "boundary_flags": self._clean_boundary_flags(),
            "next_action": {"id": "run_next_auto_mode_gate_for_verified_route"},
        }

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
            "entered_next_gate": False,
            "ran_next_gate_command": False,
            "wrote_formal_state": False,
            "executed_selected_route": False,
            "exported_or_accepted_formal_package": False,
            "verified_route_specific_artifact": False,
            "recorded_verified_route_completion_ledger": False,
        }

    def _source_paths(self) -> dict:
        return {
            "verified_route_completion_ledger_entry": (
                "Results/json/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.json"
            ),
            "verified_route_completion_ledger": (
                "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

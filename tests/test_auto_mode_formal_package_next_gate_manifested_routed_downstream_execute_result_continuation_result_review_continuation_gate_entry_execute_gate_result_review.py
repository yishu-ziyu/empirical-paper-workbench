import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review import (
    build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review,
    write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedDownstreamExecuteResultContinuationResultReviewContinuationGateEntryExecuteGateResultReviewTests(
    unittest.TestCase
):
    """BDD: P7-BQ reviews the P7-BP continuation execute gate result."""

    def test_bdd_p7bq_export_entered_with_clean_route_execution_dry_run_is_review_ready(self) -> None:
        """行为 1：export entered + clean route-specific artifact execution dry-run 可继续。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
            Path("."),
            self._export_execute_gate_entered("pdf_export"),
            self._route_specific_artifact_execution("pdf_export"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                "continuation_result_review_continuation_gate_entry_execute_gate_result_review.v1"
            ),
        )
        self.assertEqual(
            report["status"],
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "route_specific_artifact_execution_result_review_ready"
            ),
        )
        self.assertTrue(report["downstream_execute_result_continuation_result_review_continuation_reviewed"])
        self.assertTrue(
            report[
                "can_continue_after_downstream_execute_result_continuation_result_review_continuation"
            ]
        )
        self.assertTrue(report["can_continue_to_route_specific_artifact_execution"])
        self.assertFalse(report["can_continue_to_product_review_packet"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["continuation_kind"], "route_specific_artifact_execution_continuation")
        self.assertTrue(report["route_specific_artifact_execution_result_reviewed"])
        self.assertEqual(report["route_specific_artifact_execution_status"], "route_specific_artifact_execution_dry_run_ready")
        self.assertEqual(len(report["route_specific_artifact_execution_records"]), 1)
        record = report["route_specific_artifact_execution_records"][0]
        self.assertEqual(record["record_id"], "route_specific_artifact_execution_dry_run::pdf_export")
        self.assertEqual(record["review_status"], "route_specific_artifact_execution_dry_run_accepted_for_explicit_execution")
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bq_manual_continuation_recorded_is_review_ready(self) -> None:
        """行为 2：manual product-review packet continuation 可继续到产品审阅包。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
            Path("."),
            self._manual_execute_gate_recorded(),
            {},
        )

        self.assertEqual(
            report["status"],
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "product_review_packet_continuation_result_review_ready"
            ),
        )
        self.assertTrue(report["downstream_execute_result_continuation_result_review_continuation_reviewed"])
        self.assertFalse(report["can_continue_to_route_specific_artifact_execution"])
        self.assertTrue(report["can_continue_to_product_review_packet"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["continuation_kind"], "product_review_packet_continuation")
        self.assertTrue(report["product_review_packet_continuation_reviewed"])
        self.assertEqual(len(report["product_review_packet_input_records"]), 1)
        record = report["product_review_packet_input_records"][0]
        self.assertEqual(record["record_id"], "product_review_packet_continuation::manual_acceptance")
        self.assertEqual(record["review_status"], "product_review_packet_continuation_accepted_for_product_review_packet")
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bq_current_blocked_execute_gate_blocks_result_review(self) -> None:
        """行为 3：当前 P7-BP blocked 时不生成可继续记录。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
            Path("."),
            self._blocked_execute_gate(),
            {},
        )

        self.assertEqual(
            report["status"],
            (
                "blocked_by_manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_gate_entry_execute_gate"
            ),
        )
        self.assertFalse(report["downstream_execute_result_continuation_result_review_continuation_reviewed"])
        self.assertFalse(
            report[
                "can_continue_after_downstream_execute_result_continuation_result_review_continuation"
            ]
        )
        self.assertEqual(report["route_specific_artifact_execution_records"], [])
        self.assertEqual(report["product_review_packet_input_records"], [])
        self.assertIn(
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_execute_gate_not_completed"
            ),
            report["blocking_reasons"],
        )

    def test_bdd_p7bq_missing_invalid_or_not_completed_execute_gate_blocks_review(self) -> None:
        """行为 4：P7-BP 缺失、schema 错、未完成或有 blockers 时阻断。"""
        wrong_schema = self._export_execute_gate_entered("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        dry_run = self._export_execute_gate_entered("pdf_export")
        dry_run["status"] = (
            "manifested_routed_downstream_execute_result_continuation_result_review_"
            "route_specific_artifact_execution_dry_run_ready"
        )
        blocked = self._export_execute_gate_entered("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                Path("."),
                source,
                {},
            )
            for source in [{}, wrong_schema, dry_run, blocked]
        ]

        self.assertTrue(
            all(
                report["status"]
                == (
                    "blocked_by_manifested_routed_downstream_execute_result_continuation_result_review_"
                    "continuation_gate_entry_execute_gate"
                )
                for report in reports
            )
        )
        self.assertIn(
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_execute_gate_missing_or_invalid_schema"
            ),
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_execute_gate_missing_or_invalid_schema"
            ),
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_execute_gate_not_completed"
            ),
            reports[2]["blocking_reasons"],
        )
        self.assertIn(
            "source_downstream_execute_result_continuation_result_review_continuation_execute_gate_has_blocking_reasons",
            reports[3]["blocking_reasons"],
        )

    def test_bdd_p7bq_export_route_execution_dry_run_contract_must_be_clean(self) -> None:
        """行为 5：export delegated execution 缺失、错配或不 clean 时阻断。"""
        missing_execution = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
            Path("."),
            self._export_execute_gate_entered("pdf_export"),
            {},
        )
        wrong_execution_status = self._route_specific_artifact_execution("pdf_export")
        wrong_execution_status["status"] = "blocked_by_route_specific_artifact_execution_result_review"
        wrong_execution_route = self._route_specific_artifact_execution("pdf_export")
        wrong_execution_route["verified_route_type"] = "docx_export"
        dirty_execution = self._route_specific_artifact_execution("pdf_export")
        dirty_execution["route_specific_artifact_executed"] = True

        reports = [
            missing_execution,
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                Path("."),
                self._export_execute_gate_entered("pdf_export"),
                wrong_execution_status,
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                Path("."),
                self._export_execute_gate_entered("pdf_export"),
                wrong_execution_route,
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                Path("."),
                self._export_execute_gate_entered("pdf_export"),
                dirty_execution,
            ),
        ]

        self.assertEqual(reports[0]["status"], "blocked_by_route_specific_artifact_execution_dry_run")
        self.assertEqual(reports[1]["status"], "blocked_by_route_specific_artifact_execution_dry_run")
        self.assertEqual(reports[2]["status"], "blocked_by_route_specific_artifact_execution_dry_run_contract")
        self.assertEqual(reports[3]["status"], "blocked_by_route_specific_artifact_execution_dry_run_boundary")
        self.assertIn("route_specific_artifact_execution_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("route_specific_artifact_execution_not_dry_run_ready", reports[1]["blocking_reasons"])
        self.assertIn("route_specific_artifact_execution_route_type_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("route_specific_artifact_execution_executed_route_specific_artifact", reports[3]["blocking_reasons"])

    def test_bdd_p7bq_manual_product_review_packet_continuation_record_must_be_clean(self) -> None:
        """行为 6：manual continuation record 必须单一、匹配且可继续。"""
        missing = self._manual_execute_gate_recorded()
        missing["product_review_packet_continuation_records"] = []
        duplicated = self._manual_execute_gate_recorded()
        duplicated["product_review_packet_continuation_records"].append(
            dict(duplicated["product_review_packet_continuation_records"][0])
        )
        mismatch = self._manual_execute_gate_recorded()
        mismatch["product_review_packet_continuation_records"][0]["verified_route_type"] = "pdf_export"
        unreviewable = self._manual_execute_gate_recorded()
        unreviewable["product_review_packet_continuation_records"][0]["terminal_completion"] = False
        no_note = self._manual_execute_gate_recorded()
        no_note["product_review_packet_continuation_records"][0]["note"] = ""

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                Path("."),
                source,
                {},
            )
            for source in [missing, duplicated, mismatch, unreviewable, no_note]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_product_review_packet_continuation_result_contract"
                for report in reports
            )
        )
        self.assertIn("product_review_packet_continuation_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("product_review_packet_continuation_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("product_review_packet_continuation_route_type_mismatch:manual_acceptance", reports[2]["blocking_reasons"])
        self.assertIn("product_review_packet_continuation_terminal_completion_missing:manual_acceptance", reports[3]["blocking_reasons"])
        self.assertIn("product_review_packet_continuation_note_missing:manual_acceptance", reports[4]["blocking_reasons"])

    def test_bdd_p7bq_boundary_violations_block_review(self) -> None:
        """行为 7：P7-BP 或 delegated dry-run 出现正式动作或边界越权时阻断。"""
        source_ran = self._export_execute_gate_entered("pdf_export")
        source_ran["route_specific_artifact_executed"] = True
        source_wrote = self._manual_execute_gate_recorded()
        source_wrote["can_write_product_state"] = True
        delegated_dirty = self._route_specific_artifact_execution("pdf_export")
        delegated_dirty["can_write_product_state"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                Path("."),
                source_ran,
                self._route_specific_artifact_execution("pdf_export"),
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                Path("."),
                source_wrote,
                {},
            ),
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                Path("."),
                self._export_execute_gate_entered("pdf_export"),
                delegated_dirty,
            ),
        ]

        self.assertEqual(
            reports[0]["status"],
            (
                "blocked_by_manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_execute_boundary"
            ),
        )
        self.assertEqual(
            reports[1]["status"],
            (
                "blocked_by_manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_execute_boundary"
            ),
        )
        self.assertEqual(reports[2]["status"], "blocked_by_route_specific_artifact_execution_dry_run_boundary")
        self.assertIn(
            (
                "downstream_execute_result_continuation_result_review_continuation_execute_gate_"
                "executed_route_specific_artifact"
            ),
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            (
                "downstream_execute_result_continuation_result_review_continuation_execute_gate_"
                "allows_product_state_write"
            ),
            reports[1]["blocking_reasons"],
        )
        self.assertIn("route_specific_artifact_execution_allows_product_state_write", reports[2]["blocking_reasons"])

    def test_bdd_p7bq_writes_result_review_only_and_cli_defaults_blocked(self) -> None:
        """行为 8：只写 P7-BQ report/review；CLI 默认读取当前 blocked P7-BP。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review(
                project_root,
                self._manual_execute_gate_recorded(),
                {},
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review_outputs(
                    project_root,
                    report,
                )
            )
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_result_review.json"
                ).exists()
            )

            source_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate.json"
            )
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(json.dumps(self._blocked_execute_gate()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    (
                        "Program/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                        "continuation_result_review_continuation_gate_entry_execute_gate_result_review.py"
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
                (
                    "status=blocked_by_manifested_routed_downstream_execute_result_continuation_result_review_"
                    "continuation_gate_entry_execute_gate"
                ),
                result.stdout,
            )
            self.assertIn(
                "downstream_execute_result_continuation_result_review_continuation_reviewed=false",
                result.stdout,
            )
            self.assertIn(
                "can_continue_after_downstream_execute_result_continuation_result_review_continuation=false",
                result.stdout,
            )
            self.assertIn("route_specific_artifact_execution_records=0", result.stdout)
            self.assertIn("product_review_packet_input_records=0", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)

    def _export_execute_gate_entered(self, route_type: str) -> dict:
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                "continuation_result_review_continuation_gate_entry_execute_gate.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": (
                "ready_for_manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_gate_entry"
            ),
            "status": (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "route_specific_artifact_execution_entered"
            ),
            "mode": "execute",
            "confirm_downstream_execute_result_continuation": True,
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "downstream_kind": "selected_route_execution",
            "continuation_kind": "route_specific_artifact_execution_continuation",
            "can_execute_downstream_execute_result_continuation_result_review_continuation_with_confirmation": True,
            "requires_explicit_continuation_command": True,
            "continuation_execute_command": [
                "python3",
                "Program/auto_mode_formal_package_next_gate_route_specific_artifact_execution.py",
            ],
            "continuation_execute_command_executed": True,
            "this_command_ran_continuation_command": True,
            "route_specific_artifact_execution_entered": True,
            "route_specific_artifact_execution_report_path": (
                "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
            ),
            "route_specific_artifact_execution_review_path": (
                "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_execution.md"
            ),
            "route_specific_artifact_execution_returncode": 0,
            "route_specific_artifact_execution_status": "route_specific_artifact_execution_dry_run_ready",
            "route_specific_artifact_execution_result": {
                "returncode": 0,
                "status": "route_specific_artifact_execution_dry_run_ready",
                "report_path": "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json",
                "review_path": "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_execution.md",
            },
            "product_review_packet_continuation_recorded": False,
            "product_review_packet_continuation_records": [],
            "route_specific_artifact_executed": False,
            "route_specific_command_executed": False,
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
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _manual_execute_gate_recorded(self) -> dict:
        report = self._export_execute_gate_entered("manual_acceptance")
        report["status"] = (
            "manifested_routed_downstream_execute_result_continuation_result_review_"
            "product_review_packet_recorded"
        )
        report["routed_next_gate"] = "formal_package_delivery_completion_gate"
        report["downstream_kind"] = "product_review_preparation"
        report["continuation_kind"] = "product_review_packet_continuation"
        report["requires_explicit_continuation_command"] = False
        report["continuation_execute_command"] = []
        report["continuation_execute_command_executed"] = False
        report["this_command_ran_continuation_command"] = False
        report["route_specific_artifact_execution_entered"] = False
        report["route_specific_artifact_execution_report_path"] = ""
        report["route_specific_artifact_execution_review_path"] = ""
        report["route_specific_artifact_execution_returncode"] = None
        report["route_specific_artifact_execution_status"] = ""
        report["route_specific_artifact_execution_result"] = {}
        report["product_review_packet_continuation_recorded"] = True
        report["product_review_packet_continuation_records"] = [self._product_review_packet_continuation_record()]
        return report

    def _blocked_execute_gate(self) -> dict:
        report = self._export_execute_gate_entered("pdf_export")
        report["source_status"] = "blocked_by_manifested_routed_downstream_execute_result_continuation_result_review"
        report["status"] = (
            "blocked_by_manifested_routed_downstream_execute_result_continuation_result_review_"
            "continuation_gate_entry"
        )
        report["mode"] = "dry-run"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["downstream_kind"] = ""
        report["continuation_kind"] = ""
        report["can_execute_downstream_execute_result_continuation_result_review_continuation_with_confirmation"] = False
        report["requires_explicit_continuation_command"] = False
        report["continuation_execute_command"] = []
        report["continuation_execute_command_executed"] = False
        report["this_command_ran_continuation_command"] = False
        report["route_specific_artifact_execution_entered"] = False
        report["route_specific_artifact_execution_status"] = ""
        report["route_specific_artifact_execution_result"] = {}
        report["blocking_reasons"] = [
            "manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_not_ready"
        ]
        return report

    def _route_specific_artifact_execution(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "route_specific_artifact_executor_entry_result_review_ready",
            "status": "route_specific_artifact_execution_dry_run_ready",
            "mode": "dry-run",
            "confirm_artifact_execution": False,
            "verified_route_type": route_type,
            "can_execute_route_specific_artifact_with_confirmation": True,
            "requires_explicit_route_specific_artifact_execution_command": True,
            "route_specific_artifact_execution_command": ["python3", "Program/auto_mode_formal_package_route_specific_artifact_executor.py"],
            "route_specific_artifact_execution_command_executed": False,
            "this_command_ran_route_specific_artifact_executor": False,
            "route_specific_artifact_executor_report_path": (
                "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
            ),
            "route_specific_artifact_executor_review_path": (
                "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md"
            ),
            "route_specific_artifact_executor_returncode": None,
            "route_specific_artifact_executor_status": "",
            "route_specific_artifact_executor_result": {},
            "route_specific_artifact_execution_record": {
                "record_id": f"artifact_executor_dry_run::{route_type}",
                "route_type": route_type,
                "artifact_executor_report_path": (
                    "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
                ),
                "artifact_executor_review_path": (
                    "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md"
                ),
                "delegated_report_path": "Results/json/formal_pdf_final_writeback.json",
                "delegated_review_path": "Reviews/formal_pdf_final_writeback.md",
                "route_specific_command": ["python3", "Program/formal_pdf_final_writeback.py"],
                "review_status": "artifact_executor_dry_run_accepted_for_explicit_artifact_execution",
                "can_continue_to_route_specific_artifact_execution": True,
            },
            "route_specific_artifact_executed": False,
            "route_specific_command_executed": False,
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
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _product_review_packet_continuation_record(self) -> dict:
        return {
            "record_id": "product_review_packet_continuation::manual_acceptance",
            "verified_route_type": "manual_acceptance",
            "continuation_kind": "product_review_packet_continuation",
            "next_report_path": "Results/json/auto_mode_formal_package_product_review_packet.json",
            "next_review_path": "Reviews/auto_mode_formal_package_product_review_packet.md",
            "source_product_review_preparation_report_path": (
                "Results/json/auto_mode_formal_package_product_review_preparation.json"
            ),
            "source_product_review_preparation_review_path": (
                "Reviews/auto_mode_formal_package_product_review_preparation.md"
            ),
            "terminal_status": "terminal_delivery_completion_ready_for_product_review",
            "terminal_completion": True,
            "reviewer": "unit_test_reviewer",
            "note": "Record product-review packet continuation.",
            "continuation_status": "product_review_packet_continuation_recorded",
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
            "manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                "continuation_result_review_continuation_gate_entry_execute_gate.json"
            ),
            "route_specific_artifact_execution": (
                "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

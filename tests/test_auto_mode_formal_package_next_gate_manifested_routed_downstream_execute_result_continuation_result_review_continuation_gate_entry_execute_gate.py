import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate import (
    build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate,
    run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate,
    write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedDownstreamExecuteResultContinuationResultReviewContinuationGateEntryExecuteGateTests(
    unittest.TestCase
):
    """BDD: P7-BP turns the P7-BO continuation entry into an explicit execute gate."""

    def test_bdd_p7bp_export_ready_dry_run_previews_route_specific_artifact_execution_without_running_it(
        self,
    ) -> None:
        """行为 1：export ready dry-run 只预览 route-specific artifact execution。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_export_gate_entry("pdf_export"),
            mode="dry-run",
            source_paths=self._source_paths(),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            report["schema_version"],
            (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                "continuation_result_review_continuation_gate_entry_execute_gate.v1"
            ),
        )
        self.assertEqual(
            report["status"],
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "route_specific_artifact_execution_dry_run_ready"
            ),
        )
        self.assertTrue(
            report[
                "can_execute_downstream_execute_result_continuation_result_review_continuation_with_confirmation"
            ]
        )
        self.assertTrue(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["continuation_kind"], "route_specific_artifact_execution_continuation")
        self.assertEqual(report["continuation_execute_command"][0], "python3")
        self.assertEqual(
            report["continuation_execute_command"][1],
            "Program/auto_mode_formal_package_next_gate_route_specific_artifact_execution.py",
        )
        self.assertFalse(report["continuation_execute_command_executed"])
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["route_specific_artifact_execution_entered"])
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bp_manual_ready_dry_run_previews_product_review_packet_continuation(self) -> None:
        """行为 2：manual ready dry-run 只预览 product-review packet continuation。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_manual_gate_entry(),
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            report["status"],
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "product_review_packet_dry_run_ready"
            ),
        )
        self.assertTrue(
            report[
                "can_execute_downstream_execute_result_continuation_result_review_continuation_with_confirmation"
            ]
        )
        self.assertFalse(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["continuation_kind"], "product_review_packet_continuation")
        self.assertEqual(report["continuation_execute_command"], [])
        self.assertFalse(report["product_review_packet_continuation_recorded"])
        self.assertFalse(report["continuation_execute_command_executed"])
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bp_current_blocked_gate_entry_blocks_execute_gate(self) -> None:
        """行为 3：当前 P7-BO blocked 时不生成 continuation execute。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
            Path("."),
            self._blocked_gate_entry(),
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            report["status"],
            (
                "blocked_by_manifested_routed_downstream_execute_result_continuation_"
                "result_review_continuation_gate_entry"
            ),
        )
        self.assertFalse(
            report[
                "can_execute_downstream_execute_result_continuation_result_review_continuation_with_confirmation"
            ]
        )
        self.assertEqual(report["continuation_execute_command"], [])
        self.assertFalse(report["product_review_packet_continuation_recorded"])
        self.assertIn(
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_gate_entry_not_ready"
            ),
            report["blocking_reasons"],
        )

    def test_bdd_p7bp_missing_invalid_or_not_ready_gate_entry_blocks_execute_gate(self) -> None:
        """行为 4：P7-BO 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._ready_export_gate_entry("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        no_continue = self._ready_export_gate_entry("pdf_export")
        no_continue[
            "can_request_downstream_execute_result_continuation_result_review_continuation"
        ] = False
        blocked = self._ready_export_gate_entry("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [{}, wrong_schema, no_continue, blocked]
        ]

        self.assertTrue(
            all(
                report["status"]
                == (
                    "blocked_by_manifested_routed_downstream_execute_result_continuation_"
                    "result_review_continuation_gate_entry"
                )
                for report in reports
            )
        )
        self.assertIn(
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_gate_entry_missing_or_invalid_schema"
            ),
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_gate_entry_missing_or_invalid_schema"
            ),
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_gate_entry_cannot_request_continuation"
            ),
            reports[2]["blocking_reasons"],
        )
        self.assertIn(
            "source_downstream_execute_result_continuation_result_review_continuation_gate_entry_has_blocking_reasons",
            reports[3]["blocking_reasons"],
        )

    def test_bdd_p7bp_continuation_input_record_contract_must_be_clean(self) -> None:
        """行为 5：continuation input record 必须单一、匹配、已接受且可继续。"""
        missing = self._ready_export_gate_entry("pdf_export")
        missing["continuation_input_records"] = []
        duplicated = self._ready_export_gate_entry("pdf_export")
        duplicated["continuation_input_records"].append(dict(duplicated["continuation_input_records"][0]))
        mismatch = self._ready_export_gate_entry("pdf_export")
        mismatch["continuation_input_records"][0]["verified_route_type"] = "docx_export"
        not_accepted = self._ready_manual_gate_entry()
        not_accepted["continuation_input_records"][0]["review_status"] = "waiting"
        cannot_continue = self._ready_manual_gate_entry()
        cannot_continue["continuation_input_records"][0]["can_continue_to_product_review_packet"] = False

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing, duplicated, mismatch, not_accepted, cannot_continue]
        ]

        self.assertTrue(
            all(
                report["status"]
                == (
                    "blocked_by_manifested_routed_downstream_execute_result_continuation_"
                    "result_review_continuation_gate_entry_contract"
                )
                for report in reports
            )
        )
        self.assertIn("continuation_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("continuation_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("continuation_input_record_route_type_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn(
            "product_review_packet_continuation_record_not_accepted:manual_acceptance",
            reports[3]["blocking_reasons"],
        )
        self.assertIn(
            "product_review_packet_continuation_record_cannot_continue:manual_acceptance",
            reports[4]["blocking_reasons"],
        )

    def test_bdd_p7bp_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 6：execute 模式必须有确认、reviewer 和 note。"""
        no_confirm = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_export_gate_entry("pdf_export"),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_metadata = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_manual_gate_entry(),
            mode="execute",
            confirm_downstream_execute_result_continuation=True,
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            no_confirm["status"],
            (
                "blocked_by_missing_downstream_execute_result_continuation_result_review_"
                "continuation_execute_confirmation"
            ),
        )
        self.assertIn(
            "confirm_downstream_execute_result_continuation_required",
            no_confirm["blocking_reasons"],
        )
        self.assertEqual(
            no_metadata["status"],
            (
                "blocked_by_downstream_execute_result_continuation_result_review_"
                "continuation_execute_metadata"
            ),
        )
        self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
        self.assertIn(
            "downstream_execute_result_continuation_result_review_continuation_note_required",
            no_metadata["blocking_reasons"],
        )
        self.assertFalse(no_confirm["continuation_execute_command_executed"])
        self.assertFalse(no_metadata["product_review_packet_continuation_recorded"])

    def test_bdd_p7bp_confirmed_manual_records_product_review_packet_continuation_only(self) -> None:
        """行为 7：confirmed manual execute 只记录产品审阅包 continuation。"""
        report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_manual_gate_entry(),
            mode="execute",
            confirm_downstream_execute_result_continuation=True,
            reviewer="unit_test_reviewer",
            note="Record product-review packet continuation.",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            report["status"],
            (
                "manifested_routed_downstream_execute_result_continuation_result_review_"
                "product_review_packet_recorded"
            ),
        )
        self.assertTrue(report["product_review_packet_continuation_recorded"])
        self.assertEqual(len(report["product_review_packet_continuation_records"]), 1)
        self.assertFalse(report["continuation_execute_command_executed"])
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["route_specific_artifact_execution_entered"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bp_confirmed_export_enters_route_specific_artifact_execution_dry_run_only(self) -> None:
        """行为 8：confirmed export execute 进入 route-specific artifact execution dry-run。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
                project_root,
                self._ready_export_gate_entry("pdf_export"),
                mode="execute",
                confirm_downstream_execute_result_continuation=True,
                reviewer="unit_test_reviewer",
                note="Enter route-specific artifact execution dry-run.",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate_outputs(
                    project_root,
                    report,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(
                report["status"],
                (
                    "manifested_routed_downstream_execute_result_continuation_result_review_"
                    "route_specific_artifact_execution_entered"
                ),
            )
            self.assertTrue(report["continuation_execute_command_executed"])
            self.assertTrue(report["this_command_ran_continuation_command"])
            self.assertTrue(report["route_specific_artifact_execution_entered"])
            self.assertEqual(
                report["route_specific_artifact_execution_status"],
                "route_specific_artifact_execution_dry_run_ready",
            )
            self.assertFalse(report["route_specific_artifact_executed"])
            self.assertFalse(report["selected_route_executed"])
            self.assertFalse(report["export_or_acceptance_executed"])
            self.assertFalse(report["rendered_pdf"])
            self.assertFalse(report["rendered_docx"])
            self.assertFalse(report["package_manifest_generated"])
            self.assertFalse(report["manual_acceptance_performed"])
            self.assertFalse(report["can_write_product_state"])
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
                ).exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate.json"
                ).exists()
            )

    def test_bdd_p7bp_boundary_violations_and_cli_defaults_blocked(self) -> None:
        """行为 3/4 补充：边界越权阻断；CLI 默认读取当前 blocked P7-BO。"""
        source_ran = self._ready_export_gate_entry("pdf_export")
        source_ran["this_command_ran_continuation_command"] = True
        source_executed = self._ready_export_gate_entry("pdf_export")
        source_executed["route_specific_artifact_executed"] = True
        source_wrote = self._ready_export_gate_entry("pdf_export")
        source_wrote["can_write_product_state"] = True
        source_flag = self._ready_export_gate_entry("pdf_export")
        source_flag["boundary_flags"]["wrote_formal_state"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry_execute_gate(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [source_ran, source_executed, source_wrote, source_flag]
        ]

        self.assertTrue(
            all(
                report["status"]
                == (
                    "blocked_by_manifested_routed_downstream_execute_result_continuation_"
                    "result_review_continuation_gate_entry_boundary"
                )
                for report in reports
            )
        )
        self.assertIn(
            "downstream_execute_result_continuation_result_review_continuation_gate_entry_ran_continuation_command",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "downstream_execute_result_continuation_result_review_continuation_gate_entry_executed_route_specific_artifact",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "downstream_execute_result_continuation_result_review_continuation_gate_entry_allows_product_state_write",
            reports[2]["blocking_reasons"],
        )
        self.assertIn(
            (
                "downstream_execute_result_continuation_result_review_continuation_gate_entry_"
                "boundary_violation:wrote_formal_state"
            ),
            reports[3]["blocking_reasons"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            source_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry.json"
            )
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(json.dumps(self._blocked_gate_entry()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    (
                        "Program/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                        "continuation_result_review_continuation_gate_entry_execute_gate.py"
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
                    "status=blocked_by_manifested_routed_downstream_execute_result_continuation_"
                    "result_review_continuation_gate_entry"
                ),
                result.stdout,
            )
            self.assertIn(
                "can_execute_downstream_execute_result_continuation_result_review_continuation_with_confirmation=false",
                result.stdout,
            )
            self.assertIn("continuation_execute_command=0", result.stdout)
            self.assertIn("continuation_execute_command_executed=false", result.stdout)
            self.assertIn("product_review_packet_continuation_recorded=false", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)

    def _ready_export_gate_entry(self, route_type: str) -> dict:
        record = self._export_continuation_record(route_type)
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                "continuation_result_review_continuation_gate_entry.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_routed_downstream_execute_result_continuation_result_review_ready",
            "status": (
                "ready_for_manifested_routed_downstream_execute_result_continuation_result_review_"
                "continuation_gate_entry"
            ),
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "downstream_kind": "selected_route_execution",
            "continuation_kind": "route_specific_artifact_execution_continuation",
            "downstream_execute_result_continuation_result_review_gate_entry_recorded": True,
            "can_request_downstream_execute_result_continuation_result_review_continuation": True,
            "requires_explicit_continuation_command": True,
            "continuation_input_records": [record],
            "continuation_command_executed": False,
            "this_command_ran_continuation_command": False,
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
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _ready_manual_gate_entry(self) -> dict:
        report = self._ready_export_gate_entry("manual_acceptance")
        report["source_status"] = "manifested_routed_downstream_execute_result_continuation_result_review_ready"
        report["routed_next_gate"] = "formal_package_delivery_completion_gate"
        report["downstream_kind"] = "product_review_preparation"
        report["continuation_kind"] = "product_review_packet_continuation"
        report["requires_explicit_continuation_command"] = False
        report["continuation_input_records"] = [self._manual_continuation_record()]
        return report

    def _blocked_gate_entry(self) -> dict:
        report = self._ready_export_gate_entry("pdf_export")
        report["source_status"] = "blocked_by_manifested_routed_downstream_execute_result_continuation_result_review"
        report["status"] = "blocked_by_manifested_routed_downstream_execute_result_continuation_result_review"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["downstream_kind"] = ""
        report["continuation_kind"] = ""
        report["downstream_execute_result_continuation_result_review_gate_entry_recorded"] = False
        report["can_request_downstream_execute_result_continuation_result_review_continuation"] = False
        report["requires_explicit_continuation_command"] = False
        report["continuation_input_records"] = []
        report["blocking_reasons"] = [
            "manifested_routed_downstream_execute_result_continuation_result_review_not_ready",
        ]
        return report

    def _export_continuation_record(self, route_type: str) -> dict:
        return {
            "record_id": (
                "manifested_routed_downstream_execute_result_continuation_result_review::"
                f"route_specific_artifact_execution::{route_type}"
            ),
            "source_record_id": f"artifact_executor_dry_run::{route_type}",
            "verified_route_type": route_type,
            "source_continuation_kind": "route_specific_artifact_executor_continuation",
            "continuation_kind": "route_specific_artifact_execution_continuation",
            "next_command": "auto_mode_formal_package_next_gate_route_specific_artifact_execution",
            "command_path": "Program/auto_mode_formal_package_next_gate_route_specific_artifact_execution.py",
            "next_report_path": "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json",
            "next_review_path": "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_execution.md",
            "artifact_executor_report_path": "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
            "artifact_executor_review_path": "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md",
            "delegated_report_path": "Results/json/formal_pdf_final_writeback.json",
            "delegated_review_path": "Reviews/formal_pdf_final_writeback.md",
            "route_specific_command": ["python3", "Program/formal_pdf_final_writeback.py"],
            "review_status": "route_specific_artifact_execution_input_accepted_for_continuation",
            "requires_explicit_continuation_command": True,
            "can_continue_to_route_specific_artifact_execution": True,
        }

    def _manual_continuation_record(self) -> dict:
        return {
            "record_id": (
                "manifested_routed_downstream_execute_result_continuation_result_review::"
                "product_review_packet::manual_acceptance"
            ),
            "source_record_id": "product_review_packet_preparation::manual_acceptance",
            "verified_route_type": "manual_acceptance",
            "routed_next_gate": "formal_package_delivery_completion_gate",
            "downstream_kind": "product_review_preparation",
            "continuation_kind": "product_review_packet_continuation",
            "next_command": "product_review_packet",
            "command_path": "",
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
            "review_status": "product_review_packet_input_accepted_for_continuation",
            "requires_explicit_continuation_command": False,
            "can_continue_to_product_review_packet": True,
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
            "manifested_routed_downstream_execute_result_continuation_result_review_continuation_gate_entry": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                "continuation_result_review_continuation_gate_entry.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

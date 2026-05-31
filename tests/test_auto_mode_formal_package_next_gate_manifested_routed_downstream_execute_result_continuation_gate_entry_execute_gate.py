import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate import (
    build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate,
    run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate,
    write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedDownstreamExecuteResultContinuationGateEntryExecuteGateTests(
    unittest.TestCase
):
    """BDD: P7-BM turns the P7-BL continuation entry into an explicit execute gate."""

    def test_bdd_p7bm_export_ready_dry_run_previews_artifact_executor_entry_without_running_it(self) -> None:
        """行为 1：export ready dry-run 只预览 artifact executor entry command。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_export_gate_entry("pdf_export"),
            mode="dry-run",
            source_paths=self._source_paths(),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate.v1",
        )
        self.assertEqual(
            report["status"],
            "manifested_routed_downstream_execute_result_continuation_artifact_executor_entry_dry_run_ready",
        )
        self.assertTrue(report["can_execute_downstream_execute_result_continuation_with_confirmation"])
        self.assertTrue(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["continuation_kind"], "route_specific_artifact_executor_continuation")
        self.assertEqual(report["continuation_execute_command"][0], "python3")
        self.assertEqual(
            report["continuation_execute_command"][1],
            "Program/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.py",
        )
        self.assertFalse(report["continuation_execute_command_executed"])
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["route_specific_artifact_executor_entry_entered"])
        self.assertFalse(report["route_specific_artifact_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bm_manual_ready_dry_run_previews_product_review_packet_preparation(self) -> None:
        """行为 2：manual ready dry-run 只预览 product-review packet preparation。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_manual_gate_entry(),
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            report["status"],
            "manifested_routed_downstream_execute_result_continuation_product_review_packet_preparation_dry_run_ready",
        )
        self.assertTrue(report["can_execute_downstream_execute_result_continuation_with_confirmation"])
        self.assertFalse(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["continuation_kind"], "product_review_packet_continuation")
        self.assertEqual(report["continuation_execute_command"], [])
        self.assertFalse(report["product_review_packet_preparation_recorded"])
        self.assertFalse(report["continuation_execute_command_executed"])
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bm_current_blocked_gate_entry_blocks_execute_gate(self) -> None:
        """行为 3：当前 P7-BL blocked 时不生成 continuation execute。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
            Path("."),
            self._blocked_gate_entry(),
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            report["status"],
            "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry",
        )
        self.assertFalse(report["can_execute_downstream_execute_result_continuation_with_confirmation"])
        self.assertEqual(report["continuation_execute_command"], [])
        self.assertFalse(report["product_review_packet_preparation_recorded"])
        self.assertIn(
            "manifested_routed_downstream_execute_result_continuation_gate_entry_not_ready",
            report["blocking_reasons"],
        )

    def test_bdd_p7bm_missing_invalid_or_not_ready_gate_entry_blocks_execute_gate(self) -> None:
        """行为 4：P7-BL 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._ready_export_gate_entry("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        no_continue = self._ready_export_gate_entry("pdf_export")
        no_continue["can_request_downstream_execute_result_continuation"] = False
        blocked = self._ready_export_gate_entry("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [{}, wrong_schema, no_continue, blocked]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry"
                for report in reports
            )
        )
        self.assertIn(
            "manifested_routed_downstream_execute_result_continuation_gate_entry_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_downstream_execute_result_continuation_gate_entry_missing_or_invalid_schema",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_downstream_execute_result_continuation_gate_entry_cannot_request_continuation",
            reports[2]["blocking_reasons"],
        )
        self.assertIn(
            "source_downstream_execute_result_continuation_gate_entry_has_blocking_reasons",
            reports[3]["blocking_reasons"],
        )

    def test_bdd_p7bm_continuation_input_record_contract_must_be_clean(self) -> None:
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
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing, duplicated, mismatch, not_accepted, cannot_continue]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry_contract"
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

    def test_bdd_p7bm_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 6：execute 模式必须有确认、reviewer 和 note。"""
        no_confirm = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_export_gate_entry("pdf_export"),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_metadata = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_manual_gate_entry(),
            mode="execute",
            confirm_downstream_execute_result_continuation=True,
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            no_confirm["status"],
            "blocked_by_missing_downstream_execute_result_continuation_execute_confirmation",
        )
        self.assertIn("confirm_downstream_execute_result_continuation_required", no_confirm["blocking_reasons"])
        self.assertEqual(no_metadata["status"], "blocked_by_downstream_execute_result_continuation_execute_metadata")
        self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
        self.assertIn("downstream_execute_result_continuation_note_required", no_metadata["blocking_reasons"])
        self.assertFalse(no_confirm["continuation_execute_command_executed"])
        self.assertFalse(no_metadata["product_review_packet_preparation_recorded"])

    def test_bdd_p7bm_confirmed_manual_records_product_review_packet_preparation_only(self) -> None:
        """行为 7：confirmed manual execute 只记录产品审阅包准备，不运行外部命令。"""
        report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
            Path("."),
            self._ready_manual_gate_entry(),
            mode="execute",
            confirm_downstream_execute_result_continuation=True,
            reviewer="unit_test_reviewer",
            note="Record product-review packet preparation.",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            report["status"],
            "manifested_routed_downstream_execute_result_continuation_product_review_packet_preparation_recorded",
        )
        self.assertTrue(report["product_review_packet_preparation_recorded"])
        self.assertEqual(len(report["product_review_packet_preparation_records"]), 1)
        self.assertFalse(report["continuation_execute_command_executed"])
        self.assertFalse(report["this_command_ran_continuation_command"])
        self.assertFalse(report["route_specific_artifact_executor_entry_entered"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bm_confirmed_export_enters_artifact_executor_entry_dry_run_only(self) -> None:
        """行为 8：confirmed export execute 进入 artifact executor entry dry-run，但不产出正式包。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_selected_route_execute.json",
                self._selected_route_execute("pdf_export"),
            )
            self._write_json(
                project_root
                / "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json",
                self._selected_route_execute_manifest("pdf_export"),
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
                project_root,
                self._ready_export_gate_entry("pdf_export"),
                mode="execute",
                confirm_downstream_execute_result_continuation=True,
                reviewer="unit_test_reviewer",
                note="Enter artifact executor entry dry-run.",
                repo_root=REPO_ROOT,
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_outputs(
                    project_root,
                    report,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(
                report["status"],
                "manifested_routed_downstream_execute_result_continuation_artifact_executor_entry_entered",
            )
            self.assertTrue(report["continuation_execute_command_executed"])
            self.assertTrue(report["this_command_ran_continuation_command"])
            self.assertTrue(report["route_specific_artifact_executor_entry_entered"])
            self.assertEqual(report["route_specific_artifact_executor_entry_status"], "next_gate_route_specific_artifact_executor_entered")
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
                    / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
                ).exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate.json"
                ).exists()
            )

    def test_bdd_p7bm_boundary_violations_and_cli_defaults_blocked(self) -> None:
        """行为 3/4 补充：边界越权阻断；CLI 默认读取当前 blocked P7-BL。"""
        source_ran = self._ready_export_gate_entry("pdf_export")
        source_ran["this_command_ran_continuation_command"] = True
        source_executed = self._ready_export_gate_entry("pdf_export")
        source_executed["route_specific_artifact_executed"] = True
        source_wrote = self._ready_export_gate_entry("pdf_export")
        source_wrote["can_write_product_state"] = True
        source_flag = self._ready_export_gate_entry("pdf_export")
        source_flag["boundary_flags"]["wrote_formal_state"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [source_ran, source_executed, source_wrote, source_flag]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry_boundary"
                for report in reports
            )
        )
        self.assertIn("downstream_execute_result_continuation_gate_entry_ran_continuation_command", reports[0]["blocking_reasons"])
        self.assertIn("downstream_execute_result_continuation_gate_entry_executed_route_specific_artifact", reports[1]["blocking_reasons"])
        self.assertIn("downstream_execute_result_continuation_gate_entry_allows_product_state_write", reports[2]["blocking_reasons"])
        self.assertIn("downstream_execute_result_continuation_gate_entry_boundary_violation:wrote_formal_state", reports[3]["blocking_reasons"])

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            source_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry.json"
            )
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(json.dumps(self._blocked_gate_entry()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate.py",
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
                "status=blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry",
                result.stdout,
            )
            self.assertIn("can_execute_downstream_execute_result_continuation_with_confirmation=false", result.stdout)
            self.assertIn("continuation_execute_command=0", result.stdout)
            self.assertIn("continuation_execute_command_executed=false", result.stdout)
            self.assertIn("product_review_packet_preparation_recorded=false", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)

    def _ready_export_gate_entry(self, route_type: str) -> dict:
        record = self._export_continuation_record(route_type)
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                "continuation_gate_entry.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_routed_next_gate_downstream_execute_result_review_ready",
            "status": "ready_for_manifested_routed_downstream_execute_result_continuation_gate_entry",
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "downstream_kind": "selected_route_execution",
            "continuation_kind": "route_specific_artifact_executor_continuation",
            "downstream_execute_result_continuation_gate_entry_recorded": True,
            "can_request_downstream_execute_result_continuation": True,
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
        report["source_status"] = "manifested_routed_next_gate_product_review_preparation_result_review_ready"
        report["routed_next_gate"] = "formal_package_delivery_completion_gate"
        report["downstream_kind"] = "product_review_preparation"
        report["continuation_kind"] = "product_review_packet_continuation"
        report["requires_explicit_continuation_command"] = False
        report["continuation_input_records"] = [self._manual_continuation_record()]
        return report

    def _blocked_gate_entry(self) -> dict:
        report = self._ready_export_gate_entry("pdf_export")
        report["source_status"] = "blocked_by_manifested_routed_next_gate_downstream_execute_gate"
        report["status"] = "blocked_by_manifested_routed_next_gate_downstream_execute_result_review"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["downstream_kind"] = ""
        report["continuation_kind"] = ""
        report["downstream_execute_result_continuation_gate_entry_recorded"] = False
        report["can_request_downstream_execute_result_continuation"] = False
        report["requires_explicit_continuation_command"] = False
        report["continuation_input_records"] = []
        report["blocking_reasons"] = [
            "manifested_routed_next_gate_downstream_execute_result_review_not_ready",
        ]
        return report

    def _export_continuation_record(self, route_type: str) -> dict:
        return {
            "record_id": (
                "manifested_routed_downstream_execute_result_continuation::"
                f"route_specific_artifact_executor::{route_type}"
            ),
            "verified_route_type": route_type,
            "routed_next_gate": "formal_package_export_acceptance_router",
            "downstream_kind": "selected_route_execution",
            "continuation_kind": "route_specific_artifact_executor_continuation",
            "next_command": "auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry",
            "command_path": "Program/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.py",
            "next_report_path": "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json",
            "next_review_path": "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.md",
            "selected_route_execute_report_path": "Results/json/auto_mode_formal_package_selected_route_execute.json",
            "selected_route_execute_review_path": "Reviews/auto_mode_formal_package_selected_route_execute.md",
            "selected_route_execute_manifest_path": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
            "operation_id": f"selected_route_execute::{route_type}",
            "route_execution_id": "selected_formal_package_route_execution::formal_pdf_export_preflight",
            "routed_action": "formal_pdf_export_preflight",
            "route_specific_next_command": "formal_pdf_export_execute",
            "planned_outputs": ["Submissions/formal_package/paper.pdf"],
            "review_status": "route_specific_artifact_executor_input_accepted_for_continuation",
            "requires_explicit_continuation_command": True,
            "can_continue_to_route_specific_artifact_executor_entry": True,
        }

    def _manual_continuation_record(self) -> dict:
        return {
            "record_id": (
                "manifested_routed_downstream_execute_result_continuation::"
                "product_review_packet::manual_acceptance"
            ),
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
            "review_status": "product_review_preparation_result_accepted_for_product_review_packet_continuation",
            "requires_explicit_continuation_command": False,
            "can_continue_to_product_review_packet": True,
        }

    def _selected_route_execute(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
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
            "generated_at": "2026-05-31T00:00:00+00:00",
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
            "manifested_routed_downstream_execute_result_continuation_gate_entry": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
                "continuation_gate_entry.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

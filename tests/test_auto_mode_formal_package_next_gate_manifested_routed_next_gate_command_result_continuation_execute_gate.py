import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate import (
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate,
    run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateManifestedRoutedNextGateCommandResultContinuationExecuteGateTests(unittest.TestCase):
    """BDD: P7-BG executes or records a P7-BF continuation only after confirmation."""

    def test_bdd_p7bg_export_route_dry_run_builds_command_without_running_it(self) -> None:
        """行为 1：export-router ready 输入可 dry-run 预览 continuation command。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = (
                build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
                    project_root,
                    self._ready_gate_entry("pdf_export"),
                    mode="dry-run",
                    source_paths=self._source_paths(),
                    repo_root=REPO_ROOT,
                )
            )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.v1",
        )
        self.assertEqual(report["status"], "manifested_routed_next_gate_result_continuation_execute_dry_run_ready")
        self.assertTrue(report["can_execute_manifested_routed_next_gate_result_continuation_with_confirmation"])
        self.assertTrue(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "pdf_export")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(report["continuation_command"][0], "python3")
        self.assertEqual(
            report["continuation_command"][1],
            "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
        )
        self.assertIn("--export-acceptance-router", report["continuation_command"])
        self.assertFalse(report["continuation_executed"])
        self.assertFalse(report["this_command_ran_continuation"])
        self.assertFalse(report["terminal_continuation_recorded"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bg_manual_terminal_dry_run_has_no_external_command(self) -> None:
        """行为 2：manual terminal 输入可预览终态记录，不生成外部命令。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
            Path("."),
            self._ready_gate_entry("manual_acceptance"),
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "manifested_routed_next_gate_result_continuation_execute_dry_run_ready")
        self.assertTrue(report["can_execute_manifested_routed_next_gate_result_continuation_with_confirmation"])
        self.assertFalse(report["requires_explicit_continuation_command"])
        self.assertEqual(report["verified_route_type"], "manual_acceptance")
        self.assertEqual(report["routed_next_gate"], "formal_package_delivery_completion_gate")
        self.assertEqual(report["continuation_command"], [])
        self.assertFalse(report["continuation_executed"])
        self.assertFalse(report["terminal_continuation_recorded"])

    def test_bdd_p7bg_current_blocked_gate_entry_blocks_continuation_execution(self) -> None:
        """行为 3：当前 P7-BF blocked 时不运行 continuation。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
            Path("."),
            self._blocked_gate_entry(),
            mode="dry-run",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_manifested_routed_next_gate_result_continuation_gate_entry")
        self.assertFalse(report["can_execute_manifested_routed_next_gate_result_continuation_with_confirmation"])
        self.assertEqual(report["continuation_command"], [])
        self.assertEqual(report["continuation_input_record"], {})
        self.assertFalse(report["continuation_executed"])
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_gate_entry_not_ready",
            report["blocking_reasons"],
        )

    def test_bdd_p7bg_missing_invalid_or_not_ready_gate_entry_blocks_execution(self) -> None:
        """行为 4：P7-BF 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._ready_gate_entry("pdf_export")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._ready_gate_entry("pdf_export")
        not_ready["status"] = "blocked_by_manifested_routed_next_gate_command_result_review"
        blocked = self._ready_gate_entry("pdf_export")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [{}, wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_manifested_routed_next_gate_result_continuation_gate_entry"
                for report in reports
            )
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_gate_entry_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_gate_entry_missing_or_invalid_schema",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "manifested_routed_next_gate_result_continuation_gate_entry_not_ready",
            reports[2]["blocking_reasons"],
        )
        self.assertIn("source_continuation_gate_entry_has_blocking_reasons", reports[3]["blocking_reasons"])

    def test_bdd_p7bg_continuation_input_record_contract_must_be_clean(self) -> None:
        """行为 5：continuation input 缺失、重复、错配或标记自执行时阻断。"""
        missing = self._ready_gate_entry("pdf_export")
        missing["continuation_input_records"] = []
        duplicated = self._ready_gate_entry("pdf_export")
        duplicated["continuation_input_records"].append(dict(duplicated["continuation_input_records"][0]))
        wrong_command = self._ready_gate_entry("pdf_export")
        wrong_command["continuation_input_records"][0]["command_path"] = "Program/wrong.py"
        marked_run = self._ready_gate_entry("pdf_export")
        marked_run["continuation_input_records"][0]["will_run_continuation_by_this_command"] = True

        reports = [
            build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing, duplicated, wrong_command, marked_run]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_manifested_routed_next_gate_result_continuation_execute_contract"
                for report in reports
            )
        )
        self.assertIn("continuation_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("continuation_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("continuation_command_path_mismatch:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("continuation_input_marked_run_continuation:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7bg_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 6：execute 模式必须有确认、reviewer 和 note。"""
        no_confirm = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
            Path("."),
            self._ready_gate_entry("pdf_export"),
            mode="execute",
            repo_root=REPO_ROOT,
        )
        no_metadata = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
            Path("."),
            self._ready_gate_entry("pdf_export"),
            mode="execute",
            confirm_continuation_execute=True,
            repo_root=REPO_ROOT,
        )

        self.assertEqual(
            no_confirm["status"],
            "blocked_by_missing_manifested_routed_next_gate_result_continuation_execute_confirmation",
        )
        self.assertIn("confirm_continuation_execute_required", no_confirm["blocking_reasons"])
        self.assertEqual(
            no_metadata["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_execute_metadata",
        )
        self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
        self.assertIn("continuation_execute_note_required", no_metadata["blocking_reasons"])
        self.assertFalse(no_confirm["continuation_executed"])
        self.assertFalse(no_metadata["continuation_executed"])

    def test_bdd_p7bg_confirmed_export_execution_runs_selected_route_preflight(self) -> None:
        """行为 7：confirmed export execute 运行 selected-route preflight 并记录结果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_export_acceptance_router.json",
                self._ready_export_acceptance_router("formal_pdf_export_preflight"),
            )

            report, exit_code = (
                run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
                    project_root,
                    self._ready_gate_entry("pdf_export"),
                    mode="execute",
                    confirm_continuation_execute=True,
                    reviewer="unit_test_reviewer",
                    note="Run continuation preflight.",
                    repo_root=REPO_ROOT,
                )
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate_outputs(
                    project_root,
                    report,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(report["status"], "manifested_routed_next_gate_result_continuation_executed")
            self.assertTrue(report["continuation_executed"])
            self.assertTrue(report["this_command_ran_continuation"])
            self.assertFalse(report["terminal_continuation_recorded"])
            self.assertEqual(report["continuation_returncode"], 0)
            self.assertEqual(
                report["continuation_status"],
                "ready_for_selected_formal_package_route_execution_review",
            )
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
                ).exists()
            )
            self.assertFalse(report["selected_route_executed"])
            self.assertFalse(report["export_or_acceptance_executed"])
            self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7bg_confirmed_manual_terminal_records_without_external_command(self) -> None:
        """行为 8：confirmed manual terminal 只记录终态 continuation，不运行外部命令。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report, exit_code = (
                run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
                    project_root,
                    self._ready_gate_entry("manual_acceptance"),
                    mode="execute",
                    confirm_continuation_execute=True,
                    reviewer="unit_test_reviewer",
                    note="Record terminal continuation.",
                    repo_root=REPO_ROOT,
                )
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate_outputs(
                    project_root,
                    report,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(report["status"], "manifested_routed_next_gate_terminal_continuation_recorded")
            self.assertTrue(report["terminal_continuation_recorded"])
            self.assertTrue(report["this_command_recorded_terminal_continuation"])
            self.assertFalse(report["continuation_executed"])
            self.assertFalse(report["this_command_ran_continuation"])
            self.assertEqual(report["continuation_command"], [])
            self.assertEqual(report["continuation_returncode"], None)
            self.assertEqual(report["continuation_status"], "terminal_delivery_completion_ready_for_product_review")
            self.assertFalse(report["can_write_product_state"])
            self.assertFalse(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.json"
                ).exists()
            )

    def test_bdd_p7bg_missing_continuation_command_file_blocks_export_execution(self) -> None:
        """行为 9：export continuation command 文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
            Path("."),
            self._ready_gate_entry("pdf_export"),
            mode="execute",
            confirm_continuation_execute=True,
            reviewer="unit_test_reviewer",
            note="Try continuation.",
            repo_root=Path("/tmp/nonexistent-repo-for-p7bg"),
        )

        self.assertEqual(
            report["status"],
            "blocked_by_manifested_routed_next_gate_result_continuation_command_unavailable",
        )
        self.assertIn(
            "continuation_command_file_missing:Program/auto_mode_formal_package_selected_route_execution_preflight.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["continuation_executed"])
        self.assertFalse(report["this_command_ran_continuation"])

    def test_bdd_p7bg_cli_defaults_to_current_blocked_gate_entry(self) -> None:
        """行为 10：CLI 默认读取当前 blocked P7-BF，写 blocked execute report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            gate_entry_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.json"
            )
            gate_entry_path.parent.mkdir(parents=True, exist_ok=True)
            gate_entry_path.write_text(json.dumps(self._blocked_gate_entry()), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    (
                        "Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
                        "continuation_execute_gate.py"
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
            self.assertIn("status=blocked_by_manifested_routed_next_gate_result_continuation_gate_entry", result.stdout)
            self.assertIn("continuation_command=0", result.stdout)
            self.assertIn("continuation_executed=false", result.stdout)
            self.assertIn("terminal_continuation_recorded=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.md"
                ).exists()
            )

    def _ready_gate_entry(self, route_type: str) -> dict:
        gate_id = (
            "formal_package_delivery_completion_gate"
            if route_type == "manual_acceptance"
            else "formal_package_export_acceptance_router"
        )
        delegated_status = (
            "formal_package_delivery_review_ready"
            if route_type == "manual_acceptance"
            else "formal_package_export_acceptance_route_recorded"
        )
        continuation_kind = (
            "delivery_completion_terminal_record"
            if route_type == "manual_acceptance"
            else "selected_route_execution_preflight"
        )
        next_command = (
            "none"
            if route_type == "manual_acceptance"
            else "auto_mode_formal_package_selected_route_execution_preflight"
        )
        command_path = (
            ""
            if route_type == "manual_acceptance"
            else "Program/auto_mode_formal_package_selected_route_execution_preflight.py"
        )
        next_report_path = (
            "Results/json/auto_mode_formal_package_delivery_completion_gate.json"
            if route_type == "manual_acceptance"
            else "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
        )
        next_review_path = (
            "Reviews/auto_mode_formal_package_delivery_completion_gate.md"
            if route_type == "manual_acceptance"
            else "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md"
        )
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "manifested_routed_next_gate_command_execute_gate_entry_result_review_ready",
            "status": "ready_for_manifested_routed_next_gate_command_result_continuation_gate_entry",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "delegated_status": delegated_status,
            "command_result_continuation_gate_entry_recorded": True,
            "can_request_manifested_routed_next_gate_result_continuation": True,
            "requires_explicit_continuation_command": route_type != "manual_acceptance",
            "continuation_executed": False,
            "this_command_ran_continuation": False,
            "next_gate_command_executed": True,
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "continuation_input_records": [
                {
                    "record_id": (
                        "manifested_routed_next_gate_command_result_continuation::"
                        f"{gate_id}::{route_type}"
                    ),
                    "source_delegated_result_record_id": (
                        "manifested_routed_next_gate_command_result::"
                        f"{gate_id}::{route_type}"
                    ),
                    "verified_route_type": route_type,
                    "routed_next_gate": gate_id,
                    "delegated_status": delegated_status,
                    "delegated_schema_version": (
                        "p7.auto_mode_formal_package_delivery_completion_gate.v1"
                        if route_type == "manual_acceptance"
                        else "p7.auto_mode_formal_package_export_acceptance_router.v1"
                    ),
                    "source_report_path": (
                        "Results/json/auto_mode_formal_package_delivery_completion_gate.json"
                        if route_type == "manual_acceptance"
                        else "Results/json/auto_mode_formal_package_export_acceptance_router.json"
                    ),
                    "source_review_path": (
                        "Reviews/auto_mode_formal_package_delivery_completion_gate.md"
                        if route_type == "manual_acceptance"
                        else "Reviews/auto_mode_formal_package_export_acceptance_router.md"
                    ),
                    "continuation_kind": continuation_kind,
                    "next_command": next_command,
                    "command_path": command_path,
                    "next_report_path": next_report_path,
                    "next_review_path": next_review_path,
                    "continuation_status": (
                        "terminal_delivery_completion_ready_for_product_review"
                        if route_type == "manual_acceptance"
                        else "pending_explicit_continuation_command"
                    ),
                    "requires_explicit_continuation_command": route_type != "manual_acceptance",
                    "completion_terminal": route_type == "manual_acceptance",
                    "will_run_continuation_by_this_command": False,
                    "will_execute_export_or_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                }
            ],
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_gate_entry(self) -> dict:
        report = self._ready_gate_entry("pdf_export")
        report["status"] = "blocked_by_manifested_routed_next_gate_command_result_review"
        report["verified_route_type"] = ""
        report["routed_next_gate"] = ""
        report["delegated_status"] = ""
        report["command_result_continuation_gate_entry_recorded"] = False
        report["can_request_manifested_routed_next_gate_result_continuation"] = False
        report["requires_explicit_continuation_command"] = False
        report["next_gate_command_executed"] = False
        report["continuation_input_records"] = []
        report["blocking_reasons"] = ["manifested_routed_next_gate_command_result_review_not_ready"]
        return report

    def _ready_export_acceptance_router(self, routed_action: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_export_acceptance_router.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "ready_for_formal_package_export_acceptance_review",
            "status": "formal_package_export_acceptance_route_recorded",
            "decision": "pdf_export",
            "route_request": {
                "decision": "pdf_export",
                "confirm_route": True,
                "reviewer": "reviewer-a",
                "note": "Route selected for later explicit execution.",
                "metadata_complete": True,
            },
            "can_route_export_or_acceptance": True,
            "route_recorded": True,
            "routed_action": routed_action,
            "selected_plan_item": {
                "action_id": routed_action,
                "label": "Formal PDF Export Preflight",
                "description": "Later explicit command.",
                "source_formal_targets": [
                    "Submissions/formal_package/manuscript/paper.md",
                    "Submissions/formal_package/bibliography/literature_review_packet.json",
                ],
                "execution_status": "pending_explicit_export_or_acceptance_command",
                "requires_explicit_export_or_acceptance_command": True,
                "this_command_rendered_or_accepted": False,
                "this_command_wrote_product_state": False,
            },
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_boundary_flags(),
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
        }

    def _source_paths(self) -> dict:
        return {
            "manifested_routed_next_gate_command_result_continuation_gate_entry": (
                "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

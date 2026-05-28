import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_selected_route_execute import (
    build_auto_mode_formal_package_selected_route_execute,
    write_auto_mode_formal_package_selected_route_execute_outputs,
)


class AutoModeFormalPackageSelectedRouteExecuteTests(unittest.TestCase):
    """BDD: P7-AA gates selected formal package route execution."""

    def test_bdd_p7aa_ready_pdf_route_supports_dry_run_without_export(self) -> None:
        """行为 1：ready PDF route 可 dry-run，但不导出。"""
        report = build_auto_mode_formal_package_selected_route_execute(
            self._ready_preflight("pdf_export"),
            mode="dry-run",
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_package_selected_route_execute.v1")
        self.assertEqual(report["status"], "selected_route_execute_dry_run_ready")
        self.assertEqual(report["mode"], "dry-run")
        self.assertTrue(report["can_execute_selected_route_with_confirmation"])
        self.assertFalse(report["selected_route_execute_manifest_recorded"])
        self.assertEqual(len(report["selected_route_execute_operations"]), 1)
        self.assertEqual(report["selected_route_execute_operations"][0]["route_type"], "pdf_export")
        self.assertEqual(
            report["selected_route_execute_operations"][0]["planned_outputs"],
            ["Submissions/formal_package/paper.pdf"],
        )
        self.assertFalse(report["selected_route_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["rendered_pdf"])
        self.assertFalse(report["rendered_docx"])
        self.assertFalse(report["package_manifest_generated"])
        self.assertFalse(report["manual_acceptance_performed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7aa_maps_docx_package_and_manual_routes(self) -> None:
        """行为 2：DOCX、package manifest、manual acceptance 路线映射到对应操作。"""
        expectations = {
            "docx_export": ["Submissions/formal_package/paper.docx"],
            "package_manifest": ["Submissions/formal_package/manifest.json"],
            "manual_acceptance": ["Reviews/formal_package_manual_acceptance.md"],
        }

        for route_type, planned_outputs in expectations.items():
            with self.subTest(route_type=route_type):
                report = build_auto_mode_formal_package_selected_route_execute(
                    self._ready_preflight(route_type),
                    mode="dry-run",
                )

                self.assertEqual(report["status"], "selected_route_execute_dry_run_ready")
                self.assertEqual(report["selected_route_execute_operations"][0]["route_type"], route_type)
                self.assertEqual(report["selected_route_execute_operations"][0]["planned_outputs"], planned_outputs)
                self.assertFalse(report["export_or_acceptance_executed"])

    def test_bdd_p7aa_current_blocked_preflight_blocks_execute_gate(self) -> None:
        """行为 3：当前 P7-Z blocked 时不能生成 execute operation。"""
        report = build_auto_mode_formal_package_selected_route_execute(
            self._blocked_preflight(),
            mode="dry-run",
        )

        self.assertEqual(report["status"], "blocked_by_selected_route_execution_preflight")
        self.assertFalse(report["can_execute_selected_route_with_confirmation"])
        self.assertEqual(report["selected_route_execute_operations"], [])
        self.assertFalse(report["selected_route_execute_manifest_recorded"])
        self.assertIn("selected_route_execution_preflight_not_ready", report["blocking_reasons"])

    def test_bdd_p7aa_missing_invalid_or_unready_preflight_blocks_execution(self) -> None:
        """行为 4：preflight 缺失、schema 错误或未 ready 时阻断。"""
        missing = build_auto_mode_formal_package_selected_route_execute({}, mode="dry-run")
        invalid = self._ready_preflight("pdf_export")
        invalid["schema_version"] = "wrong.schema"
        unready = self._ready_preflight("pdf_export")
        unready["status"] = "blocked_by_export_acceptance_router"

        invalid_report = build_auto_mode_formal_package_selected_route_execute(invalid, mode="dry-run")
        unready_report = build_auto_mode_formal_package_selected_route_execute(unready, mode="dry-run")

        self.assertEqual(missing["status"], "blocked_by_selected_route_execution_preflight")
        self.assertIn("selected_route_execution_preflight_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(invalid_report["status"], "blocked_by_selected_route_execution_preflight")
        self.assertIn("selected_route_execution_preflight_missing_or_invalid_schema", invalid_report["blocking_reasons"])
        self.assertEqual(unready_report["status"], "blocked_by_selected_route_execution_preflight")
        self.assertIn("selected_route_execution_preflight_not_ready", unready_report["blocking_reasons"])

    def test_bdd_p7aa_execute_requires_explicit_confirmation(self) -> None:
        """行为 5：execute 缺 confirm 时阻断。"""
        report = build_auto_mode_formal_package_selected_route_execute(
            self._ready_preflight("pdf_export"),
            mode="execute",
            confirm_execute=False,
            reviewer="unit_test_reviewer",
            note="Execute selected route.",
        )

        self.assertEqual(report["status"], "blocked_by_missing_selected_route_execute_confirmation")
        self.assertFalse(report["selected_route_execute_manifest_recorded"])
        self.assertIn("confirm_execute_required", report["blocking_reasons"])

    def test_bdd_p7aa_execute_requires_reviewer_and_note(self) -> None:
        """行为 6：execute 缺 reviewer/note 时阻断。"""
        report = build_auto_mode_formal_package_selected_route_execute(
            self._ready_preflight("pdf_export"),
            mode="execute",
            confirm_execute=True,
            reviewer="",
            note="",
        )

        self.assertEqual(report["status"], "blocked_by_selected_route_execute_metadata")
        self.assertFalse(report["selected_route_execute_manifest_recorded"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("execute_note_required", report["blocking_reasons"])

    def test_bdd_p7aa_bad_selected_route_plan_contract_blocks_execution(self) -> None:
        """行为 7：selected route plan 不干净时阻断。"""
        unknown = self._ready_preflight("pdf_export")
        unknown["selected_route_execution_plan"][0]["route_type"] = "unknown_route"
        duplicated = self._ready_preflight("pdf_export")
        duplicated["selected_route_execution_plan"].append(dict(duplicated["selected_route_execution_plan"][0]))
        already_marked = self._ready_preflight("pdf_export")
        already_marked["selected_route_execution_plan"][0]["will_execute_by_this_command"] = True
        no_command = self._ready_preflight("pdf_export")
        no_command["selected_route_execution_plan"][0]["next_command"] = ""
        no_outputs = self._ready_preflight("pdf_export")
        no_outputs["selected_route_execution_plan"][0]["planned_outputs"] = []

        reports = [
            build_auto_mode_formal_package_selected_route_execute(item, mode="dry-run")
            for item in [unknown, duplicated, already_marked, no_command, no_outputs]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_selected_route_execute_contract" for report in reports))
        self.assertIn("selected_route_type_unknown:unknown_route", reports[0]["blocking_reasons"])
        self.assertIn("selected_route_execution_plan_not_single", reports[1]["blocking_reasons"])
        self.assertIn("selected_route_marked_execute_by_this_command:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("selected_route_next_command_missing:pdf_export", reports[3]["blocking_reasons"])
        self.assertIn("selected_route_planned_outputs_missing:pdf_export", reports[4]["blocking_reasons"])

    def test_bdd_p7aa_confirmed_execute_records_manifest_only(self) -> None:
        """行为 8：确认 execute 只写 execute manifest，不写正式包产物。"""
        report = build_auto_mode_formal_package_selected_route_execute(
            self._ready_preflight("package_manifest"),
            mode="execute",
            confirm_execute=True,
            reviewer="unit_test_reviewer",
            note="Record selected route execute manifest for later artifact executor.",
            execute_manifest_path=Path("workspace/formal_package_selected_route_execute/custom/execute_manifest.json"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path, manifest_path = write_auto_mode_formal_package_selected_route_execute_outputs(
                project_root,
                report,
                execute_manifest_path=Path("workspace/formal_package_selected_route_execute/custom/execute_manifest.json"),
            )

            self.assertEqual(report["status"], "selected_route_execute_manifest_recorded")
            self.assertTrue(report["selected_route_execute_manifest_recorded"])
            self.assertFalse(report["selected_route_executed"])
            self.assertFalse(report["package_manifest_generated"])
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIsNotNone(manifest_path)
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "p7.auto_mode_formal_package_selected_route_execute_manifest.v1")
            self.assertEqual(len(manifest["selected_route_execute_operations"]), 1)
            self.assertFalse(manifest["selected_route_executed"])
            self.assertFalse(manifest["export_or_acceptance_executed"])
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.docx").exists())
            self.assertFalse((project_root / "Submissions/formal_package/manifest.json").exists())
            self.assertFalse((project_root / "Reviews/formal_package_manual_acceptance.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_selected_route_execute.json").exists())

    def test_bdd_p7aa_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 9：CLI 默认读取当前 blocked P7-Z，写 blocked execute gate。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
                self._blocked_preflight(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_selected_route_execute.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_selected_route_execution_preflight", result.stdout)
            self.assertIn("can_execute_selected_route_with_confirmation=false", result.stdout)
            self.assertIn("selected_route_execute_manifest_recorded=false", result.stdout)
            self.assertIn("selected_route_execute_operations=0", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_package_selected_route_execute.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_package_selected_route_execute.md").exists())
            self.assertFalse(
                (
                    project_root
                    / "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
                ).exists()
            )

    def _ready_preflight(self, route_type: str) -> dict:
        planned_outputs = {
            "pdf_export": ["Submissions/formal_package/paper.pdf"],
            "docx_export": ["Submissions/formal_package/paper.docx"],
            "package_manifest": ["Submissions/formal_package/manifest.json"],
            "manual_acceptance": ["Reviews/formal_package_manual_acceptance.md"],
        }[route_type]
        routed_action = {
            "pdf_export": "formal_pdf_export_preflight",
            "docx_export": "formal_docx_export_preflight",
            "package_manifest": "formal_submission_package_manifest_preflight",
            "manual_acceptance": "manual_acceptance_packet_preflight",
        }[route_type]
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execution_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "formal_package_export_acceptance_route_recorded",
            "status": "ready_for_selected_formal_package_route_execution_review",
            "can_request_selected_route_execution": True,
            "requires_explicit_route_execute_command": True,
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
            "selected_route_execution_plan": [
                {
                    "route_execution_id": f"selected_formal_package_route_execution::{routed_action}",
                    "routed_action": routed_action,
                    "route_type": route_type,
                    "next_command": f"formal_{route_type}_execute",
                    "source_formal_targets": [
                        "Submissions/formal_package/manuscript/paper.md",
                    ],
                    "planned_outputs": planned_outputs,
                    "execution_status": "pending_explicit_route_execute_command",
                    "requires_explicit_route_execute_command": True,
                    "will_execute_by_this_command": False,
                    "will_render_pdf_by_this_command": False,
                    "will_render_docx_by_this_command": False,
                    "will_generate_manifest_by_this_command": False,
                    "will_perform_manual_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_preflight(self) -> dict:
        preflight = self._ready_preflight("pdf_export")
        preflight["source_status"] = "blocked_by_export_acceptance_preflight"
        preflight["status"] = "blocked_by_export_acceptance_router"
        preflight["can_request_selected_route_execution"] = False
        preflight["requires_explicit_route_execute_command"] = False
        preflight["blocking_reasons"] = ["export_acceptance_router_not_route_recorded"]
        preflight["selected_route_execution_plan"] = []
        return preflight

    def _clean_boundary_flags(self) -> dict:
        return {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "reran_models": False,
            "modified_statistical_execution_artifacts": False,
            "executed_target_adapters": False,
            "wrote_formal_state": False,
            "created_or_repaired_candidate_targets": False,
            "promoted_candidate_targets": False,
            "exported_or_accepted_formal_package": False,
            "generated_package_manifest": False,
            "performed_manual_acceptance": False,
        }

    def _source_paths(self) -> dict:
        return {
            "selected_route_execution_preflight": (
                "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

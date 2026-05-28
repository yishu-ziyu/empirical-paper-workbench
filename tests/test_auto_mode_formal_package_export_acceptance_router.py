import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_export_acceptance_router import (
    build_auto_mode_formal_package_export_acceptance_router,
    write_auto_mode_formal_package_export_acceptance_router_outputs,
)


class AutoModeFormalPackageExportAcceptanceRouterTests(unittest.TestCase):
    """BDD: P7-Y records an explicit route from P7-X without exporting or accepting."""

    def test_bdd_p7y_ready_defer_waits_without_route(self) -> None:
        """行为 1：P7-X ready 但 defer 时等待人工选择。"""
        report = build_auto_mode_formal_package_export_acceptance_router(
            self._ready_preflight(),
            decision="defer",
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_package_export_acceptance_router.v1")
        self.assertEqual(report["status"], "waiting_for_formal_package_export_acceptance_decision")
        self.assertFalse(report["can_route_export_or_acceptance"])
        self.assertFalse(report["route_recorded"])
        self.assertEqual(report["routed_action"], "")
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["rendered_pdf"])
        self.assertFalse(report["rendered_docx"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7y_confirmed_pdf_export_records_route_without_export(self) -> None:
        """行为 2：确认 PDF 路由后只记录下一步，不导出。"""
        report = build_auto_mode_formal_package_export_acceptance_router(
            self._ready_preflight(),
            decision="pdf_export",
            confirm_route=True,
            reviewer="reviewer-a",
            note="PDF export is the next explicit command.",
        )

        self.assertEqual(report["status"], "formal_package_export_acceptance_route_recorded")
        self.assertTrue(report["can_route_export_or_acceptance"])
        self.assertTrue(report["route_recorded"])
        self.assertEqual(report["routed_action"], "formal_pdf_export_preflight")
        self.assertEqual(report["selected_plan_item"]["action_id"], "formal_pdf_export_preflight")
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["rendered_pdf"])
        self.assertFalse(report["rendered_docx"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7y_current_blocked_preflight_blocks_router(self) -> None:
        """行为 3：当前 P7-X blocked 时不能记录路线。"""
        report = build_auto_mode_formal_package_export_acceptance_router(
            self._blocked_preflight(),
            decision="defer",
        )

        self.assertEqual(report["status"], "blocked_by_export_acceptance_preflight")
        self.assertFalse(report["can_route_export_or_acceptance"])
        self.assertFalse(report["route_recorded"])
        self.assertEqual(report["routed_action"], "")
        self.assertIn("export_acceptance_preflight_not_ready", report["blocking_reasons"])

    def test_bdd_p7y_unknown_or_missing_plan_action_blocks_route(self) -> None:
        """行为 4：未知 decision 或不在 P7-X plan 中的动作必须阻断。"""
        unknown = build_auto_mode_formal_package_export_acceptance_router(
            self._ready_preflight(),
            decision="spreadsheet_export",
            confirm_route=True,
            reviewer="reviewer-a",
            note="Unknown route.",
        )
        missing_plan = self._ready_preflight()
        missing_plan["export_acceptance_plan"] = [
            item
            for item in missing_plan["export_acceptance_plan"]
            if item["action_id"] != "formal_pdf_export_preflight"
        ]
        missing = build_auto_mode_formal_package_export_acceptance_router(
            missing_plan,
            decision="pdf_export",
            confirm_route=True,
            reviewer="reviewer-a",
            note="PDF route.",
        )

        self.assertEqual(unknown["status"], "blocked_by_unknown_export_acceptance_decision")
        self.assertIn("export_acceptance_decision_invalid:spreadsheet_export", unknown["blocking_reasons"])
        self.assertEqual(missing["status"], "blocked_by_export_acceptance_route")
        self.assertIn("export_acceptance_action_not_in_preflight_plan:formal_pdf_export_preflight", missing["blocking_reasons"])

    def test_bdd_p7y_route_requires_confirmation_reviewer_and_note(self) -> None:
        """行为 5：非 defer 路由必须有确认、reviewer 和 note。"""
        missing_confirm = build_auto_mode_formal_package_export_acceptance_router(
            self._ready_preflight(),
            decision="pdf_export",
            reviewer="reviewer-a",
            note="PDF route.",
        )
        missing_reviewer = build_auto_mode_formal_package_export_acceptance_router(
            self._ready_preflight(),
            decision="pdf_export",
            confirm_route=True,
            note="PDF route.",
        )
        missing_note = build_auto_mode_formal_package_export_acceptance_router(
            self._ready_preflight(),
            decision="pdf_export",
            confirm_route=True,
            reviewer="reviewer-a",
        )

        self.assertEqual(missing_confirm["status"], "blocked_by_missing_export_acceptance_route_confirmation")
        self.assertIn("confirm_route_required", missing_confirm["blocking_reasons"])
        self.assertEqual(missing_reviewer["status"], "blocked_by_export_acceptance_route_metadata")
        self.assertIn("reviewer_required", missing_reviewer["blocking_reasons"])
        self.assertEqual(missing_note["status"], "blocked_by_export_acceptance_route_metadata")
        self.assertIn("route_note_required", missing_note["blocking_reasons"])

    def test_bdd_p7y_boundary_violations_block_router(self) -> None:
        """行为 6：P7-X 带导出、渲染、正式层或产品层副作用时阻断。"""
        rendered = self._ready_preflight()
        rendered["rendered_pdf"] = True
        product_state = self._ready_preflight()
        product_state["can_write_product_state"] = True
        boundary = self._ready_preflight()
        boundary["boundary_flags"]["exported_or_accepted_formal_package"] = True

        rendered_report = build_auto_mode_formal_package_export_acceptance_router(rendered)
        product_report = build_auto_mode_formal_package_export_acceptance_router(product_state)
        boundary_report = build_auto_mode_formal_package_export_acceptance_router(boundary)

        self.assertEqual(rendered_report["status"], "blocked_by_export_acceptance_preflight")
        self.assertIn("export_acceptance_preflight_rendered_pdf", rendered_report["blocking_reasons"])
        self.assertEqual(product_report["status"], "blocked_by_export_acceptance_preflight")
        self.assertIn("export_acceptance_preflight_allows_product_state_write", product_report["blocking_reasons"])
        self.assertEqual(boundary_report["status"], "blocked_by_export_acceptance_preflight")
        self.assertIn(
            "export_acceptance_preflight_boundary_violation:exported_or_accepted_formal_package",
            boundary_report["blocking_reasons"],
        )

    def test_bdd_p7y_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 3：CLI 默认读取当前 blocked P7-X，继续不记录路线。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_export_acceptance_preflight.json",
                self._blocked_preflight(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_export_acceptance_router.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_export_acceptance_preflight", result.stdout)
            self.assertIn("can_route_export_or_acceptance=false", result.stdout)
            self.assertIn("route_recorded=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_package_export_acceptance_router.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_package_export_acceptance_router.md").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.docx").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_export_acceptance_router.json").exists())

    def test_bdd_p7y_writes_report_and_review_only(self) -> None:
        """行为 7：只写 router report/review，不导出不验收不写产品状态。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_export_acceptance_router(
                self._ready_preflight(),
                decision="manual_acceptance",
                confirm_route=True,
                reviewer="reviewer-a",
                note="Manual acceptance should be a later command.",
            )
            report_path, review_path = write_auto_mode_formal_package_export_acceptance_router_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "formal_package_export_acceptance_route_recorded")
            self.assertEqual(written["routed_action"], "manual_acceptance_packet_preflight")
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.docx").exists())
            self.assertFalse((project_root / "Submissions/formal_package/manifest.json").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_export_acceptance_router.json").exists())

    def _ready_preflight(self) -> dict:
        plan = []
        for action_id in [
            "formal_pdf_export_preflight",
            "formal_docx_export_preflight",
            "formal_submission_package_manifest_preflight",
            "manual_acceptance_packet_preflight",
        ]:
            plan.append(
                {
                    "action_id": action_id,
                    "label": action_id.replace("_", " ").title(),
                    "description": "Later explicit command.",
                    "source_formal_targets": [
                        "Submissions/formal_package/manuscript/paper.md",
                        "Submissions/formal_package/bibliography/literature_review_packet.json",
                    ],
                    "execution_status": "pending_explicit_export_or_acceptance_command",
                    "requires_explicit_export_or_acceptance_command": True,
                    "this_command_rendered_or_accepted": False,
                    "this_command_wrote_product_state": False,
                }
            )
        return {
            "schema_version": "p7.auto_mode_formal_package_export_acceptance_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_formal_package_export_acceptance_review",
            "can_enter_formal_package_export_acceptance": True,
            "requires_explicit_export_or_acceptance_command": True,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "source_verification": {"status": "promoted_formal_package_verified_for_review"},
            "formal_package_summary": {
                "formal_target_count": 2,
                "target_groups": ["formal_manuscript_sources", "formal_bibliography_sources"],
                "formal_target_paths": [
                    "Submissions/formal_package/manuscript/paper.md",
                    "Submissions/formal_package/bibliography/literature_review_packet.json",
                ],
                "all_targets_verified": True,
            },
            "export_acceptance_plan": plan,
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_preflight(self) -> dict:
        report = self._ready_preflight()
        report["status"] = "blocked_by_promoted_package_verification"
        report["can_enter_formal_package_export_acceptance"] = False
        report["requires_explicit_export_or_acceptance_command"] = False
        report["export_acceptance_plan"] = []
        report["blocking_reasons"] = ["promoted_formal_package_verification_not_ready"]
        return report

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
        }

    def _source_paths(self) -> dict:
        return {
            "export_acceptance_preflight": "Results/json/auto_mode_formal_package_export_acceptance_preflight.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

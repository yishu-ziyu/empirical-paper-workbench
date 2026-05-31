import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review import (
    build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review,
    write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateRoutedNextGateEntryPreflightEntryResultReviewTests(unittest.TestCase):
    """BDD: P7-BA reviews P7-AZ before the explicit routed next-gate entry gate."""

    def test_bdd_p7ba_ready_entry_and_clean_preflight_create_explicit_entry_input(self) -> None:
        """行为 1：ready P7-AZ 和 clean preflight 才生成 explicit entry input。"""
        preflight = self._ready_preflight("package_manifest")
        report = (
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
                Path("."),
                self._ready_entry("package_manifest"),
                preflight,
                source_paths=self._source_paths(),
            )
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.v1",
        )
        self.assertEqual(report["status"], "routed_next_gate_entry_preflight_entry_result_review_ready")
        self.assertTrue(report["routed_next_gate_entry_preflight_entry_result_reviewed"])
        self.assertTrue(report["can_continue_to_explicit_routed_next_gate_entry"])
        self.assertTrue(report["can_request_routed_next_gate_entry"])
        self.assertTrue(report["requires_explicit_next_gate_entry_command"])
        self.assertEqual(report["verified_route_type"], "package_manifest")
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(report["routed_next_gate_entry_preflight_status"], "ready_for_routed_next_gate_entry_review")
        self.assertEqual(report["next_gate_entry_plan"], preflight["next_gate_entry_plan"])
        self.assertEqual(len(report["explicit_routed_next_gate_entry_input_records"]), 1)
        record = report["explicit_routed_next_gate_entry_input_records"][0]
        self.assertEqual(
            record["record_id"],
            "explicit_routed_next_gate_entry_input::formal_package_export_acceptance_router::package_manifest",
        )
        self.assertEqual(
            record["routed_next_gate_entry_preflight_report_path"],
            "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json",
        )
        self.assertEqual(
            record["review_status"],
            "routed_next_gate_entry_preflight_accepted_for_explicit_entry_gate",
        )
        self.assertFalse(report["explicit_routed_next_gate_entry_executed"])
        self.assertFalse(report["this_command_entered_next_gate"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ba_current_blocked_entry_blocks_review(self) -> None:
        """行为 2：当前 P7-AZ blocked 时继续阻断，不生成 explicit entry input。"""
        report = (
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
                Path("."),
                {},
                {},
            )
        )

        self.assertEqual(report["status"], "blocked_by_routed_next_gate_entry_preflight_entry")
        self.assertFalse(report["routed_next_gate_entry_preflight_entry_result_reviewed"])
        self.assertFalse(report["can_continue_to_explicit_routed_next_gate_entry"])
        self.assertEqual(report["explicit_routed_next_gate_entry_input_records"], [])
        self.assertIn(
            "routed_next_gate_entry_preflight_entry_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7ba_missing_invalid_or_not_entered_entry_blocks_review(self) -> None:
        """行为 3：P7-AZ 缺失、schema 错、未 entered 或有 blockers 时阻断。"""
        wrong_schema = self._ready_entry("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_entered = self._ready_entry("package_manifest")
        not_entered["status"] = "blocked_by_verified_route_next_gate_router_entry_result_review"
        blocked = self._ready_entry("package_manifest")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
                Path("."),
                source,
                self._ready_preflight("package_manifest"),
            )
            for source in [wrong_schema, not_entered, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_routed_next_gate_entry_preflight_entry" for report in reports)
        )
        self.assertIn(
            "routed_next_gate_entry_preflight_entry_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn("routed_next_gate_entry_preflight_entry_not_entered", reports[1]["blocking_reasons"])
        self.assertIn("source_preflight_entry_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7ba_entry_result_must_match_existing_preflight_output(self) -> None:
        """行为 4：P7-AZ 记录的 preflight 路径、状态和摘要必须匹配真实 preflight。"""
        wrong_path = self._ready_entry("package_manifest")
        wrong_path["routed_next_gate_entry_preflight_report_path"] = "Results/json/wrong.json"
        wrong_status = self._ready_entry("package_manifest")
        wrong_status["routed_next_gate_entry_preflight_result"]["status"] = "blocked"
        summary_mismatch = self._ready_entry("package_manifest")
        summary_mismatch["routed_next_gate_entry_preflight_result"][
            "routed_next_gate_entry_preflight_report_summary"
        ]["routed_next_gate"] = "wrong_gate"

        reports = [
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
                Path("."),
                source,
                self._ready_preflight("package_manifest"),
            )
            for source in [wrong_path, wrong_status, summary_mismatch]
        ]

        self.assertTrue(
            all(
                report["status"]
                == "blocked_by_routed_next_gate_entry_preflight_entry_result_contract"
                for report in reports
            )
        )
        self.assertIn(
            "routed_next_gate_entry_preflight_report_path_mismatch:package_manifest",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "routed_next_gate_entry_preflight_result_status_mismatch:package_manifest",
            reports[1]["blocking_reasons"],
        )
        self.assertIn(
            "routed_next_gate_entry_preflight_summary_routed_next_gate_mismatch:package_manifest",
            reports[2]["blocking_reasons"],
        )

    def test_bdd_p7ba_preflight_must_be_clean_for_explicit_entry(self) -> None:
        """行为 5：preflight schema、状态、请求权限和 entry plan 必须干净。"""
        wrong_schema = self._ready_preflight("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._ready_preflight("package_manifest")
        not_ready["status"] = "blocked_by_verified_route_next_gate_router"
        no_plan = self._ready_preflight("package_manifest")
        no_plan["next_gate_entry_plan"] = []
        plan_mismatch = self._ready_preflight("package_manifest")
        plan_mismatch["next_gate_entry_plan"][0]["gate_id"] = "wrong_gate"

        reports = [
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
                Path("."),
                self._ready_entry("package_manifest"),
                source,
            )
            for source in [wrong_schema, not_ready, no_plan, plan_mismatch]
        ]

        self.assertEqual(reports[0]["status"], "blocked_by_routed_next_gate_entry_preflight_review")
        self.assertIn("routed_next_gate_entry_preflight_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertEqual(reports[1]["status"], "blocked_by_routed_next_gate_entry_preflight_review")
        self.assertIn("routed_next_gate_entry_preflight_not_ready", reports[1]["blocking_reasons"])
        self.assertEqual(reports[2]["status"], "blocked_by_routed_next_gate_entry_preflight_review")
        self.assertIn("routed_next_gate_entry_plan_missing", reports[2]["blocking_reasons"])
        self.assertEqual(
            reports[3]["status"],
            "blocked_by_routed_next_gate_entry_preflight_entry_result_contract",
        )
        self.assertIn(
            "routed_next_gate_entry_gate_mismatch:formal_package_export_acceptance_router",
            reports[3]["blocking_reasons"],
        )

    def test_bdd_p7ba_boundary_violations_block_review(self) -> None:
        """行为 6：正式层写入或越界标志都会阻断。"""
        entry_boundary = self._ready_entry("package_manifest")
        entry_boundary["can_write_product_state"] = True
        preflight_boundary = self._ready_preflight("package_manifest")
        preflight_boundary["this_command_entered_next_gate"] = True
        preflight_boundary["boundary_flags"]["modified_product_state"] = True

        entry_report = (
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
                Path("."),
                entry_boundary,
                self._ready_preflight("package_manifest"),
            )
        )
        preflight_report = (
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
                Path("."),
                self._ready_entry("package_manifest"),
                preflight_boundary,
            )
        )

        self.assertEqual(
            entry_report["status"],
            "blocked_by_routed_next_gate_entry_preflight_entry_result_boundary",
        )
        self.assertIn("routed_next_gate_entry_preflight_entry_allows_product_state_write", entry_report["blocking_reasons"])
        self.assertEqual(
            preflight_report["status"],
            "blocked_by_routed_next_gate_entry_preflight_entry_result_boundary",
        )
        self.assertIn("routed_next_gate_entry_preflight_entered_next_gate", preflight_report["blocking_reasons"])
        self.assertIn(
            "routed_next_gate_entry_preflight_boundary_violation:modified_product_state",
            preflight_report["blocking_reasons"],
        )

    def test_bdd_p7ba_writes_result_review_only(self) -> None:
        """行为 7：只写 P7-BA result review，不进入下一关、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = (
                build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
                    project_root,
                    self._ready_entry("package_manifest"),
                    self._ready_preflight("package_manifest"),
                )
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "routed_next_gate_entry_preflight_entry_result_review_ready")
            self.assertFalse(written["explicit_routed_next_gate_entry_executed"])
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.json"
                ).exists()
            )

    def test_bdd_p7ba_cli_defaults_to_current_blocked_preflight_entry(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AZ report，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            entry_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.json"
            )
            preflight_path = project_root / "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json"
            entry_path.parent.mkdir(parents=True, exist_ok=True)
            entry_path.write_text(
                json.dumps({"status": "blocked_by_verified_route_next_gate_router_entry_result_review"}),
                encoding="utf-8",
            )
            preflight_path.write_text(json.dumps({}), encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_routed_next_gate_entry_preflight_entry", result.stdout)
            self.assertIn("routed_next_gate_entry_preflight_entry_result_reviewed=false", result.stdout)
            self.assertIn("can_continue_to_explicit_routed_next_gate_entry=false", result.stdout)
            self.assertIn("explicit_routed_next_gate_entry_input_records=0", result.stdout)
            self.assertIn("explicit_routed_next_gate_entry_executed=false", result.stdout)
            self.assertIn("this_command_entered_next_gate=false", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.json"
                ).exists()
            )

    def _ready_entry(self, route_type: str) -> dict:
        preflight = self._ready_preflight(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "verified_route_next_gate_router_entry_result_review_ready",
            "status": "next_gate_routed_next_gate_entry_preflight_entered",
            "verified_route_type": route_type,
            "routed_next_gate": preflight["routed_next_gate"],
            "can_enter_routed_next_gate_entry_preflight": True,
            "routed_next_gate_entry_preflight_entry_command": ["python3"],
            "routed_next_gate_entry_preflight_entry_command_executed": True,
            "this_command_ran_routed_next_gate_entry_preflight": True,
            "routed_next_gate_entry_preflight_report_path": (
                "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json"
            ),
            "routed_next_gate_entry_preflight_review_path": (
                "Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md"
            ),
            "routed_next_gate_entry_preflight_returncode": 0,
            "routed_next_gate_entry_preflight_status": "ready_for_routed_next_gate_entry_review",
            "routed_next_gate_entry_preflight_result": {
                "stdout": "",
                "stderr": "",
                "returncode": 0,
                "status": "ready_for_routed_next_gate_entry_review",
                "report_path": "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json",
                "review_path": "Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md",
                "routed_next_gate_entry_preflight_report_summary": {
                    "schema_version": "p7.auto_mode_formal_package_routed_next_gate_entry_preflight.v1",
                    "status": "ready_for_routed_next_gate_entry_review",
                    "verified_route_type": route_type,
                    "routed_next_gate": preflight["routed_next_gate"],
                    "can_request_routed_next_gate_entry": True,
                    "next_gate_entry_plan_count": 1,
                    "blocking_reasons": [],
                },
            },
            "can_request_routed_next_gate_entry": True,
            "requires_explicit_next_gate_entry_command": True,
            "next_gate_entry_plan": preflight["next_gate_entry_plan"],
            "next_gate_entered": False,
            "this_command_entered_next_gate": False,
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
            "next_action": {"id": "review_routed_next_gate_entry_preflight_result"},
        }

    def _ready_preflight(self, route_type: str) -> dict:
        gate_id = (
            "formal_package_delivery_completion_gate"
            if route_type == "manual_acceptance"
            else "formal_package_export_acceptance_router"
        )
        action = (
            "finalize_formal_package_delivery_review"
            if route_type == "manual_acceptance"
            else "continue_formal_package_export_acceptance_cycle"
        )
        next_command = (
            "auto_mode_formal_package_delivery_completion_gate"
            if route_type == "manual_acceptance"
            else "auto_mode_formal_package_export_acceptance_router"
        )
        entry_kind = "delivery_completion" if route_type == "manual_acceptance" else "continue_export_acceptance_cycle"
        return {
            "schema_version": "p7.auto_mode_formal_package_routed_next_gate_entry_preflight.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "verified_route_next_gate_route_recorded",
            "status": "ready_for_routed_next_gate_entry_review",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "can_request_routed_next_gate_entry": True,
            "requires_explicit_next_gate_entry_command": True,
            "next_gate_entered": False,
            "this_command_entered_next_gate": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "source_router": {},
            "next_gate_entry_plan": [
                {
                    "entry_id": f"routed_next_gate_entry::{gate_id}::{route_type}",
                    "source_route_id": f"verified_route_next_gate::{route_type}",
                    "verified_route_type": route_type,
                    "gate_id": gate_id,
                    "entry_kind": entry_kind,
                    "next_gate_action": action,
                    "next_command": next_command,
                    "entry_status": "pending_explicit_next_gate_entry_command",
                    "requires_explicit_next_gate_entry_command": True,
                    "will_enter_next_gate_by_this_command": False,
                    "will_execute_export_or_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                    "handoff_summary": "Package manifest completion is verified.",
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
            "next_action": {"id": next_command},
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
            "ran_routed_next_gate_entry_preflight": False,
        }

    def _source_paths(self) -> dict:
        return {
            "routed_next_gate_entry_preflight_entry": (
                "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.json"
            ),
            "routed_next_gate_entry_preflight": (
                "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

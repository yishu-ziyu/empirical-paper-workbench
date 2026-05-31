import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review import (
    build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review,
    write_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateVerifiedRouteNextGateRouterEntryResultReviewTests(unittest.TestCase):
    """BDD: P7-AY reviews P7-AX before routed next gate entry preflight."""

    def test_bdd_p7ay_ready_entry_and_clean_router_are_review_ready(self) -> None:
        """行为 1：ready P7-AX 和干净 router 输出才放行到 routed next gate preflight。"""
        report = build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
            Path("."),
            self._ready_entry("package_manifest"),
            self._ready_router("package_manifest"),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.v1",
        )
        self.assertEqual(report["status"], "verified_route_next_gate_router_entry_result_review_ready")
        self.assertTrue(report["verified_route_next_gate_router_entry_result_reviewed"])
        self.assertTrue(report["can_continue_to_routed_next_gate_entry_preflight"])
        self.assertEqual(report["verified_route_type"], "package_manifest")
        self.assertEqual(report["verified_route_next_gate_router_status"], "verified_route_next_gate_route_recorded")
        self.assertTrue(report["next_gate_route_recorded"])
        self.assertTrue(report["can_enter_routed_next_gate"])
        self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
        self.assertEqual(len(report["routed_next_gate_entry_preflight_input_records"]), 1)
        record = report["routed_next_gate_entry_preflight_input_records"][0]
        self.assertEqual(
            record["record_id"],
            "routed_next_gate_entry_preflight_input::formal_package_export_acceptance_router::package_manifest",
        )
        self.assertEqual(
            record["verified_route_next_gate_router_report_path"],
            "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json",
        )
        self.assertEqual(
            record["review_status"],
            "verified_route_next_gate_router_entry_accepted_for_routed_next_gate_entry_preflight",
        )
        self.assertFalse(report["routed_next_gate_entry_preflight_executed"])
        self.assertFalse(report["this_command_ran_routed_next_gate_entry_preflight"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ay_current_blocked_entry_blocks_review(self) -> None:
        """行为 2：当前 P7-AX blocked 时继续阻断，不生成 preflight input。"""
        report = build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
            Path("."),
            {},
            {},
        )

        self.assertEqual(report["status"], "blocked_by_verified_route_next_gate_router_entry")
        self.assertFalse(report["verified_route_next_gate_router_entry_result_reviewed"])
        self.assertFalse(report["can_continue_to_routed_next_gate_entry_preflight"])
        self.assertEqual(report["routed_next_gate_entry_preflight_input_records"], [])
        self.assertIn(
            "verified_route_next_gate_router_entry_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7ay_missing_invalid_or_not_entered_entry_blocks_review(self) -> None:
        """行为 3：P7-AX 缺失、schema 错、未 entered 或有 blockers 时阻断。"""
        wrong_schema = self._ready_entry("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_entered = self._ready_entry("package_manifest")
        not_entered["status"] = "blocked_by_verified_route_completion_ledger_entry_result_review"
        blocked = self._ready_entry("package_manifest")
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
                Path("."),
                source,
                self._ready_router("package_manifest"),
            )
            for source in [wrong_schema, not_entered, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_verified_route_next_gate_router_entry" for report in reports)
        )
        self.assertIn("verified_route_next_gate_router_entry_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertIn("verified_route_next_gate_router_entry_not_entered", reports[1]["blocking_reasons"])
        self.assertIn("source_router_entry_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7ay_entry_result_must_match_existing_router(self) -> None:
        """行为 4：P7-AX 记录的 router 路径、状态和摘要必须匹配真实 router。"""
        wrong_path = self._ready_entry("package_manifest")
        wrong_path["verified_route_next_gate_router_report_path"] = "Results/json/wrong.json"
        wrong_status = self._ready_entry("package_manifest")
        wrong_status["verified_route_next_gate_router_result"]["status"] = "blocked"
        summary_mismatch = self._ready_entry("package_manifest")
        summary_mismatch["verified_route_next_gate_router_result"][
            "verified_route_next_gate_router_report_summary"
        ]["routed_next_gate"] = "wrong_gate"

        reports = [
            build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
                Path("."),
                source,
                self._ready_router("package_manifest"),
            )
            for source in [wrong_path, wrong_status, summary_mismatch]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_verified_route_next_gate_router_entry_result_contract"
                for report in reports
            )
        )
        self.assertIn("verified_route_next_gate_router_report_path_mismatch:package_manifest", reports[0]["blocking_reasons"])
        self.assertIn("verified_route_next_gate_router_result_status_mismatch:package_manifest", reports[1]["blocking_reasons"])
        self.assertIn(
            "verified_route_next_gate_router_summary_routed_next_gate_mismatch:package_manifest",
            reports[2]["blocking_reasons"],
        )

    def test_bdd_p7ay_router_must_be_clean_for_routed_preflight(self) -> None:
        """行为 5：router schema、状态、route record 和 next gate route 必须干净。"""
        wrong_schema = self._ready_router("package_manifest")
        wrong_schema["schema_version"] = "wrong.schema"
        not_recorded = self._ready_router("package_manifest")
        not_recorded["status"] = "blocked_by_verified_route_next_gate_contract"
        no_route = self._ready_router("package_manifest")
        no_route["next_gate_route"] = {}
        route_mismatch = self._ready_router("package_manifest")
        route_mismatch["next_gate_route"]["gate_id"] = "wrong_gate"

        reports = [
            build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
                Path("."),
                self._ready_entry("package_manifest"),
                source,
            )
            for source in [wrong_schema, not_recorded, no_route, route_mismatch]
        ]

        self.assertEqual(reports[0]["status"], "blocked_by_verified_route_next_gate_router_review")
        self.assertIn("verified_route_next_gate_router_missing_or_invalid_schema", reports[0]["blocking_reasons"])
        self.assertEqual(reports[1]["status"], "blocked_by_verified_route_next_gate_router_review")
        self.assertIn("verified_route_next_gate_router_not_route_recorded", reports[1]["blocking_reasons"])
        self.assertEqual(reports[2]["status"], "blocked_by_routed_next_gate_entry_preflight_probe")
        self.assertIn("next_gate_route_missing", reports[2]["blocking_reasons"])
        self.assertEqual(reports[3]["status"], "blocked_by_routed_next_gate_entry_preflight_probe")
        self.assertIn(
            "routed_next_gate_entry_preflight_probe_status:blocked_by_routed_next_gate_entry_contract",
            reports[3]["blocking_reasons"],
        )

    def test_bdd_p7ay_boundary_violations_block_review(self) -> None:
        """行为 6：正式层写入或越界标志都会阻断。"""
        entry_boundary = self._ready_entry("package_manifest")
        entry_boundary["can_write_product_state"] = True
        router_boundary = self._ready_router("package_manifest")
        router_boundary["this_command_entered_next_gate"] = True
        router_boundary["boundary_flags"]["modified_product_state"] = True

        entry_report = build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
            Path("."),
            entry_boundary,
            self._ready_router("package_manifest"),
        )
        router_report = build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
            Path("."),
            self._ready_entry("package_manifest"),
            router_boundary,
        )

        self.assertEqual(entry_report["status"], "blocked_by_verified_route_next_gate_router_entry")
        self.assertIn("router_entry_can_write_product_state", entry_report["blocking_reasons"])
        self.assertEqual(
            router_report["status"],
            "blocked_by_verified_route_next_gate_router_entry_result_boundary",
        )
        self.assertIn("verified_route_next_gate_router_entered_next_gate", router_report["blocking_reasons"])
        self.assertIn(
            "verified_route_next_gate_router_boundary_violation:modified_product_state",
            router_report["blocking_reasons"],
        )

    def test_bdd_p7ay_writes_result_review_only(self) -> None:
        """行为 7：只写 P7-AY result review，不运行 preflight、不写 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
                project_root,
                self._ready_entry("package_manifest"),
                self._ready_router("package_manifest"),
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "verified_route_next_gate_router_entry_result_review_ready")
            self.assertFalse(written["routed_next_gate_entry_preflight_executed"])
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.json"
                ).exists()
            )

    def test_bdd_p7ay_cli_defaults_to_current_blocked_router_entry(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AX report，写 blocked result review。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            entry_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry.json"
            )
            entry_path.parent.mkdir(parents=True, exist_ok=True)
            entry_path.write_text(
                json.dumps({"status": "blocked_by_verified_route_completion_ledger_entry_result_review"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_verified_route_next_gate_router_entry", result.stdout)
            self.assertIn("can_continue_to_routed_next_gate_entry_preflight=false", result.stdout)
            self.assertIn("routed_next_gate_entry_preflight_input_records=0", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.json"
                ).exists()
            )

    def _ready_entry(self, route_type: str) -> dict:
        router = self._ready_router(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "verified_route_completion_ledger_entry_result_review_ready",
            "status": "next_gate_verified_route_next_gate_router_entered",
            "verified_route_type": route_type,
            "can_enter_verified_route_next_gate_router": True,
            "verified_route_next_gate_router_entry_command_executed": True,
            "this_command_ran_verified_route_next_gate_router": True,
            "verified_route_next_gate_router_report_path": (
                "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json"
            ),
            "verified_route_next_gate_router_review_path": (
                "Reviews/auto_mode_formal_package_verified_route_next_gate_router.md"
            ),
            "verified_route_next_gate_router_returncode": 0,
            "verified_route_next_gate_router_status": "verified_route_next_gate_route_recorded",
            "verified_route_next_gate_router_result": {
                "stdout": "",
                "stderr": "",
                "returncode": 0,
                "status": "verified_route_next_gate_route_recorded",
                "report_path": "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json",
                "review_path": "Reviews/auto_mode_formal_package_verified_route_next_gate_router.md",
                "verified_route_next_gate_router_report_summary": {
                    "schema_version": "p7.auto_mode_formal_package_verified_route_next_gate_router.v1",
                    "status": "verified_route_next_gate_route_recorded",
                    "verified_route_type": route_type,
                    "next_gate_route_recorded": True,
                    "can_enter_routed_next_gate": True,
                    "routed_next_gate": router["routed_next_gate"],
                    "blocking_reasons": [],
                },
            },
            "next_gate_route_recorded": True,
            "can_enter_routed_next_gate": True,
            "routed_next_gate": router["routed_next_gate"],
            "next_gate_route": router["next_gate_route"],
            "route_completion_ledger_recorded": True,
            "can_enter_next_auto_mode_gate": True,
            "route_completion_record_count": 1,
            "route_completion_records": router["route_completion_records"],
            "entered_next_gate": False,
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
            "next_action": {"id": "run_routed_next_auto_mode_gate"},
        }

    def _ready_router(self, route_type: str) -> dict:
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
        return {
            "schema_version": "p7.auto_mode_formal_package_verified_route_next_gate_router.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "verified_route_completion_ledger_recorded",
            "status": "verified_route_next_gate_route_recorded",
            "verified_route_type": route_type,
            "next_gate_route_recorded": True,
            "can_enter_routed_next_gate": True,
            "routed_next_gate": gate_id,
            "next_gate_route": {
                "route_id": f"verified_route_next_gate::{route_type}",
                "route_type": route_type,
                "gate_id": gate_id,
                "next_gate_action": action,
                "routing_status": "pending_next_auto_mode_gate",
                "requires_explicit_next_gate_command": True,
                "this_command_entered_next_gate": False,
                "description": "Package manifest completion is verified.",
            },
            "route_completion_records_count": 1,
            "route_completion_ledger_recorded": True,
            "can_enter_next_auto_mode_gate": True,
            "export_or_acceptance_executed": False,
            "this_command_entered_next_gate": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "source_ledger": {},
            "route_completion_records": [self._completion_record(route_type)],
            "boundary_flags": self._clean_boundary_flags(),
            "next_action": {"id": gate_id},
        }

    def _completion_record(self, route_type: str) -> dict:
        return {
            "completion_id": f"verified_route_completion::{route_type}",
            "completion_status": "verified_route_completion_recorded",
            "route_type": route_type,
            "delegated_status": "route_done",
            "source_verification_status": "route_specific_artifact_verified_for_review",
            "source_product_state_verified": route_type == "manual_acceptance",
            "artifact_count": 1,
            "artifact_ids": ["package_manifest"],
            "verified_artifacts": [
                {
                    "artifact_id": "package_manifest",
                    "path": "Submissions/formal_package/package_manifest",
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
            "recorded_verified_route_next_gate_router": False,
        }

    def _source_paths(self) -> dict:
        return {
            "verified_route_next_gate_router_entry": (
                "Results/json/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry.json"
            ),
            "verified_route_next_gate_router": (
                "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json"
            ),
        }


if __name__ == "__main__":
    unittest.main()

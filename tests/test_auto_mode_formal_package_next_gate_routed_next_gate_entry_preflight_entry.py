import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry import (
    build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry,
    run_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry,
    write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateRoutedNextGateEntryPreflightEntryTests(unittest.TestCase):
    """BDD: P7-AZ enters the existing routed next gate entry preflight after P7-AY."""

    def test_bdd_p7az_ready_result_review_runs_existing_preflight(self) -> None:
        """行为 1：ready P7-AY 会调用既有 preflight 并记录进入计划。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            router = self._ready_router("package_manifest")
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json",
                router,
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
                project_root,
                self._result_review("package_manifest", router),
                repo_root=REPO_ROOT,
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_outputs(
                    project_root,
                    report,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(
                report["schema_version"],
                "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.v1",
            )
            self.assertEqual(report["status"], "next_gate_routed_next_gate_entry_preflight_entered")
            self.assertTrue(report["routed_next_gate_entry_preflight_entry_command_executed"])
            self.assertTrue(report["this_command_ran_routed_next_gate_entry_preflight"])
            self.assertEqual(
                report["routed_next_gate_entry_preflight_status"],
                "ready_for_routed_next_gate_entry_review",
            )
            self.assertTrue(report["can_request_routed_next_gate_entry"])
            self.assertEqual(report["verified_route_type"], "package_manifest")
            self.assertEqual(report["routed_next_gate"], "formal_package_export_acceptance_router")
            self.assertEqual(len(report["next_gate_entry_plan"]), 1)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.json"
                ).exists()
            )

    def test_bdd_p7az_current_blocked_result_review_blocks_preflight_entry(self) -> None:
        """行为 2：当前 P7-AY blocked 时不运行 preflight。"""
        report = build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
            Path("."),
            {},
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_verified_route_next_gate_router_entry_result_review")
        self.assertFalse(report["can_enter_routed_next_gate_entry_preflight"])
        self.assertEqual(report["routed_next_gate_entry_preflight_entry_command"], [])
        self.assertFalse(report["routed_next_gate_entry_preflight_entry_command_executed"])
        self.assertIn(
            "verified_route_next_gate_router_entry_result_review_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7az_missing_invalid_or_not_ready_result_review_blocks_entry(self) -> None:
        """行为 3：P7-AY 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        router = self._ready_router("package_manifest")
        wrong_schema = self._result_review("package_manifest", router)
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._result_review("package_manifest", router)
        not_ready["status"] = "blocked_by_verified_route_next_gate_router_entry"
        blocked = self._result_review("package_manifest", router)
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_verified_route_next_gate_router_entry_result_review"
                for report in reports
            )
        )
        self.assertIn(
            "verified_route_next_gate_router_entry_result_review_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "verified_route_next_gate_router_entry_result_review_not_ready",
            reports[1]["blocking_reasons"],
        )
        self.assertIn("source_result_review_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7az_preflight_input_record_contract_must_be_clean(self) -> None:
        """行为 4：preflight input record 缺失、重复、错配或未放行时阻断。"""
        router = self._ready_router("package_manifest")
        missing_record = self._result_review("package_manifest", router)
        missing_record["routed_next_gate_entry_preflight_input_records"] = []
        duplicated = self._result_review("package_manifest", router)
        duplicated["routed_next_gate_entry_preflight_input_records"].append(
            dict(duplicated["routed_next_gate_entry_preflight_input_records"][0])
        )
        wrong_path = self._result_review("package_manifest", router)
        wrong_path["routed_next_gate_entry_preflight_input_records"][0][
            "verified_route_next_gate_router_report_path"
        ] = "Results/json/wrong.json"
        wrong_status = self._result_review("package_manifest", router)
        wrong_status["routed_next_gate_entry_preflight_input_records"][0]["review_status"] = "wrong_status"

        reports = [
            build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_record, duplicated, wrong_path, wrong_status]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_routed_next_gate_entry_preflight_entry_contract"
                for report in reports
            )
        )
        self.assertIn("routed_next_gate_entry_preflight_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_preflight_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn(
            "verified_route_next_gate_router_report_path_mismatch:package_manifest",
            reports[2]["blocking_reasons"],
        )
        self.assertIn(
            "routed_next_gate_entry_preflight_input_record_review_status_mismatch:package_manifest",
            reports[3]["blocking_reasons"],
        )

    def test_bdd_p7az_missing_preflight_command_file_blocks_entry(self) -> None:
        """行为 5：preflight command 文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
            Path("."),
            self._result_review("package_manifest", self._ready_router("package_manifest")),
            repo_root=Path("/tmp/nonexistent-repo-for-p7az"),
        )

        self.assertEqual(report["status"], "blocked_by_routed_next_gate_entry_preflight_command_unavailable")
        self.assertIn(
            "routed_next_gate_entry_preflight_command_file_missing:Program/auto_mode_formal_package_routed_next_gate_entry_preflight.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["routed_next_gate_entry_preflight_entry_command_executed"])

    def test_bdd_p7az_preflight_failure_is_recorded_as_blocked(self) -> None:
        """行为 6：既有 preflight 运行后仍 blocked 时，P7-AZ 不放行。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            good_router = self._ready_router("package_manifest")
            bad_router = self._ready_router("package_manifest")
            bad_router["next_gate_route"] = {}
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json",
                bad_router,
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
                project_root,
                self._result_review("package_manifest", good_router),
                repo_root=REPO_ROOT,
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(report["status"], "blocked_by_routed_next_gate_entry_preflight_failure")
            self.assertTrue(report["routed_next_gate_entry_preflight_entry_command_executed"])
            self.assertEqual(
                report["routed_next_gate_entry_preflight_status"],
                "blocked_by_routed_next_gate_entry_contract",
            )
            self.assertFalse(report["can_request_routed_next_gate_entry"])
            self.assertIn(
                "routed_next_gate_entry_preflight_status:blocked_by_routed_next_gate_entry_contract",
                report["blocking_reasons"],
            )

    def test_bdd_p7az_cli_defaults_to_current_blocked_result_review(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AY report，写 blocked preflight entry。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_review_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.json"
            )
            result_review_path.parent.mkdir(parents=True, exist_ok=True)
            result_review_path.write_text(
                json.dumps({"status": "blocked_by_verified_route_next_gate_router_entry"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_verified_route_next_gate_router_entry_result_review", result.stdout)
            self.assertIn("can_enter_routed_next_gate_entry_preflight=false", result.stdout)
            self.assertIn("routed_next_gate_entry_preflight_entry_command_executed=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.json"
                ).exists()
            )

    def _result_review(self, route_type: str, router: dict) -> dict:
        routed_next_gate = router["routed_next_gate"]
        route = router["next_gate_route"]
        return {
            "schema_version": (
                "p7.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.v1"
            ),
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_verified_route_next_gate_router_entered",
            "status": "verified_route_next_gate_router_entry_result_review_ready",
            "verified_route_type": route_type,
            "verified_route_next_gate_router_status": "verified_route_next_gate_route_recorded",
            "verified_route_next_gate_router_entry_result_reviewed": True,
            "can_continue_to_routed_next_gate_entry_preflight": True,
            "next_gate_route_recorded": True,
            "can_enter_routed_next_gate": True,
            "routed_next_gate": routed_next_gate,
            "next_gate_route": route,
            "route_completion_record_count": 1,
            "route_completion_records": router["route_completion_records"],
            "routed_next_gate_entry_preflight_input_records": [
                {
                    "record_id": f"routed_next_gate_entry_preflight_input::{routed_next_gate}::{route_type}",
                    "verified_route_type": route_type,
                    "routed_next_gate": routed_next_gate,
                    "verified_route_next_gate_router_status": "verified_route_next_gate_route_recorded",
                    "verified_route_next_gate_router_report_path": (
                        "Results/json/auto_mode_formal_package_verified_route_next_gate_router.json"
                    ),
                    "verified_route_next_gate_router_review_path": (
                        "Reviews/auto_mode_formal_package_verified_route_next_gate_router.md"
                    ),
                    "next_gate_route_id": route["route_id"],
                    "next_gate_action": route["next_gate_action"],
                    "route_completion_record_count": 1,
                    "review_status": (
                        "verified_route_next_gate_router_entry_accepted_for_routed_next_gate_entry_preflight"
                    ),
                    "can_continue_to_routed_next_gate_entry_preflight": True,
                }
            ],
            "routed_next_gate_entry_preflight_executed": False,
            "this_command_ran_routed_next_gate_entry_preflight": False,
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
            "next_action": {"id": "run_routed_next_gate_entry_preflight"},
        }

    def _ready_router(self, route_type: str) -> dict:
        routed_next_gate = (
            "formal_package_delivery_completion_gate"
            if route_type == "manual_acceptance"
            else "formal_package_export_acceptance_router"
        )
        next_gate_action = (
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
            "routed_next_gate": routed_next_gate,
            "next_gate_route": {
                "route_id": f"verified_route_next_gate::{route_type}",
                "route_type": route_type,
                "gate_id": routed_next_gate,
                "next_gate_action": next_gate_action,
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
            "next_action": {"id": routed_next_gate},
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
            "recorded_verified_route_next_gate_router": False,
            "ran_routed_next_gate_entry_preflight": False,
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

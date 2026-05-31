import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry import (
    build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry,
    run_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry,
    write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateVerifiedRouteCompletionLedgerEntryTests(unittest.TestCase):
    """BDD: P7-AV enters the existing verified route completion ledger after P7-AU."""

    def test_bdd_p7av_ready_result_review_runs_existing_completion_ledger(self) -> None:
        """行为 1：ready P7-AU 会调用既有 completion ledger 并记录成功结果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            verification = self._verified_route("package_manifest")
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json",
                verification,
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
                project_root,
                self._result_review("package_manifest", verification),
                repo_root=REPO_ROOT,
            )
            report_path, review_path = write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_outputs(
                project_root,
                report,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(
                report["schema_version"],
                "p7.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.v1",
            )
            self.assertEqual(report["status"], "next_gate_verified_route_completion_ledger_entered")
            self.assertTrue(report["verified_route_completion_ledger_entry_command_executed"])
            self.assertTrue(report["this_command_ran_verified_route_completion_ledger"])
            self.assertEqual(report["verified_route_completion_ledger_status"], "verified_route_completion_ledger_recorded")
            self.assertTrue(report["route_completion_ledger_recorded"])
            self.assertTrue(report["can_enter_next_auto_mode_gate"])
            self.assertEqual(report["verified_route_type"], "package_manifest")
            self.assertEqual(report["route_completion_record_count"], 1)
            self.assertTrue(
                (
                    project_root / "Results/json/auto_mode_formal_package_verified_route_completion_ledger.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.json"
                ).exists()
            )

    def test_bdd_p7av_current_blocked_result_review_blocks_ledger_entry(self) -> None:
        """行为 2：当前 P7-AU blocked 时不运行 completion ledger。"""
        report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
            Path("."),
            {},
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_verification_entry_result_review")
        self.assertFalse(report["can_enter_verified_route_completion_ledger"])
        self.assertEqual(report["verified_route_completion_ledger_entry_command"], [])
        self.assertFalse(report["verified_route_completion_ledger_entry_command_executed"])
        self.assertIn(
            "route_specific_artifact_verification_entry_result_review_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7av_missing_invalid_or_not_ready_result_review_blocks_entry(self) -> None:
        """行为 3：P7-AU 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        verification = self._verified_route("package_manifest")
        wrong_schema = self._result_review("package_manifest", verification)
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._result_review("package_manifest", verification)
        not_ready["status"] = "blocked_by_route_specific_artifact_verification_entry"
        blocked = self._result_review("package_manifest", verification)
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(
            all(
                report["status"] == "blocked_by_route_specific_artifact_verification_entry_result_review"
                for report in reports
            )
        )
        self.assertIn(
            "route_specific_artifact_verification_entry_result_review_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn(
            "route_specific_artifact_verification_entry_result_review_not_ready",
            reports[1]["blocking_reasons"],
        )
        self.assertIn("source_result_review_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7av_ledger_input_record_contract_must_be_clean(self) -> None:
        """行为 4：ledger input record 缺失、重复、错配或未放行时阻断。"""
        verification = self._verified_route("package_manifest")
        missing_record = self._result_review("package_manifest", verification)
        missing_record["verified_route_completion_ledger_input_records"] = []
        duplicated = self._result_review("package_manifest", verification)
        duplicated["verified_route_completion_ledger_input_records"].append(
            dict(duplicated["verified_route_completion_ledger_input_records"][0])
        )
        wrong_path = self._result_review("package_manifest", verification)
        wrong_path["verified_route_completion_ledger_input_records"][0][
            "route_specific_artifact_verification_report_path"
        ] = "Results/json/wrong.json"
        wrong_status = self._result_review("package_manifest", verification)
        wrong_status["verified_route_completion_ledger_input_records"][0]["review_status"] = "wrong_status"

        reports = [
            build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_record, duplicated, wrong_path, wrong_status]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_verified_route_completion_ledger_entry_contract" for report in reports)
        )
        self.assertIn("verified_route_completion_ledger_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("verified_route_completion_ledger_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("route_specific_artifact_verification_report_path_mismatch:package_manifest", reports[2]["blocking_reasons"])
        self.assertIn("verified_route_completion_ledger_input_record_review_status_mismatch:package_manifest", reports[3]["blocking_reasons"])

    def test_bdd_p7av_missing_completion_ledger_command_file_blocks_entry(self) -> None:
        """行为 5：completion ledger command 文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
            Path("."),
            self._result_review("package_manifest", self._verified_route("package_manifest")),
            repo_root=Path("/tmp/nonexistent-repo-for-p7av"),
        )

        self.assertEqual(report["status"], "blocked_by_verified_route_completion_ledger_command_unavailable")
        self.assertIn(
            "verified_route_completion_ledger_command_file_missing:Program/auto_mode_formal_package_verified_route_completion_ledger.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["verified_route_completion_ledger_entry_command_executed"])

    def test_bdd_p7av_completion_ledger_failure_is_recorded_as_blocked(self) -> None:
        """行为 6：既有 ledger 运行后仍 blocked 时，P7-AV 不放行。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            good_verification = self._verified_route("package_manifest")
            bad_verification = self._verified_route("package_manifest")
            bad_verification["artifact_verification_records"] = []
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json",
                bad_verification,
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
                project_root,
                self._result_review("package_manifest", good_verification),
                repo_root=REPO_ROOT,
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(report["status"], "blocked_by_verified_route_completion_ledger_failure")
            self.assertTrue(report["verified_route_completion_ledger_entry_command_executed"])
            self.assertEqual(
                report["verified_route_completion_ledger_status"],
                "blocked_by_verified_route_completion_contract",
            )
            self.assertFalse(report["route_completion_ledger_recorded"])
            self.assertIn(
                "verified_route_completion_ledger_status:blocked_by_verified_route_completion_contract",
                report["blocking_reasons"],
            )

    def test_bdd_p7av_cli_defaults_to_current_blocked_result_review(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AU report，写 blocked ledger entry。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_review_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.json"
            )
            result_review_path.parent.mkdir(parents=True, exist_ok=True)
            result_review_path.write_text(
                json.dumps({"status": "blocked_by_route_specific_artifact_verification_entry"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_route_specific_artifact_verification_entry_result_review", result.stdout)
            self.assertIn("can_enter_verified_route_completion_ledger=false", result.stdout)
            self.assertIn("verified_route_completion_ledger_entry_command_executed=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root / "Reviews/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.json"
                ).exists()
            )

    def _result_review(self, route_type: str, verification: dict) -> dict:
        artifact_records = verification["artifact_verification_records"]
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_route_specific_artifact_verification_entered",
            "status": "route_specific_artifact_verification_entry_result_review_ready",
            "verified_route_type": route_type,
            "route_specific_artifact_verification_status": "route_specific_artifact_verified_for_review",
            "artifact_verification_entry_result_reviewed": True,
            "can_continue_to_verified_route_completion_ledger": True,
            "verified_route_completion_ledger_input_records": [
                {
                    "record_id": f"route_specific_artifact_verification_result::{route_type}",
                    "verified_route_type": route_type,
                    "route_specific_artifact_verification_status": "route_specific_artifact_verified_for_review",
                    "route_specific_artifact_verification_report_path": (
                        "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json"
                    ),
                    "route_specific_artifact_verification_review_path": (
                        "Reviews/auto_mode_formal_package_route_specific_artifact_verification.md"
                    ),
                    "delegated_status": verification["delegated_status"],
                    "artifact_verification_record_count": len(artifact_records),
                    "artifact_ids": [record["artifact_id"] for record in artifact_records],
                    "review_status": "route_specific_artifact_verification_accepted_for_verified_route_completion_ledger",
                    "can_continue_to_verified_route_completion_ledger": True,
                }
            ],
            "route_specific_artifact_verified": True,
            "source_product_state_verified": route_type == "manual_acceptance",
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "artifact_verification_record_count": len(artifact_records),
            "artifact_verification_records": artifact_records,
            "delegated_status": verification["delegated_status"],
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_result_review_boundary_flags(),
            **self._route_flags(route_type),
        }

    def _verified_route(self, route_type: str) -> dict:
        records = {
            "package_manifest": [
                self._artifact("package_manifest", "Submissions/formal_package/manifest.json", 200, "manifest-sha"),
                self._artifact("paper_pdf", "Submissions/formal_package/paper.pdf", 300, "pdf-sha"),
                self._artifact("paper_docx", "Submissions/formal_package/paper.docx", 400, "docx-sha"),
            ],
            "pdf_export": [self._artifact("paper_pdf", "Submissions/formal_package/paper.pdf", 300, "pdf-sha")],
            "docx_export": [self._artifact("paper_docx", "Submissions/formal_package/paper.docx", 400, "docx-sha")],
            "manual_acceptance": [
                self._artifact(
                    "manual_acceptance_state",
                    "state/product/formal_submission_package_manual_acceptance.json",
                    500,
                    "state-sha",
                )
            ],
        }[route_type]
        return {
            "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_verification.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "route_specific_artifact_verified_for_review",
            "route_type": route_type,
            "verified_route_type": route_type,
            "delegated_status": self._delegated_status(route_type),
            "route_specific_artifact_verified": True,
            "source_product_state_verified": route_type == "manual_acceptance",
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "source_paths": {
                "route_specific_artifact_verification": (
                    "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json"
                )
            },
            "source_executor": {"status": "route_specific_artifact_executed", "route_type": route_type},
            "source_delegated_report": {"status": self._delegated_status(route_type)},
            "artifact_verification_records": records,
            "boundary_flags": self._clean_verification_boundary_flags(),
            "next_action": {"id": "record_verified_route_completion"},
            **self._route_flags(route_type),
        }

    def _artifact(self, artifact_id: str, path: str, bytes_value: int, sha256: str) -> dict:
        return {
            "artifact_id": artifact_id,
            "path": path,
            "exists": True,
            "bytes": bytes_value,
            "delegated_bytes": bytes_value,
            "sha256": sha256,
            "delegated_sha256": sha256,
            "verification_status": "verified",
        }

    def _delegated_status(self, route_type: str) -> str:
        return {
            "pdf_export": "final_pdf_written",
            "docx_export": "docx_exported",
            "package_manifest": "formal_submission_package_ready",
            "manual_acceptance": "formal_submission_package_accepted",
        }[route_type]

    def _route_flags(self, route_type: str) -> dict:
        return {
            "rendered_pdf": route_type == "pdf_export",
            "rendered_docx": route_type == "docx_export",
            "package_manifest_generated": route_type == "package_manifest",
            "manual_acceptance_performed": route_type == "manual_acceptance",
        }

    def _clean_result_review_boundary_flags(self) -> dict:
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

    def _clean_verification_boundary_flags(self) -> dict:
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
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

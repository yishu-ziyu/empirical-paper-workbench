import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry import (
    build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry,
    run_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageNextGateRouteSpecificArtifactVerificationEntryTests(unittest.TestCase):
    """BDD: P7-AT enters existing route-specific artifact verification after P7-AS."""

    def test_bdd_p7at_ready_result_review_runs_existing_artifact_verification(self) -> None:
        """行为 1：ready P7-AS 会调用既有 artifact verification 并记录成功结果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            delegated = self._write_package_manifest_fixture(project_root)
            executor = self._completed_executor("package_manifest", delegated)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
                executor,
            )
            self._write_json(
                project_root / "Results/json/formal_submission_package_manifest.json",
                delegated,
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
                project_root,
                self._result_review("package_manifest", executor),
                repo_root=REPO_ROOT,
            )
            report_path, review_path = (
                write_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_outputs(
                    project_root,
                    report,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(
                report["schema_version"],
                "p7.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.v1",
            )
            self.assertEqual(report["status"], "next_gate_route_specific_artifact_verification_entered")
            self.assertTrue(report["route_specific_artifact_verification_entry_command_executed"])
            self.assertTrue(report["this_command_ran_route_specific_artifact_verification"])
            self.assertEqual(
                report["route_specific_artifact_verification_status"],
                "route_specific_artifact_verified_for_review",
            )
            self.assertTrue(report["route_specific_artifact_verified"])
            self.assertEqual(report["verified_route_type"], "package_manifest")
            self.assertEqual(report["verification_artifact_record_count"], 3)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.json"
                ).exists()
            )

    def test_bdd_p7at_current_blocked_result_review_blocks_verification_entry(self) -> None:
        """行为 2：当前 P7-AS blocked 时不运行 artifact verification。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
            Path("."),
            {},
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_execution_result_review")
        self.assertFalse(report["can_enter_route_specific_artifact_verification"])
        self.assertEqual(report["route_specific_artifact_verification_entry_command"], [])
        self.assertFalse(report["route_specific_artifact_verification_entry_command_executed"])
        self.assertIn(
            "route_specific_artifact_execution_result_review_missing_or_invalid_schema",
            report["blocking_reasons"],
        )

    def test_bdd_p7at_missing_invalid_or_not_ready_result_review_blocks_entry(self) -> None:
        """行为 3：P7-AS 缺失、schema 错、未 ready 或有 blockers 时阻断。"""
        wrong_schema = self._result_review("package_manifest", self._completed_executor("package_manifest", {}))
        wrong_schema["schema_version"] = "wrong.schema"
        not_ready = self._result_review("package_manifest", self._completed_executor("package_manifest", {}))
        not_ready["status"] = "blocked_by_route_specific_artifact_execution"
        blocked = self._result_review("package_manifest", self._completed_executor("package_manifest", {}))
        blocked["blocking_reasons"] = ["source_blocked"]

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [wrong_schema, not_ready, blocked]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_execution_result_review" for report in reports)
        )
        self.assertIn(
            "route_specific_artifact_execution_result_review_missing_or_invalid_schema",
            reports[0]["blocking_reasons"],
        )
        self.assertIn("route_specific_artifact_execution_result_review_not_ready", reports[1]["blocking_reasons"])
        self.assertIn("source_result_review_has_blocking_reasons", reports[2]["blocking_reasons"])

    def test_bdd_p7at_verification_input_record_contract_must_be_clean(self) -> None:
        """行为 4：verification input record 缺失、重复、错配或未接受时阻断。"""
        executor = self._completed_executor("package_manifest", {"status": "formal_submission_package_ready"})
        missing_record = self._result_review("package_manifest", executor)
        missing_record["route_specific_artifact_verification_input_records"] = []
        duplicated = self._result_review("package_manifest", executor)
        duplicated["route_specific_artifact_verification_input_records"].append(
            dict(duplicated["route_specific_artifact_verification_input_records"][0])
        )
        wrong_path = self._result_review("package_manifest", executor)
        wrong_path["route_specific_artifact_verification_input_records"][0][
            "artifact_executor_report_path"
        ] = "Results/json/wrong.json"
        wrong_status = self._result_review("package_manifest", executor)
        wrong_status["route_specific_artifact_verification_input_records"][0]["review_status"] = "wrong_status"

        reports = [
            build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
                Path("."),
                source,
                repo_root=REPO_ROOT,
            )
            for source in [missing_record, duplicated, wrong_path, wrong_status]
        ]

        self.assertTrue(
            all(report["status"] == "blocked_by_route_specific_artifact_verification_entry_contract" for report in reports)
        )
        self.assertIn("route_specific_artifact_verification_input_record_missing", reports[0]["blocking_reasons"])
        self.assertIn("route_specific_artifact_verification_input_record_not_single", reports[1]["blocking_reasons"])
        self.assertIn("artifact_executor_report_path_mismatch:package_manifest", reports[2]["blocking_reasons"])
        self.assertIn("route_specific_artifact_verification_input_record_review_status_mismatch:package_manifest", reports[3]["blocking_reasons"])

    def test_bdd_p7at_missing_artifact_verification_command_file_blocks_entry(self) -> None:
        """行为 5：artifact verification command 文件不存在时阻断，不尝试执行。"""
        report = build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
            Path("."),
            self._result_review("package_manifest", self._completed_executor("package_manifest", {})),
            repo_root=Path("/tmp/nonexistent-repo-for-p7at"),
        )

        self.assertEqual(report["status"], "blocked_by_route_specific_artifact_verification_command_unavailable")
        self.assertIn(
            "route_specific_artifact_verification_command_file_missing:Program/auto_mode_formal_package_route_specific_artifact_verification.py",
            report["blocking_reasons"],
        )
        self.assertFalse(report["route_specific_artifact_verification_entry_command_executed"])

    def test_bdd_p7at_verification_failure_is_recorded_as_blocked(self) -> None:
        """行为 6：既有 verification 运行后仍 blocked 时，P7-AT 不放行。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            delegated = self._package_manifest_delegated_report(
                project_root,
                project_root / "Submissions/formal_package/missing.pdf",
                project_root / "Submissions/formal_package/missing.docx",
            )
            executor = self._completed_executor("package_manifest", delegated)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
                executor,
            )
            self._write_json(
                project_root / "Results/json/formal_submission_package_manifest.json",
                delegated,
            )

            report, exit_code = run_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
                project_root,
                self._result_review("package_manifest", executor),
                repo_root=REPO_ROOT,
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(report["status"], "blocked_by_route_specific_artifact_verification_failure")
            self.assertTrue(report["route_specific_artifact_verification_entry_command_executed"])
            self.assertEqual(
                report["route_specific_artifact_verification_status"],
                "blocked_by_route_specific_artifact_integrity",
            )
            self.assertFalse(report["route_specific_artifact_verified"])
            self.assertIn(
                "route_specific_artifact_verification_status:blocked_by_route_specific_artifact_integrity",
                report["blocking_reasons"],
            )

    def test_bdd_p7at_cli_defaults_to_current_blocked_result_review(self) -> None:
        """行为 7：CLI 默认读取当前 blocked P7-AS report，写 blocked verification entry。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_review_path = (
                project_root
                / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.json"
            )
            result_review_path.parent.mkdir(parents=True, exist_ok=True)
            result_review_path.write_text(
                json.dumps({"status": "blocked_by_route_specific_artifact_execution"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_route_specific_artifact_execution_result_review", result.stdout)
            self.assertIn("can_enter_route_specific_artifact_verification=false", result.stdout)
            self.assertIn("route_specific_artifact_verification_entry_command_executed=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.json"
                ).exists()
            )

    def _result_review(self, route_type: str, executor: dict) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "next_gate_route_specific_artifact_executed",
            "status": "route_specific_artifact_execution_result_review_ready",
            "verified_route_type": route_type,
            "artifact_executor_status": "route_specific_artifact_executed",
            "artifact_execution_result_reviewed": True,
            "can_continue_to_route_specific_artifact_verification": True,
            "route_specific_artifact_verification_input_records": [
                {
                    "record_id": f"artifact_execution_result::{route_type}",
                    "verified_route_type": route_type,
                    "artifact_executor_status": "route_specific_artifact_executed",
                    "artifact_executor_report_path": "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
                    "artifact_executor_review_path": "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md",
                    "delegated_report_path": executor.get(
                        "delegated_report_path",
                        "Results/json/formal_submission_package_manifest.json",
                    ),
                    "delegated_review_path": executor.get(
                        "delegated_review_path",
                        "Reviews/formal_submission_package_acceptance.md",
                    ),
                    "delegated_status": executor.get("delegated_status", "formal_submission_package_ready"),
                    "review_status": "artifact_execution_accepted_for_route_specific_artifact_verification",
                    "can_continue_to_route_specific_artifact_verification": True,
                }
            ],
            "route_specific_command_executed": True,
            "route_specific_artifact_executed": True,
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "rendered_pdf": route_type == "pdf_export",
            "rendered_docx": route_type == "docx_export",
            "package_manifest_generated": route_type == "package_manifest",
            "manual_acceptance_performed": route_type == "manual_acceptance",
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": route_type == "manual_acceptance",
            "blocking_reasons": [],
            "boundary_flags": self._clean_result_review_boundary_flags(),
        }

    def _completed_executor(self, route_type: str, delegated_report: dict) -> dict:
        flags = {
            "rendered_pdf": route_type == "pdf_export",
            "rendered_docx": route_type == "docx_export",
            "package_manifest_generated": route_type == "package_manifest",
            "manual_acceptance_performed": route_type == "manual_acceptance",
        }
        delegated_paths = {
            "pdf_export": "Results/json/formal_pdf_final_writeback.json",
            "docx_export": "Results/json/formal_docx_export.json",
            "package_manifest": "Results/json/formal_submission_package_manifest.json",
            "manual_acceptance": "Results/json/formal_submission_package_manual_acceptance.json",
        }
        delegated_review_paths = {
            "pdf_export": "Reviews/formal_pdf_final_writeback.md",
            "docx_export": "Reviews/formal_docx_export.md",
            "package_manifest": "Reviews/formal_submission_package_acceptance.md",
            "manual_acceptance": "Reviews/formal_submission_package_manual_acceptance.md",
        }
        return {
            "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_executor.v1",
            "generated_at": "2026-05-31T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "route_specific_artifact_executed",
            "mode": "execute",
            "confirm_artifact_execution": True,
            "route_type": route_type,
            "route_specific_artifact_executed": True,
            "route_specific_command_executed": True,
            "delegated_returncode": 0,
            "delegated_status": delegated_report.get("status", "formal_submission_package_ready"),
            "delegated_report_path": delegated_paths[route_type],
            "delegated_review_path": delegated_review_paths[route_type],
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": route_type == "manual_acceptance",
            "blocking_reasons": [],
            "selected_route_operation": {
                "operation_id": f"selected_route_execute::{route_type}",
                "route_type": route_type,
                "operation_status": "executed",
            },
            "route_specific_result": {
                "status": delegated_report.get("status", "formal_submission_package_ready"),
                "returncode": 0,
                "report_path": delegated_paths[route_type],
            },
            "boundary_flags": self._clean_executor_boundary_flags(),
            **flags,
        }

    def _write_package_manifest_fixture(self, project_root: Path) -> dict:
        pdf = self._write_bytes(project_root / "Submissions/formal_package/paper.pdf", b"%PDF\n")
        docx = self._write_bytes(project_root / "Submissions/formal_package/paper.docx", b"docx\n")
        delegated = self._package_manifest_delegated_report(project_root, pdf, docx)
        self._write_json(
            project_root / "Submissions/formal_package/manifest.json",
            {
                "schema_version": delegated["schema_version"],
                "status": delegated["status"],
                "artifacts": delegated["artifacts"],
            },
        )
        return delegated

    def _package_manifest_delegated_report(self, project_root: Path, pdf: Path, docx: Path) -> dict:
        return {
            "schema_version": "p6.formal_submission_package_manifest.v1",
            "status": "formal_submission_package_ready",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "package_manifest": "Submissions/formal_package/manifest.json",
            "package_manifest_written": True,
            "artifacts": {
                "paper_pdf": self._artifact(project_root, pdf, "Submissions/formal_package/paper.pdf"),
                "paper_docx": self._artifact(project_root, docx, "Submissions/formal_package/paper.docx"),
            },
            "blocking_reasons": [],
            "boundary_flags": {
                "modified_formal_manuscript": False,
                "modified_formal_bibliography": False,
                "modified_project_bibliography": False,
                "modified_design_spec": False,
                "modified_run_plan": False,
                "modified_product_state": False,
            },
        }

    def _artifact(self, project_root: Path, path: Path, rel_path: str) -> dict:
        del project_root
        exists = path.exists()
        return {
            "path": rel_path,
            "exists": exists,
            "bytes": path.stat().st_size if exists else 999,
            "sha256": self._sha256(path) if exists else "missing",
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
        }

    def _clean_executor_boundary_flags(self) -> dict:
        return {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "reran_models": False,
            "modified_statistical_execution_artifacts": False,
        }

    def _write_bytes(self, path: Path, data: bytes) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        digest.update(path.read_bytes())
        return digest.hexdigest()

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_route_specific_artifact_verification import (
    build_auto_mode_formal_package_route_specific_artifact_verification,
    write_auto_mode_formal_package_route_specific_artifact_verification_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageRouteSpecificArtifactVerificationTests(unittest.TestCase):
    """BDD: P7-AC verifies the selected route artifact before route completion is trusted."""

    def test_bdd_p7ac_completed_pdf_route_verifies_final_pdf_fingerprint(self) -> None:
        """行为 1：PDF route 完成后，复验 final PDF 的路径、bytes 和 sha256。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            pdf = self._write_bytes(project_root / "Submissions/formal_package/paper.pdf", b"%PDF-1.4\nfinal pdf\n")
            delegated = self._pdf_delegated_report(pdf)

            report = build_auto_mode_formal_package_route_specific_artifact_verification(
                project_root,
                self._completed_executor("pdf_export", delegated),
                delegated,
                source_paths=self._source_paths(),
            )

            self.assertEqual(report["schema_version"], "p7.auto_mode_formal_package_route_specific_artifact_verification.v1")
            self.assertEqual(report["status"], "route_specific_artifact_verified_for_review")
            self.assertTrue(report["route_specific_artifact_verified"])
            self.assertEqual(report["verified_route_type"], "pdf_export")
            self.assertFalse(report["formal_writeback_executed"])
            self.assertFalse(report["this_command_wrote_formal_state"])
            self.assertFalse(report["can_write_product_state"])
            self.assertEqual(len(report["artifact_verification_records"]), 1)
            record = report["artifact_verification_records"][0]
            self.assertEqual(record["artifact_id"], "paper_pdf")
            self.assertEqual(record["path"], "Submissions/formal_package/paper.pdf")
            self.assertEqual(record["verification_status"], "verified")
            self.assertEqual(record["sha256"], delegated["final_pdf_sha256"])
            self.assertEqual(record["bytes"], delegated["final_pdf_bytes"])

    def test_bdd_p7ac_current_blocked_executor_blocks_verification(self) -> None:
        """行为 2：当前 P7-AB blocked 时不能验证任何路线产物。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_auto_mode_formal_package_route_specific_artifact_verification(
                Path(tmpdir),
                self._blocked_executor(),
                {},
            )

            self.assertEqual(report["status"], "blocked_by_route_specific_artifact_executor")
            self.assertFalse(report["route_specific_artifact_verified"])
            self.assertEqual(report["artifact_verification_records"], [])
            self.assertIn("route_specific_artifact_executor_not_completed", report["blocking_reasons"])

    def test_bdd_p7ac_missing_invalid_executor_or_delegated_report_blocks_verification(self) -> None:
        """行为 3：executor 或 delegated report 缺失/错误时先阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            pdf = self._write_bytes(project_root / "Submissions/formal_package/paper.pdf", b"%PDF\n")
            delegated = self._pdf_delegated_report(pdf)
            missing_executor = build_auto_mode_formal_package_route_specific_artifact_verification(
                project_root,
                {},
                delegated,
            )
            invalid_delegated = build_auto_mode_formal_package_route_specific_artifact_verification(
                project_root,
                self._completed_executor("pdf_export", delegated),
                {"schema_version": "wrong.schema", "status": "final_pdf_written"},
            )

            self.assertEqual(missing_executor["status"], "blocked_by_route_specific_artifact_executor")
            self.assertIn("route_specific_artifact_executor_missing_or_invalid_schema", missing_executor["blocking_reasons"])
            self.assertEqual(invalid_delegated["status"], "blocked_by_delegated_artifact_report")
            self.assertIn("delegated_report_schema_mismatch:pdf_export", invalid_delegated["blocking_reasons"])

    def test_bdd_p7ac_executor_completion_contract_must_be_clean(self) -> None:
        """行为 4：P7-AB 完成状态、路线类型和路线 flags 必须一致。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            pdf = self._write_bytes(project_root / "Submissions/formal_package/paper.pdf", b"%PDF\n")
            delegated = self._pdf_delegated_report(pdf)
            unknown = self._completed_executor("pdf_export", delegated)
            unknown["route_type"] = "unknown_route"
            not_executed = self._completed_executor("pdf_export", delegated)
            not_executed["route_specific_command_executed"] = False
            mismatched_flags = self._completed_executor("pdf_export", delegated)
            mismatched_flags["rendered_docx"] = True

            reports = [
                build_auto_mode_formal_package_route_specific_artifact_verification(project_root, executor, delegated)
                for executor in [unknown, not_executed, mismatched_flags]
            ]

            self.assertTrue(all(report["status"] == "blocked_by_route_specific_artifact_contract" for report in reports))
            self.assertIn("route_type_unknown:unknown_route", reports[0]["blocking_reasons"])
            self.assertIn("route_specific_command_not_executed", reports[1]["blocking_reasons"])
            self.assertIn("executor_route_flag_mismatch:pdf_export", reports[2]["blocking_reasons"])

    def test_bdd_p7ac_pdf_docx_artifacts_must_exist_inside_formal_package_and_match(self) -> None:
        """行为 5：PDF/DOCX 必须在正式包目录且文件指纹一致。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            outside_pdf = self._write_bytes(project_root / "workspace/paper.pdf", b"%PDF\n")
            outside_report = build_auto_mode_formal_package_route_specific_artifact_verification(
                project_root,
                self._completed_executor("pdf_export", self._pdf_delegated_report(outside_pdf, path="workspace/paper.pdf")),
                self._pdf_delegated_report(outside_pdf, path="workspace/paper.pdf"),
            )

            docx = self._write_bytes(project_root / "Submissions/formal_package/paper.docx", b"docx before\n")
            delegated_docx = self._docx_delegated_report(docx)
            docx.write_bytes(b"docx after\n")
            changed_report = build_auto_mode_formal_package_route_specific_artifact_verification(
                project_root,
                self._completed_executor("docx_export", delegated_docx),
                delegated_docx,
            )

            self.assertEqual(outside_report["status"], "blocked_by_route_specific_artifact_integrity")
            self.assertIn("artifact_outside_formal_package:paper_pdf", outside_report["blocking_reasons"])
            self.assertEqual(changed_report["status"], "blocked_by_route_specific_artifact_integrity")
            self.assertIn("artifact_bytes_mismatch:paper_docx", changed_report["blocking_reasons"])
            self.assertIn("artifact_sha256_mismatch:paper_docx", changed_report["blocking_reasons"])

    def test_bdd_p7ac_package_manifest_route_verifies_manifest_and_package_artifacts(self) -> None:
        """行为 6：package manifest route 复验 manifest 以及其中 PDF/DOCX 指纹。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            pdf = self._write_bytes(project_root / "Submissions/formal_package/paper.pdf", b"%PDF\n")
            docx = self._write_bytes(project_root / "Submissions/formal_package/paper.docx", b"docx\n")
            manifest_path = project_root / "Submissions/formal_package/manifest.json"
            delegated = self._package_manifest_delegated_report(project_root, pdf, docx)
            self._write_json(
                manifest_path,
                {
                    "schema_version": delegated["schema_version"],
                    "status": delegated["status"],
                    "artifacts": delegated["artifacts"],
                },
            )

            report = build_auto_mode_formal_package_route_specific_artifact_verification(
                project_root,
                self._completed_executor("package_manifest", delegated),
                delegated,
            )

            self.assertEqual(report["status"], "route_specific_artifact_verified_for_review")
            self.assertTrue(report["route_specific_artifact_verified"])
            self.assertEqual(
                {record["artifact_id"] for record in report["artifact_verification_records"]},
                {"package_manifest", "paper_pdf", "paper_docx"},
            )

    def test_bdd_p7ac_manual_acceptance_route_verifies_state_copy_and_artifacts(self) -> None:
        """行为 7：manual acceptance route 复验验收记录、state 副本和 PDF/DOCX 指纹。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            pdf = self._write_bytes(project_root / "Submissions/formal_package/paper.pdf", b"%PDF\n")
            docx = self._write_bytes(project_root / "Submissions/formal_package/paper.docx", b"docx\n")
            delegated = self._manual_acceptance_delegated_report(pdf, docx)
            self._write_json(project_root / "state/product/formal_submission_package_manual_acceptance.json", delegated)

            report = build_auto_mode_formal_package_route_specific_artifact_verification(
                project_root,
                self._completed_executor("manual_acceptance", delegated),
                delegated,
            )

            self.assertEqual(report["status"], "route_specific_artifact_verified_for_review")
            self.assertTrue(report["route_specific_artifact_verified"])
            self.assertTrue(report["source_product_state_verified"])
            self.assertEqual(report["delegated_status"], "formal_submission_package_accepted")
            self.assertEqual(
                {record["artifact_id"] for record in report["artifact_verification_records"]},
                {"manual_acceptance_state", "paper_pdf", "paper_docx"},
            )

    def test_bdd_p7ac_cli_defaults_to_current_blocked_executor(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AB，写 blocked verification report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
                self._blocked_executor(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_route_specific_artifact_verification.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_route_specific_artifact_executor", result.stdout)
            self.assertIn("route_specific_artifact_verified=false", result.stdout)
            self.assertTrue(
                (
                    project_root / "Results/json/auto_mode_formal_package_route_specific_artifact_verification.json"
                ).exists()
            )
            self.assertTrue(
                (project_root / "Reviews/auto_mode_formal_package_route_specific_artifact_verification.md").exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_package_route_specific_artifact_verification.json"
                ).exists()
            )

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
        return {
            "schema_version": "p7.auto_mode_formal_package_route_specific_artifact_executor.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "route_specific_artifact_executed",
            "route_type": route_type,
            "route_specific_artifact_executed": True,
            "route_specific_command_executed": True,
            "delegated_returncode": 0,
            "delegated_status": delegated_report.get("status", ""),
            "delegated_report_path": delegated_paths[route_type],
            "delegated_review_path": delegated_paths[route_type].replace("Results/json", "Reviews").replace(".json", ".md"),
            "selected_route_executed": True,
            "export_or_acceptance_executed": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": route_type == "manual_acceptance",
            "blocking_reasons": [],
            "selected_route_operation": self._route_operation(route_type),
            "route_specific_result": {
                "status": delegated_report.get("status", ""),
                "returncode": 0,
                "report_path": delegated_paths[route_type],
            },
            "boundary_flags": self._clean_boundary_flags(),
            **flags,
        }

    def _blocked_executor(self) -> dict:
        report = self._completed_executor("pdf_export", {"status": "final_pdf_written"})
        report["status"] = "blocked_by_selected_route_execute"
        report["route_type"] = ""
        report["route_specific_artifact_executed"] = False
        report["route_specific_command_executed"] = False
        report["delegated_returncode"] = None
        report["delegated_status"] = ""
        report["delegated_report_path"] = ""
        report["selected_route_executed"] = False
        report["export_or_acceptance_executed"] = False
        report["rendered_pdf"] = False
        report["blocking_reasons"] = ["selected_route_execute_not_manifest_recorded"]
        report["selected_route_operation"] = {}
        report["route_specific_result"] = {}
        return report

    def _route_operation(self, route_type: str) -> dict:
        planned_outputs = {
            "pdf_export": ["Submissions/formal_package/paper.pdf"],
            "docx_export": ["Submissions/formal_package/paper.docx"],
            "package_manifest": ["Submissions/formal_package/manifest.json"],
            "manual_acceptance": ["Reviews/formal_package_manual_acceptance.md"],
        }[route_type]
        return {
            "operation_id": f"selected_route_execute::{route_type}",
            "route_execution_id": f"selected_formal_package_route_execution::{route_type}",
            "route_type": route_type,
            "planned_outputs": planned_outputs,
            "operation_status": "planned_not_executed",
        }

    def _pdf_delegated_report(self, pdf: Path, *, path: str = "Submissions/formal_package/paper.pdf") -> dict:
        return {
            "schema_version": "p6.formal_pdf_final_writeback.v1",
            "status": "final_pdf_written",
            "final_pdf": path,
            "final_pdf_exists": True,
            "final_pdf_sha256": self._sha256(pdf),
            "final_pdf_bytes": pdf.stat().st_size,
            "this_command_wrote_final_pdf": True,
            "this_command_wrote_docx": False,
            "this_command_wrote_formal_state": False,
            "blocking_reasons": [],
        }

    def _docx_delegated_report(self, docx: Path) -> dict:
        return {
            "schema_version": "p6.formal_docx_export.v1",
            "status": "docx_exported",
            "docx": "Submissions/formal_package/paper.docx",
            "docx_exists": True,
            "docx_sha256": self._sha256(docx),
            "docx_bytes": docx.stat().st_size,
            "this_command_wrote_docx": True,
            "this_command_wrote_pdf": False,
            "this_command_wrote_formal_state": False,
            "blocking_reasons": [],
        }

    def _package_manifest_delegated_report(self, project_root: Path, pdf: Path, docx: Path) -> dict:
        return {
            "schema_version": "p6.formal_submission_package_manifest.v1",
            "status": "formal_submission_package_ready",
            "package_manifest": "Submissions/formal_package/manifest.json",
            "package_manifest_written": True,
            "artifacts": {
                "paper_pdf": self._artifact(project_root, pdf),
                "paper_docx": self._artifact(project_root, docx),
            },
            "blocking_reasons": [],
            "boundary_flags": {
                "this_command_rendered_pdf": False,
                "this_command_rendered_docx": False,
                "this_command_wrote_final_outputs": False,
                "this_command_wrote_formal_state": False,
            },
        }

    def _manual_acceptance_delegated_report(self, pdf: Path, docx: Path) -> dict:
        return {
            "schema_version": "p6.formal_submission_package_manual_acceptance.v1",
            "status": "formal_submission_package_accepted",
            "decision": "accept",
            "actor": "mahaoxuan",
            "note": "Accepted in test.",
            "accepted": True,
            "needs_revision": False,
            "accepted_artifacts": {
                "paper_pdf": {
                    "path": "Submissions/formal_package/paper.pdf",
                    "exists": True,
                    "bytes": pdf.stat().st_size,
                    "sha256": self._sha256(pdf),
                    "summary_bytes": pdf.stat().st_size,
                    "summary_sha256": self._sha256(pdf),
                    "hash_matches_summary": True,
                    "bytes_match_summary": True,
                },
                "paper_docx": {
                    "path": "Submissions/formal_package/paper.docx",
                    "exists": True,
                    "bytes": docx.stat().st_size,
                    "sha256": self._sha256(docx),
                    "summary_bytes": docx.stat().st_size,
                    "summary_sha256": self._sha256(docx),
                    "hash_matches_summary": True,
                    "bytes_match_summary": True,
                },
            },
            "blocking_reasons": [],
        }

    def _artifact(self, project_root: Path, path: Path) -> dict:
        return {
            "path": str(path.relative_to(project_root)),
            "exists": True,
            "bytes": path.stat().st_size,
            "sha256": self._sha256(path),
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
        }

    def _source_paths(self) -> dict:
        return {
            "route_specific_artifact_executor": "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json",
            "delegated_report": "Results/json/formal_pdf_final_writeback.json",
        }

    def _write_bytes(self, path: Path, payload: bytes) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return path

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _sha256(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()

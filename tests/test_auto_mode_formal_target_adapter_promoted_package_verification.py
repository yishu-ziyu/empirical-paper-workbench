import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_promoted_package_verification import (
    build_auto_mode_formal_target_adapter_promoted_package_verification,
    write_auto_mode_formal_target_adapter_promoted_package_verification_outputs,
)


class AutoModeFormalTargetAdapterPromotedPackageVerificationTests(unittest.TestCase):
    """BDD: P7-W verifies promoted formal package targets without writing product state."""

    def test_bdd_p7w_completed_promotion_verifies_formal_targets(self) -> None:
        """行为 1：completed promotion + manifest 复验正式目标文件。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._promotion_manifest(project_root)
            report = build_auto_mode_formal_target_adapter_promoted_package_verification(
                project_root,
                self._completed_execute_report(manifest),
                manifest,
                source_paths=self._source_paths(),
            )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_target_adapter_promoted_package_verification.v1")
        self.assertEqual(report["status"], "promoted_formal_package_verified_for_review")
        self.assertTrue(report["formal_package_verified"])
        self.assertTrue(report["promoted_formal_targets_verified"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(len(report["formal_target_verification_records"]), 6)
        self.assertTrue(
            all(item["verification_status"] == "verified" for item in report["formal_target_verification_records"])
        )

    def test_bdd_p7w_current_blocked_promotion_execute_blocks_verification(self) -> None:
        """行为 2：当前 P7-V blocked 时不能验证正式包。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_auto_mode_formal_target_adapter_promoted_package_verification(
                Path(tmpdir),
                self._blocked_execute_report(),
                {},
            )

        self.assertEqual(report["status"], "blocked_by_candidate_promotion_execute")
        self.assertFalse(report["formal_package_verified"])
        self.assertEqual(report["formal_target_verification_records"], [])
        self.assertIn("candidate_promotion_execute_not_completed", report["blocking_reasons"])
        self.assertIn("promotion_manifest_not_recorded", report["blocking_reasons"])

    def test_bdd_p7w_missing_or_invalid_manifest_blocks_verification(self) -> None:
        """行为 3：promotion manifest 缺失或 schema 错误时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._promotion_manifest(project_root)
            manifest["schema_version"] = "wrong.schema"
            report = build_auto_mode_formal_target_adapter_promoted_package_verification(
                project_root,
                self._completed_execute_report(manifest),
                manifest,
            )

        self.assertEqual(report["status"], "blocked_by_candidate_promotion_manifest")
        self.assertFalse(report["formal_package_verified"])
        self.assertIn("promotion_manifest_missing_or_invalid_schema", report["blocking_reasons"])

    def test_bdd_p7w_execute_report_must_be_completed_promotion_state(self) -> None:
        """行为 4：dry-run 或未 completed 的 execute report 不能验证正式包。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._promotion_manifest(project_root)
            execute_report = self._completed_execute_report(manifest)
            execute_report["status"] = "candidate_promotion_dry_run_ready"
            execute_report["candidate_targets_promoted"] = False
            execute_report["promotion_manifest_recorded"] = False

            report = build_auto_mode_formal_target_adapter_promoted_package_verification(
                project_root,
                execute_report,
                manifest,
            )

        self.assertEqual(report["status"], "blocked_by_candidate_promotion_execute")
        self.assertIn("candidate_promotion_execute_not_completed", report["blocking_reasons"])
        self.assertIn("candidate_targets_not_promoted", report["blocking_reasons"])

    def test_bdd_p7w_missing_changed_or_outside_formal_target_blocks_verification(self) -> None:
        """行为 5：正式目标缺失、被改或路径越界时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._promotion_manifest(project_root)
            missing_target = project_root / manifest["promoted_targets"][0]["formal_target_path"]
            missing_target.unlink()
            changed_target = project_root / manifest["promoted_targets"][1]["formal_target_path"]
            changed_target.write_text("changed formal target\n", encoding="utf-8")
            manifest["promoted_targets"][2]["formal_target_path"] = "workspace/not-formal/method_gate.md"

            report = build_auto_mode_formal_target_adapter_promoted_package_verification(
                project_root,
                self._completed_execute_report(manifest),
                manifest,
            )

        self.assertEqual(report["status"], "blocked_by_promoted_formal_package_verification")
        self.assertFalse(report["formal_package_verified"])
        self.assertIn("promoted_formal_target_missing:formal_manuscript_sources", report["blocking_reasons"])
        self.assertIn("promoted_formal_target_bytes_mismatch:formal_bibliography_sources", report["blocking_reasons"])
        self.assertIn("promoted_formal_target_sha256_mismatch:formal_bibliography_sources", report["blocking_reasons"])
        self.assertIn("formal_target_outside_formal_package:method_review_records", report["blocking_reasons"])

    def test_bdd_p7w_boundary_violations_block_verification(self) -> None:
        """行为 6：product/render/model 等越界副作用阻断正式包验证。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._promotion_manifest(project_root)
            manifest["boundary_flags"]["modified_product_state"] = True
            execute_report = self._completed_execute_report(manifest)
            execute_report["boundary_flags"]["rendered_pdf"] = True

            report = build_auto_mode_formal_target_adapter_promoted_package_verification(
                project_root,
                execute_report,
                manifest,
            )

        self.assertEqual(report["status"], "blocked_by_candidate_promotion_boundary")
        self.assertIn("candidate_promotion_execute_boundary_violation:rendered_pdf", report["blocking_reasons"])
        self.assertIn("promotion_manifest_boundary_violation:modified_product_state", report["blocking_reasons"])

    def test_bdd_p7w_cli_defaults_to_current_blocked_promotion_execute(self) -> None:
        """行为 2：CLI 默认读取当前 blocked P7-V，不验证正式包。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_candidate_promotion_execute.json",
                self._blocked_execute_report(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_promoted_package_verification.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_candidate_promotion_execute", result.stdout)
            self.assertIn("formal_package_verified=false", result.stdout)
            self.assertTrue(
                (
                    project_root / "Results/json/auto_mode_formal_target_adapter_promoted_package_verification.json"
                ).exists()
            )
            self.assertTrue(
                (project_root / "Reviews/auto_mode_formal_target_adapter_promoted_package_verification.md").exists()
            )
            self.assertFalse(
                (
                    project_root / "state/product/auto_mode_formal_target_adapter_promoted_package_verification.json"
                ).exists()
            )

    def test_bdd_p7w_writes_report_and_review_without_new_state(self) -> None:
        """行为 7：只写验证 report/review，不新增正式或产品状态。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._promotion_manifest(project_root)
            report = build_auto_mode_formal_target_adapter_promoted_package_verification(
                project_root,
                self._completed_execute_report(manifest),
                manifest,
            )
            report_path, review_path = write_auto_mode_formal_target_adapter_promoted_package_verification_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "promoted_formal_package_verified_for_review")
            self.assertFalse(
                (
                    project_root / "state/product/auto_mode_formal_target_adapter_promoted_package_verification.json"
                ).exists()
            )

    def _completed_execute_report(self, manifest: dict) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_candidate_promotion_execute.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "verified_candidate_promotion_completed",
            "mode": "promote",
            "confirm_promote": True,
            "can_promote_with_confirmation": True,
            "promotion_manifest_recorded": True,
            "promotion_manifest_path": "workspace/formal_target_adapter_candidate_promotion/auto_mode/formal_target_adapter_candidate_promotion_manifest.json",
            "candidate_targets_promoted": True,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": True,
            "this_command_wrote_formal_state": True,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "promotion_operations": [
                {
                    "execution_id": target["execution_id"],
                    "promotion_id": target["promotion_id"],
                    "writeback_target_group": target["writeback_target_group"],
                    "candidate_path": target["candidate_path"],
                    "formal_target_path": target["formal_target_path"],
                }
                for target in manifest.get("promoted_targets", [])
            ],
            "boundary_flags": self._source_boundary_flags(),
        }

    def _blocked_execute_report(self) -> dict:
        report = self._completed_execute_report({"promoted_targets": []})
        report["status"] = "blocked_by_candidate_promotion_execution_preflight"
        report["mode"] = "dry-run"
        report["confirm_promote"] = False
        report["can_promote_with_confirmation"] = False
        report["promotion_manifest_recorded"] = False
        report["promotion_manifest_path"] = ""
        report["candidate_targets_promoted"] = False
        report["formal_writeback_executed"] = False
        report["this_command_wrote_formal_state"] = False
        report["blocking_reasons"] = ["promotion_execution_preflight_not_ready"]
        report["promotion_operations"] = []
        report["boundary_flags"] = self._verification_boundary_flags()
        return report

    def _promotion_manifest(self, project_root: Path) -> dict:
        targets = []
        for number, group, formal_target in [
            ("01", "formal_manuscript_sources", "manuscript/paper.md"),
            ("02", "formal_bibliography_sources", "bibliography/literature_review_packet.json"),
            ("03", "method_review_records", "reviews/method_gate.md"),
            ("04", "statistical_result_records", "evidence/results_evidence_package.json"),
            ("05", "reproducibility_records", "reproducibility/reproducibility_readme.md"),
            ("06", "formal_package_records", "manifest.json"),
        ]:
            formal_target_path = f"Submissions/formal_package/{formal_target}"
            absolute_target = project_root / formal_target_path
            absolute_target.parent.mkdir(parents=True, exist_ok=True)
            content = f"promoted::{group}\n"
            absolute_target.write_text(content, encoding="utf-8")
            encoded = content.encode("utf-8")
            targets.append(
                {
                    "execution_id": f"verified_candidate_promotion_execution::{number}::{group}",
                    "promotion_id": f"verified_candidate_promotion::{number}::{group}",
                    "writeback_target_group": group,
                    "candidate_path": f"Submissions/auto_mode/cgss_social_capital_happiness/{formal_target}",
                    "formal_target_path": formal_target_path,
                    "bytes": len(encoded),
                    "sha256": hashlib.sha256(encoded).hexdigest(),
                }
            )
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_candidate_promotion_manifest.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_execute_report": "Results/json/auto_mode_formal_target_adapter_candidate_promotion_execute.json",
            "manifest_path": "workspace/formal_target_adapter_candidate_promotion/auto_mode/formal_target_adapter_candidate_promotion_manifest.json",
            "reviewer": "unit_test_reviewer",
            "note": "Promote verified candidates into formal package.",
            "candidate_targets_promoted": True,
            "formal_writeback_executed": True,
            "this_command_wrote_formal_state": True,
            "can_write_product_state": False,
            "promoted_targets": targets,
            "boundary_flags": self._source_boundary_flags(),
        }

    def _source_boundary_flags(self) -> dict:
        flags = self._verification_boundary_flags()
        flags["modified_formal_manuscript"] = True
        flags["modified_formal_bibliography"] = True
        flags["wrote_formal_state"] = True
        flags["promoted_candidate_targets"] = True
        return flags

    def _verification_boundary_flags(self) -> dict:
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
        }

    def _source_paths(self) -> dict:
        return {
            "candidate_promotion_execute": "Results/json/auto_mode_formal_target_adapter_candidate_promotion_execute.json",
            "promotion_manifest": "workspace/formal_target_adapter_candidate_promotion/auto_mode/formal_target_adapter_candidate_promotion_manifest.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

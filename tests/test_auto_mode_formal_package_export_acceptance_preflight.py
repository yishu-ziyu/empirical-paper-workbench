import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_export_acceptance_preflight import (
    build_auto_mode_formal_package_export_acceptance_preflight,
    write_auto_mode_formal_package_export_acceptance_preflight_outputs,
)


class AutoModeFormalPackageExportAcceptancePreflightTests(unittest.TestCase):
    """BDD: P7-X routes a verified formal package toward export / acceptance without exporting."""

    def test_bdd_p7x_verified_package_creates_export_acceptance_plan(self) -> None:
        """行为 1：正式包复验通过后生成导出/验收计划。"""
        report = build_auto_mode_formal_package_export_acceptance_preflight(
            self._verified_package_report(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_package_export_acceptance_preflight.v1")
        self.assertEqual(report["status"], "ready_for_formal_package_export_acceptance_review")
        self.assertTrue(report["can_enter_formal_package_export_acceptance"])
        self.assertTrue(report["requires_explicit_export_or_acceptance_command"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["rendered_pdf"])
        self.assertFalse(report["rendered_docx"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(len(report["export_acceptance_plan"]), 4)
        self.assertEqual(
            [item["action_id"] for item in report["export_acceptance_plan"]],
            [
                "formal_pdf_export_preflight",
                "formal_docx_export_preflight",
                "formal_submission_package_manifest_preflight",
                "manual_acceptance_packet_preflight",
            ],
        )

    def test_bdd_p7x_current_blocked_verification_blocks_preflight(self) -> None:
        """行为 2：当前 P7-W blocked 时不能进入导出/验收。"""
        report = build_auto_mode_formal_package_export_acceptance_preflight(
            self._blocked_package_report(),
        )

        self.assertEqual(report["status"], "blocked_by_promoted_package_verification")
        self.assertFalse(report["can_enter_formal_package_export_acceptance"])
        self.assertFalse(report["requires_explicit_export_or_acceptance_command"])
        self.assertEqual(report["export_acceptance_plan"], [])
        self.assertIn("promoted_formal_package_verification_not_ready", report["blocking_reasons"])

    def test_bdd_p7x_missing_invalid_or_unverified_report_blocks_preflight(self) -> None:
        """行为 3：P7-W 报告缺失、schema 错误或未 verified 时阻断。"""
        missing = build_auto_mode_formal_package_export_acceptance_preflight({})
        invalid = self._verified_package_report()
        invalid["schema_version"] = "wrong.schema"
        invalid_report = build_auto_mode_formal_package_export_acceptance_preflight(invalid)
        unverified = self._verified_package_report()
        unverified["formal_package_verified"] = False
        unverified_report = build_auto_mode_formal_package_export_acceptance_preflight(unverified)

        self.assertEqual(missing["status"], "blocked_by_promoted_package_verification")
        self.assertIn("promoted_formal_package_verification_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(invalid_report["status"], "blocked_by_promoted_package_verification")
        self.assertIn(
            "promoted_formal_package_verification_missing_or_invalid_schema",
            invalid_report["blocking_reasons"],
        )
        self.assertEqual(unverified_report["status"], "blocked_by_promoted_package_verification")
        self.assertIn("formal_package_not_verified", unverified_report["blocking_reasons"])

    def test_bdd_p7x_bad_formal_target_records_block_preflight(self) -> None:
        """行为 4：正式包记录缺失、未 verified 或路径越界时阻断。"""
        missing_records = self._verified_package_report()
        missing_records["formal_target_verification_records"] = []
        not_verified = self._verified_package_report()
        not_verified["formal_target_verification_records"][0]["verification_status"] = "missing"
        outside = self._verified_package_report()
        outside["formal_target_verification_records"][1]["formal_target_path"] = "workspace/not-formal/paper.md"

        missing_report = build_auto_mode_formal_package_export_acceptance_preflight(missing_records)
        not_verified_report = build_auto_mode_formal_package_export_acceptance_preflight(not_verified)
        outside_report = build_auto_mode_formal_package_export_acceptance_preflight(outside)

        self.assertEqual(missing_report["status"], "blocked_by_formal_package_target_records")
        self.assertIn("formal_target_verification_records_missing", missing_report["blocking_reasons"])
        self.assertEqual(not_verified_report["status"], "blocked_by_formal_package_target_records")
        self.assertIn("formal_target_not_verified:formal_manuscript_sources", not_verified_report["blocking_reasons"])
        self.assertEqual(outside_report["status"], "blocked_by_formal_package_target_records")
        self.assertIn(
            "formal_target_outside_formal_package:formal_bibliography_sources",
            outside_report["blocking_reasons"],
        )

    def test_bdd_p7x_boundary_violations_block_preflight(self) -> None:
        """行为 5：P7-W 带 product/render/model 副作用时阻断。"""
        report_with_boundary = self._verified_package_report()
        report_with_boundary["boundary_flags"]["rendered_pdf"] = True
        report_with_boundary["can_write_product_state"] = True

        report = build_auto_mode_formal_package_export_acceptance_preflight(report_with_boundary)

        self.assertEqual(report["status"], "blocked_by_promoted_package_verification_boundary")
        self.assertIn("promoted_package_verification_allows_product_state_write", report["blocking_reasons"])
        self.assertIn("promoted_package_verification_boundary_violation:rendered_pdf", report["blocking_reasons"])

    def test_bdd_p7x_cli_defaults_to_current_blocked_verification(self) -> None:
        """行为 2：CLI 默认读取当前 blocked P7-W，继续不导出。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_promoted_package_verification.json",
                self._blocked_package_report(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_export_acceptance_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_promoted_package_verification", result.stdout)
            self.assertIn("can_enter_formal_package_export_acceptance=false", result.stdout)
            self.assertIn("export_acceptance_plan=0", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_package_export_acceptance_preflight.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_package_export_acceptance_preflight.md").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.docx").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_export_acceptance_preflight.json").exists())

    def test_bdd_p7x_writes_report_and_review_only(self) -> None:
        """行为 6：只写预检 report/review，不导出不写产品状态。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_package_export_acceptance_preflight(
                self._verified_package_report(),
            )
            report_path, review_path = write_auto_mode_formal_package_export_acceptance_preflight_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "ready_for_formal_package_export_acceptance_review")
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.docx").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_export_acceptance_preflight.json").exists())

    def _verified_package_report(self) -> dict:
        records = []
        for number, group, target in [
            ("01", "formal_manuscript_sources", "manuscript/paper.md"),
            ("02", "formal_bibliography_sources", "bibliography/literature_review_packet.json"),
            ("03", "method_review_records", "reviews/method_gate.md"),
            ("04", "statistical_result_records", "evidence/results_evidence_package.json"),
            ("05", "reproducibility_records", "reproducibility/reproducibility_readme.md"),
            ("06", "formal_package_records", "manifest.json"),
        ]:
            records.append(
                {
                    "execution_id": f"verified_candidate_promotion_execution::{number}::{group}",
                    "promotion_id": f"verified_candidate_promotion::{number}::{group}",
                    "writeback_target_group": group,
                    "candidate_path": f"Submissions/auto_mode/cgss_social_capital_happiness/{target}",
                    "formal_target_path": f"Submissions/formal_package/{target}",
                    "exists": True,
                    "bytes": 100 + int(number),
                    "manifest_bytes": 100 + int(number),
                    "sha256": f"sha-{number}",
                    "manifest_sha256": f"sha-{number}",
                    "verification_status": "verified",
                }
            )
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_promoted_package_verification.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "promoted_formal_package_verified_for_review",
            "formal_package_verified": True,
            "promoted_formal_targets_verified": True,
            "candidate_targets_promoted": True,
            "source_formal_writeback_executed": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "formal_target_verification_records": records,
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_package_report(self) -> dict:
        report = self._verified_package_report()
        report["status"] = "blocked_by_candidate_promotion_execute"
        report["formal_package_verified"] = False
        report["promoted_formal_targets_verified"] = False
        report["candidate_targets_promoted"] = False
        report["source_formal_writeback_executed"] = False
        report["blocking_reasons"] = ["candidate_promotion_execute_not_completed"]
        report["formal_target_verification_records"] = []
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
        }

    def _source_paths(self) -> dict:
        return {
            "promoted_package_verification": "Results/json/auto_mode_formal_target_adapter_promoted_package_verification.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

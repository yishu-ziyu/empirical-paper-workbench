import json
import tempfile
import unittest
import subprocess
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_candidate_verification import (
    build_auto_mode_formal_target_adapter_candidate_verification,
    write_auto_mode_formal_target_adapter_candidate_verification_outputs,
)


class AutoModeFormalTargetAdapterCandidateVerificationTests(unittest.TestCase):
    """BDD: P7-R verifies materialized candidate targets without promoting them."""

    def test_bdd_p7r_completed_materialization_verifies_candidate_targets(self) -> None:
        """行为 1：completed materialization 生成候选目标验证记录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._materialization_manifest(project_root)
            report = build_auto_mode_formal_target_adapter_candidate_verification(
                project_root,
                self._completed_execute_report(),
                manifest,
                source_paths=self._source_paths(),
            )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_target_adapter_candidate_verification.v1")
        self.assertEqual(report["status"], "candidate_targets_verified_for_review")
        self.assertTrue(report["candidate_targets_verified"])
        self.assertFalse(report["formal_target_adapters_executed"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(len(report["target_verification_records"]), 6)
        self.assertTrue(all(item["verification_status"] == "verified" for item in report["target_verification_records"]))

    def test_bdd_p7r_current_blocked_materialization_execute_blocks_verification(self) -> None:
        """行为 2：当前 P7-Q blocked 时不能验证候选目标。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_auto_mode_formal_target_adapter_candidate_verification(
                Path(tmpdir),
                self._blocked_execute_report(),
                {},
            )

        self.assertEqual(report["status"], "blocked_by_materialization_execute")
        self.assertFalse(report["candidate_targets_verified"])
        self.assertEqual(report["target_verification_records"], [])
        self.assertIn("materialization_execute_not_completed", report["blocking_reasons"])
        self.assertIn("materialization_manifest_not_recorded", report["blocking_reasons"])

    def test_bdd_p7r_missing_or_invalid_manifest_blocks_verification(self) -> None:
        """行为 3：materialization manifest 缺失或 schema 错误时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = self._materialization_manifest(Path(tmpdir))
            manifest["schema_version"] = "wrong.schema"
            report = build_auto_mode_formal_target_adapter_candidate_verification(
                Path(tmpdir),
                self._completed_execute_report(),
                manifest,
            )

        self.assertEqual(report["status"], "blocked_by_materialization_manifest")
        self.assertFalse(report["candidate_targets_verified"])
        self.assertIn("materialization_manifest_missing_or_invalid_schema", report["blocking_reasons"])

    def test_bdd_p7r_execute_report_must_be_completed_materialization_state(self) -> None:
        """行为 4：execute report 未 completed/materialized 时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._materialization_manifest(project_root)
            execute_report = self._completed_execute_report()
            execute_report["status"] = "adapter_materialization_dry_run_ready"
            execute_report["candidate_targets_materialized"] = False
            execute_report["materialization_manifest_recorded"] = False

            report = build_auto_mode_formal_target_adapter_candidate_verification(
                project_root,
                execute_report,
                manifest,
            )

        self.assertEqual(report["status"], "blocked_by_materialization_execute")
        self.assertIn("materialization_execute_not_completed", report["blocking_reasons"])
        self.assertIn("candidate_targets_not_materialized", report["blocking_reasons"])

    def test_bdd_p7r_missing_target_or_byte_mismatch_blocks_verification(self) -> None:
        """行为 5：目标缺失或 bytes 不一致时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._materialization_manifest(project_root)
            missing_target = project_root / manifest["materialized_targets"][0]["target_path"]
            missing_target.unlink()
            mismatch_target = project_root / manifest["materialized_targets"][1]["target_path"]
            mismatch_target.write_text("changed bytes\n", encoding="utf-8")

            report = build_auto_mode_formal_target_adapter_candidate_verification(
                project_root,
                self._completed_execute_report(),
                manifest,
            )

        self.assertEqual(report["status"], "blocked_by_candidate_target_verification")
        self.assertFalse(report["candidate_targets_verified"])
        self.assertIn("candidate_target_missing:formal_manuscript_sources", report["blocking_reasons"])
        self.assertIn("candidate_target_bytes_mismatch:formal_bibliography_sources", report["blocking_reasons"])

    def test_bdd_p7r_boundary_violations_block_verification(self) -> None:
        """行为 6：execute/manifest 边界越界时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = self._materialization_manifest(project_root)
            manifest["boundary_flags"]["modified_product_state"] = True
            execute_report = self._completed_execute_report()
            execute_report["boundary_flags"]["wrote_formal_state"] = True

            report = build_auto_mode_formal_target_adapter_candidate_verification(
                project_root,
                execute_report,
                manifest,
            )

        self.assertEqual(report["status"], "blocked_by_materialization_boundary")
        self.assertIn("materialization_execute_boundary_violation:wrote_formal_state", report["blocking_reasons"])
        self.assertIn("materialization_manifest_boundary_violation:modified_product_state", report["blocking_reasons"])

    def test_bdd_p7r_cli_defaults_to_current_blocked_state(self) -> None:
        """行为 7：CLI 默认读取当前 blocked execute，写 blocked verification。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_materialization_execute.json",
                self._blocked_execute_report(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_candidate_verification.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_materialization_execute", result.stdout)
            self.assertIn("candidate_targets_verified=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_target_adapter_candidate_verification.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_target_adapter_candidate_verification.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_target_adapter_candidate_verification.json").exists())

    def test_bdd_p7r_writes_report_and_review_without_formal_state(self) -> None:
        """行为 1/7：只写验证 report/review，不写正式层。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_target_adapter_candidate_verification(
                project_root,
                self._completed_execute_report(),
                self._materialization_manifest(project_root),
            )
            report_path, review_path = write_auto_mode_formal_target_adapter_candidate_verification_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "candidate_targets_verified_for_review")
            self.assertFalse((project_root / "state/product/auto_mode_formal_target_adapter_candidate_verification.json").exists())

    def _completed_execute_report(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_materialization_execute.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "adapter_materialization_completed",
            "mode": "materialize",
            "confirm_materialize": True,
            "can_materialize_with_confirmation": True,
            "materialization_manifest_recorded": True,
            "materialization_manifest_path": "workspace/formal_target_adapter_materialization/auto_mode/formal_target_adapter_materialization_manifest.json",
            "candidate_targets_materialized": True,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "boundary_flags": self._clean_execute_boundary_flags(),
        }

    def _blocked_execute_report(self) -> dict:
        report = self._completed_execute_report()
        report["status"] = "blocked_by_materialization_preflight"
        report["mode"] = "dry-run"
        report["confirm_materialize"] = False
        report["can_materialize_with_confirmation"] = False
        report["materialization_manifest_recorded"] = False
        report["materialization_manifest_path"] = ""
        report["candidate_targets_materialized"] = False
        report["blocking_reasons"] = [
            "materialization_preflight_not_ready",
            "materialization_plan_missing",
        ]
        return report

    def _materialization_manifest(self, project_root: Path) -> dict:
        targets = []
        for number, group, target in [
            ("01", "formal_manuscript_sources", "manuscript/paper.md"),
            ("02", "formal_bibliography_sources", "bibliography/literature_review_packet.json"),
            ("03", "method_review_records", "reviews/method_gate.md"),
            ("04", "statistical_result_records", "evidence/results_evidence_package.json"),
            ("05", "reproducibility_records", "reproducibility/reproducibility_readme.md"),
            ("06", "formal_package_records", "manifest.json"),
        ]:
            target_path = f"Submissions/auto_mode/cgss_social_capital_happiness/{target}"
            absolute_target = project_root / target_path
            absolute_target.parent.mkdir(parents=True, exist_ok=True)
            content = f"materialized::{group}\n"
            absolute_target.write_text(content, encoding="utf-8")
            targets.append(
                {
                    "operation_id": f"adapter_materialization::{number}::{group}",
                    "writeback_target_group": group,
                    "source_path": f"workspace/paper_packages/cgss_social_capital_happiness/{group}.json",
                    "target_path": target_path,
                    "bytes": len(content.encode("utf-8")),
                }
            )
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_materialization_manifest.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_execute_report": "Results/json/auto_mode_formal_target_adapter_materialization_execute.json",
            "manifest_path": "workspace/formal_target_adapter_materialization/auto_mode/formal_target_adapter_materialization_manifest.json",
            "reviewer": "unit_test_reviewer",
            "note": "Candidate targets materialized for verification.",
            "candidate_targets_materialized": True,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "materialized_targets": targets,
            "boundary_flags": self._clean_manifest_boundary_flags(),
        }

    def _clean_execute_boundary_flags(self) -> dict:
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
        }

    def _clean_manifest_boundary_flags(self) -> dict:
        flags = self._clean_execute_boundary_flags()
        flags["materialized_candidate_targets"] = False
        return flags

    def _source_paths(self) -> dict:
        return {
            "materialization_execute": "Results/json/auto_mode_formal_target_adapter_materialization_execute.json",
            "materialization_manifest": "workspace/formal_target_adapter_materialization/auto_mode/formal_target_adapter_materialization_manifest.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

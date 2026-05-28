import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_preflight import (
    build_auto_mode_formal_target_adapter_candidate_promotion_preflight,
    write_auto_mode_formal_target_adapter_candidate_promotion_preflight_outputs,
)


class AutoModeFormalTargetAdapterCandidatePromotionPreflightTests(unittest.TestCase):
    """BDD: P7-S turns verified candidate targets into promotion preflight only."""

    def test_bdd_p7s_verified_candidates_create_promotion_preflight_plan(self) -> None:
        """行为 1：已验证 candidate targets 生成 promotion preflight plan。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_preflight(
            self._verified_candidate_report(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_target_adapter_candidate_promotion_preflight.v1",
        )
        self.assertEqual(report["status"], "ready_for_verified_candidate_promotion_review")
        self.assertTrue(report["can_request_verified_candidate_promotion_approval"])
        self.assertTrue(report["requires_separate_promotion_approval"])
        self.assertTrue(report["requires_explicit_promotion_execute_command"])
        self.assertFalse(report["candidate_targets_promoted"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(len(report["promotion_plan"]), 6)
        self.assertTrue(
            all(item["promotion_status"] == "pending_separate_approval" for item in report["promotion_plan"])
        )
        self.assertTrue(all(item["candidate_path"].startswith("Submissions/auto_mode/") for item in report["promotion_plan"]))
        self.assertTrue(all(item["formal_target_path"].startswith("Submissions/formal_package/") for item in report["promotion_plan"]))

    def test_bdd_p7s_current_blocked_verification_blocks_promotion_preflight(self) -> None:
        """行为 2：当前 P7-R blocked 时不能生成 promotion preflight plan。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_preflight(
            self._blocked_candidate_report(),
        )

        self.assertEqual(report["status"], "blocked_by_candidate_verification")
        self.assertFalse(report["can_request_verified_candidate_promotion_approval"])
        self.assertFalse(report["requires_separate_promotion_approval"])
        self.assertFalse(report["requires_explicit_promotion_execute_command"])
        self.assertEqual(report["promotion_plan"], [])
        self.assertIn("candidate_verification_not_ready", report["blocking_reasons"])
        self.assertIn("candidate_targets_not_verified", report["blocking_reasons"])
        self.assertEqual(
            report["source_candidate_verification"]["blocking_reasons"],
            ["materialization_execute_not_completed"],
        )

    def test_bdd_p7s_missing_or_invalid_verification_schema_blocks_preflight(self) -> None:
        """行为 3：verification report 缺失或 schema 错误时阻断。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_preflight({})

        self.assertEqual(report["status"], "blocked_by_candidate_verification")
        self.assertFalse(report["can_request_verified_candidate_promotion_approval"])
        self.assertIn("candidate_verification_missing_or_invalid_schema", report["blocking_reasons"])
        self.assertEqual(report["promotion_plan"], [])

    def test_bdd_p7s_each_record_must_be_verified_and_auditable(self) -> None:
        """行为 4：逐项记录必须 verified、位于 auto_mode 且有 sha256。"""
        verification = self._verified_candidate_report()
        verification["target_verification_records"][0]["verification_status"] = "missing"
        verification["target_verification_records"][1]["target_path"] = "Submissions/manual/bibliography.json"
        verification["target_verification_records"][2]["sha256"] = ""
        verification["target_verification_records"][3]["exists"] = False

        report = build_auto_mode_formal_target_adapter_candidate_promotion_preflight(verification)

        self.assertEqual(report["status"], "blocked_by_verified_candidate_records")
        self.assertFalse(report["can_request_verified_candidate_promotion_approval"])
        self.assertIn("candidate_target_not_verified:formal_manuscript_sources", report["blocking_reasons"])
        self.assertIn("candidate_target_outside_auto_mode_submission:formal_bibliography_sources", report["blocking_reasons"])
        self.assertIn("candidate_target_sha256_missing_or_invalid:method_review_records", report["blocking_reasons"])
        self.assertIn("candidate_target_not_confirmed_existing:statistical_result_records", report["blocking_reasons"])
        self.assertEqual(report["promotion_plan"], [])

    def test_bdd_p7s_boundary_violation_blocks_preflight(self) -> None:
        """行为 5：P7-R 边界越界时阻断 promotion preflight。"""
        verification = self._verified_candidate_report()
        verification["boundary_flags"]["modified_product_state"] = True
        verification["boundary_flags"]["wrote_formal_state"] = True

        report = build_auto_mode_formal_target_adapter_candidate_promotion_preflight(verification)

        self.assertEqual(report["status"], "blocked_by_candidate_verification_boundary")
        self.assertFalse(report["can_request_verified_candidate_promotion_approval"])
        self.assertIn("candidate_verification_boundary_violation:modified_product_state", report["blocking_reasons"])
        self.assertIn("candidate_verification_boundary_violation:wrote_formal_state", report["blocking_reasons"])
        self.assertEqual(report["promotion_plan"], [])

    def test_bdd_p7s_cli_defaults_to_current_blocked_verification(self) -> None:
        """行为 6：CLI 默认读取当前 blocked P7-R，写 blocked preflight。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_candidate_verification.json",
                self._blocked_candidate_report(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_candidate_promotion_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_candidate_verification", result.stdout)
            self.assertIn("candidate_targets_promoted=false", result.stdout)
            self.assertIn("can_write_product_state=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_target_adapter_candidate_promotion_preflight.json"
                ).exists()
            )
            self.assertTrue(
                (project_root / "Reviews/auto_mode_formal_target_adapter_candidate_promotion_preflight.md").exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_target_adapter_candidate_promotion_preflight.json"
                ).exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())

    def test_bdd_p7s_writes_report_and_review_without_promoting_candidates(self) -> None:
        """行为 7：只写 preflight report/review，不提升 candidate target。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_preflight(
            self._verified_candidate_report(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path = write_auto_mode_formal_target_adapter_candidate_promotion_preflight_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "ready_for_verified_candidate_promotion_review")
            self.assertIn("Candidate Promotion Preflight", review_path.read_text(encoding="utf-8"))
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_target_adapter_candidate_promotion_preflight.json"
                ).exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())

    def _verified_candidate_report(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_candidate_verification.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "candidate_targets_verified_for_review",
            "candidate_targets_verified": True,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "target_verification_records": [
                self._verified_record("01", "formal_manuscript_sources", "manuscript/paper.md"),
                self._verified_record("02", "formal_bibliography_sources", "bibliography/literature_review_packet.json"),
                self._verified_record("03", "method_review_records", "reviews/method_gate.md"),
                self._verified_record("04", "statistical_result_records", "evidence/results_evidence_package.json"),
                self._verified_record("05", "reproducibility_records", "reproducibility/reproducibility_readme.md"),
                self._verified_record("06", "formal_package_records", "manifest.json"),
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_candidate_report(self) -> dict:
        report = self._verified_candidate_report()
        report["status"] = "blocked_by_materialization_execute"
        report["candidate_targets_verified"] = False
        report["blocking_reasons"] = ["materialization_execute_not_completed"]
        report["target_verification_records"] = []
        return report

    def _verified_record(self, number: str, group: str, target: str) -> dict:
        return {
            "operation_id": f"adapter_materialization::{number}::{group}",
            "writeback_target_group": group,
            "source_path": f"workspace/paper_packages/cgss_social_capital_happiness/{group}.json",
            "target_path": f"Submissions/auto_mode/cgss_social_capital_happiness/{target}",
            "exists": True,
            "bytes": 32,
            "manifest_bytes": 32,
            "sha256": "a" * 64,
            "verification_status": "verified",
        }

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
        }

    def _source_paths(self) -> dict:
        return {
            "candidate_verification": "Results/json/auto_mode_formal_target_adapter_candidate_verification.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

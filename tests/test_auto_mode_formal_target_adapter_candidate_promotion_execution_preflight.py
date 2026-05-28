import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_execution_preflight import (
    build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight,
    write_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight_outputs,
)


class AutoModeFormalTargetAdapterCandidatePromotionExecutionPreflightTests(unittest.TestCase):
    """BDD: P7-U prepares approved candidate promotion for a later execute node."""

    def test_bdd_p7u_effective_approval_creates_execution_preflight_without_promotion(self) -> None:
        """行为 1：生效审批生成执行预检计划，但本节点不提升 candidate。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight(
            self._approved_ledger(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.v1",
        )
        self.assertEqual(report["status"], "ready_for_verified_candidate_promotion_execution_review")
        self.assertTrue(report["can_request_verified_candidate_promotion_execution"])
        self.assertTrue(report["requires_explicit_promotion_execute_command"])
        self.assertFalse(report["candidate_targets_promoted"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(len(report["promotion_execution_plan"]), 2)
        for item in report["promotion_execution_plan"]:
            self.assertEqual(item["execution_status"], "pending_explicit_promotion_execute_command")
            self.assertFalse(item["promoted_by_this_command"])

    def test_bdd_p7u_blocks_when_approval_is_not_effective(self) -> None:
        """行为 2：P7-T blocked 或未 approve 时不能进入执行预检。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight(
            self._blocked_ledger(),
        )

        self.assertEqual(report["status"], "blocked_by_candidate_promotion_approval")
        self.assertFalse(report["can_request_verified_candidate_promotion_execution"])
        self.assertFalse(report["candidate_targets_promoted"])
        self.assertIn("candidate_promotion_approval_not_effective", report["blocking_reasons"])
        self.assertIn("candidate_promotion_approval_has_blocking_reasons", report["blocking_reasons"])
        self.assertEqual(report["promotion_execution_plan"], [])

    def test_bdd_p7u_blocks_malformed_approved_promotion_plan(self) -> None:
        """行为 3：审批清单缺路径、目标或校验信息时阻断。"""
        missing_plan = self._approved_ledger()
        missing_plan["approved_promotion_plan"] = []
        missing_report = build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight(missing_plan)

        malformed_plan = self._approved_ledger()
        malformed_plan["approved_promotion_plan"][0]["candidate_path"] = "tmp/paper.md"
        malformed_plan["approved_promotion_plan"][0]["formal_target_path"] = "tmp/formal.md"
        malformed_plan["approved_promotion_plan"][0]["candidate_sha256"] = "not-a-sha"
        malformed_report = build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight(
            malformed_plan,
        )

        self.assertEqual(missing_report["status"], "blocked_by_approved_promotion_plan")
        self.assertIn("approved_promotion_plan_missing", missing_report["blocking_reasons"])
        self.assertEqual(malformed_report["status"], "blocked_by_approved_promotion_plan")
        self.assertIn(
            "candidate_path_outside_auto_mode_submission:formal_manuscript_sources",
            malformed_report["blocking_reasons"],
        )
        self.assertIn(
            "formal_target_path_outside_formal_package:formal_manuscript_sources",
            malformed_report["blocking_reasons"],
        )
        self.assertIn(
            "candidate_sha256_missing_or_invalid:formal_manuscript_sources",
            malformed_report["blocking_reasons"],
        )

    def test_bdd_p7u_boundary_violation_blocks_execution_preflight(self) -> None:
        """行为 4：审批账本出现边界越界时阻断。"""
        ledger = self._approved_ledger()
        ledger["boundary_flags"]["promoted_candidate_targets"] = True
        report = build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight(ledger)

        self.assertEqual(report["status"], "blocked_by_candidate_promotion_approval_boundary")
        self.assertFalse(report["can_request_verified_candidate_promotion_execution"])
        self.assertIn(
            "candidate_promotion_approval_boundary_violation:promoted_candidate_targets",
            report["blocking_reasons"],
        )
        self.assertEqual(report["promotion_execution_plan"], [])

    def test_bdd_p7u_writes_json_and_markdown_without_promoting_candidates(self) -> None:
        """行为 6：只写 execution preflight JSON/Markdown，不提升 candidate。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight(
            self._approved_ledger(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path = (
                write_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight_outputs(
                    project_root,
                    report,
                )
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "ready_for_verified_candidate_promotion_execution_review")
            self.assertIn("Candidate Promotion Execution Preflight", review_path.read_text(encoding="utf-8"))
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json"
                ).exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())

    def test_bdd_p7u_cli_defaults_to_current_blocked_approval(self) -> None:
        """行为 5：CLI 默认读取当前 blocked P7-T，继续不提升 candidate。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_candidate_promotion_approval.json",
                self._blocked_ledger(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_candidate_promotion_approval", result.stdout)
            self.assertIn("can_request_verified_candidate_promotion_execution=false", result.stdout)
            self.assertIn("candidate_targets_promoted=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json"
                ).exists()
            )
            self.assertTrue(
                (
                    project_root
                    / "Reviews/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.md"
                ).exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json"
                ).exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())

    def _approved_ledger(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_candidate_promotion_approval.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "approved_for_verified_candidate_promotion_execution_preflight",
            "approved": True,
            "verified_candidate_promotion_allowed": True,
            "can_enter_verified_candidate_promotion_execution_preflight": True,
            "candidate_targets_promoted": False,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "approval": {
                "decision": "approve",
                "reviewer": "unit_test_reviewer",
                "note": "Approved for candidate promotion execution preflight.",
                "approved": True,
                "metadata_complete": True,
            },
            "approved_promotion_plan": [
                self._approved_item("01", "formal_manuscript_sources", "manuscript/paper.md"),
                self._approved_item("02", "formal_bibliography_sources", "bibliography/literature.json"),
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_ledger(self) -> dict:
        ledger = self._approved_ledger()
        ledger["status"] = "blocked_by_candidate_promotion_preflight"
        ledger["approved"] = False
        ledger["verified_candidate_promotion_allowed"] = False
        ledger["can_enter_verified_candidate_promotion_execution_preflight"] = False
        ledger["blocking_reasons"] = ["candidate_promotion_preflight_not_ready"]
        ledger["approval"]["decision"] = "defer"
        ledger["approval"]["approved"] = False
        ledger["approval"]["metadata_complete"] = False
        ledger["approved_promotion_plan"] = []
        return ledger

    def _approved_item(self, number: str, group: str, target: str) -> dict:
        return {
            "promotion_id": f"verified_candidate_promotion::{number}::{group}",
            "operation_id": f"adapter_materialization::{number}::{group}",
            "writeback_target_group": group,
            "candidate_path": f"Submissions/auto_mode/cgss_social_capital_happiness/{target}",
            "candidate_bytes": 32,
            "candidate_sha256": "a" * 64,
            "formal_target_path": f"Submissions/formal_package/{target}",
            "approval_status": "approved_for_verified_candidate_promotion_execution_preflight",
            "requires_explicit_promotion_execute_command": True,
            "promoted_by_this_command": False,
            "this_command_wrote_formal_state": False,
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
            "promoted_candidate_targets": False,
        }

    def _source_paths(self) -> dict:
        return {
            "candidate_promotion_approval": (
                "Results/json/auto_mode_formal_target_adapter_candidate_promotion_approval.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_approval import (
    build_auto_mode_formal_target_adapter_candidate_promotion_approval,
    write_auto_mode_formal_target_adapter_candidate_promotion_approval_outputs,
)


class AutoModeFormalTargetAdapterCandidatePromotionApprovalTests(unittest.TestCase):
    """BDD: P7-T records candidate promotion approval without promoting candidates."""

    def test_bdd_p7t_approve_ready_preflight_records_approval_without_promotion(self) -> None:
        """行为 1：ready preflight + approve 只授权下一道 promotion execution preflight。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_approval(
            self._ready_preflight(),
            decision="approve",
            reviewer="unit_test_reviewer",
            note="Approve verified candidate promotion for the next execution preflight.",
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_target_adapter_candidate_promotion_approval.v1",
        )
        self.assertEqual(report["status"], "approved_for_verified_candidate_promotion_execution_preflight")
        self.assertTrue(report["approved"])
        self.assertTrue(report["verified_candidate_promotion_allowed"])
        self.assertTrue(report["can_enter_verified_candidate_promotion_execution_preflight"])
        self.assertFalse(report["candidate_targets_promoted"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(len(report["approved_promotion_plan"]), 2)
        self.assertTrue(
            all(
                item["approval_status"] == "approved_for_verified_candidate_promotion_execution_preflight"
                for item in report["approved_promotion_plan"]
            )
        )

    def test_bdd_p7t_defer_waits_without_approving_candidate_promotion(self) -> None:
        """行为 2：defer 不允许进入 candidate promotion execution preflight。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_approval(
            self._ready_preflight(),
            decision="defer",
        )

        self.assertEqual(report["status"], "waiting_for_human_verified_candidate_promotion_approval")
        self.assertFalse(report["approved"])
        self.assertFalse(report["verified_candidate_promotion_allowed"])
        self.assertFalse(report["can_enter_verified_candidate_promotion_execution_preflight"])
        self.assertFalse(report["candidate_targets_promoted"])
        self.assertEqual(report["approved_promotion_plan"], [])

    def test_bdd_p7t_blocks_when_promotion_preflight_is_not_ready(self) -> None:
        """行为 3：P7-S blocked 时不能靠 approve 绕过。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_approval(
            self._blocked_preflight(),
            decision="approve",
            reviewer="unit_test_reviewer",
            note="Attempted approval should not bypass blocked P7-S.",
        )

        self.assertEqual(report["status"], "blocked_by_candidate_promotion_preflight")
        self.assertFalse(report["approved"])
        self.assertFalse(report["verified_candidate_promotion_allowed"])
        self.assertIn("candidate_promotion_preflight_not_ready", report["blocking_reasons"])
        self.assertIn("candidate_verification_not_ready", report["source_preflight"]["blocking_reasons"])
        self.assertEqual(report["approved_promotion_plan"], [])

    def test_bdd_p7t_approve_requires_reviewer_and_note(self) -> None:
        """行为 4：approve 缺 reviewer/note 时阻断。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_approval(
            self._ready_preflight(),
            decision="approve",
            reviewer="",
            note="",
        )

        self.assertEqual(report["status"], "blocked_by_candidate_promotion_approval_metadata")
        self.assertFalse(report["approved"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("approval_note_required", report["blocking_reasons"])

    def test_bdd_p7t_revise_and_reject_do_not_approve_candidate_promotion(self) -> None:
        """行为 5：revise/reject 只记录路线，不启用 candidate promotion。"""
        revise_report = build_auto_mode_formal_target_adapter_candidate_promotion_approval(
            self._ready_preflight(),
            decision="revise",
            reviewer="unit_test_reviewer",
            note="Revise verified candidate targets before promotion.",
        )
        reject_report = build_auto_mode_formal_target_adapter_candidate_promotion_approval(
            self._ready_preflight(),
            decision="reject",
            reviewer="unit_test_reviewer",
            note="Reject verified candidate promotion.",
        )

        self.assertEqual(revise_report["status"], "verified_candidate_promotion_needs_revision")
        self.assertEqual(reject_report["status"], "verified_candidate_promotion_rejected")
        self.assertFalse(revise_report["verified_candidate_promotion_allowed"])
        self.assertFalse(reject_report["verified_candidate_promotion_allowed"])
        self.assertFalse(revise_report["can_enter_verified_candidate_promotion_execution_preflight"])
        self.assertFalse(reject_report["can_enter_verified_candidate_promotion_execution_preflight"])

    def test_bdd_p7t_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 6：CLI 默认读取当前 blocked P7-S，继续不批准提升。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_candidate_promotion_preflight.json",
                self._blocked_preflight(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_candidate_promotion_approval.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_candidate_promotion_preflight", result.stdout)
            self.assertIn("verified_candidate_promotion_allowed=false", result.stdout)
            self.assertIn("candidate_targets_promoted=false", result.stdout)
            self.assertTrue(
                (
                    project_root
                    / "Results/json/auto_mode_formal_target_adapter_candidate_promotion_approval.json"
                ).exists()
            )
            self.assertTrue(
                (project_root / "Reviews/auto_mode_formal_target_adapter_candidate_promotion_approval.md").exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_target_adapter_candidate_promotion_approval.json"
                ).exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())

    def test_bdd_p7t_writes_json_and_markdown_without_promoting_candidates(self) -> None:
        """行为 7：只写 approval JSON/Markdown，不提升 candidate target。"""
        report = build_auto_mode_formal_target_adapter_candidate_promotion_approval(
            self._ready_preflight(),
            decision="approve",
            reviewer="unit_test_reviewer",
            note="Approve verified candidate promotion for the next execution preflight.",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path = write_auto_mode_formal_target_adapter_candidate_promotion_approval_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "approved_for_verified_candidate_promotion_execution_preflight")
            self.assertIn("Candidate Promotion Approval", review_path.read_text(encoding="utf-8"))
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_target_adapter_candidate_promotion_approval.json"
                ).exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())

    def _ready_preflight(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_candidate_promotion_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_verified_candidate_promotion_review",
            "can_request_verified_candidate_promotion_approval": True,
            "requires_separate_promotion_approval": True,
            "requires_explicit_promotion_execute_command": True,
            "candidate_targets_promoted": False,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "promotion_plan": [
                self._promotion_item("01", "formal_manuscript_sources", "manuscript/paper.md"),
                self._promotion_item("02", "formal_bibliography_sources", "bibliography/literature_review_packet.json"),
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_preflight(self) -> dict:
        preflight = self._ready_preflight()
        preflight["status"] = "blocked_by_candidate_verification"
        preflight["can_request_verified_candidate_promotion_approval"] = False
        preflight["requires_separate_promotion_approval"] = False
        preflight["requires_explicit_promotion_execute_command"] = False
        preflight["blocking_reasons"] = [
            "candidate_verification_not_ready",
            "candidate_targets_not_verified",
        ]
        preflight["promotion_plan"] = []
        return preflight

    def _promotion_item(self, number: str, group: str, target: str) -> dict:
        return {
            "promotion_id": f"verified_candidate_promotion::{number}::{group}",
            "operation_id": f"adapter_materialization::{number}::{group}",
            "writeback_target_group": group,
            "source_path": f"workspace/paper_packages/cgss_social_capital_happiness/{group}.json",
            "candidate_path": f"Submissions/auto_mode/cgss_social_capital_happiness/{target}",
            "candidate_bytes": 32,
            "candidate_sha256": "a" * 64,
            "formal_target_path": f"Submissions/formal_package/{target}",
            "promotion_status": "pending_separate_approval",
            "requires_separate_promotion_approval": True,
            "requires_explicit_promotion_execute_command": True,
            "promoted_by_this_command": False,
            "writes_formal_state": False,
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
            "candidate_promotion_preflight": (
                "Results/json/auto_mode_formal_target_adapter_candidate_promotion_preflight.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

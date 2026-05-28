import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_execute import (
    build_auto_mode_formal_target_adapter_candidate_promotion_execute,
    write_auto_mode_formal_target_adapter_candidate_promotion_execute_outputs,
)


class AutoModeFormalTargetAdapterCandidatePromotionExecuteTests(unittest.TestCase):
    """BDD: P7-V explicitly promotes verified candidate targets into the formal package."""

    def test_bdd_p7v_confirmed_promote_copies_candidates_and_writes_manifest(self) -> None:
        """行为 1：确认 promote 后复制候选成果到正式位置，并写 promotion manifest。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            content = "# Paper\n\nVerified candidate manuscript.\n"
            self._write_candidate(project_root, content)

            report = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
                project_root,
                self._ready_preflight(content),
                mode="promote",
                confirm_promote=True,
                reviewer="unit_test_reviewer",
                note="Promote verified candidate manuscript.",
            )
            report_path, review_path, manifest_path = (
                write_auto_mode_formal_target_adapter_candidate_promotion_execute_outputs(project_root, report)
            )
            formal_target = project_root / "Submissions/formal_package/manuscript/paper.md"

            self.assertEqual(report["schema_version"], "p7.auto_mode_formal_target_adapter_candidate_promotion_execute.v1")
            self.assertEqual(report["status"], "verified_candidate_promotion_completed")
            self.assertTrue(report["candidate_targets_promoted"])
            self.assertTrue(report["this_command_wrote_formal_state"])
            self.assertFalse(report["can_write_product_state"])
            self.assertTrue(formal_target.exists())
            self.assertEqual(formal_target.read_text(encoding="utf-8"), content)
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIsNotNone(manifest_path)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "p7.auto_mode_formal_target_adapter_candidate_promotion_manifest.v1")
            self.assertEqual(manifest["promoted_targets"][0]["formal_target_path"], "Submissions/formal_package/manuscript/paper.md")
            self.assertFalse(
                (
                    project_root
                    / "state/product/auto_mode_formal_target_adapter_candidate_promotion_execute.json"
                ).exists()
            )

    def test_bdd_p7v_dry_run_does_not_copy_candidates(self) -> None:
        """行为 2：默认 dry-run 只显示可提升操作，不复制正式成果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            content = "# Paper\n\nVerified candidate manuscript.\n"
            self._write_candidate(project_root, content)

            report = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
                project_root,
                self._ready_preflight(content),
            )
            report_path, review_path, manifest_path = (
                write_auto_mode_formal_target_adapter_candidate_promotion_execute_outputs(project_root, report)
            )

            self.assertEqual(report["status"], "candidate_promotion_dry_run_ready")
            self.assertTrue(report["can_promote_with_confirmation"])
            self.assertFalse(report["candidate_targets_promoted"])
            self.assertFalse(report["formal_writeback_executed"])
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIsNone(manifest_path)

    def test_bdd_p7v_blocks_when_preflight_is_not_ready(self) -> None:
        """行为 3：当前 P7-U blocked 时不能提升候选成果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
                project_root,
                self._blocked_preflight(),
                mode="promote",
                confirm_promote=True,
                reviewer="unit_test_reviewer",
                note="Should not bypass blocked P7-U.",
            )

            self.assertEqual(report["status"], "blocked_by_candidate_promotion_execution_preflight")
            self.assertFalse(report["can_promote_with_confirmation"])
            self.assertFalse(report["candidate_targets_promoted"])
            self.assertIn("promotion_execution_preflight_not_ready", report["blocking_reasons"])
            self.assertEqual(report["promotion_operations"], [])

    def test_bdd_p7v_promote_requires_confirmation_reviewer_and_note(self) -> None:
        """行为 4：promote 缺确认、reviewer 或 note 时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            content = "# Paper\n\nVerified candidate manuscript.\n"
            self._write_candidate(project_root, content)

            missing_confirmation = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
                project_root,
                self._ready_preflight(content),
                mode="promote",
                confirm_promote=False,
                reviewer="unit_test_reviewer",
                note="Missing explicit confirmation.",
            )
            missing_metadata = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
                project_root,
                self._ready_preflight(content),
                mode="promote",
                confirm_promote=True,
                reviewer="",
                note="",
            )

            self.assertEqual(missing_confirmation["status"], "blocked_by_missing_candidate_promotion_confirmation")
            self.assertIn("confirm_promote_required", missing_confirmation["blocking_reasons"])
            self.assertEqual(missing_metadata["status"], "blocked_by_candidate_promotion_metadata")
            self.assertIn("reviewer_required", missing_metadata["blocking_reasons"])
            self.assertIn("promotion_note_required", missing_metadata["blocking_reasons"])
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())

    def test_bdd_p7v_blocks_missing_changed_candidate_or_existing_formal_target(self) -> None:
        """行为 5：候选缺失、校验不符或正式目标已存在时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            content = "# Paper\n\nVerified candidate manuscript.\n"
            preflight = self._ready_preflight(content)

            missing_candidate = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
                project_root,
                preflight,
            )
            self._write_candidate(project_root, content + "changed\n")
            changed_candidate = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
                project_root,
                preflight,
            )
            formal_target = project_root / "Submissions/formal_package/manuscript/paper.md"
            formal_target.parent.mkdir(parents=True, exist_ok=True)
            formal_target.write_text("existing formal target", encoding="utf-8")
            existing_formal = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
                project_root,
                self._ready_preflight(content + "changed\n"),
            )

            self.assertEqual(missing_candidate["status"], "blocked_by_candidate_promotion_contract")
            self.assertIn("candidate_target_missing:formal_manuscript_sources", missing_candidate["blocking_reasons"])
            self.assertEqual(changed_candidate["status"], "blocked_by_candidate_promotion_contract")
            self.assertIn("candidate_bytes_mismatch:formal_manuscript_sources", changed_candidate["blocking_reasons"])
            self.assertIn("candidate_sha256_mismatch:formal_manuscript_sources", changed_candidate["blocking_reasons"])
            self.assertEqual(existing_formal["status"], "blocked_by_candidate_promotion_contract")
            self.assertIn("formal_target_already_exists:formal_manuscript_sources", existing_formal["blocking_reasons"])

    def test_bdd_p7v_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 3：CLI 默认读取当前 blocked P7-U，继续不提升正式成果。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root
                / "Results/json/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json",
                self._blocked_preflight(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_candidate_promotion_execute.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_candidate_promotion_execution_preflight", result.stdout)
            self.assertIn("candidate_targets_promoted=false", result.stdout)
            self.assertTrue(
                (
                    project_root / "Results/json/auto_mode_formal_target_adapter_candidate_promotion_execute.json"
                ).exists()
            )
            self.assertTrue(
                (project_root / "Reviews/auto_mode_formal_target_adapter_candidate_promotion_execute.md").exists()
            )
            self.assertFalse((project_root / "Submissions/formal_package/manuscript/paper.md").exists())
            self.assertFalse(
                (
                    project_root / "state/product/auto_mode_formal_target_adapter_candidate_promotion_execute.json"
                ).exists()
            )

    def _ready_preflight(self, content: str) -> dict:
        encoded = content.encode("utf-8")
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_verified_candidate_promotion_execution_review",
            "can_request_verified_candidate_promotion_execution": True,
            "requires_explicit_promotion_execute_command": True,
            "candidate_targets_promoted": False,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "promotion_execution_plan": [
                {
                    "execution_id": "verified_candidate_promotion_execution::01::formal_manuscript_sources",
                    "promotion_id": "verified_candidate_promotion::01::formal_manuscript_sources",
                    "operation_id": "adapter_materialization::01::formal_manuscript_sources",
                    "writeback_target_group": "formal_manuscript_sources",
                    "candidate_path": "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md",
                    "candidate_bytes": len(encoded),
                    "candidate_sha256": hashlib.sha256(encoded).hexdigest(),
                    "formal_target_path": "Submissions/formal_package/manuscript/paper.md",
                    "execution_status": "pending_explicit_promotion_execute_command",
                    "requires_explicit_promotion_execute_command": True,
                    "promoted_by_this_command": False,
                    "this_command_wrote_formal_state": False,
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_preflight(self) -> dict:
        preflight = self._ready_preflight("# Paper\n\nVerified candidate manuscript.\n")
        preflight["status"] = "blocked_by_candidate_promotion_approval"
        preflight["can_request_verified_candidate_promotion_execution"] = False
        preflight["requires_explicit_promotion_execute_command"] = False
        preflight["blocking_reasons"] = ["candidate_promotion_approval_not_effective"]
        preflight["promotion_execution_plan"] = []
        return preflight

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

    def _write_candidate(self, project_root: Path, content: str) -> None:
        candidate = project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(content, encoding="utf-8")

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

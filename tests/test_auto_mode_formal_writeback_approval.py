import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_writeback_approval import (
    build_auto_mode_formal_writeback_approval,
    write_auto_mode_formal_writeback_approval_outputs,
)


class AutoModeFormalWritebackApprovalTests(unittest.TestCase):
    """BDD: P7-K records explicit formal writeback approval without executing it."""

    def test_bdd_p7k_approve_ready_preflight_records_approval_without_writeback(self) -> None:
        """行为 1：ready preflight + approve 只授权下一道执行预检。"""
        report = build_auto_mode_formal_writeback_approval(
            self._ready_preflight(),
            decision="approve",
            reviewer="unit_test_reviewer",
            note="Approve formal writeback for the next execution preflight.",
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_writeback_approval.v1")
        self.assertEqual(report["status"], "approved_for_formal_writeback_execution_preflight")
        self.assertTrue(report["approved"])
        self.assertTrue(report["formal_writeback_allowed"])
        self.assertTrue(report["can_enter_formal_writeback_execution_preflight"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        self.assertEqual(report["approval"]["decision"], "approve")
        categories = {item["category"] for item in report["approved_scope"]}
        self.assertEqual(
            categories,
            {
                "manuscript",
                "bibliography",
                "method_review",
                "statistical_results",
                "reproducibility",
                "package_artifacts",
            },
        )
        for item in report["approved_scope"]:
            self.assertEqual(item["approval_status"], "approved_for_formal_writeback_execution_preflight")
            self.assertFalse(item["this_command_wrote_formal_state"])

    def test_bdd_p7k_defer_waits_without_approving_writeback(self) -> None:
        """行为 2：defer 不允许进入实际写回预检。"""
        report = build_auto_mode_formal_writeback_approval(
            self._ready_preflight(),
            decision="defer",
        )

        self.assertEqual(report["status"], "waiting_for_human_formal_writeback_approval")
        self.assertFalse(report["approved"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertFalse(report["can_enter_formal_writeback_execution_preflight"])
        self.assertEqual(report["approved_scope"], [])

    def test_bdd_p7k_blocks_when_promotion_preflight_is_not_ready(self) -> None:
        """行为 3：P7-J preflight 未 ready 时不能靠 approve 绕过。"""
        report = build_auto_mode_formal_writeback_approval(
            self._blocked_preflight(),
            decision="approve",
            reviewer="unit_test_reviewer",
            note="Attempted approval should not bypass blocked preflight.",
        )

        self.assertEqual(report["status"], "blocked_by_formal_promotion_preflight")
        self.assertFalse(report["approved"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertIn("formal_promotion_preflight_not_ready", report["blocking_reasons"])
        self.assertIn("final_review_decision_not_approved_for_preflight", report["source_preflight"]["blocking_reasons"])

    def test_bdd_p7k_approve_requires_reviewer_and_note(self) -> None:
        """行为 4：approve 缺 reviewer/note 时阻断。"""
        report = build_auto_mode_formal_writeback_approval(
            self._ready_preflight(),
            decision="approve",
            reviewer="",
            note="",
        )

        self.assertEqual(report["status"], "blocked_by_formal_writeback_approval_metadata")
        self.assertFalse(report["approved"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("approval_note_required", report["blocking_reasons"])

    def test_bdd_p7k_revise_and_reject_do_not_approve_writeback(self) -> None:
        """行为 5：revise/reject 只记录路线，不启用写回。"""
        revise_report = build_auto_mode_formal_writeback_approval(
            self._ready_preflight(),
            decision="revise",
            reviewer="unit_test_reviewer",
            note="Needs another paper package revision.",
        )
        reject_report = build_auto_mode_formal_writeback_approval(
            self._ready_preflight(),
            decision="reject",
            reviewer="unit_test_reviewer",
            note="Do not promote this package.",
        )

        self.assertEqual(revise_report["status"], "formal_writeback_needs_revision")
        self.assertEqual(reject_report["status"], "formal_writeback_rejected")
        self.assertFalse(revise_report["formal_writeback_allowed"])
        self.assertFalse(reject_report["formal_writeback_allowed"])
        self.assertFalse(revise_report["can_enter_formal_writeback_execution_preflight"])
        self.assertFalse(reject_report["can_enter_formal_writeback_execution_preflight"])

    def test_bdd_p7k_writes_json_and_markdown_without_formal_state(self) -> None:
        """行为 6：只写 approval JSON/Markdown，不写正式层。"""
        report = build_auto_mode_formal_writeback_approval(
            self._ready_preflight(),
            decision="approve",
            reviewer="unit_test_reviewer",
            note="Approve formal writeback for the next execution preflight.",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path = write_auto_mode_formal_writeback_approval_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIn("Auto Mode Formal Writeback Approval", review_path.read_text(encoding="utf-8"))
            self.assertFalse((project_root / "state/product/auto_mode_formal_writeback_approval.json").exists())
            self.assertFalse((project_root / "Manuscripts/sections/introduction.md").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())

    def test_bdd_p7k_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 7：CLI 默认读取当前 blocked preflight，继续禁止正式写回。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_promotion_preflight.json",
                self._blocked_preflight(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_writeback_approval.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_formal_promotion_preflight", result.stdout)
            self.assertIn("formal_writeback_allowed=false", result.stdout)
            self.assertIn("this_command_wrote_formal_state=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_writeback_approval.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_writeback_approval.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_writeback_approval.json").exists())

    def _ready_preflight(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_promotion_preflight.v1",
            "status": "ready_for_formal_writeback_approval",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "can_request_formal_writeback_approval": True,
            "requires_separate_formal_writeback_approval": True,
            "formal_writeback_allowed": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "promotion_scope": [
                self._scope_item("manuscript"),
                self._scope_item("bibliography"),
                self._scope_item("method_review"),
                self._scope_item("statistical_results"),
                self._scope_item("reproducibility"),
                self._scope_item("package_artifacts"),
            ],
            "approval_contract": {
                "ready_for_formal_writeback_approval": True,
                "required_next_decision": "human_approve_auto_mode_formal_writeback",
                "approval_record_path": "Results/json/auto_mode_formal_writeback_approval.json",
                "approval_review_path": "Reviews/auto_mode_formal_writeback_approval.md",
            },
            "boundary_flags": {
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
            },
        }

    def _blocked_preflight(self) -> dict:
        preflight = self._ready_preflight()
        preflight["status"] = "blocked_by_final_review_decision"
        preflight["can_request_formal_writeback_approval"] = False
        preflight["blocking_reasons"] = [
            "final_review_decision_not_approved_for_preflight",
            "final_review_decision_not_approve",
        ]
        preflight["promotion_scope"] = []
        preflight["approval_contract"]["ready_for_formal_writeback_approval"] = False
        return preflight

    def _scope_item(self, category: str) -> dict:
        return {
            "category": category,
            "label": category.replace("_", " ").title(),
            "evidence_refs": [{"target": f"{category}.md", "kind": "unit_test"}],
            "approval_status": "pending_formal_writeback_approval",
            "requires_human_confirmation": True,
            "can_write_formal_state": False,
            "next_gates": ["formal_writeback_execution_preflight"],
        }

    def _source_paths(self) -> dict:
        return {
            "formal_promotion_preflight": "Results/json/auto_mode_formal_promotion_preflight.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

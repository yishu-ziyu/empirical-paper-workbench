import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_revision_queue_approval import (
    build_revision_queue_approval,
    write_revision_queue_approval_outputs,
)


class CgssRevisionQueueApprovalTests(unittest.TestCase):
    """BDD: human decisions are recorded before CGSS revision queues can become work orders."""

    def test_bdd_61_defer_records_pending_decision_without_approved_queue(self) -> None:
        record = build_revision_queue_approval(
            self._pending_queue(),
            decision="defer",
            reviewer="",
            note="",
        )

        self.assertEqual(record["schema_version"], "p6.cgss_revision_queue_approval.v1")
        self.assertEqual(record["status"], "pending_human_revision_queue_decision")
        self.assertEqual(record["decision"], "defer")
        self.assertFalse(record["approved"])
        self.assertFalse(record["formal_writeback_allowed"])
        self.assertFalse(record["can_write_product_state"])
        self.assertEqual(record["approved_queue"], {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path, approved_queue_path = write_revision_queue_approval_outputs(
                Path(tmpdir),
                record,
                Path("Results/json/cgss_social_capital_happiness_revision_queue_approval.json"),
                Path("Reviews/cgss_social_capital_happiness_revision_queue_approval.md"),
                Path("Results/json/cgss_social_capital_happiness_revision_task_queue_approved.json"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIsNone(approved_queue_path)
            self.assertFalse((Path(tmpdir) / "Results/json/cgss_social_capital_happiness_revision_task_queue_approved.json").exists())
            self.assertFalse((Path(tmpdir) / "state/product/agent_task_queue.json").exists())

    def test_bdd_61_approve_requires_reviewer_and_note(self) -> None:
        record = build_revision_queue_approval(
            self._pending_queue(),
            decision="approve",
            reviewer="",
            note="",
        )

        self.assertEqual(record["status"], "blocked_missing_human_approval_metadata")
        self.assertFalse(record["approved"])
        self.assertIn("reviewer_required", record["blocking_reasons"])
        self.assertIn("approval_note_required", record["blocking_reasons"])
        self.assertEqual(record["approved_queue"], {})

    def test_bdd_61_approve_creates_approved_queue_sidecar_only(self) -> None:
        record = build_revision_queue_approval(
            self._pending_queue(),
            decision="approve",
            reviewer="mahaoxuan",
            note="批准 8 条草案层修订任务进入 Agent 工单。",
        )

        self.assertEqual(record["status"], "revision_queue_approved_for_agent_work_orders")
        self.assertTrue(record["approved"])
        self.assertEqual(record["approved_queue"]["status"], "approved_for_agent_work_orders")
        self.assertTrue(record["approved_queue"]["promotion"]["allowed"])
        self.assertEqual(record["approved_queue"]["human_approval"]["decision"], "human_approve_cgss_revision_task_queue")
        self.assertFalse(record["approved_queue"]["formal_writeback_allowed"])

        with tempfile.TemporaryDirectory() as tmpdir:
            _, _, approved_queue_path = write_revision_queue_approval_outputs(
                Path(tmpdir),
                record,
                Path("Results/json/cgss_social_capital_happiness_revision_queue_approval.json"),
                Path("Reviews/cgss_social_capital_happiness_revision_queue_approval.md"),
                Path("Results/json/cgss_social_capital_happiness_revision_task_queue_approved.json"),
            )

            self.assertIsNotNone(approved_queue_path)
            payload = json.loads(approved_queue_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "approved_for_agent_work_orders")
            self.assertEqual(payload["human_approval"]["approved_by"], "mahaoxuan")
            self.assertFalse((Path(tmpdir) / "state/product/agent_task_queue.json").exists())

    def test_bdd_61_revise_and_reject_do_not_create_approved_queue(self) -> None:
        for decision in ("revise", "reject"):
            with self.subTest(decision=decision):
                record = build_revision_queue_approval(
                    self._pending_queue(),
                    decision=decision,
                    reviewer="mahaoxuan",
                    note="需要先调整任务描述。",
                )

                self.assertFalse(record["approved"])
                self.assertEqual(record["approved_queue"], {})
                self.assertIn(record["status"], {"revision_queue_needs_changes", "revision_queue_rejected"})
                self.assertFalse(record["promotion"]["allowed"])

    def test_bdd_61_cli_defaults_to_defer_without_product_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(project_root / "Results/json/queue.json", self._pending_queue())

            result = subprocess.run(
                [
                    "python3",
                    "Program/cgss_revision_queue_approval.py",
                    "--project-root",
                    str(project_root),
                    "--queue",
                    "Results/json/queue.json",
                    "--output-result",
                    "Results/json/cgss_social_capital_happiness_revision_queue_approval.json",
                    "--output-review",
                    "Reviews/cgss_social_capital_happiness_revision_queue_approval.md",
                    "--output-approved-queue",
                    "Results/json/cgss_social_capital_happiness_revision_task_queue_approved.json",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=pending_human_revision_queue_decision", result.stdout)
            self.assertIn("approved=false", result.stdout)
            self.assertIn("approved_queue=none", result.stdout)
            self.assertTrue((project_root / "Reviews/cgss_social_capital_happiness_revision_queue_approval.md").exists())
            self.assertFalse((project_root / "Results/json/cgss_social_capital_happiness_revision_task_queue_approved.json").exists())
            self.assertFalse((project_root / "state/product/agent_task_queue.json").exists())

    def _pending_queue(self) -> dict:
        return {
            "schema_version": "p6.cgss_revision_task_queue.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "needs_human_revision_queue_approval",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_cgss_revision_task_queue",
            },
            "agent_task_queue": [
                {
                    "task_id": "literature.verify_open_seed_sources",
                    "agent": "LiteratureAgent",
                    "title": "核验未批准文献与 CGSS 官方来源",
                    "objective": "补齐访问日期、DOI/Zotero 元数据和中文文献人工核验结论。",
                    "evidence_inputs": ["literature_seed_package.seed_sources"],
                    "output_target": "Reviews/agent_packets/literatureagent/cgss_source_verification.md",
                    "status": "queued_for_human_approved_revision",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                }
            ],
            "agent_packets": [],
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

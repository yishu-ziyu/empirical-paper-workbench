import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from Program.workbench.cgss_revision_work_orders import (
    build_cgss_revision_work_orders,
    write_revision_work_order_outputs,
)


class CgssRevisionWorkOrdersTests(unittest.TestCase):
    """BDD: human approval gates CGSS revision queue expansion into agent work orders."""

    def test_bdd_60_pending_queue_blocks_without_agent_packet_files(self) -> None:
        queue = self._pending_queue()
        manifest = build_cgss_revision_work_orders(queue)

        self.assertEqual(manifest["schema_version"], "p6.cgss_revision_work_orders.v1")
        self.assertEqual(manifest["status"], "blocked_revision_queue_not_approved")
        self.assertEqual(manifest["work_orders"], [])
        self.assertFalse(manifest["formal_writeback_allowed"])
        self.assertFalse(manifest["can_write_product_state"])
        self.assertIn("human_approve_cgss_revision_task_queue", manifest["blocking_reasons"])

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path, written_files = write_revision_work_order_outputs(
                Path(tmpdir),
                manifest,
                Path("Results/json/cgss_social_capital_happiness_revision_work_orders.json"),
                Path("Reviews/cgss_social_capital_happiness_revision_work_orders.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(written_files, [])
            self.assertFalse((Path(tmpdir) / "Reviews/agent_packets/literatureagent/cgss_source_verification.md").exists())
            self.assertFalse((Path(tmpdir) / "state/product/agent_task_queue.json").exists())

    def test_bdd_60_approved_queue_maps_tasks_to_draft_work_orders(self) -> None:
        manifest = build_cgss_revision_work_orders(self._approved_queue())

        self.assertEqual(manifest["status"], "ready_for_agent_draft_execution")
        self.assertEqual(len(manifest["work_orders"]), 3)
        self.assertTrue(manifest["draft_layer_only"])
        self.assertFalse(manifest["formal_writeback_allowed"])
        self.assertFalse(manifest["can_write_product_state"])

        first = manifest["work_orders"][0]
        self.assertEqual(first["id"], "literature.verify_open_seed_sources")
        self.assertEqual(first["task_id"], "literature.verify_open_seed_sources")
        self.assertEqual(first["agent"], "LiteratureAgent")
        self.assertEqual(first["draft_output_path"], "Reviews/agent_packets/literatureagent/cgss_source_verification.md")
        self.assertEqual(first["inputs"], ["literature_seed_package.seed_sources"])
        self.assertTrue(first["requires_human_confirmation"])
        self.assertFalse(first["formal_writeback_allowed"])
        self.assertFalse(first["can_write_product_state"])
        self.assertIn("state/product", first["write_boundary"]["must_not_write"])

    def test_bdd_60_approved_queue_writes_agent_work_order_files(self) -> None:
        manifest = build_cgss_revision_work_orders(self._approved_queue())

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_path, review_path, written_files = write_revision_work_order_outputs(
                project_root,
                manifest,
                Path("Results/json/cgss_social_capital_happiness_revision_work_orders.json"),
                Path("Reviews/cgss_social_capital_happiness_revision_work_orders.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(len(written_files), 3)
            source_file = project_root / "Reviews/agent_packets/literatureagent/cgss_source_verification.md"
            self.assertTrue(source_file.exists())
            text = source_file.read_text(encoding="utf-8")
            self.assertIn("CGSS Agent 草案工单", text)
            self.assertIn("literature.verify_open_seed_sources", text)
            self.assertIn("formal_writeback_allowed: false", text)
            self.assertFalse((project_root / "state/product/agent_task_queue.json").exists())

    def test_bdd_60_cli_blocks_real_pending_queue_without_agent_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(project_root / "Results/json/queue.json", self._pending_queue())

            result = subprocess.run(
                [
                    "python3",
                    "Program/cgss_revision_work_orders.py",
                    "--project-root",
                    str(project_root),
                    "--queue",
                    "Results/json/queue.json",
                    "--output-result",
                    "Results/json/cgss_social_capital_happiness_revision_work_orders.json",
                    "--output-review",
                    "Reviews/cgss_social_capital_happiness_revision_work_orders.md",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_revision_queue_not_approved", result.stdout)
            self.assertIn("written_work_orders=0", result.stdout)
            self.assertTrue((project_root / "Results/json/cgss_social_capital_happiness_revision_work_orders.json").exists())
            self.assertTrue((project_root / "Reviews/cgss_social_capital_happiness_revision_work_orders.md").exists())
            self.assertFalse((project_root / "Reviews/agent_packets/literatureagent/cgss_source_verification.md").exists())
            self.assertFalse((project_root / "state/product/agent_task_queue.json").exists())

    def _approved_queue(self) -> dict:
        queue = deepcopy(self._pending_queue())
        queue["status"] = "approved_for_agent_work_orders"
        queue["human_approval"] = {
            "status": "approved",
            "decision": "human_approve_cgss_revision_task_queue",
            "approved_by": "unit_test_reviewer",
        }
        queue["promotion"]["allowed"] = True
        return queue

    def _pending_queue(self) -> dict:
        return {
            "schema_version": "p6.cgss_revision_task_queue.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "needs_human_revision_queue_approval",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "source_artifacts": {
                "literature_seed_package": {"path": "Results/json/seed.json"},
                "method_structure_gate_packet": {"path": "Results/json/method.json"},
            },
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
                },
                {
                    "task_id": "method.review_blocked_causal_methods",
                    "agent": "MethodAgent",
                    "title": "复核暂不进入的因果方法族",
                    "objective": "检查 DID、IV、RDD、PSM、DML 等方法族的阻断理由。",
                    "evidence_inputs": ["method_structure_gate_packet.method_claim_gates.blocked_method_families"],
                    "output_target": "Reviews/agent_packets/methodagent/cgss_blocked_method_review.md",
                    "status": "queued_for_human_approved_revision",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                },
                {
                    "task_id": "reviewer.prepare_human_approval_checklist",
                    "agent": "ReviewerAgent",
                    "title": "生成人工批准检查清单",
                    "objective": "把文献、方法和写作任务压缩成人工审阅前必须确认的清单。",
                    "evidence_inputs": ["revision_task_queue.agent_packets"],
                    "output_target": "Reviews/agent_packets/revieweragent/cgss_human_approval_checklist.md",
                    "status": "queued_for_human_approved_revision",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                },
            ],
            "agent_packets": [
                {
                    "agent": "LiteratureAgent",
                    "write_boundary": {
                        "draft_layer_only": True,
                        "formal_writeback_allowed": False,
                        "must_not_write": ["Manuscripts/sections", "state/product"],
                    },
                },
                {
                    "agent": "MethodAgent",
                    "write_boundary": {
                        "draft_layer_only": True,
                        "formal_writeback_allowed": False,
                        "must_not_write": ["DesignSpec", "RunPlan", "state/product"],
                    },
                },
                {
                    "agent": "ReviewerAgent",
                    "write_boundary": {
                        "draft_layer_only": True,
                        "formal_writeback_allowed": False,
                        "must_not_write": ["state/product/agent_task_queue.json", "formal manuscript"],
                    },
                },
            ],
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

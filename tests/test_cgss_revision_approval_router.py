import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_revision_approval_router import (
    build_cgss_revision_approval_route,
    write_cgss_revision_approval_route_outputs,
)


class CgssRevisionApprovalRouterTests(unittest.TestCase):
    """BDD: human approval records route CGSS revision work without replacing human approval."""

    def test_bdd_router_defer_waits_for_human_confirmation_without_writes(self) -> None:
        record = build_cgss_revision_approval_route(self._approval_record("defer"))

        self.assertEqual(record["schema_version"], "p6.cgss_revision_approval_router.v1")
        self.assertEqual(record["status"], "waiting_for_human_revision_queue_decision")
        self.assertEqual(record["route"], "wait_for_human_confirmation")
        self.assertFalse(record["approved"])
        self.assertFalse(record["agent_work_orders_generated"])
        self.assertFalse(record["formal_writeback_allowed"])
        self.assertFalse(record["can_write_product_state"])

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            review_path, work_order_paths = write_cgss_revision_approval_route_outputs(
                project_root,
                record,
                Path("Reviews/cgss_social_capital_happiness_revision_approval_router.md"),
            )

            self.assertTrue(review_path.exists())
            self.assertTrue((project_root / "Results/json/cgss_social_capital_happiness_revision_approval_router.json").exists())
            self.assertEqual(work_order_paths, [])
            self.assertFalse((project_root / "Reviews/agent_packets/literatureagent/cgss_source_verification.md").exists())
            self.assertFalse((project_root / "Manuscripts/sections/introduction.md").exists())
            self.assertFalse((project_root / "state/product/agent_task_queue.json").exists())

    def test_bdd_router_revise_routes_to_queue_update_without_work_orders(self) -> None:
        record = build_cgss_revision_approval_route(self._approval_record("revise"))

        self.assertEqual(record["status"], "revision_queue_update_required")
        self.assertEqual(record["route"], "revision_queue_update")
        self.assertFalse(record["agent_work_orders_generated"])
        self.assertIn("revise_cgss_revision_task_queue", record["next_actions"])

    def test_bdd_router_reject_routes_to_rebuild_or_stop_without_work_orders(self) -> None:
        record = build_cgss_revision_approval_route(self._approval_record("reject"))

        self.assertEqual(record["status"], "revision_queue_rebuild_or_stop_required")
        self.assertEqual(record["route"], "rebuild_or_stop")
        self.assertFalse(record["agent_work_orders_generated"])
        self.assertIn("rebuild_or_stop_cgss_revision_task_queue", record["next_actions"])

    def test_bdd_router_approve_with_approved_queue_writes_draft_work_orders_only(self) -> None:
        record = build_cgss_revision_approval_route(self._approval_record("approve", approved_queue=True))

        self.assertEqual(record["status"], "approved_queue_routed_to_agent_work_orders")
        self.assertEqual(record["route"], "agent_draft_work_orders")
        self.assertTrue(record["approved"])
        self.assertTrue(record["agent_work_orders_generated"])
        self.assertEqual(record["work_order_manifest"]["status"], "ready_for_agent_draft_execution")
        self.assertFalse(record["formal_writeback_allowed"])
        self.assertFalse(record["can_write_product_state"])

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            review_path, work_order_paths = write_cgss_revision_approval_route_outputs(
                project_root,
                record,
                Path("Reviews/cgss_social_capital_happiness_revision_approval_router.md"),
            )

            self.assertTrue(review_path.exists())
            route_json = project_root / "Results/json/cgss_social_capital_happiness_revision_approval_router.json"
            self.assertTrue(route_json.exists())
            self.assertFalse(json.loads(route_json.read_text(encoding="utf-8"))["formal_writeback_allowed"])
            self.assertEqual(len(work_order_paths), 1)
            self.assertTrue((project_root / "Reviews/agent_packets/literatureagent/cgss_source_verification.md").exists())
            self.assertTrue((project_root / "Results/json/cgss_social_capital_happiness_revision_work_orders.json").exists())
            self.assertTrue((project_root / "Reviews/cgss_social_capital_happiness_revision_work_orders.md").exists())
            self.assertFalse((project_root / "Manuscripts/sections/introduction.md").exists())
            self.assertFalse((project_root / "state/product/agent_task_queue.json").exists())

    def test_bdd_router_cli_defaults_to_real_approval_json_and_router_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/cgss_social_capital_happiness_revision_queue_approval.json",
                self._approval_record("defer"),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/cgss_revision_approval_router.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=waiting_for_human_revision_queue_decision", result.stdout)
            self.assertIn("route=wait_for_human_confirmation", result.stdout)
            self.assertIn("work_orders=0", result.stdout)
            self.assertTrue((project_root / "Results/json/cgss_social_capital_happiness_revision_approval_router.json").exists())
            self.assertTrue((project_root / "Reviews/cgss_social_capital_happiness_revision_approval_router.md").exists())
            self.assertFalse((project_root / "Reviews/agent_packets/literatureagent/cgss_source_verification.md").exists())
            self.assertFalse((project_root / "state/product/agent_task_queue.json").exists())

    def _approval_record(self, decision: str, approved_queue: bool = False) -> dict:
        record = {
            "schema_version": "p6.cgss_revision_queue_approval.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "decision": decision,
            "status": {
                "defer": "pending_human_revision_queue_decision",
                "revise": "revision_queue_needs_changes",
                "reject": "revision_queue_rejected",
                "approve": "revision_queue_approved_for_agent_work_orders",
            }[decision],
            "approved": decision == "approve",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "can_write_product_state": False,
            "approved_queue": {},
        }
        if approved_queue:
            record["approved_queue"] = self._approved_queue()
        return record

    def _approved_queue(self) -> dict:
        return {
            "schema_version": "p6.cgss_revision_task_queue.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "approved_for_agent_work_orders",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "can_write_product_state": False,
            "promotion": {
                "allowed": True,
                "required_decision": "human_review_agent_work_order_outputs",
            },
            "human_approval": {
                "status": "approved",
                "decision": "human_approve_cgss_revision_task_queue",
                "approved_by": "unit_test_reviewer",
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

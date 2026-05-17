from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class AgentTaskDispatchAuditApiTests(unittest.TestCase):
    """BDD: Agent Task Queue 每个任务必须经过人工派工审阅，不能默认执行。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="agent-task-dispatch-audit-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "dispatch-audit",
                "title": "Dispatch Audit Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self._write_confirmed_research_states()
        self._write_supervisor_plan()
        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")
        self.assertEqual(created.status_code, 201, msg=created.text)

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_queue_item_is_blocked_until_human_dispatch_review(self) -> None:
        """行为 1：新建队列中的任务不能绕过人工派工审阅。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 200, msg=response.text)
        task = response.json()["agent_task_queue"]["tasks"][0]
        self.assertEqual(task["status"], "queued")
        self.assertFalse(task["can_execute"])
        self.assertEqual(task["next_action"], "dispatch_review_required")
        self.assertEqual(
            task["dispatch_readiness"]["blockers"][0]["code"],
            "dispatch_review_required",
        )
        self.assertNotIn("execution_backend", task)
        self.assertNotIn("dispatched_at", task)

    def test_bdd_2_user_approves_queue_item_for_dispatch(self) -> None:
        """行为 2：批准派工会写入审阅者、备注、时间和 local_file 证据。"""
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/dispatch-review",
            json={"action": "approve", "note": "数据画像任务可以执行"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        task = response.json()["agent_task_queue"]["tasks"][0]
        self.assertEqual(task["status"], "reviewed_for_dispatch")
        self.assertFalse(task["can_execute"])
        self.assertEqual(task["next_action"], "select_execution_backend")
        self.assertEqual(task["dispatch_readiness"]["blockers"], [])
        self.assertEqual(task["dispatch_review"]["action"], "approve")
        self.assertEqual(task["dispatch_review"]["reviewer"], "human")
        self.assertEqual(task["dispatch_review"]["note"], "数据画像任务可以执行")
        self.assertEqual(task["dispatch_review"]["evidence_level"], "local_file")
        self.assertTrue(task["dispatch_review"]["reviewed_at"])
        self.assertEqual(task["audit_log"][-1]["event"], "dispatch_review_recorded")

        saved = json.loads(
            (self.project_root / "state" / "product" / "agent_task_queue.json").read_text(encoding="utf-8")
        )
        self.assertEqual(saved["tasks"][0]["status"], "reviewed_for_dispatch")
        self.assertEqual(saved["tasks"][0]["dispatch_review"]["note"], "数据画像任务可以执行")

    def test_bdd_3_user_rejects_queue_item_and_blocks_execution(self) -> None:
        """行为 3：拒绝派工会把任务变成 blocked，并把阻断原因放在摘要层。"""
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_02/dispatch-review",
            json={"action": "reject", "note": "识别策略不完整"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        task = response.json()["agent_task_queue"]["tasks"][1]
        self.assertEqual(task["status"], "blocked")
        self.assertFalse(task["can_execute"])
        self.assertEqual(task["next_action"], "revise_dispatch_task")
        self.assertEqual(task["dispatch_review"]["action"], "reject")
        self.assertEqual(task["dispatch_review"]["note"], "识别策略不完整")
        self.assertEqual(task["dispatch_readiness"]["blockers"][0]["code"], "dispatch_rejected")
        self.assertEqual(task["blockers"][0]["code"], "dispatch_rejected")

    def test_bdd_4_dispatch_audit_does_not_mutate_research_state_files(self) -> None:
        """行为 4：派工审阅只写 queue 文件，不改正式研究状态。"""
        protected_paths = [
            self.project_root / "state" / "product" / "research_question.json",
            self.project_root / "state" / "product" / "variable_roles.json",
            self.project_root / "state" / "product" / "design_spec.json",
            self.project_root / "state" / "product" / "run_plan.json",
            self.project_root / "state" / "product" / "supervisor_plan.json",
        ]
        before = {path.name: path.read_text(encoding="utf-8") for path in protected_paths}

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/dispatch-review",
            json={"action": "approve", "note": "只批准派工，不改研究设定"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        after = {path.name: path.read_text(encoding="utf-8") for path in protected_paths}
        self.assertEqual(before, after)

    def _write_confirmed_research_states(self) -> None:
        state_root = self.project_root / "state" / "product"
        state_root.mkdir(parents=True, exist_ok=True)
        states = {
            "research_question.json": {"status": "confirmed", "question": "培训是否影响工资？"},
            "variable_roles.json": {"status": "approved", "roles": {"outcome": ["wage"], "treatment": ["trained"]}},
            "design_spec.json": {"status": "approved", "model": {"estimator": "ols"}},
            "run_plan.json": {"status": "approved", "tasks": [{"id": "baseline_ols"}]},
        }
        for filename, payload in states.items():
            (state_root / filename).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_supervisor_plan(self) -> None:
        path = self.project_root / "state" / "product" / "supervisor_plan.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        plan = {
            "id": "supervisor_plan",
            "version": 1,
            "status": "approved",
            "can_dispatch": True,
            "evidence_level": "local_execution",
            "objective": "拆成可审阅的子 Agent 任务",
            "path": "state/product/supervisor_plan.json",
            "input_research_question": {"question": "培训是否影响工资？", "version": 1},
            "input_evidence": {
                "research_question_path": "state/product/research_question.json",
                "variable_role_set_path": "state/product/variable_roles.json",
                "design_spec_path": "state/product/design_spec.json",
                "run_plan_path": "state/product/run_plan.json",
            },
            "subagent_dispatch": [
                {"agent_id": "data_profile", "role": "Data Agent", "task": "读取真实数据字段画像"},
                {"agent_id": "design_review", "role": "Design Agent", "task": "复核识别策略完整性"},
            ],
            "evidence_requirements": [
                {"id": "dataset_profile", "requirement": "保留字段画像", "evidence_level": "local_file"}
            ],
            "risks": [{"id": "heuristic_roles", "description": "字段候选不能直接写入论文"}],
        }
        path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: dispatch-audit\n  title: Dispatch Audit Project\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained\n10,1\n12,0\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class AgentTaskDispatchAuditFrontendTests(unittest.TestCase):
    """BDD: 前端必须把派工审阅做成摘要层动作，细节默认折叠。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_frontend_exposes_one_dispatch_review_area_per_task(self) -> None:
        """行为 5：任务卡片摘要层必须显示派工审阅区，细节仍默认折叠。"""
        self.assertIn("reviewDispatch", self.app_js)
        self.assertIn("handleReviewAgentTaskDispatch", self.app_js)
        self.assertIn("data-dispatch-review-action", self.app_js)
        self.assertIn("派工审阅", self.app_js)
        self.assertIn("批准派工", self.app_js)
        self.assertIn("要求修改", self.app_js)
        self.assertIn("阻断任务", self.app_js)
        self.assertIn("dispatch_review_required", self.app_js)
        self.assertIn("agent-task-dispatch-review", self.styles_css)
        self.assertIn("agent-task-dispatch-actions", self.styles_css)
        self.assertNotIn("agent-task-details\" open", self.app_js)


if __name__ == "__main__":
    unittest.main()

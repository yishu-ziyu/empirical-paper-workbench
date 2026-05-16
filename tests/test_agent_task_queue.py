from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class AgentTaskQueueApiTests(unittest.TestCase):
    """BDD: Agent Task Queue 只能从 approved SupervisorPlan 派生，且默认摘要优先。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="agent-task-queue-"))
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
                "slug": "agent-task-queue",
                "title": "Agent Task Queue Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self._approve_research_states()

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_create_queue_requires_approved_supervisor_plan(self) -> None:
        """行为 1：没有 approved SupervisorPlan 时，不允许创建任务队列。"""
        missing = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(missing.status_code, 409, msg=missing.text)
        self.assertEqual(missing.json()["error"]["code"], "supervisor_plan_required")
        self.assertFalse((self.project_root / "state" / "product" / "agent_task_queue.json").exists())

        self._write_supervisor_plan(status="needs_review", can_dispatch=False)

        blocked = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "supervisor_plan_not_approved")
        self.assertFalse((self.project_root / "state" / "product" / "agent_task_queue.json").exists())

    def test_bdd_2_approved_plan_persists_summary_first_agent_task_queue(self) -> None:
        """行为 2：approved SupervisorPlan 可以生成摘要优先的 Agent Task Queue。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True)

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        queue = response.json()["agent_task_queue"]
        self.assertEqual(queue["status"], "ready_for_dispatch")
        self.assertEqual(queue["evidence_level"], "local_file")
        self.assertEqual(queue["source_supervisor_plan"]["status"], "approved")
        self.assertEqual(queue["source_supervisor_plan"]["version"], 3)
        self.assertTrue(queue["ui_contract"]["summary_first"])
        self.assertTrue(queue["ui_contract"]["details_collapsed_by_default"])
        self.assertEqual(queue["summary"]["total_tasks"], 2)
        self.assertEqual(queue["summary"]["queued_count"], 2)
        self.assertEqual(queue["summary"]["blocked_count"], 0)
        self.assertEqual(queue["summary"]["owner_agents"], ["pipeline_data", "pipeline_execution"])
        self.assertEqual(queue["tasks"][0]["owner_agent"], "pipeline_data")
        self.assertEqual(queue["tasks"][0]["role"], "Data Agent")
        self.assertEqual(queue["tasks"][0]["title"], "检查数据和变量角色")
        self.assertEqual(queue["tasks"][0]["status"], "queued")
        self.assertEqual(queue["tasks"][0]["blockers"], [])
        self.assertIn("supervisor_plan", queue["tasks"][0]["input_evidence"])
        self.assertIn("output_requirements", queue["tasks"][0])
        self.assertIn("risk_flags", queue["tasks"][0])
        self.assertEqual(queue["tasks"][0]["audit_log"][0]["event"], "task_created_from_supervisor_plan")

        saved_path = self.project_root / "state" / "product" / "agent_task_queue.json"
        self.assertTrue(saved_path.exists())
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["summary"]["total_tasks"], 2)
        self.assertEqual(saved["path"], "state/product/agent_task_queue.json")

    def test_bdd_3_get_returns_persisted_queue_or_empty_blocked_state(self) -> None:
        """行为 3：GET API 必须跨 session 恢复队列，未创建时返回可解释空态。"""
        empty = self.client.get(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(empty.status_code, 200, msg=empty.text)
        self.assertEqual(empty.json()["agent_task_queue"]["status"], "empty")
        self.assertFalse(empty.json()["agent_task_queue"]["can_create"])
        self.assertEqual(empty.json()["agent_task_queue"]["blockers"][0]["code"], "supervisor_plan_required")

        self._write_supervisor_plan(status="approved", can_dispatch=True)
        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")
        self.assertEqual(created.status_code, 201, msg=created.text)

        restored = self.client.get(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(restored.status_code, 200, msg=restored.text)
        self.assertEqual(restored.json()["agent_task_queue"]["status"], "ready_for_dispatch")
        self.assertEqual(restored.json()["agent_task_queue"]["summary"]["total_tasks"], 2)

    def test_bdd_4_queue_creation_does_not_mutate_research_states_or_supervisor_plan(self) -> None:
        """行为 4：创建队列不能篡改已确认研究状态或已批准计划。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True)
        state_paths = [
            self.project_root / "state" / "product" / "research_question.json",
            self.project_root / "state" / "product" / "variable_roles.json",
            self.project_root / "state" / "product" / "design_spec.json",
            self.project_root / "state" / "product" / "run_plan.json",
            self.project_root / "state" / "product" / "supervisor_plan.json",
        ]
        before = {path.name: path.read_text(encoding="utf-8") for path in state_paths}

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        after = {path.name: path.read_text(encoding="utf-8") for path in state_paths}
        self.assertEqual(before, after)

    def test_bdd_7_empty_subagent_dispatch_blocks_queue_creation(self) -> None:
        """边界：approved plan 没有子 Agent 分工时，不能创建空派工队列。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True, subagent_dispatch=[])

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "subagent_dispatch_required")
        self.assertFalse((self.project_root / "state" / "product" / "agent_task_queue.json").exists())

    def _write_supervisor_plan(
        self,
        status: str,
        can_dispatch: bool,
        subagent_dispatch: list[dict] | None = None,
    ) -> None:
        path = self.project_root / "state" / "product" / "supervisor_plan.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        plan = {
            "id": "supervisor_plan",
            "version": 3,
            "status": status,
            "can_dispatch": can_dispatch,
            "evidence_level": "local_execution",
            "objective": "把 approved plan 拆成可审阅任务队列",
            "path": "state/product/supervisor_plan.json",
            "input_research_question": {
                "question": "培训是否影响工资？",
                "topic_session_id": "topic_session_v1",
                "version": 1,
            },
            "input_evidence": {
                "research_question_path": "state/product/research_question.json",
                "variable_role_set_path": "state/product/variable_roles.json",
                "design_spec_path": "state/product/design_spec.json",
                "run_plan_path": "state/product/run_plan.json",
            },
            "stage_plan": [
                {"stage": "数据与变量", "goal": "复核字段角色与样本口径", "status": "planned"},
                {"stage": "实证执行", "goal": "运行 OLS 并交叉验证 StatsPAI", "status": "planned"},
            ],
            "subagent_dispatch": subagent_dispatch
            if subagent_dispatch is not None
            else [
                {"agent_id": "pipeline_data", "role": "Data Agent", "task": "检查数据和变量角色"},
                {"agent_id": "pipeline_execution", "role": "Execution Agent", "task": "执行并验证模型"},
            ],
            "evidence_requirements": [
                {"id": "dataset_profile", "requirement": "保留字段画像和样本量", "evidence_level": "local_file"},
                {"id": "model_run", "requirement": "保留运行日志和回归结果", "evidence_level": "local_execution"},
            ],
            "risks": [
                {"id": "heuristic_roles", "level": "medium", "description": "变量角色候选不能直接进入论文"}
            ],
            "human_gates": [
                {"id": "review_supervisor_plan", "label": "人工确认 SupervisorPlan", "required": True}
            ],
        }
        path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    def _approve_research_states(self) -> None:
        question = self.client.put(
            f"/api/v1/projects/{self.project_id}/research-question/current",
            json={"question": "培训是否影响工资？", "source": "project_seed", "note": "选题已确认。"},
        )
        self.assertEqual(question.status_code, 200, msg=question.text)
        roles = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/analysis_sample.csv",
                "roles": {
                    "outcome": ["wage"],
                    "treatment": ["trained"],
                    "controls": ["edu", "experience"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "变量角色已确认。",
            },
        )
        self.assertEqual(roles.status_code, 200, msg=roles.text)
        design = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "培训是否影响工资？",
                "identification_strategy": {
                    "name": "baseline_ols",
                    "summary": "在已确认控制变量下估计培训对工资的相关关系。",
                    "assumptions": ["控制教育和经验后，处理变量外生。"],
                    "threats": ["遗漏变量偏误", "样本选择偏误"],
                },
                "model": {
                    "estimator": "ols",
                    "formula": "wage ~ trained + edu + experience",
                    "fixed_effects": [],
                    "cluster_by": [],
                    "sample_filter": "all",
                },
                "note": "研究设计已确认。",
            },
        )
        self.assertEqual(design.status_code, 200, msg=design.text)
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        run_plan = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={"tasks": draft["tasks"], "outputs": draft["outputs"], "note": "执行计划已确认。"},
        )
        self.assertEqual(run_plan.status_code, 200, msg=run_plan.text)

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: agent-task-queue\n  title: Agent Task Queue Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n12,0,14,5\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class AgentTaskQueueFrontendTests(unittest.TestCase):
    """BDD: Overview 必须把 Agent Task Queue 做成摘要优先的干净派工台。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_frontend_contains_summary_first_queue_surface(self) -> None:
        """行为 5：前端必须有摘要优先的 Agent Task Queue 面板。"""
        self.assertIn("agent-task-queue-panel", self.index_html)
        self.assertIn("agent-task-queue-body", self.index_html)
        self.assertIn("renderAgentTaskQueue", self.app_js)
        self.assertIn("agent-task-queue-summary", self.app_js)
        self.assertIn("任务总数", self.app_js)
        self.assertIn("负责人 Agent", self.app_js)
        self.assertIn("阻塞项", self.app_js)
        self.assertIn(".agent-task-queue-card", self.styles_css)

    def test_bdd_6_frontend_can_create_queue_only_as_explicit_action(self) -> None:
        """行为 6：未创建队列时，前端必须显示明确的人工创建按钮和安全边界。"""
        self.assertIn("v2api.agentTaskQueue.create", self.app_js)
        self.assertIn("handleCreateAgentTaskQueue", self.app_js)
        self.assertIn("data-agent-task-create-action", self.app_js)
        self.assertIn("创建 Agent 任务队列", self.app_js)
        self.assertIn("不会自动执行或改写研究状态", self.app_js)

    def test_bdd_8_task_details_are_progressively_disclosed(self) -> None:
        """行为 8：输入证据、输出要求、风险和审计日志必须默认折叠。"""
        self.assertIn("agent-task-progressive-disclosure", self.app_js)
        self.assertIn("查看任务详情", self.app_js)
        self.assertIn("输入证据", self.app_js)
        self.assertIn("输出要求", self.app_js)
        self.assertIn("审计日志", self.app_js)
        self.assertIn("details_collapsed_by_default", self.app_js)


if __name__ == "__main__":
    unittest.main()

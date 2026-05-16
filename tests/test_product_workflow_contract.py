from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ProductWorkflowContractTests(unittest.TestCase):
    """BDD: 产品必须围绕实证论文主流程，而不是围绕 run 日志面板。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="workflow-contract-"))
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
                "slug": "workflow-contract",
                "title": "Workflow Contract Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_home_next_action_is_variable_roles_before_run_selection(self) -> None:
        """行为 1：有数据但未确认变量角色时，首页主行动必须是确认变量角色。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/overview")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        contract = body["workflow_contract"]
        self.assertEqual(contract["next_action"]["id"], "confirm_variable_roles")
        self.assertEqual(contract["next_action"]["workspace"], "data-design")
        self.assertNotEqual(contract["next_action"]["id"], "select_run")

    def test_bdd_2_full_run_is_blocked_until_roles_design_and_run_plan_exist(self) -> None:
        """行为 2：变量角色、研究设计和 Run Plan 未确认前不能启动完整实证 run。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/overview")

        self.assertEqual(response.status_code, 200, msg=response.text)
        readiness = response.json()["workflow_contract"]["run_readiness"]
        self.assertFalse(readiness["can_start_full_run"])
        self.assertEqual(
            readiness["blockers"],
            ["variable_roles_unconfirmed", "design_unconfirmed", "run_plan_missing"],
        )

    def test_bdd_7_workflow_contract_declares_llm_supervisor_layer(self) -> None:
        """行为 7：工作流契约必须显式声明 LLM Supervisor，而不是只靠工程状态机推进。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/overview")

        self.assertEqual(response.status_code, 200, msg=response.text)
        intelligence = response.json()["workflow_contract"]["intelligence_layer"]
        self.assertEqual(intelligence["supervisor_agent_id"], "pipeline_supervisor")
        self.assertEqual(intelligence["provider"]["provider"], "local_codex")
        self.assertIn("available", intelligence["provider"])
        self.assertIn("execution_enabled", intelligence["provider"])
        self.assertIn(intelligence["status"], {"ready", "blocked"})
        self.assertEqual(intelligence["evidence_level"], "local_file")
        self.assertIn("dispatch_plan", intelligence)

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: workflow-contract\n  title: Workflow Contract Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class ProductWorkflowFrontendContractTests(unittest.TestCase):
    """BDD: 前端信息架构必须呈现 5 个工作区和下一步研究决策。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_3_primary_navigation_uses_five_product_workspaces(self) -> None:
        """行为 3：一阶导航必须是产品工作区，而不是七八个技术页面。"""
        for label in ("工作台首页", "数据与设计", "实证执行", "结果与草稿", "审阅与导出"):
            self.assertIn(label, self.index_html)
        self.assertIn("product-workspace-nav", self.index_html)

    def test_bdd_4_home_renders_next_decision_and_workflow_spine(self) -> None:
        """行为 4：首页必须显示下一步研究决策和产品主链路。"""
        self.assertIn("product-next-action", self.index_html)
        self.assertIn("workflow-spine", self.index_html)
        self.assertIn("renderWorkflowContract", self.app_js)
        self.assertIn("workflow_contract", self.app_js)
        self.assertIn("confirm_variable_roles", self.app_js)

    def test_bdd_5_data_workspace_routes_to_variable_role_confirmation_before_run(self) -> None:
        """行为 5：数据工作区主行动是确认变量角色，而不是直接启动 run。"""
        self.assertIn("variable-role-workflow-card", self.index_html)
        self.assertIn("检查并确认变量角色", self.app_js)
        self.assertIn("data-open-design-action", self.app_js)
        self.assertNotIn("用此数据启动试运行", self.app_js)

    def test_bdd_6_execution_workspace_starts_with_run_plan_preflight(self) -> None:
        """行为 6：执行工作区必须先显示 Run Plan 预检和阻塞项。"""
        self.assertIn("run-plan-preflight", self.index_html)
        self.assertIn("run-blockers", self.index_html)
        self.assertIn("renderExecutionPreflight", self.app_js)
        self.assertIn("can_start_full_run", self.app_js)
        self.assertIn("variable_roles_unconfirmed", self.app_js)

    def test_bdd_8_home_shows_llm_supervisor_readiness(self) -> None:
        """行为 8：首页必须展示本地大模型中控状态，而不是把 Agent 当静态装饰。"""
        self.assertIn("llm-supervisor-panel", self.index_html)
        self.assertIn("renderIntelligenceLayer", self.app_js)
        self.assertIn("intelligence_layer", self.app_js)
        for label in ("智能中控", "本地 Codex", "Supervisor", "派工计划"):
            self.assertIn(label, self.app_js + self.index_html)

    def test_bdd_9_llm_supervisor_details_are_progressively_disclosed(self) -> None:
        """行为 9：智能中控只在首屏展示决策摘要，Provider 与派工细节按需展开。"""
        self.assertIn("intelligence-progressive-disclosure", self.app_js)
        self.assertIn('class="progressive-disclosure llm-supervisor-details"', self.app_js)
        self.assertIn("查看中控详情", self.app_js)
        self.assertIn("disclosure-panel", self.app_js)
        self.assertIn(".progressive-disclosure", self.styles_css)

    def test_bdd_10_home_starts_from_topic_intake_not_full_workbench(self) -> None:
        """行为 10：首页首屏必须先让用户输入或选择研究选题。"""
        self.assertIn("research-topic-intake", self.index_html)
        for label in ("开始一项实证研究", "输入研究问题", "从已有选题继续", "从真实数据候选池开始"):
            self.assertIn(label, self.index_html + self.app_js)

    def test_bdd_11_home_workbench_details_are_hidden_until_topic_confirmation(self) -> None:
        """行为 11：研究判断区默认隐藏，确认选题后再展开。"""
        self.assertIn("research-workbench-after-topic", self.index_html)
        self.assertIn("is-topic-pending", self.index_html)
        self.assertIn("renderResearchTopicIntake", self.app_js)
        self.assertIn("confirmResearchTopic", self.app_js)
        self.assertIn("researchTopicConfirmed", self.app_js)
        self.assertIn(".research-workbench-after-topic.is-topic-pending", self.styles_css)

    def test_bdd_12_topic_intake_links_to_data_first_path_without_binding_data(self) -> None:
        """行为 12：没有明确选题时，可以从真实数据候选池进入数据与设计页。"""
        self.assertIn("data-topic-start-action", self.app_js)
        self.assertIn('switchView("data-variables")', self.app_js)
        self.assertNotIn("autoBindDatasetFromTopicIntake", self.app_js)


if __name__ == "__main__":
    unittest.main()

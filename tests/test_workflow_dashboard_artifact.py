from __future__ import annotations

import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = ROOT / "docs/product-control/workflow-dashboard.html"
STATE_PATH = ROOT / "docs/product-control/workflow-dashboard-state.json"
README_PATH = ROOT / "docs/product-control/README.md"


class WorkflowDashboardArtifactTests(unittest.TestCase):
    """BDD: a visual project-control dashboard keeps the development tree visible."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.dashboard = DASHBOARD_PATH.read_text(encoding="utf-8")
        cls.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        cls.readme = README_PATH.read_text(encoding="utf-8")

    def test_bdd_workflow_dashboard_shows_ai_powered_development_phases(self) -> None:
        """行为 1：仪表盘必须用中文显示 7 个开发阶段和当前/下一阶段。"""
        for phase in ["追问", "调研", "原型", "规格", "拆任务", "实现", "复核"]:
            self.assertIn(phase, self.dashboard)
        self.assertIn("当前步骤", self.dashboard)
        self.assertEqual("交付 / 验收", self.state["current_step"])
        self.assertIn("下一步", self.dashboard)
        self.assertEqual("补齐真实字段后重跑", self.state["next_step"])

    def test_bdd_workflow_dashboard_shows_ceo_readable_executive_summary(self) -> None:
        """行为 2：仪表盘首屏必须先给老板可读的项目结论和决策请求。"""
        expected = {
            "title": "老板先看这里",
            "goal": "给本科生交付可审计的论文初稿",
            "current_truth": "Demo 线已走到 P16 阻断交付：能交付半成品论文，不能声称完整实证结果",
            "decision_needed": "是否补齐真实字段并重跑 P13-P16",
            "next_action": "补齐 parent_education 和 experience 后重跑 P13-P16 闭环",
        }
        for text in expected.values():
            self.assertIn(text, self.dashboard + json.dumps(self.state, ensure_ascii=False))
        self.assertEqual(expected, self.state["executive_summary"])
        self.assertIn("data-dashboard-section=\"executive_summary\"", self.dashboard)
        self.assertIn("renderExecutiveSummary", self.dashboard)

    def test_bdd_workflow_dashboard_shows_current_gate_and_blocker(self) -> None:
        """行为 3：仪表盘必须用中文显示当前门禁、阻断点和模型暂停。"""
        self.assertIn("P16 半成品交付包已生成", self.dashboard + json.dumps(self.state, ensure_ascii=False))
        self.assertIn("真实 CSV 缺少 parent_education 和 experience", self.state["blocker"])
        self.assertIn("P16 阻断交付分支", self.state["blocked_branch"])
        self.assertEqual("p16_blocked_branch_ready", self.state["status_code"])
        self.assertIn("不运行模型", self.dashboard)
        self.assertEqual(
            ["现在能交付什么", "还缺什么", "下一步做什么"],
            [item["label"] for item in self.state["plain_summary"]],
        )

    def test_bdd_workflow_dashboard_shows_design_tree_branches(self) -> None:
        """行为 4：仪表盘必须用中文显示 P12-P16 的分支树和禁止路径。"""
        for branch in [
            "P12 方法规格预检",
            "P13 运行计划校验",
            "P14 执行账本",
            "P15 半成品交付",
            "P16 用户验收",
        ]:
            self.assertIn(branch, self.dashboard)
        self.assertIn("return-to-p12-design-tree", self.dashboard)
        self.assertIn("do-not-jump-to-run-id", self.dashboard)

    def test_bdd_workflow_dashboard_shows_human_qa_checklist_and_is_linked(self) -> None:
        """行为 5：仪表盘必须给中文人工验收清单，并从 product-control README 可发现。"""
        for item in ["打开页面", "当前面板", "预检产物", "禁止入口", "截图证据"]:
            self.assertIn(item, self.dashboard)
        self.assertIn("workflow-dashboard.html", self.readme)
        self.assertIn("工作流仪表盘", self.readme)

    def test_bdd_workflow_dashboard_uses_dynamic_state_source(self) -> None:
        """行为 6：仪表盘必须从 JSON 状态源轮询渲染，而不是只能手改 HTML。"""
        self.assertEqual("workflow_dashboard_state.v1", self.state["schema_version"])
        self.assertEqual("P16 半成品交付包已生成", self.state["current_gate"])
        self.assertEqual("真实 CSV 缺少 parent_education 和 experience，不能运行父母教育工资模型", self.state["blocker"])
        self.assertGreaterEqual(self.state["poll_interval_ms"], 1000)
        self.assertIn("data-dashboard-state-endpoint", self.dashboard)
        self.assertIn("workflow-dashboard-state.json", self.dashboard)
        self.assertIn("renderDashboardState", self.dashboard)
        self.assertIn("renderPlainSummary", self.dashboard)
        self.assertIn("setInterval", self.dashboard)
        self.assertIn("fetch(", self.dashboard)

    def test_bdd_workflow_dashboard_fastapi_routes_serve_html_and_state(self) -> None:
        """行为 7：FastAPI 必须提供动态仪表盘页面和无缓存状态 API。"""
        from Product import app as product_app

        client = TestClient(product_app.app)
        page_response = client.get("/workflow-dashboard")
        self.assertEqual(200, page_response.status_code)
        self.assertIn("项目工作流仪表盘", page_response.text)
        self.assertIn("data-dashboard-state-endpoint", page_response.text)

        state_response = client.get("/api/v1/workflow-dashboard/state")
        self.assertEqual(200, state_response.status_code)
        self.assertEqual("no-store", state_response.headers.get("cache-control"))
        state = state_response.json()
        self.assertEqual("workflow_dashboard_state.v1", state["schema_version"])
        self.assertEqual("P16 半成品交付包已生成", state["current_gate"])
        self.assertEqual("不运行模型", state["forbidden_output"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

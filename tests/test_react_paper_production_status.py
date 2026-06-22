from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_SRC = ROOT / "Product" / "web-react" / "src"


class ReactPaperProductionStatusTests(unittest.TestCase):
    """BDD: 浏览器工作台必须接入论文生产链，而不是停在旧研究简报或旧 P 阶段面板。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = (WEB_REACT_SRC / "App.tsx").read_text(encoding="utf-8")
        cls.component_path = WEB_REACT_SRC / "components" / "PaperProductionStatusPanel.tsx"
        cls.component = cls.component_path.read_text(encoding="utf-8") if cls.component_path.exists() else ""
        cls.styles = (WEB_REACT_SRC / "styles.css").read_text(encoding="utf-8")

    def test_bdd_1_main_workbench_mounts_paper_production_as_the_primary_surface(self) -> None:
        """Given 用户输入题目 When 进入工作台 Then 第一入口只挂论文生产状态。"""

        self.assertTrue(self.component_path.exists(), "PaperProductionStatusPanel.tsx is missing.")
        self.assertIn("PaperProductionStatusPanel", self.app)
        self.assertIn('data-testid="paper-production-status"', self.component)
        self.assertNotIn("ProductControlP0Panel", self.app)
        self.assertNotIn('className="analysis-workspace__technical-details"', self.app)
        self.assertLess(
            self.app.index("<summary>研究流程</summary>"),
            self.app.index("<BriefPanel"),
        )
        self.assertLess(
            self.app.index("<BriefPanel"),
            self.app.rindex("</details>\n      </section>"),
        )
        self.assertIn("proj_cgss_social_capital_happiness", self.app)
        self.assertIn("互联网", self.app)
        self.assertNotIn('projectId.startsWith("proj_cgss_")', self.component)

    def test_bdd_2_component_uses_real_pipeline_quality_and_headless_endpoints(self) -> None:
        """Given 第二层和第三层已有 API When 用户操作 Then 不能只跑旧 BriefPanel。"""

        for endpoint in (
            "/api/v1/workflows",
            "/api/v1/workflows/${workflowId}/start",
            "/product-control/headless-state",
            "/product-control/course-paper-quality",
        ):
            self.assertIn(endpoint, self.component)
        self.assertIn("apiUrl", self.component)
        self.assertIn("startPaperWorkflow", self.component)
        self.assertIn("runQualityGate", self.component)

    def test_bdd_3_component_exposes_the_10_node_paper_pipeline_contract(self) -> None:
        """Given 一篇课程论文要交付 When 展示生产链 Then 十个论文节点必须可见。"""

        for agent_name in (
            "ResearchIntentAgent",
            "LiteratureAgent",
            "DataAgent",
            "MethodAgent",
            "ExecutionAgent",
            "RobustnessAgent",
            "ManuscriptAgent",
            "ReviewerAgent",
            "ReplicationAgent",
            "ExportAgent",
        ):
            self.assertIn(agent_name, self.component)

    def test_bdd_4_component_consumes_ui_neutral_business_contract_fields(self) -> None:
        """Given UI 后续会重做 When 当前组件取数 Then 必须只依赖业务 view model。"""

        for field in (
            "component_id",
            "status",
            "user_summary",
            "primary_action",
            "blockers",
            "artifacts",
            "evidence",
            "audit",
            "review_summary",
            "top_priorities",
            "section_gaps",
        ):
            self.assertIn(field, self.component)

    def test_bdd_5_visible_copy_is_user_delivery_oriented(self) -> None:
        """Given 用户只关心能否跑出论文 When 默认查看 Then 展示交付状态和动作。"""

        for label in (
            "论文生产状态",
            "启动论文生产链",
            "论文审阅",
            "生成论文审阅报告",
            "修订优先级",
            "最终 PDF",
            "刷新状态",
        ):
            self.assertIn(label, self.component)
        for selector in (
            ".paper-production-status",
            ".paper-production-status__pipeline",
            ".paper-production-status__delivery",
            ".paper-production-status__review-summary",
        ):
            self.assertIn(selector, self.styles)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_SRC = ROOT / "Product" / "web-react" / "src"


class MainWorkbenchCleanUiTests(unittest.TestCase):
    """BDD: 首页研究工作台必须以当前卡点为主，而不是调试文字堆叠。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = (WEB_REACT_SRC / "App.tsx").read_text(encoding="utf-8")
        cls.product_control = (
            WEB_REACT_SRC / "components" / "ProductControlP0Panel.tsx"
        ).read_text(encoding="utf-8")
        cls.styles = (WEB_REACT_SRC / "styles.css").read_text(encoding="utf-8")

    def test_bdd_1_parent_education_demo_uses_canonical_project(self) -> None:
        """Given 固定演示题目 When 生成项目编号 Then 读取真实 demo 项目。"""

        self.assertIn("CANONICAL_PARENT_EDUCATION_PROJECT_ID", self.app)
        self.assertIn("proj_empirical_paper_template_main", self.app)
        self.assertIn("canonicalProjectIdForTask", self.app)
        self.assertLess(
            self.app.index("canonicalProjectIdForTask"),
            self.app.index("const candidateProjectId"),
        )
        self.assertRegex(self.app, re.compile(r"父母.*教育水平|父母.*受教育水平", re.S))

    def test_bdd_2_connection_status_is_collapsed(self) -> None:
        """Given 首页有服务诊断 When 渲染头部 Then 默认折叠在连接状态内。"""

        self.assertIn('className="analysis-workspace__connection"', self.app)
        self.assertIn("<summary>连接状态</summary>", self.app)
        self.assertIn("<PaperProductionStatusPanel", self.app)
        self.assertLess(
            self.app.index('className="analysis-workspace__connection"'),
            self.app.index("<PaperProductionStatusPanel"),
        )

    def test_bdd_3_current_p17_gate_is_first_and_old_gates_are_secondary(self) -> None:
        """Given 已进入 P17 When 渲染产品控制 Then P17 在 P11/P9 前且旧门禁折叠。"""

        self.assertIn("product-control-p0-panel--clean", self.product_control)
        self.assertLess(
            self.product_control.index('data-testid="product-control-p17-data-repair-preflight"'),
            self.product_control.index('data-testid="product-control-p11-source-metadata-contract"'),
        )
        self.assertLess(
            self.product_control.index('data-testid="product-control-p17-data-repair-preflight"'),
            self.product_control.index('data-testid="product-control-p9-variable-role-formal-save"'),
        )
        self.assertIn("product-control-secondary-workspace", self.product_control)

    def test_bdd_4_stage_route_is_folded_below_product_control(self) -> None:
        """Given 当前卡点是主任务 When 渲染阶段路线 Then 路线说明折叠。"""

        self.assertIn('className="analysis-workspace__flow-details"', self.app)
        self.assertIn("<summary>研究流程</summary>", self.app)
        self.assertIn("<PaperProductionStatusPanel", self.app)
        self.assertNotIn("<ProductControlP0Panel", self.app)
        self.assertLess(
            self.app.index("<PaperProductionStatusPanel"),
            self.app.index('className="analysis-workspace__flow-details"'),
        )

    def test_bdd_5_clean_light_workspace_and_overflow_guard_exist(self) -> None:
        """Given 桌面和移动端 When 页面渲染 Then 有清爽主题和溢出保护。"""

        for token in (
            "body:has(.analysis-workspace)",
            ".analysis-workspace__connection",
            ".analysis-workspace__flow-details",
            ".product-control-p0-panel--clean",
            "overflow-x: hidden",
            "overflow-wrap: anywhere",
        ):
            self.assertIn(token, self.styles)

    def test_bdd_6_brief_panel_uses_same_light_surface(self) -> None:
        """Given 下方还有研究简报 When 渲染 Then 不能保留旧深色大面板。"""

        self.assertIn(".analysis-workspace .task-brief__main", self.styles)
        self.assertIn(".analysis-workspace .task-brief__inspector", self.styles)
        self.assertIn(".analysis-workspace .task-brief__decision", self.styles)

    def test_bdd_7_default_product_control_is_user_facing(self) -> None:
        """Given 用户看首页 When 当前卡点出现 Then 默认层讲业务下一步。"""

        self.assertIn('data-testid="research-progress-card"', self.product_control)
        self.assertIn("补齐数据字段后再继续分析", self.product_control)
        self.assertIn("父母教育信息", self.product_control)
        self.assertIn("工作经验", self.product_control)
        self.assertLess(
            self.product_control.index('data-testid="research-progress-card"'),
            self.product_control.index('data-testid="product-control-gate-summary"'),
        )

    def test_bdd_8_technical_detail_is_collapsed_by_default(self) -> None:
        """Given 工程细节仍保留 When 默认渲染 Then 技术详情必须折叠。"""

        self.assertIn("product-control-technical-details", self.product_control)
        self.assertIn("<summary>技术详情</summary>", self.product_control)
        self.assertLess(
            self.product_control.index("product-control-technical-details"),
            self.product_control.index('data-testid="product-control-gate-summary"'),
        )
        self.assertNotIn('open={!dataRepairPreflightReport}', self.product_control)
        self.assertIn(".product-control-technical-details", self.styles)
        self.assertIn(".research-progress-card", self.styles)
        self.assertIn(".product-control-technical-details:not([open]) > :not(summary)", self.styles)


if __name__ == "__main__":
    unittest.main()

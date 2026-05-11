from __future__ import annotations

import unittest
from pathlib import Path


class AgentClusterFrontendInteractionTests(unittest.TestCase):
    """BDD: 用户点击 Agent 行后，应能在右侧 drawer 查看该 Agent 的工作内容。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_agent_detail_drawer_shell_exists(self) -> None:
        """行为 1/4：右侧 Agent Drawer 必须有稳定 DOM 容器和关闭入口。"""
        self.assertIn('id="agent-detail-drawer"', self.index_html)
        self.assertIn('id="agent-detail-drawer-content"', self.index_html)
        self.assertIn('id="close-agent-detail-drawer"', self.index_html)
        self.assertIn(".agent-detail-drawer", self.styles_css)
        self.assertIn(".agent-detail-drawer.is-open", self.styles_css)

    def test_agent_rows_have_click_and_keyboard_open_handlers(self) -> None:
        """行为 1/5：Agent 行必须支持鼠标点击和键盘激活，不能只依赖 hover。"""
        self.assertIn('tabindex="0"', self.app_js)
        self.assertIn('role="button"', self.app_js)
        self.assertIn('panel.addEventListener("click"', self.app_js)
        self.assertIn('panel.addEventListener("keydown"', self.app_js)
        self.assertIn("openAgentDetail", self.app_js)

    def test_agent_detail_shows_governance_and_cost_sections(self) -> None:
        """行为 1/3：详情必须展示成本追踪、权限、能力注册等 Agent 治理信息。"""
        for label in ("成本追踪", "权限", "能力注册"):
            self.assertIn(label, self.app_js)

    def test_agent_detail_embeds_artifact_preview(self) -> None:
        """行为 2：在 Agent Drawer 内点击产物后，应在 drawer 内嵌正文预览。"""
        self.assertIn("agent-detail-artifact-preview", self.index_html + self.app_js + self.styles_css)
        self.assertIn("openAgentArtifactPreview", self.app_js)
        self.assertIn("renderAgentArtifactPreview", self.app_js)
        self.assertNotIn("void openArtifactPreview(output.dataset.path)", self.app_js)

    # ========== 候选任务 B：完善 Agent Drawer 用户体验 ==========

    def test_agent_row_active_state_style_exists(self) -> None:
        """行为 1：Agent 行必须有 is-active 样式类和对应的 JS 设置逻辑。"""
        # CSS 中必须有 is-active 样式定义
        self.assertIn(".agent-row.is-active", self.styles_css)
        # JS 中必须根据 activeAgentTaskId 设置/移除 is-active
        self.assertIn("is-active", self.app_js)
        # 必须有更新 active 行的逻辑（通过 data-task-id 匹配）
        self.assertIn("data-task-id", self.app_js)

    def test_agent_detail_drawer_has_prev_next_navigation(self) -> None:
        """行为 2/3：Drawer header 必须有上一个/下一个按钮和导航函数。"""
        # HTML 中必须有导航按钮
        self.assertIn("prev-agent-button", self.index_html)
        self.assertIn("next-agent-button", self.index_html)
        # JS 中必须有导航函数
        self.assertIn("navigateToPrevAgent", self.app_js)
        self.assertIn("navigateToNextAgent", self.app_js)
        # 边界处理：第一个上一个 disabled，最后一个下一个 disabled
        self.assertIn("disabled", self.app_js)

    def test_artifact_preview_has_loading_state(self) -> None:
        """行为 4：产物预览必须有明确的 loading 状态指示。"""
        # renderAgentArtifactPreview 必须在 loading 时返回特定提示文本
        self.assertIn("正在读取产物正文", self.app_js)
        # 必须有 loading 状态变量控制
        self.assertIn("agentDetailPreviewLoading", self.app_js)

    def test_artifact_preview_has_error_state(self) -> None:
        """行为 5：产物预览必须在读取失败时显示错误信息。"""
        # renderAgentArtifactPreview 必须处理 error 状态
        self.assertIn("无法读取产物正文", self.app_js)
        # 错误状态应该由 apiError 驱动
        self.assertIn("apiError", self.app_js)

    def test_artifact_preview_has_empty_state(self) -> None:
        """行为 6：当 Agent 无产物时，预览区域必须显示空状态提示。"""
        # 必须在 renderAgentArtifactPreview 中显示精确的空状态提示
        self.assertIn("等待研究完成后自动生成", self.app_js)
        # 空状态应该在 outputs 为空时触发
        self.assertIn("outputs", self.app_js)

    def test_long_content_readability_styles(self) -> None:
        """行为 7：长正文预览区域必须有可读的 CSS 样式。"""
        # 预览区域必须有合适的行高
        self.assertIn("line-height", self.styles_css)
        # 预览区域必须有合适的字体大小
        self.assertIn("font-size", self.styles_css)
        # 预览区域必须有滚动支持
        self.assertIn("overflow", self.styles_css)
        # 预览 body 类必须存在
        self.assertIn("agent-detail-preview-body", self.styles_css)


if __name__ == "__main__":
    unittest.main()

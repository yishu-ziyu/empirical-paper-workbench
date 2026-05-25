from __future__ import annotations

import re
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_ROOT = REPO_ROOT / "Product" / "web-react"


class ReactAgentActivityPanelContractTest(unittest.TestCase):
    """P3-E：实证队列安全审计与运作账本高保真交互契约。"""

    def test_agent_activity_panel_component_exists(self) -> None:
        component_path = WEB_REACT_ROOT / "src" / "components" / "AgentActivityPanel.tsx"
        self.assertTrue(component_path.exists(), "AgentActivityPanel component is missing.")

        source = component_path.read_text(encoding="utf-8")
        expected_markers = [
            "AgentActivityPanel",
            "AgentActivity",
            "DEFAULT_ACTIVITIES",
            "Supervisor",
            "LiteratureAgent",
            "DataAgent",
            "MethodAgent",
            "ExecutionAgent",
            "ReviewerAgent",
            "ManuscriptAgent",
            "ExportAgent",
            "开始真实数据与方法执行",
            "审计轨迹入口",
            "modal-overlay",
            "showAuditModal",
        ]
        for marker in expected_markers:
            self.assertIn(marker, source, f"Missing component marker: {marker}")

    def test_app_composes_agent_activity_panel_flow(self) -> None:
        source = (WEB_REACT_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn("AgentActivityPanel", source)
        self.assertIn("onStartExecution", source)
        self.assertIn("onBack", source)
        self.assertIn("planApproved", source)
        self.assertIn("executionStarted", source)
        self.assertNotIn('setActiveStage("variables")', source)

    def test_static_activity_artifacts_are_explicitly_mock(self) -> None:
        """业务规则：前端静态队列数据不能伪装成真实本地文件或真实执行证据。"""
        source = (WEB_REACT_ROOT / "src" / "components" / "AgentActivityPanel.tsx").read_text(encoding="utf-8")
        default_block = source.split("const DEFAULT_ACTIVITIES", 1)[1].split("interface AgentActivityPanelProps", 1)[0]

        self.assertIn('evidence_level: "mock"', default_block)
        for forbidden_level in ["local_file", "local_execution", "external_source"]:
            self.assertNotIn(
                f'evidence_level: "{forbidden_level}"',
                default_block,
                f"Mock AgentActivityPanel data must not claim {forbidden_level} evidence.",
            )

    def test_global_execution_gate_requires_confirmation_modal(self) -> None:
        """业务规则：全局开始执行按钮必须先确认范围、证据、正式层边界和风险。"""
        source = (WEB_REACT_ROOT / "src" / "components" / "AgentActivityPanel.tsx").read_text(encoding="utf-8")
        required_markers = [
            "showStartExecutionModal",
            "执行范围",
            "证据要求",
            "正式层边界",
            "已知风险",
            "确认授权执行",
        ]
        for marker in required_markers:
            self.assertIn(marker, source, f"Missing global execution confirmation marker: {marker}")

    def test_styles_contain_agent_console_rules_without_color_noise(self) -> None:
        styles_path = WEB_REACT_ROOT / "src" / "styles.css"
        self.assertTrue(styles_path.exists(), "React styles are missing.")

        css = styles_path.read_text(encoding="utf-8").lower()
        required_markers = [
            "agent-console__back-row",
            "agent-console__filters",
            "agent-console__list",
            "agent-console__item",
            "agent-console__global-actions",
        ]
        for marker in required_markers:
            self.assertIn(marker, css, f"Missing CSS class: {marker}")

        forbidden_color_tokens = [
            "green",
            "blue",
            "purple",
            "amber",
            "orange",
            "teal",
            "cyan",
            "pink",
            "red",
            "violet",
        ]
        for token in forbidden_color_tokens:
            self.assertIsNone(re.search(rf"\b{token}\b", css), f"Harsh color word found: {token}")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_ROOT = REPO_ROOT / "Product" / "web-react"


class ReactInputTabsContractTest(unittest.TestCase):
    """P3：新的 React 入口只先承载研究输入器和阶段滑动导航。"""

    def test_react_vite_shell_is_separate_from_legacy_web(self) -> None:
        package_path = WEB_REACT_ROOT / "package.json"
        vite_config_path = WEB_REACT_ROOT / "vite.config.ts"

        self.assertTrue(package_path.exists(), "P3 must create an isolated React package.")
        package = json.loads(package_path.read_text(encoding="utf-8"))

        self.assertEqual(package.get("scripts", {}).get("build"), "vite build")
        self.assertIn("react", package.get("dependencies", {}))
        self.assertIn("vite", package.get("devDependencies", {}))

        vite_config = vite_config_path.read_text(encoding="utf-8")
        self.assertIn('outDir: "../web-dist"', vite_config)
        self.assertNotIn('outDir: "../web"', vite_config)

    def test_research_command_input_supports_topic_files_paste_and_model_choice(self) -> None:
        component_path = WEB_REACT_ROOT / "src" / "components" / "ResearchCommandInput.tsx"
        self.assertTrue(component_path.exists(), "Research input component is missing.")

        source = component_path.read_text(encoding="utf-8")
        expected_markers = [
            "ResearchCommandInput",
            "FileWithPreview",
            "PastedContent",
            "handlePaste",
            "handleDrop",
            "ModeSelectorDropdown",
            "onSubmit",
            "research-input",
        ]
        for marker in expected_markers:
            self.assertIn(marker, source)

    def test_slide_tabs_exposes_research_lifecycle_and_keyboard_selection(self) -> None:
        component_path = WEB_REACT_ROOT / "src" / "components" / "SlideTabs.tsx"
        self.assertTrue(component_path.exists(), "SlideTabs component is missing.")

        source = component_path.read_text(encoding="utf-8")
        for label in ["任务书", "递归搜索", "数据变量", "方法设计", "执行实验"]:
            self.assertIn(label, source)
        self.assertIn("motion", source)
        self.assertIn("onKeyDown", source)
        self.assertIn("aria-selected", source)

    def test_locked_stage_tabs_do_not_become_visually_selected(self) -> None:
        """行为 21：未解锁阶段可提示用户，但不能被滑块或 active 样式选中。"""
        component_path = WEB_REACT_ROOT / "src" / "components" / "SlideTabs.tsx"
        app_path = WEB_REACT_ROOT / "src" / "App.tsx"

        source = component_path.read_text(encoding="utf-8")
        app_source = app_path.read_text(encoding="utf-8")

        self.assertIn("disabled?: boolean", source)
        self.assertIn("DEFAULT_CURSOR_POSITION", source)
        self.assertIn("aria-disabled={tab.disabled ? \"true\" : undefined}", source)
        self.assertIn("slide-tabs__tab--locked", source)
        self.assertIn("useLayoutEffect", source)
        self.assertIn("requestAnimationFrame", source)
        self.assertIn("initial={false}", source)
        self.assertIn("setCursorTo(activeId)", source)
        self.assertIn("if (target?.disabled)", source)
        self.assertIn("returnActiveCursor", source)
        self.assertIn("if (tab.disabled) return;", source)
        self.assertIn("disabled: !unlocked", app_source)
        self.assertIn('label: info.label', app_source)
        self.assertNotIn('label: unlocked ? info.label : `${info.label} (待解锁)`', app_source)

    def test_dotted_surface_background_uses_three_without_adding_page_copy(self) -> None:
        component_path = WEB_REACT_ROOT / "src" / "components" / "DottedSurface.tsx"
        self.assertTrue(component_path.exists(), "DottedSurface component is missing.")

        package = json.loads((WEB_REACT_ROOT / "package.json").read_text(encoding="utf-8"))
        source = component_path.read_text(encoding="utf-8")
        app_source = (WEB_REACT_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")

        self.assertIn("three", package.get("dependencies", {}))
        self.assertIn("import * as THREE from \"three\"", source)
        self.assertIn("WebGLRenderer", source)
        self.assertIn("requestAnimationFrame", source)
        self.assertIn("DottedSurface", app_source)
        self.assertNotIn("Dotted Surface", app_source)

    def test_app_composes_intake_then_analysis_primitives_without_a_full_dashboard(self) -> None:
        app_path = WEB_REACT_ROOT / "src" / "App.tsx"
        self.assertTrue(app_path.exists(), "React App shell is missing.")

        source = app_path.read_text(encoding="utf-8")
        self.assertIn("ResearchCommandInput", source)
        self.assertIn("SlideTabs", source)
        self.assertIn("SystemStatusBar", source)
        self.assertIn("stage-panel__current-action", source)
        self.assertIn("analysis-workspace", source)
        self.assertIn("AgentTaskQueuePanel", source)
        self.assertNotIn("RightAuditDrawer", source)
        self.assertNotIn("系统只进入草案层", source)
        self.assertNotIn("这个 React 切片", source)
        self.assertNotIn("不展开 Agent", source)

    def test_react_agent_task_queue_is_wired_to_project_api(self) -> None:
        """行为：React 工作台必须展示真实 Agent 队列入口，并使用当前项目 API。"""
        component_path = WEB_REACT_ROOT / "src" / "components" / "AgentTaskQueuePanel.tsx"
        app_path = WEB_REACT_ROOT / "src" / "App.tsx"
        styles_path = WEB_REACT_ROOT / "src" / "styles.css"
        self.assertTrue(component_path.exists(), "AgentTaskQueuePanel component is missing.")

        source = component_path.read_text(encoding="utf-8")
        app_source = app_path.read_text(encoding="utf-8")
        styles = styles_path.read_text(encoding="utf-8")

        for marker in [
            "AgentTaskQueuePanel",
            "/api/v1/projects/",
            "/agent-task-queue",
            "loadQueue",
            "createQueue",
            "reviewDraftSectionTasks",
            "data-testid=\"agent-task-queue-panel\"",
            "批准给 WriterAgent",
            "要求修订",
            "拒绝任务包",
            "正式层仍保持锁定",
            "draft-section-tasks-review",
        ]:
            self.assertIn(marker, source)
        self.assertIn("<AgentTaskQueuePanel", app_source)
        self.assertIn("effectiveProjectId", app_source)
        self.assertIn('projectId={effectiveProjectId}', app_source)
        self.assertIn(".agent-task-queue-panel", styles)
        self.assertIn(".agent-task-queue-review", styles)

    def test_brief_panel_hides_raw_network_errors_from_users(self) -> None:
        """行为：研究简报服务未连上时，不能把底层网络错误直接展示给用户。"""
        component_path = WEB_REACT_ROOT / "src" / "components" / "BriefPanel.tsx"
        source = component_path.read_text(encoding="utf-8")

        self.assertIn("SERVICE_ERROR_MESSAGE", source)
        self.assertIn("toBriefErrorMessage", source)
        self.assertIn("Failed to fetch", source)
        self.assertNotIn("setError(err instanceof Error ? err.message : SERVICE_ERROR_MESSAGE)", source)

    def test_new_react_styles_are_black_white_gray_only(self) -> None:
        styles_path = WEB_REACT_ROOT / "src" / "styles.css"
        self.assertTrue(styles_path.exists(), "React styles are missing.")

        css = styles_path.read_text(encoding="utf-8").lower()
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
            self.assertIsNone(re.search(rf"\b{token}\b", css), token)

        required_markers = [
            "--color-bg",
            "--color-panel",
            "--color-ink",
            "--color-muted",
            "research-input",
            "slide-tabs",
        ]
        for marker in required_markers:
            self.assertIn(marker, css)

    def test_start_screen_contrast_uses_soft_gray_tokens(self) -> None:
        styles_path = WEB_REACT_ROOT / "src" / "styles.css"
        css = styles_path.read_text(encoding="utf-8").lower()

        overly_harsh_tokens = [
            "#000000",
            "#ffffff",
            "#050505",
            "#0b0b0b",
        ]
        for token in overly_harsh_tokens:
            self.assertNotIn(token, css)

        self.assertIn("--color-bg: #242424", css)
        self.assertIn("--color-panel: #2b2b2b", css)
        self.assertIn("--color-panel-soft: #323232", css)
        self.assertIn("--color-ink: #c8c8c8", css)


if __name__ == "__main__":
    unittest.main()

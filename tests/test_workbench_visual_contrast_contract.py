from __future__ import annotations

import unittest
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_ROOT = REPO_ROOT / "Product" / "web-react"


class WorkbenchVisualContrastContractTests(unittest.TestCase):
    """BDD: 工作台控件必须可读，整体黑白对比不能过硬。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = (WEB_REACT_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
        cls.css = (WEB_REACT_ROOT / "src" / "styles.css").read_text(encoding="utf-8")
        cls.surface = (
            WEB_REACT_ROOT / "src" / "components" / "DottedSurface.tsx"
        ).read_text(encoding="utf-8")
        cls.system_status = (
            WEB_REACT_ROOT / "src" / "components" / "SystemStatusBar.tsx"
        ).read_text(encoding="utf-8")
        cls.brief_panel = (
            WEB_REACT_ROOT / "src" / "components" / "BriefPanel.tsx"
        ).read_text(encoding="utf-8")
        cls.auto_research = (
            WEB_REACT_ROOT / "src" / "components" / "AutoResearchStream.tsx"
        ).read_text(encoding="utf-8")
        cls.search_panel = (
            WEB_REACT_ROOT / "src" / "components" / "SearchPanel.tsx"
        ).read_text(encoding="utf-8")
        cls.variables_panel = (
            WEB_REACT_ROOT / "src" / "components" / "VariablesPanel.tsx"
        ).read_text(encoding="utf-8")
        cls.design_panel = (
            WEB_REACT_ROOT / "src" / "components" / "DesignPanel.tsx"
        ).read_text(encoding="utf-8")
        cls.execution_panel = (
            WEB_REACT_ROOT / "src" / "components" / "ExecutionPanel.tsx"
        ).read_text(encoding="utf-8")
        cls.audit_panel = (
            WEB_REACT_ROOT / "src" / "components" / "IdentificationAuditPanel.tsx"
        ).read_text(encoding="utf-8")
        cls.reasoning_chain = (
            WEB_REACT_ROOT / "src" / "components" / "ReasoningChainView.tsx"
        ).read_text(encoding="utf-8")
        cls.methods_drawer = (
            WEB_REACT_ROOT / "src" / "components" / "MethodsDrawer.tsx"
        ).read_text(encoding="utf-8")

    def _css_block(self, selector: str) -> str:
        pattern = re.compile(rf"{re.escape(selector)}\s*\{{(?P<body>.*?)\n\}}", re.S)
        match = pattern.search(self.css)
        self.assertIsNotNone(match, f"missing css selector: {selector}")
        return match.group("body")

    def _rgba_alpha_for_var(self, var_name: str) -> float:
        pattern = re.compile(
            rf"{re.escape(var_name)}:\s*rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*(?P<alpha>[0-9.]+)\s*\);"
        )
        match = pattern.search(self.css)
        self.assertIsNotNone(match, f"missing rgba var: {var_name}")
        return float(match.group("alpha"))

    def test_bdd_saved_brief_button_has_readable_monochrome_states(self) -> None:
        """行为 10：已落盘简报入口在深色背景上不能出现白块白字。"""
        self.assertIn("查看已保存的简报", self.app)
        self.assertIn("workbench-saved-brief", self.app)
        self.assertIn(".workbench-saved-brief", self.css)
        self.assertIn(".workbench-saved-brief:disabled", self.css)
        self.assertIn("--color-button-disabled-bg", self.css)
        self.assertIn("--color-button-disabled-text", self.css)
        self.assertIn("background: var(--color-button-disabled-bg)", self.css)
        self.assertIn("color: var(--color-button-disabled-text)", self.css)
        self.assertNotIn("opacity: 0.88", self.css)

    def test_bdd_workbench_uses_softer_dark_contrast(self) -> None:
        """行为 11：工作台背景和文字使用柔和黑白灰，不回到高硬度黑白。"""
        self.assertIn("--color-bg: #242424", self.css)
        self.assertIn("--color-panel: #2b2b2b", self.css)
        self.assertIn("--color-ink: #c8c8c8", self.css)
        self.assertIn(
            "background: radial-gradient(ellipse at top, #2d2d2d 0%, #242424 100%)",
            self.css,
        )
        self.assertIn("opacity: 0.06", self.css)
        self.assertIn("opacity: 0.06", self.surface)

    def test_bdd_disabled_actions_cannot_be_overridden_into_white_blocks(self) -> None:
        """行为 21：禁用按钮必须强制继承暗色可读状态，不能被基础按钮白底覆盖。"""
        alpha = self._rgba_alpha_for_var("--color-button-disabled-bg")
        self.assertGreaterEqual(alpha, 0.07)
        self.assertLessEqual(alpha, 0.09)

        for selector in [
            ".btn:disabled",
            ".btn--primary:disabled",
            ".task-brief__restart:disabled",
            ".workbench-saved-brief:disabled",
            ".step-card__buttons .btn:disabled",
            ".step-card__buttons .btn:not(.btn--primary):disabled",
        ]:
            block = self._css_block(selector)
            self.assertIn(
                "background: var(--color-button-disabled-bg) !important",
                block,
            )
            self.assertIn(
                "color: var(--color-button-disabled-text) !important",
                block,
            )

    def test_bdd_background_particles_stay_below_primary_content_contrast(self) -> None:
        """行为 22：背景粒子只是质感，不能抢主内容的视觉层级。"""
        self.assertIn("opacity: 0.06", self.css)
        self.assertIn("opacity: 0.06", self.surface)

    def test_bdd_stage_navigation_uses_research_task_language(self) -> None:
        """行为 12：阶段导航要说用户任务，不裸露单一来源或后端术语。"""
        for text in [
            "研究简报",
            "文献检索",
            "变量审阅",
            "方法选择",
            "论文生成",
            "识别审计",
        ]:
            self.assertIn(text, self.app)
        for forbidden in ["arxiv 召回", "Pre-trend + 弱 IV 诊断 + DAG", "StatsPAI 估算候选识别策略"]:
            self.assertNotIn(forbidden, self.app)

    def test_bdd_system_status_bar_uses_chinese_product_labels(self) -> None:
        """行为 13：顶部状态栏要显示中文产品语义，不显示 caps/artifacts/obs 缩写。"""
        for text in ["能力", "成本", "产物", "审计"]:
            self.assertIn(text, self.system_status)
        for forbidden in [">caps<", ">artifacts<", ">obs<", "Capabilities", "Cost breakdown", "Artifacts", "Observability", "No data"]:
            self.assertNotIn(forbidden, self.system_status)

    def test_bdd_variable_role_cards_are_monochrome(self) -> None:
        """行为 14：变量角色卡只使用黑白灰角色 token，不使用彩色语义噪声。"""
        for forbidden in ["#c1440e", "#1f6feb", "#8b5cf6", "#0e8a86"]:
            self.assertNotIn(forbidden, self.variables_panel)
        self.assertIn("--variables-role", self.variables_panel)

    def test_bdd_execution_panel_uses_dark_workbench_and_clear_action_copy(self) -> None:
        """行为 15：执行页不能残留白底主题，主按钮要说清楚产物目标。"""
        for forbidden in ["background: #fafafa", "#eef2ff", "#c7d2fe", "#1e3a8a", "#047857", "#fef3c7", "#fee2e2"]:
            self.assertNotIn(forbidden, self.execution_panel)
        self.assertNotIn("开始跑", self.execution_panel)
        self.assertIn("生成论文与结果包", self.execution_panel)
        self.assertIn("已完成", self.execution_panel)

    def test_bdd_identification_audit_uses_dark_workbench_and_human_copy(self) -> None:
        """行为 16：识别审计页要用中文审计语义，不显示浅色主题或开发命令。"""
        for forbidden in ["background: #fafafa", "background: #ffffff", "#e0e7ff", "#fee2e2", "#fffbeb", "#f9fafb"]:
            self.assertNotIn(forbidden, self.audit_panel)
        for forbidden in ["Pre-trend test", "Weak-IV diagnostics", "DAG visualization", "uvicorn Product.app:app", "VITE_API_BASE_URL"]:
            self.assertNotIn(forbidden, self.audit_panel)
        for text in ["趋势检验", "工具变量强度", "因果路径"]:
            self.assertIn(text, self.audit_panel)

    def test_bdd_nested_execution_details_do_not_reintroduce_light_theme(self) -> None:
        """行为 17：推理链和方法抽屉展开后也不能重新出现白底和彩色风险噪声。"""
        for source in [self.reasoning_chain, self.methods_drawer]:
            for forbidden in ["#f9fafb", "#ffffff", "#ffb4b4", "#ffd07a", "#a8e6a8", "#f5e4b8"]:
                self.assertNotIn(forbidden, source)
        self.assertIn("var(--color-panel-soft)", self.reasoning_chain)
        self.assertIn("var(--color-panel-soft)", self.methods_drawer)

    def test_bdd_each_stage_explains_current_action_and_next_step(self) -> None:
        """行为 18：每个阶段页要告诉用户当前要做什么、点完进入哪里。"""
        for text in ["stage-panel__current-action", "现在只做", "完成后进入"]:
            self.assertIn(text, self.app)
        expected_copy = {
            "brief": ["先把题目变成可执行研究简报", "确认后进入文献检索"],
            "auto": ["自动整理研究简报", "完成后进入文献检索"],
            "search": ["补齐论文依据", "采纳后进入变量审阅"],
            "variables": ["审阅变量角色", "确认后进入方法选择"],
            "design": ["选择识别策略", "确认后进入论文生成"],
            "execution": ["生成论文与结果包", "完成后进入识别审计"],
            "audit": ["核验识别可信度", "审计结果会决定哪些结论可以写进正式稿"],
        }
        sources = {
            "brief": self.brief_panel,
            "auto": self.auto_research,
            "search": self.search_panel,
            "variables": self.variables_panel,
            "design": self.design_panel,
            "execution": self.execution_panel,
            "audit": self.audit_panel,
        }
        for key, texts in expected_copy.items():
            with self.subTest(stage=key):
                for text in texts:
                    self.assertIn(text, sources[key])

    def test_bdd_primary_stage_copy_hides_backend_jargon(self) -> None:
        """行为 19：主界面文案不能让用户先理解后端名词。"""
        primary_sources = [
            self.search_panel,
            self.design_panel,
            self.brief_panel,
            self.auto_research,
            self.app,
        ]
        forbidden = [
            "从 arxiv 召回",
            "递归搜索 arxiv + LLM 重排",
            "StatsPAI 估算候选方法",
            "正在调 StatsPAI + LLM 评估",
            "verdict passed",
            "verdict failed",
            "verdict gate",
            "fits data",
            "weak fit",
            "code_stub",
            "sp_output",
            "自动进入 search tab",
            "paper.pdf",
            "results.json",
            "5 tab 走通完成",
        ]
        for source in primary_sources:
            for word in forbidden:
                self.assertNotIn(word, source)

    def test_bdd_user_facing_errors_do_not_expose_raw_http_or_env_details(self) -> None:
        """行为 20：页面错误状态要说人话，HTTP 和 env 细节留给日志。"""
        user_facing_sources = [
            self.brief_panel,
            self.auto_research,
            self.search_panel,
            self.variables_panel,
            self.design_panel,
            self.audit_panel,
            self.methods_drawer,
            self.system_status,
            self.app,
        ]
        for source in user_facing_sources:
            for forbidden in ["HTTP ${", "VITE_API_BASE_URL", "uvicorn Product.app:app"]:
                self.assertNotIn(forbidden, source)
        for text in ["服务暂时没连上", "稍后重试", "不会影响已保存的研究材料"]:
            self.assertIn(
                text,
                self.search_panel
                + self.variables_panel
                + self.design_panel
                + self.brief_panel
                + self.auto_research
                + self.methods_drawer
                + self.system_status,
            )
        for text in ["本地研究服务", "模型配置", "研究材料已经保留"]:
            self.assertIn(text, self.brief_panel)


if __name__ == "__main__":
    unittest.main()

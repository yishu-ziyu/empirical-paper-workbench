from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_ROOT = REPO_ROOT / "Product" / "web-react"


class ReactTaskBriefDemoTest(unittest.TestCase):
    """P3-D：提交题目后先进入任务书阶段页和右侧 Inspector demo。"""

    def test_bdd_document_exists(self) -> None:
        bdd_path = (
            REPO_ROOT
            / "docs"
            / "architecture-v2"
            / "codex-phase-p3-task-brief-demo-bdd.md"
        )
        self.assertTrue(bdd_path.exists())
        source = bdd_path.read_text(encoding="utf-8")
        for marker in [
            "task brief stage page",
            "right inspector",
            "not a full dashboard",
            "draft-only",
        ]:
            self.assertIn(marker, source)

    def test_task_brief_component_exists_with_main_decisions_and_inspector(self) -> None:
        component_path = WEB_REACT_ROOT / "src" / "components" / "TaskBriefDemo.tsx"
        self.assertTrue(component_path.exists(), "TaskBriefDemo component is missing.")

        source = component_path.read_text(encoding="utf-8")
        for marker in [
            "TaskBriefDemo",
            "task-brief",
            "task-brief__main",
            "task-brief__inspector",
            "研究题目",
            "研究边界",
            "数据线索",
            "方法倾向",
            "下一步",
            "证据要求",
            "风险",
            "正式层边界",
        ]:
            self.assertIn(marker, source)

    def test_app_uses_task_brief_as_first_analysis_stage(self) -> None:
        source = (WEB_REACT_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn("TaskBriefDemo", source)
        self.assertIn("activeStage", source)
        self.assertIn('activeStage === "brief"', source)
        self.assertLess(source.index("<SlideTabs"), source.index("<TaskBriefDemo"))
        self.assertLess(source.index("<TaskBriefDemo"), source.index("<SemanticGlowCards"))

    def test_styles_define_stage_page_and_right_inspector_without_color_noise(self) -> None:
        css = (WEB_REACT_ROOT / "src" / "styles.css").read_text(encoding="utf-8").lower()
        for marker in [
            "task-brief",
            "task-brief__main",
            "task-brief__inspector",
            "task-brief__decision",
            "task-brief__inspector-section",
        ]:
            self.assertIn(marker, css)
        for token in ["green", "blue", "purple", "amber", "orange", "teal", "cyan", "pink", "red", "violet"]:
            self.assertIsNone(re.search(rf"\b{token}\b", css), token)


if __name__ == "__main__":
    unittest.main()

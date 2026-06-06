from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_ROOT = REPO_ROOT / "Product" / "web-react"


class BriefPanelSelfCritiqueContractTests(unittest.TestCase):
    """BDD: BriefPanel 只在 step 3 决策点显示 LLM 疑虑。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (
            WEB_REACT_ROOT / "src" / "components" / "BriefPanel.tsx"
        ).read_text(encoding="utf-8")
        cls.css = (WEB_REACT_ROOT / "src" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_ui_renders_critique_only_for_step3_awaiting(self) -> None:
        """行为 5：只有 step 3 处于 awaiting 且有疑虑时才显示辅助判断。"""
        self.assertIn('data-testid="brief-step-3-critique"', self.source)
        self.assertIn('steps[3].status === "awaiting"', self.source)
        self.assertIn("steps[3].critique", self.source)
        self.assertNotIn("steps[1].critique", self.source)
        self.assertNotIn("steps[2].critique", self.source)
        self.assertNotIn("steps[4].critique", self.source)

    def test_bdd_ui_keeps_the_three_human_decision_actions(self) -> None:
        """行为 6：辅助判断不能替用户点击，三个原动作仍交给 StepCard。"""
        for action in [
            'onContinue={() => handleResume("continue")}',
            'onModify={(userInput) => handleResume("modify", userInput)}',
            'onReselect={() => handleResume("reselect")}',
        ]:
            self.assertIn(action, self.source)
        self.assertNotIn("autoApprove", self.source)
        self.assertNotIn("autoContinue", self.source)

    def test_bdd_ui_has_compact_dark_style_for_critique_block(self) -> None:
        """行为 7：疑虑块是轻量信息提示，不新增动画和大面积视觉噪声。"""
        self.assertIn(".brief-self-critique", self.css)
        self.assertIn("font-size: 13px", self.css)
        self.assertIn("border: 0.5px solid var(--color-line-emphasis)", self.css)
        self.assertNotIn(".brief-self-critique { animation", self.css)

    def test_bdd_step3_decision_buttons_have_readable_monochrome_states(self) -> None:
        """行为 8：步骤 3 的继续/修改/重选按钮必须在深色卡片上可读。"""
        self.assertIn(".step-card__buttons .btn", self.css)
        self.assertIn(".step-card__buttons .btn:not(.btn--primary)", self.css)
        self.assertIn(".step-card__buttons .btn--ghost", self.css)
        self.assertIn("color: #101010", self.css)
        self.assertIn("color: #d8d8d8", self.css)
        self.assertIn(".step-card__buttons .btn:not(.btn--primary):disabled", self.css)
        self.assertIn("opacity: 0.88", self.css)

    def test_bdd_restart_button_has_readable_completed_state(self) -> None:
        """行为 9：任务书完成后的“重新研究”按钮在深色面板上必须可读。"""
        self.assertIn('data-testid="brief-restart"', self.source)
        self.assertIn("task-brief__restart", self.source)
        self.assertIn(".task-brief__restart", self.css)
        self.assertIn(".task-brief__restart:disabled", self.css)
        self.assertIn("color: #101010", self.css)


if __name__ == "__main__":
    unittest.main()

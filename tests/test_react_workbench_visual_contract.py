from __future__ import annotations

import re
import unittest
from pathlib import Path


class ReactWorkbenchVisualContractTests(unittest.TestCase):
    """BDD: React 研究工作台的操作按钮和背景必须能被稳定读清。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.styles_css = (root / "Product" / "web-react" / "src" / "styles.css").read_text(
            encoding="utf-8"
        )

    def test_bdd_1_disabled_actions_are_readable_not_white_blocks(self) -> None:
        """行为 1：禁用按钮应是低噪声灰态，不能变成白底白字。"""
        self.assertIn("--color-button-disabled-bg: rgba(230, 230, 230, 0.075);", self.styles_css)
        self.assertIn("--color-button-disabled-text: #8f8f8f;", self.styles_css)
        self.assertIn("--color-button-disabled-border: rgba(230, 230, 230, 0.16);", self.styles_css)
        for selector in (
            ".btn:disabled",
            ".btn--primary:disabled",
            ".task-brief__restart:disabled",
            ".step-card__buttons .btn:disabled",
        ):
            self.assertRegex(
                self.styles_css,
                re.compile(re.escape(selector) + r"\s*\{[^}]*opacity:\s*1", re.S),
            )

    def test_bdd_2_dark_surface_reduces_contrast_pressure(self) -> None:
        """行为 2：工作台暗色背景应柔和，避免纯黑底造成阅读压力。"""
        self.assertIn("--color-bg: #242424;", self.styles_css)
        self.assertIn("--color-panel: #2b2b2b;", self.styles_css)
        self.assertIn("--color-ink: #c8c8c8;", self.styles_css)
        self.assertIn("radial-gradient(ellipse at top, #2d2d2d 0%, #242424 100%)", self.styles_css)
        self.assertIn("opacity: 0.06;", self.styles_css)
        self.assertNotIn("--color-bg: #1d1d1d;", self.styles_css)


if __name__ == "__main__":
    unittest.main()

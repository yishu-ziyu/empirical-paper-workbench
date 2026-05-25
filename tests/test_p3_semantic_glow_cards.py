from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_ROOT = REPO_ROOT / "Product" / "web-react"


class ReactSemanticGlowCardsTest(unittest.TestCase):
    """P3-C：入口页保持干净，提交后在分析页显示语义分析卡。"""

    def test_bdd_document_exists(self) -> None:
        bdd_path = (
            REPO_ROOT
            / "docs"
            / "architecture-v2"
            / "codex-phase-p3-semantic-glow-cards-bdd.md"
        )
        self.assertTrue(bdd_path.exists())
        source = bdd_path.read_text(encoding="utf-8")
        for marker in [
            "first screen stays intake-only",
            "submit topic enters analysis workspace",
            "grayscale spotlight",
            "draft-only",
            "empty state",
        ]:
            self.assertIn(marker, source)

    def test_semantic_glow_cards_component_splits_meaning(self) -> None:
        component_path = WEB_REACT_ROOT / "src" / "components" / "SemanticGlowCards.tsx"
        self.assertTrue(component_path.exists(), "SemanticGlowCards component is missing.")

        source = component_path.read_text(encoding="utf-8")
        expected_markers = [
            "SemanticGlowCards",
            "GlowCard",
            "useSemanticAnalysis",
            "研究对象",
            "数据线索",
            "方法线索",
            "证据缺口",
            "下一步任务",
            "pointermove",
            "data-glow-card",
        ]
        for marker in expected_markers:
            self.assertIn(marker, source)

    def test_research_input_can_stream_draft_changes_without_rendering_cards_inline(self) -> None:
        source = (WEB_REACT_ROOT / "src" / "components" / "ResearchCommandInput.tsx").read_text(
            encoding="utf-8"
        )
        for marker in ["onDraftChange", "selectedMode", "files.length", "pastedContent.length"]:
            self.assertIn(marker, source)
        self.assertNotIn("SemanticGlowCards", source)

    def test_app_keeps_entry_page_clean_and_moves_cards_to_analysis_workspace(self) -> None:
        source = (WEB_REACT_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn("SemanticGlowCards", source)
        self.assertIn("analysis-workspace", source)
        self.assertIn("task === null", source)
        self.assertLess(source.index("start-panel"), source.index("analysis-workspace"))
        self.assertLess(source.index("<SlideTabs"), source.index("<SemanticGlowCards"))
        self.assertNotIn("<SemanticGlowCards draft={draft}", source)

    def test_styles_keep_glow_cards_in_black_white_gray_system(self) -> None:
        css = (WEB_REACT_ROOT / "src" / "styles.css").read_text(encoding="utf-8").lower()
        for marker in [
            "semantic-analysis-grid",
            "semantic-glow-card",
            "--glow-x",
            "--glow-y",
            "radial-gradient",
            "prefers-reduced-motion",
        ]:
            self.assertIn(marker, css)

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


if __name__ == "__main__":
    unittest.main()

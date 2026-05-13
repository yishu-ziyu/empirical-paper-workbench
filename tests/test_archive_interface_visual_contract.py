from __future__ import annotations

import unittest
from pathlib import Path


class ArchiveInterfaceVisualContractTests(unittest.TestCase):
    """BDD: 前端必须呈现研究档案型界面，而不是普通 SaaS 页面。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_1_shell_uses_research_archive_identity(self) -> None:
        """行为 1：首屏必须呈现研究档案身份，不做营销 hero。"""
        for text in ("研究档案", "本地证据", "相邻笔记"):
            self.assertIn(text, self.index_html)
        self.assertIn("archive-shell", self.styles_css)
        self.assertNotIn("hero-gradient-orb", self.index_html + self.styles_css)

    def test_bdd_2_persistent_archive_inspector_exposes_backlinks(self) -> None:
        """行为 2：所有页面必须有持久相邻笔记/反向链接索引。"""
        for token in ("archive-inspector", "archive-backlinks", "data-inspector-view", "mountArchiveInspector"):
            self.assertIn(token, self.index_html + self.app_js + self.styles_css)
        self.assertIn("updateArchiveInspector", self.app_js)

    def test_bdd_3_surfaces_use_ledger_shelf_note_items(self) -> None:
        """行为 3：证据与产物以档案条目陈列。"""
        for token in ("archive-ledger", "archive-shelf", "archive-note", "archive-evidence-key"):
            self.assertIn(token, self.index_html + self.app_js + self.styles_css)

    def test_bdd_4_core_states_are_visible_and_keyboard_friendly(self) -> None:
        """行为 4：hover、focus、loading、empty、error 状态必须齐全。"""
        for token in (
            ":focus-visible",
            ".archive-note:hover",
            ".archive-link:hover",
            ".is-loading",
            ".empty-state",
            ".error-banner",
            "aria-live",
        ):
            self.assertIn(token, self.index_html + self.app_js + self.styles_css)

    def test_bdd_5_no_new_framework_or_marketing_shell(self) -> None:
        """行为 5：保留 vanilla 技术栈，不引入 landing page 框架。"""
        for forbidden in ("react", "vite", "next/head", "hero-section", "marketing-hero"):
            self.assertNotIn(forbidden, (self.index_html + self.app_js).lower())


if __name__ == "__main__":
    unittest.main()

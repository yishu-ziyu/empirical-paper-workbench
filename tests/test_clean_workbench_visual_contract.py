from __future__ import annotations

import re
import unittest
from pathlib import Path


class CleanWorkbenchVisualContractTests(unittest.TestCase):
    """BDD: 研究工作台必须更干净、可扫读，并修复数据页重叠问题。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")
        cls.all_frontend = cls.index_html + cls.app_js + cls.styles_css

    def test_bdd_1_shell_removes_grid_paper_noise(self) -> None:
        """行为 1：全局背景应干净，不再使用明显纸格噪音。"""
        self.assertIn("clean-workbench-shell", self.index_html + self.styles_css)
        self.assertIn("--surface-clean", self.styles_css)
        self.assertNotIn("28px 28px", self.styles_css)
        self.assertNotIn("radial-gradient(circle at 20% 0%", self.styles_css)

    def test_bdd_2_variable_role_entry_has_no_overlap_prone_two_column_auto(self) -> None:
        """行为 2：变量确认入口不能用易重叠的 auto 双列布局。"""
        self.assertIn("research-record-card", self.app_js)
        self.assertIn("research-step-list", self.app_js)
        self.assertRegex(
            self.styles_css,
            re.compile(r"\.variable-role-workflow-layout\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)", re.S),
        )
        self.assertIn("overflow-wrap: anywhere", self.styles_css)
        self.assertNotIn("grid-template-columns: minmax(0, 1fr) auto;", self.styles_css)

    def test_bdd_3_archive_inspector_is_compact_property_rail(self) -> None:
        """行为 3：右侧档案索引应成为紧凑属性检查器。"""
        for token in ("inspector-rail", "inspector-section", "inspector-link-list"):
            self.assertIn(token, self.all_frontend)
        self.assertIn("属性检查器", self.index_html)

    def test_bdd_4_nested_cards_use_records_not_large_cards(self) -> None:
        """行为 4：子对象使用 record/list，不继续堆大卡片。"""
        for token in ("research-record-card", "record-meta-grid", "record-path", "compact-action-row"):
            self.assertIn(token, self.all_frontend)

    def test_bdd_5_keeps_existing_stack(self) -> None:
        """行为 5：不引入新前端框架或 API 迁移。"""
        for forbidden in ("react", "vite", "next/head", "tailwind"):
            self.assertNotIn(forbidden, (self.index_html + self.app_js).lower())


if __name__ == "__main__":
    unittest.main()

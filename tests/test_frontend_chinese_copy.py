from __future__ import annotations

import unittest
from pathlib import Path


class FrontendChineseCopyTests(unittest.TestCase):
    """BDD: 所有用户可见页面文案必须使用同义中文。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    def test_bdd_1_primary_navigation_uses_chinese_lifecycle_labels(self) -> None:
        """行为 1：一级导航必须使用中文研究生命周期名称。"""
        for text in ["工作台首页", "数据与设计", "实证执行", "结果与草稿", "审阅与导出"]:
            self.assertIn(text, self.index_html)

        for text in ["Workspace Home", "Data & Design", "Execution", "Results & Draft", "Review & Export"]:
            self.assertNotIn(text, self.index_html)

    def test_bdd_2_stage_pages_use_chinese_product_object_names(self) -> None:
        """行为 2：核心阶段页面必须把产品对象名称中文化。"""
        for text in ["变量角色集", "研究设计方案", "执行计划", "结果论断卡", "草稿证据绑定", "正文候选"]:
            self.assertIn(text, self.index_html + self.app_js)

        for text in ["VariableRoleSet", "DesignSpec", "RunPlan", "FindingCard", "Manuscript candidates"]:
            self.assertNotIn(text, self.index_html)

    def test_bdd_3_execution_and_export_panels_use_chinese_panel_names(self) -> None:
        """行为 3：执行与导出页面必须把内部英文面板名称改成中文。"""
        for text in ["阶段看板", "事件流", "人工确认点", "产物与证据", "前沿工程评估器"]:
            self.assertIn(text, self.index_html + self.app_js)

        for text in ["Step Board", "Event Stream", "Human-in-the-loop", "Artifacts / Evidence", "Frontier-Eng evaluator"]:
            self.assertNotIn(text, self.index_html)

    def test_bdd_4_dynamic_copy_uses_chinese_action_and_status_words(self) -> None:
        """行为 4：动态渲染文案必须避免英文操作标签。"""
        for text in ["已就绪", "已阻塞", "打开数据与设计", "本轮评估通过", "数据质量画像", "确认变量角色", "productTermLabel"]:
            self.assertIn(text, self.app_js)

        for text in [
            "Queued",
            "Planning",
            "Reviewing",
            "打开 Data & Design",
            '<span class="eyebrow">dataset_quality_profile</span>',
            '<span class="eyebrow">confirm_variable_roles</span>',
        ]:
            self.assertNotIn(text, self.app_js)

    def test_bdd_5_backend_contract_terms_are_translated_before_display(self) -> None:
        """行为 5：后端返回的契约名必须在显示层映射成中文。"""
        for text in ["变量角色集", "研究设计方案", "执行计划", "智能体控制台", "启动完整执行"]:
            self.assertIn(text, self.app_js)

        for raw in ["VariableRoleSet", "DesignSpec", "RunPlan"]:
            self.assertIn(raw, self.app_js)


if __name__ == "__main__":
    unittest.main()

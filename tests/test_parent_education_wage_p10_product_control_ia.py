from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT_PATH = ROOT / "Product/web-react/src/components/ProductControlP0Panel.tsx"
STYLES_PATH = ROOT / "Product/web-react/src/styles.css"


class ParentEducationWageP10ProductControlIATests(unittest.TestCase):
    """BDD: P10 makes Product Control current-gate-first instead of stage-stack-first."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.component = COMPONENT_PATH.read_text(encoding="utf-8")
        cls.app = (ROOT / "Product/web-react/src/App.tsx").read_text(encoding="utf-8")
        cls.styles = STYLES_PATH.read_text(encoding="utf-8")

    def test_bdd_p10a_current_gate_summary_is_first_class_surface(self) -> None:
        """行为 1：Product Control 顶部必须先解释当前卡点。"""
        self.assertIn("product-control-gate-summary", self.component)
        self.assertIn("当前门禁", self.component)
        self.assertIn("P9 正式变量表保存", self.component)
        self.assertIn("blocked_missing_dataset_source_metadata", self.component)
        self.assertIn("不能保存正式变量表", self.component)
        self.assertIn("不能创建 run id", self.component)
        self.assertIn("不能跑模型", self.component)
        self.assertIn(".product-control-gate-summary", self.styles)

    def test_bdd_p10b_history_stages_are_collapsed_by_default(self) -> None:
        """行为 2：P0-P8 历史阶段必须默认折叠，不再线性摊开。"""
        self.assertIn("<details className=\"product-control-stage-history\"", self.component)
        self.assertIn("<summary>", self.component)
        self.assertIn("阶段历史", self.component)
        self.assertIn("P7 已完成", self.component)
        self.assertIn("P8 已审批", self.component)
        self.assertIn("P9 等待 source metadata", self.component)
        self.assertNotIn("<details className=\"product-control-stage-history\" open", self.component)

    def test_bdd_p10c_p9_detail_keeps_formal_boundaries_and_no_model_entry(self) -> None:
        """行为 3：P9 仍保留细节和禁用边界，但不能出现模型执行入口。"""
        self.assertIn("product-control-current-gate-detail", self.component)
        self.assertIn("missing_source_metadata_fields", self.component)
        self.assertIn("save_formal_variable_roles_from_p8_approved_draft", self.component)
        self.assertIn("不写 DesignSpec；不写 RunPlan；不跑模型", self.component)
        self.assertIn("保存正式变量表", self.component)
        self.assertNotIn(">运行模型<", self.component)

    def test_bdd_p10d_current_gate_summary_stacks_on_mobile(self) -> None:
        """行为 4：移动端当前门禁摘要必须单列显示，不能让 blockers 压住标题。"""
        self.assertIn("@media (max-width: 720px)", self.styles)
        self.assertIn(
            ".product-control-gate-summary,\n  .product-control-stage-history summary",
            self.styles,
        )
        self.assertIn("grid-template-columns: 1fr", self.styles)

    def test_bdd_p10e_paper_production_renders_before_generic_stage_tabs(self) -> None:
        """行为 5：论文生产状态必须出现在通用研究阶段导航之前。"""
        product_control_index = self.app.index("<PaperProductionStatusPanel")
        slide_tabs_index = self.app.index("<SlideTabs")
        self.assertLess(product_control_index, slide_tabs_index)


if __name__ == "__main__":
    unittest.main(verbosity=2)

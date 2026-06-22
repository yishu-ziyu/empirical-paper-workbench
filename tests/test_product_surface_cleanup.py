from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_SRC = ROOT / "Product" / "web-react" / "src"


class ProductSurfaceCleanupTests(unittest.TestCase):
    """BDD: 当前产品入口必须从旧 demo/P-stage surface 中清出来。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app_tsx = (WEB_REACT_SRC / "App.tsx").read_text(encoding="utf-8")
        cls.fastapi_app = (ROOT / "Product" / "app.py").read_text(encoding="utf-8")
        cls.product_map = (ROOT / "docs" / "current-product-map.md").read_text(encoding="utf-8")

    def test_bdd_1_main_entry_mounts_paper_pipeline_not_p0_panel(self) -> None:
        """行为 1：React 主入口只挂论文生产状态，不挂旧 P0 聚合面板。"""

        self.assertIn("PaperProductionStatusPanel", self.app_tsx)
        self.assertIn("<PaperProductionStatusPanel", self.app_tsx)
        self.assertNotIn("ProductControlP0Panel", self.app_tsx)
        self.assertNotIn("<ProductControlP0Panel", self.app_tsx)
        self.assertNotIn("analysis-workspace__technical-details", self.app_tsx)

    def test_bdd_2_legacy_static_frontend_source_is_removed_from_runtime(self) -> None:
        """行为 2：旧静态前端源码不再作为可服务入口存在。"""

        for relative_path in (
            "Product/web/index.html",
            "Product/web/assets/app.js",
            "Product/web/assets/styles.css",
            "Product/web/styles/components.css",
            "Product/web/styles/nothing-tokens.css",
        ):
            self.assertFalse((ROOT / relative_path).exists(), relative_path)

        self.assertNotIn("WEB_ROOT", self.fastapi_app)
        self.assertNotIn('app.mount("/assets"', self.fastapi_app)
        self.assertIn("def legacy_index", self.fastapi_app)
        self.assertIn('RedirectResponse(url="/", status_code=307)', self.fastapi_app)

    def test_bdd_3_product_map_names_react_as_the_only_current_shell(self) -> None:
        """行为 3：产品地图不能继续把 legacy shell 描述成当前入口。"""

        self.assertIn("唯一当前产品壳", self.product_map)
        self.assertIn("Product/web-react/src/App.tsx", self.product_map)
        self.assertIn("Product/web 已移除", self.product_map)
        self.assertNotIn("Legacy shell：`Product/web/index.html`", self.product_map)


if __name__ == "__main__":
    unittest.main()

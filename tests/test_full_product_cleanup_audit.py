from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FullProductCleanupAuditTests(unittest.TestCase):
    """BDD: 全量清理后，当前产品说明不能再把旧入口说成主线。"""

    def test_bdd_current_docs_name_one_runtime_entry_and_removed_static_shell(self) -> None:
        """当前 README 和产品地图必须指向 React + FastAPI，不再指向 Product/web。"""

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        product_readme = (ROOT / "Product" / "README.md").read_text(encoding="utf-8")
        product_map = (ROOT / "docs" / "current-product-map.md").read_text(encoding="utf-8")

        combined = "\n".join([readme, product_readme, product_map])

        self.assertIn("Product/web-react/src/App.tsx", combined)
        self.assertIn("Product/app.py", combined)
        self.assertIn("Product/web 已移除", combined)
        self.assertNotIn("`web/`：前端静态页面", combined)
        self.assertNotIn("静态前端产品壳", combined)

    def test_bdd_audit_file_classifies_history_without_making_it_current(self) -> None:
        """历史 P 阶段可以作为证据，但必须被降级，不能继续伪装成当前产品。"""

        audit = (ROOT / "Tasks" / "full-product-cleanup-audit-2026-06-19.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("当前主推进线：CGSS 论文生产链", audit)
        self.assertIn("已删除", audit)
        self.assertIn("暂不删除但降级为历史证据", audit)
        self.assertIn("ProductControlP0Panel.tsx", audit)
        self.assertIn("不能作为用户产品语言", audit)

    def test_bdd_no_legacy_static_runtime_directory_remains(self) -> None:
        """旧 Product/web 目录本身也不能留下空壳入口。"""

        self.assertFalse((ROOT / "Product" / "web").exists())


if __name__ == "__main__":
    unittest.main()

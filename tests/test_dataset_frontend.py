from __future__ import annotations

import unittest
from pathlib import Path


class DatasetFrontendTests(unittest.TestCase):
    """BDD: 数据与变量页必须展示真实数据文件证据，而不是旧 mock 字段。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    def test_bdd_1_dataset_card_shows_path_role_and_evidence(self) -> None:
        """行为 1：数据集卡片必须显示 path、role 和 evidence_level。"""
        self.assertIn("ds.path", self.app_js)
        self.assertIn("ds.role", self.app_js)
        self.assertIn("renderEvidenceBadge(ds)", self.app_js)

    def test_bdd_2_dataset_card_uses_real_shape_fields(self) -> None:
        """行为 2：数据集卡片必须使用 row_count/column_count 展示真实 schema 摘要。"""
        self.assertIn("ds.row_count", self.app_js)
        self.assertIn("ds.column_count", self.app_js)

    def test_bdd_3_dataset_card_routes_to_variable_role_confirmation_before_run(self) -> None:
        """行为 3：数据卡片必须先进入变量角色确认，而不是直接启动 run。"""
        self.assertIn("data-open-design-action", self.app_js)
        self.assertIn("检查并确认变量角色", self.app_js)
        self.assertIn("state.selectedDatasetPath", self.app_js)
        self.assertNotIn("用此数据启动试运行", self.app_js)

    def test_bdd_4_run_creation_payload_includes_dataset_path(self) -> None:
        """行为 4：启动 run 的前端 payload 必须包含 dataset_path。"""
        self.assertIn("create(projectId, mode, datasetPath", self.app_js)
        self.assertIn("dataset_path: datasetPath", self.app_js)


if __name__ == "__main__":
    unittest.main()

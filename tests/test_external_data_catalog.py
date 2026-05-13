from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ExternalDataCatalogApiTests(unittest.TestCase):
    """BDD: 真实数据仓库必须作为只读候选池进入产品，而不是伪装成项目内数据。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.original_library_root = os.environ.get("EMPIRICAL_DATA_LIBRARY_ROOT")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="external-data-catalog-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.external_root = self.temp_dir / "实证数据库"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        self._create_external_library(self.external_root)
        os.environ["EMPIRICAL_DATA_LIBRARY_ROOT"] = str(self.external_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "external-data-catalog",
                "title": "External Data Catalog Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        if self.original_library_root is None:
            os.environ.pop("EMPIRICAL_DATA_LIBRARY_ROOT", None)
        else:
            os.environ["EMPIRICAL_DATA_LIBRARY_ROOT"] = self.original_library_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_dataset_api_returns_read_only_external_catalog(self) -> None:
        """行为 1：datasets API 必须返回只读真实数据候选池。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        self.assertEqual(response.status_code, 200, msg=response.text)
        catalog = response.json()["external_catalog"]
        self.assertEqual(catalog["evidence_level"], "local_file")
        self.assertTrue(catalog["read_only"])
        self.assertTrue(catalog["exists"])
        self.assertEqual(catalog["root"], str(self.external_root))
        self.assertGreaterEqual(catalog["total_count"], 2)
        charls = self._external_item_by_name(catalog, "CHARLS.csv")
        self.assertEqual(charls["role"], "external_candidate_dataset")
        self.assertEqual(charls["evidence_level"], "local_file")
        self.assertTrue(charls["read_only"])

    def test_bdd_2_external_csv_has_preview_quality_profile(self) -> None:
        """行为 2：外部 CSV 候选数据必须返回轻量画像。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        charls = self._external_item_by_name(response.json()["external_catalog"], "CHARLS.csv")
        profile = charls["quality_profile"]
        self.assertEqual(profile["profile_scope"], "catalog_preview")
        self.assertEqual(profile["evidence_level"], "local_file")
        self.assertTrue(profile["supported"])
        self.assertEqual(profile["row_count"], 2)
        self.assertEqual(profile["column_count"], 3)
        self.assertEqual(profile["missing_cells"], 1)
        self.assertEqual(profile["readiness_status"], "needs_review")

    def test_bdd_3_unprofiled_external_formats_stay_visible(self) -> None:
        """行为 3：DTA 等暂未画像格式也必须保留在真实候选池。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        cfps = self._external_item_by_name(response.json()["external_catalog"], "cfps2020person_202306.dta")
        self.assertEqual(cfps["file_type"], "dta")
        self.assertEqual(cfps["quality_profile"]["readiness_status"], "not_profiled")
        self.assertFalse(cfps["quality_profile"]["supported"])

    def _external_item_by_name(self, catalog: dict, name: str) -> dict:
        for item in catalog["items"]:
            if item["name"] == name:
                return item
        self.fail(f"External item {name} not found in {catalog['items']}")

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: external-data-catalog\n  title: External Data Catalog Project\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu\n10,1,16\n12,0,14\n",
            encoding="utf-8",
        )

    @staticmethod
    def _create_external_library(external_root: Path) -> None:
        (external_root / "外部源数据" / "CFPS2020").mkdir(parents=True)
        (external_root / "外部源数据" / "CHARLS.csv").write_text(
            "pid,wage,trained\n1,10,1\n2,,0\n",
            encoding="utf-8",
        )
        (external_root / "外部源数据" / "CFPS2020" / "cfps2020person_202306.dta").write_bytes(b"dta-placeholder")


class ExternalDataCatalogFrontendTests(unittest.TestCase):
    """BDD: 数据页必须把真实数据候选池渲染成独立研究资产。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_4_data_page_separates_external_catalog_from_project_data(self) -> None:
        """行为 4：前端必须单独渲染真实数据候选池。"""
        self.assertIn("external-data-library-panel", self.index_html)
        self.assertIn("external-datasets-list", self.index_html)
        self.assertIn("renderExternalDataLibrary", self.app_js)
        self.assertIn("真实数据候选池", self.app_js)
        self.assertIn("visibleItems", self.app_js)
        self.assertIn("已显示前 ${visibleItems.length} 个候选文件", self.app_js)
        self.assertIn("external-dataset-card", self.styles)

    def test_bdd_5_external_catalog_has_empty_state(self) -> None:
        """行为 5：前端必须为未配置真实数据库提供空状态。"""
        self.assertIn("external_catalog", self.app_js)
        self.assertIn("尚未找到真实数据仓库", self.app_js)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class DatasetQualityProfileApiTests(unittest.TestCase):
    """BDD: 数据集必须先形成可审计质量画像，再进入变量角色和研究设计。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dataset-quality-profile-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "dataset-quality",
                "title": "Dataset Quality Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_dataset_api_returns_local_file_quality_profile(self) -> None:
        """行为 1：datasets API 必须返回来自本地文件证据的数据质量画像。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        self.assertEqual(response.status_code, 200, msg=response.text)
        dataset = self._dataset_by_path(response.json(), "Data/Final/analysis_sample.csv")
        profile = dataset["quality_profile"]
        self.assertEqual(profile["evidence_level"], "local_file")
        self.assertEqual(profile["row_count"], 2)
        self.assertEqual(profile["column_count"], 4)
        self.assertIn("columns", profile)
        self.assertIn("checks", profile)

    def test_bdd_2_missing_values_mark_dataset_as_needs_review(self) -> None:
        """行为 2：存在缺失值时质量画像必须进入 needs_review，而不是 ready。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        dataset = self._dataset_by_path(response.json(), "Data/Final/analysis_sample.csv")
        profile = dataset["quality_profile"]
        self.assertEqual(profile["missing_cells"], 1)
        self.assertEqual(profile["missing_rate"], 0.125)
        self.assertEqual(profile["numeric_column_count"], 3)
        self.assertEqual(profile["text_column_count"], 1)
        self.assertEqual(profile["readiness_status"], "needs_review")
        checks = {item["id"]: item["status"] for item in profile["checks"]}
        self.assertEqual(checks["missing_values_checked"], "warning")

    def test_bdd_3_clean_csv_can_be_ready_for_variable_role_confirmation(self) -> None:
        """行为 3：有字段、有样本且无缺失的 CSV 可以进入 ready。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        dataset = self._dataset_by_path(response.json(), "Data/Final/clean_sample.csv")
        profile = dataset["quality_profile"]
        self.assertEqual(profile["missing_cells"], 0)
        self.assertEqual(profile["missing_rate"], 0)
        self.assertEqual(profile["readiness_status"], "ready")

    def test_bdd_4_unprofiled_dataset_keeps_local_file_evidence(self) -> None:
        """行为 4：暂未解析的真实文件也必须保留本地证据，并标记 not_profiled。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        dataset = self._dataset_by_path(response.json(), "Data/Raw/source_data.dta")
        profile = dataset["quality_profile"]
        self.assertEqual(dataset["evidence_level"], "local_file")
        self.assertEqual(profile["evidence_level"], "local_file")
        self.assertFalse(profile["supported"])
        self.assertEqual(profile["readiness_status"], "not_profiled")

    def _dataset_by_path(self, payload: dict, path: str) -> dict:
        for item in payload["items"]:
            if item["path"] == path:
                return item
        self.fail(f"Dataset path {path} not found in {payload['items']}")

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Data" / "Raw").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: dataset-quality\n  title: Dataset Quality Project\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,sector\n10,1,16,manufacturing\n12,0,,services\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "clean_sample.csv").write_text(
            "wage,trained,edu,sector\n10,1,16,manufacturing\n12,0,14,services\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Raw" / "source_data.dta").write_bytes(b"placeholder")


class DatasetQualityProfileFrontendTests(unittest.TestCase):
    """BDD: 数据页必须把质量画像作为可浏览研究对象展示。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_data_page_has_quality_profile_panel(self) -> None:
        """行为 5：数据页必须有数据质量画像面板。"""
        self.assertIn("data-quality-profile-panel", self.index_html)
        self.assertIn("data-quality-profile-body", self.index_html)
        self.assertIn("renderDatasetQualityProfile", self.app_js)
        self.assertIn("quality_profile", self.app_js)

    def test_bdd_6_frontend_surfaces_quality_metrics_and_readiness(self) -> None:
        """行为 6：前端必须展示缺失率、字段类型和 ready 状态。"""
        self.assertIn("missing_rate", self.app_js)
        self.assertIn("numeric_column_count", self.app_js)
        self.assertIn("text_column_count", self.app_js)
        self.assertIn("readiness_status", self.app_js)
        self.assertIn("quality-profile-grid", self.styles)


if __name__ == "__main__":
    unittest.main()

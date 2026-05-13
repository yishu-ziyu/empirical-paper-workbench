from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ExternalDatasetBindPreflightApiTests(unittest.TestCase):
    """BDD: 真实候选数据进入项目之前，必须先生成只读导入/绑定预检。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.original_library_root = os.environ.get("EMPIRICAL_DATA_LIBRARY_ROOT")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="external-bind-preflight-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.external_root = self.temp_dir / "实证数据库"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        self.external_file = self._create_external_library(self.external_root)
        os.environ["EMPIRICAL_DATA_LIBRARY_ROOT"] = str(self.external_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "external-bind-preflight",
                "title": "External Bind Preflight Project",
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

    def test_bdd_1_external_candidate_generates_bind_preflight(self) -> None:
        """行为 1：候选池文件可以生成 ready_for_review 预检对象。"""
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight",
            json={
                "source_path": str(self.external_file),
                "strategy": "copy_to_project_raw",
                "note": "准备用真实 CHARLS 样本替换演示数据前先做预检。",
            },
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        preflight = response.json()["preflight"]
        self.assertEqual(preflight["status"], "ready_for_review")
        self.assertEqual(preflight["evidence_level"], "local_file")
        self.assertEqual(preflight["source"]["path"], str(self.external_file))
        self.assertEqual(preflight["target"]["path"], "Data/Raw/CHARLS.csv")
        self.assertEqual(preflight["strategy"], "copy_to_project_raw")
        self.assertEqual(preflight["manifest_path"], "state/product/dataset_import_preflights.json")
        self.assertTrue(all(check["status"] == "passed" for check in preflight["checks"]))

    def test_bdd_2_preflight_does_not_copy_or_mutate_files(self) -> None:
        """行为 2：预检只写状态文件，不复制或修改数据文件。"""
        original = self.external_file.read_text(encoding="utf-8")
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight",
            json={"source_path": str(self.external_file), "strategy": "copy_to_project_raw"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        preflight = response.json()["preflight"]
        self.assertFalse(preflight["will_mutate_source"])
        self.assertFalse(preflight["will_create_project_file"])
        self.assertEqual(self.external_file.read_text(encoding="utf-8"), original)
        self.assertFalse((self.project_root / "Data" / "Raw" / "CHARLS.csv").exists())
        self.assertTrue((self.project_root / "state" / "product" / "dataset_import_preflights.json").exists())

    def test_bdd_3_rejects_paths_outside_external_catalog(self) -> None:
        """行为 3：候选池外部路径必须被拒绝。"""
        outside = self.temp_dir / "outside.csv"
        outside.write_text("id,y\n1,2\n", encoding="utf-8")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight",
            json={"source_path": str(outside), "strategy": "copy_to_project_raw"},
        )

        self.assertEqual(response.status_code, 400, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "invalid_external_dataset_path")

    def test_bdd_4_datasets_api_exposes_latest_bind_preflight(self) -> None:
        """行为 4：数据页刷新时能读取最新导入/绑定预检。"""
        self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight",
            json={"source_path": str(self.external_file), "strategy": "copy_to_project_raw"},
        )

        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        self.assertEqual(response.status_code, 200, msg=response.text)
        preflight = response.json()["external_import_preflight"]
        self.assertEqual(preflight["status"], "ready_for_review")
        self.assertEqual(preflight["source"]["name"], "CHARLS.csv")
        self.assertFalse(preflight["will_create_project_file"])

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: external-bind-preflight\n  title: External Bind Preflight Project\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu\n10,1,16\n12,0,14\n",
            encoding="utf-8",
        )

    @staticmethod
    def _create_external_library(external_root: Path) -> Path:
        source = external_root / "外部源数据" / "CHARLS.csv"
        source.parent.mkdir(parents=True)
        source.write_text("pid,wage,trained\n1,10,1\n2,12,0\n", encoding="utf-8")
        return source


class ExternalDatasetBindPreflightFrontendTests(unittest.TestCase):
    """BDD: 数据页必须提供真实候选数据预检动作和状态展示。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_external_dataset_cards_offer_preflight_action(self) -> None:
        """行为 5：真实候选数据卡必须提供导入/绑定预检动作。"""
        self.assertIn("external-bind-preflight-panel", self.index_html)
        self.assertIn("data-external-bind-preflight-action", self.app_js)
        self.assertIn("requestExternalBindPreflight", self.app_js)
        self.assertIn("datasets/external-bind-preflight", self.app_js)
        self.assertIn("external-bind-preflight-panel", self.styles)


if __name__ == "__main__":
    unittest.main()

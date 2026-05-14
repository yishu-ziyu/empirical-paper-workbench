from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ExternalDatasetImportApplyApiTests(unittest.TestCase):
    """BDD: 真实候选数据预检通过后，必须由用户显式确认接入项目。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.original_library_root = os.environ.get("EMPIRICAL_DATA_LIBRARY_ROOT")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="external-import-apply-"))
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
                "slug": "external-import-apply",
                "title": "External Import Apply Project",
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

    def test_bdd_1_local_copy_apply_creates_project_dataset_with_hash(self) -> None:
        """行为 1：本地版本确认导入后，文件进入项目 Data/Raw 并记录哈希。"""
        preflight_id = self._create_preflight()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight/{preflight_id}/apply",
            json={"action": "copy_to_project_raw", "runtime_mode": "local", "note": "确认导入本地 CHARLS 样本。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        applied = response.json()["dataset_import"]
        target = self.project_root / "Data" / "Raw" / "CHARLS.csv"
        self.assertEqual(applied["status"], "applied")
        self.assertEqual(applied["action"], "copy_to_project_raw")
        self.assertEqual(applied["target"]["path"], "Data/Raw/CHARLS.csv")
        self.assertEqual(applied["target"]["sha256"], self._sha256(self.external_file))
        self.assertTrue(applied["created_project_file"])
        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(encoding="utf-8"), self.external_file.read_text(encoding="utf-8"))

        datasets = self.client.get(f"/api/v1/projects/{self.project_id}/datasets").json()
        self.assertTrue(any(item["path"] == "Data/Raw/CHARLS.csv" for item in datasets["items"]))

    def test_bdd_2_local_bind_apply_records_external_reference_without_copy(self) -> None:
        """行为 2：本地版本仅绑定引用时，不复制文件但写入绑定记录。"""
        preflight_id = self._create_preflight()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight/{preflight_id}/apply",
            json={"action": "bind_external_reference", "runtime_mode": "local", "note": "文件较大，仅绑定本地引用。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        applied = response.json()["dataset_import"]
        self.assertEqual(applied["status"], "applied")
        self.assertEqual(applied["action"], "bind_external_reference")
        self.assertEqual(applied["binding"]["mode"], "external_reference")
        self.assertEqual(applied["source"]["path"], str(self.external_file))
        self.assertEqual(applied["source"]["sha256"], self._sha256(self.external_file))
        self.assertFalse(applied["created_project_file"])
        self.assertFalse((self.project_root / "Data" / "Raw" / "CHARLS.csv").exists())

    def test_bdd_3_cancel_preflight_does_not_create_dataset(self) -> None:
        """行为 3：取消预检只废弃状态，不创建项目数据。"""
        preflight_id = self._create_preflight()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight/{preflight_id}/apply",
            json={"action": "cancel", "runtime_mode": "local", "note": "选错数据，取消。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        applied = response.json()["dataset_import"]
        self.assertEqual(applied["status"], "cancelled")
        self.assertEqual(applied["action"], "cancel")
        self.assertFalse(applied["created_project_file"])
        self.assertFalse((self.project_root / "Data" / "Raw" / "CHARLS.csv").exists())

    def test_bdd_4_cloud_runtime_rejects_local_path_apply(self) -> None:
        """行为 4：线上版本不能直接复制或绑定本机路径。"""
        preflight_id = self._create_preflight()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight/{preflight_id}/apply",
            json={"action": "bind_external_reference", "runtime_mode": "cloud"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "cloud_upload_required")
        self.assertFalse((self.project_root / "Data" / "Raw" / "CHARLS.csv").exists())

    def _create_preflight(self) -> str:
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight",
            json={"source_path": str(self.external_file), "strategy": "copy_to_project_raw"},
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        return response.json()["preflight"]["id"]

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: external-import-apply\n  title: External Import Apply Project\n"
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

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


class ExternalDatasetImportApplyFrontendTests(unittest.TestCase):
    """BDD: 前端必须把预检后的三个用户动作说清楚。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_preflight_panel_exposes_apply_cancel_actions(self) -> None:
        """行为 5：预检面板提供确认导入、仅绑定引用、取消三个真实动作。"""
        self.assertIn("external-bind-preflight-panel", self.index_html)
        self.assertIn("data-external-preflight-apply-action", self.app_js)
        self.assertIn("requestExternalPreflightApply", self.app_js)
        self.assertIn("确认导入到项目", self.app_js)
        self.assertIn("只绑定引用", self.app_js)
        self.assertIn("取消预检", self.app_js)
        self.assertIn("datasets/external-bind-preflight", self.app_js)
        self.assertIn("preflight-action-row", self.styles)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ExternalDatasetImportProfileApiTests(unittest.TestCase):
    """BDD: 已显式接入的真实数据必须先生成安全字段画像，再进入研究设计。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.original_library_root = os.environ.get("EMPIRICAL_DATA_LIBRARY_ROOT")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="external-import-profile-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.external_root = self.temp_dir / "实证数据库"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        self.external_csv = self._create_external_csv(self.external_root)
        self.external_dta = self._create_external_dta(self.external_root)
        os.environ["EMPIRICAL_DATA_LIBRARY_ROOT"] = str(self.external_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "external-import-profile",
                "title": "External Import Profile Project",
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

    def test_bdd_1_copied_csv_import_generates_field_dictionary_profile(self) -> None:
        """行为 1：复制导入的 CSV 可以生成字段画像，并持久化到 datasets API。"""
        dataset_import_id = self._apply_dataset_import(self.external_csv, "copy_to_project_raw")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/profile",
            json={"row_limit": 200},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        profile = response.json()["dataset_import_profile"]
        self.assertEqual(profile["status"], "profiled")
        self.assertEqual(profile["evidence_level"], "local_file")
        self.assertEqual(profile["dataset_import_id"], dataset_import_id)
        self.assertEqual(profile["source"]["sha256"], self._sha256(self.external_csv))
        self.assertFalse(profile["can_feed_variable_roles"])
        self.assertEqual(profile["quality_profile"]["row_count"], 2)
        self.assertEqual([field["name"] for field in profile["fields"]], ["pid", "wage", "trained"])
        self.assertEqual(profile["fields"][0]["inferred_type"], "numeric")

        datasets = self.client.get(f"/api/v1/projects/{self.project_id}/datasets").json()
        self.assertEqual(datasets["external_import_profile"]["id"], profile["id"])
        self.assertEqual(datasets["external_import_profile"]["dataset_import_id"], dataset_import_id)

    def test_bdd_2_bound_external_reference_profiles_without_copying_file(self) -> None:
        """行为 2：仅绑定外部引用时，也能从只读本机路径读取字段结构。"""
        dataset_import_id = self._apply_dataset_import(self.external_csv, "bind_external_reference")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/profile",
            json={"row_limit": 200},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        profile = response.json()["dataset_import_profile"]
        self.assertEqual(profile["status"], "profiled")
        self.assertEqual(profile["binding"]["mode"], "external_reference")
        self.assertTrue(profile["binding"]["read_only"])
        self.assertFalse((self.project_root / "Data" / "Raw" / "CHARLS.csv").exists())
        self.assertEqual(profile["source"]["path"], str(self.external_csv))

    def test_bdd_3_valid_dta_import_generates_metadata_only_field_profile(self) -> None:
        """行为 3：有效 DTA 以 metadata-only 方式生成变量字典画像。"""
        dataset_import_id = self._apply_dataset_import(self.external_dta, "bind_external_reference")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/profile",
            json={"row_limit": 200},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        profile = response.json()["dataset_import_profile"]
        self.assertEqual(profile["status"], "profiled")
        self.assertEqual(profile["readiness_status"], "ready")
        self.assertEqual(profile["quality_profile"]["row_count"], 2)
        self.assertEqual(profile["quality_profile"]["column_count"], 4)
        self.assertEqual(profile["quality_profile"]["row_count_source"], "metadata_only")
        self.assertEqual([field["name"] for field in profile["fields"]], ["pid", "wage", "trained", "name"])
        self.assertEqual(profile["fields"][1]["label"], "hourly wage")
        self.assertEqual(profile["fields"][1]["stata_type"], "double")
        self.assertEqual(profile["fields"][3]["inferred_type"], "text")
        self.assertFalse(profile["can_feed_variable_roles"])
        self.assertIsNone(profile["blocking_reason"])

    def test_bdd_4_malformed_dta_returns_blocked_profile_without_fake_fields(self) -> None:
        """行为 4：损坏 DTA 必须返回阻塞画像，不能伪造字段或抛 500。"""
        malformed_dta = self.external_root / "外部源数据" / "BROKEN.dta"
        malformed_dta.write_bytes(b"stata-dta-placeholder")
        dataset_import_id = self._apply_dataset_import(malformed_dta, "bind_external_reference")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/profile",
            json={"row_limit": 200},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        profile = response.json()["dataset_import_profile"]
        self.assertEqual(profile["status"], "blocked")
        self.assertEqual(profile["readiness_status"], "not_profiled")
        self.assertEqual(profile["fields"], [])
        self.assertFalse(profile["can_feed_variable_roles"])
        self.assertIn("DTA 读取失败", profile["blocking_reason"])

    def test_bdd_5_changed_external_source_is_rejected_before_profile(self) -> None:
        """行为 5：外部绑定文件变化后，必须阻止画像以保护 provenance。"""
        dataset_import_id = self._apply_dataset_import(self.external_csv, "bind_external_reference")
        self.external_csv.write_text("pid,wage,trained\n1,99,1\n", encoding="utf-8")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/profile",
            json={"row_limit": 200},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "dataset_import_source_changed")

    def test_bdd_6_cancelled_import_cannot_be_profiled(self) -> None:
        """行为 6：已取消的导入记录不能进入字段画像。"""
        dataset_import_id = self._apply_dataset_import(self.external_csv, "cancel")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/profile",
            json={"row_limit": 200},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "dataset_import_not_profileable")

    def _apply_dataset_import(self, source: Path, action: str) -> str:
        preflight = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight",
            json={"source_path": str(source), "strategy": "copy_to_project_raw"},
        )
        self.assertEqual(preflight.status_code, 201, msg=preflight.text)
        preflight_id = preflight.json()["preflight"]["id"]
        applied = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/external-bind-preflight/{preflight_id}/apply",
            json={"action": action, "runtime_mode": "local"},
        )
        self.assertEqual(applied.status_code, 200, msg=applied.text)
        return applied.json()["dataset_import"]["id"]

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: external-import-profile\n  title: External Import Profile Project\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu\n10,1,16\n12,0,14\n",
            encoding="utf-8",
        )

    @staticmethod
    def _create_external_csv(external_root: Path) -> Path:
        source = external_root / "外部源数据" / "CHARLS.csv"
        source.parent.mkdir(parents=True)
        source.write_text("pid,wage,trained\n1,10,1\n2,12,0\n", encoding="utf-8")
        return source

    @staticmethod
    def _create_external_dta(external_root: Path) -> Path:
        source = external_root / "外部源数据" / "CFPS.dta"
        source.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            {
                "pid": [1, 2],
                "wage": [10.5, 12.0],
                "trained": [1, 0],
                "name": ["a", "b"],
            }
        ).to_stata(
            source,
            write_index=False,
            variable_labels={
                "pid": "person id",
                "wage": "hourly wage",
                "trained": "training status",
                "name": "respondent name",
            },
        )
        return source

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


class ExternalDatasetImportProfileFrontendTests(unittest.TestCase):
    """BDD: 数据页必须提供字段画像入口，并说明不会自动推进研究状态。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_7_frontend_exposes_profile_entry_and_non_mutation_copy(self) -> None:
        """行为 7：前端必须有字段画像入口、画像面板和不改写研究状态说明。"""
        self.assertIn("dataset-import-profile-panel", self.index_html)
        self.assertIn("data-external-import-profile-action", self.app_js)
        self.assertIn("requestExternalImportProfile", self.app_js)
        self.assertIn("生成字段画像", self.app_js)
        self.assertIn("字段画像 / 变量字典预览", self.app_js)
        self.assertIn("变量标签", self.app_js)
        self.assertIn("Stata 类型", self.app_js)
        self.assertIn("不会改写 VariableRoleSet、DesignSpec 或 RunPlan", self.app_js)
        self.assertIn("dataset-import-profile-panel", self.styles)


if __name__ == "__main__":
    unittest.main()

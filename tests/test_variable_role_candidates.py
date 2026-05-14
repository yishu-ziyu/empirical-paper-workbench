from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class VariableRoleCandidateApiTests(unittest.TestCase):
    """BDD: 真实字段画像必须先生成可审阅候选，不能自动写入 VariableRoleSet。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.original_library_root = os.environ.get("EMPIRICAL_DATA_LIBRARY_ROOT")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="variable-role-candidates-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.external_root = self.temp_dir / "实证数据库"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        self.external_dta = self._create_external_dta(self.external_root)
        os.environ["EMPIRICAL_DATA_LIBRARY_ROOT"] = str(self.external_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "variable-role-candidates",
                "title": "Variable Role Candidates Project",
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

    def test_bdd_1_profiled_dta_import_generates_reviewable_candidate_without_formal_writeback(self) -> None:
        """行为 1：已画像 DTA 生成候选，但不写入正式 variable_roles.json。"""
        dataset_import_id = self._profile_dta_import()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/variable-role-candidates",
            json={"note": "根据真实 DTA 字段画像生成候选。"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        candidate = response.json()["variable_role_candidate"]
        self.assertEqual(candidate["status"], "needs_review")
        self.assertEqual(candidate["evidence_level"], "local_file")
        self.assertEqual(candidate["dataset_import_id"], dataset_import_id)
        self.assertEqual(candidate["source"]["sha256"], self._sha256(self.external_dta))
        self.assertFalse(candidate["can_apply_to_variable_roles"])
        self.assertTrue(candidate["does_not_mutate_variable_role_set"])
        self.assertEqual(candidate["candidate_roles"]["outcome"], ["wage"])
        self.assertEqual(candidate["candidate_roles"]["treatment"], ["trained"])
        self.assertIn("edu", candidate["candidate_roles"]["controls"])
        self.assertEqual([field["name"] for field in candidate["field_options"]], ["pid", "wage", "trained", "edu", "experience"])
        self.assertFalse((self.project_root / "state" / "product" / "variable_roles.json").exists())

    def test_bdd_2_approving_candidate_keeps_formal_variable_role_set_unchanged(self) -> None:
        """行为 2：审批候选只改变候选状态，不自动写入正式 VariableRoleSet。"""
        dataset_import_id = self._profile_dta_import()
        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/variable-role-candidates",
            json={"note": "生成待审候选。"},
        )
        self.assertEqual(generated.status_code, 201, msg=generated.text)
        candidate_id = generated.json()["variable_role_candidate"]["id"]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-role-candidates/{candidate_id}/review",
            json={
                "action": "approve_candidate",
                "note": "字段角色候选可以进入正式保存步骤，但还不写回。",
                "candidate_roles": {
                    "outcome": ["wage"],
                    "treatment": ["trained"],
                    "controls": ["edu", "experience"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
            },
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        candidate = response.json()["variable_role_candidate"]
        self.assertEqual(candidate["status"], "approved_candidate")
        self.assertTrue(candidate["can_apply_to_variable_roles"])
        self.assertEqual(candidate["candidate_roles"]["controls"], ["edu", "experience"])
        self.assertEqual(candidate["review_events"][-1]["action"], "approve_candidate")
        self.assertFalse((self.project_root / "state" / "product" / "variable_roles.json").exists())

    def test_bdd_3_unprofiled_import_cannot_generate_candidate(self) -> None:
        """行为 3：未生成字段画像前，不能基于猜测创建变量角色候选。"""
        dataset_import_id = self._apply_dataset_import(self.external_dta, "bind_external_reference")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/variable-role-candidates",
            json={"note": "不应成功。"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "field_profile_required")

    def test_bdd_4_invalid_candidate_review_action_is_rejected(self) -> None:
        """行为 4：候选状态机必须拒绝非法审阅动作。"""
        dataset_import_id = self._profile_dta_import()
        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/variable-role-candidates",
            json={"note": "生成待审候选。"},
        )
        self.assertEqual(generated.status_code, 201, msg=generated.text)
        candidate_id = generated.json()["variable_role_candidate"]["id"]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-role-candidates/{candidate_id}/review",
            json={"action": "ship_it", "note": "非法动作。"},
        )

        self.assertEqual(response.status_code, 400, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "invalid_variable_role_candidate_action")

    def _profile_dta_import(self) -> str:
        dataset_import_id = self._apply_dataset_import(self.external_dta, "bind_external_reference")
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/datasets/imports/{dataset_import_id}/profile",
            json={"row_limit": 200},
        )
        self.assertEqual(response.status_code, 200, msg=response.text)
        return dataset_import_id

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
            "project:\n  slug: variable-role-candidates\n  title: Variable Role Candidates Project\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu\n10,1,16\n12,0,14\n",
            encoding="utf-8",
        )

    @staticmethod
    def _create_external_dta(external_root: Path) -> Path:
        source = external_root / "A001CFPS中国家庭追踪调查" / "2011CFPS" / "cfps2011adult_202202.dta"
        source.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            {
                "pid": [1, 2, 3],
                "wage": [10.5, 12.0, 13.2],
                "trained": [1, 0, 1],
                "edu": [16, 14, 12],
                "experience": [3, 5, 8],
            }
        ).to_stata(
            source,
            write_index=False,
            variable_labels={
                "pid": "person id",
                "wage": "hourly wage",
                "trained": "training status",
                "edu": "education years",
                "experience": "work experience",
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


class VariableRoleCandidateFrontendTests(unittest.TestCase):
    """BDD: 数据页必须把字段画像推进为显式审阅候选，而不是暗中保存。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_frontend_exposes_candidate_review_and_non_writeback_copy(self) -> None:
        """行为 5：前端必须显示候选审阅入口，并说明不会写入正式变量角色集。"""
        self.assertIn("variable-role-candidate-panel", self.index_html)
        self.assertIn("variableRoleCandidates", self.app_js)
        self.assertIn("generateVariableRoleCandidate", self.app_js)
        self.assertIn("reviewVariableRoleCandidate", self.app_js)
        self.assertIn("renderVariableRoleCandidateReview", self.app_js)
        self.assertIn("生成变量角色候选", self.app_js)
        self.assertIn("字段审阅", self.app_js)
        self.assertIn("不会写入正式变量角色集", self.app_js)
        self.assertIn("data-variable-role-candidate-generate", self.app_js)
        self.assertIn("data-variable-role-candidate-review-action", self.app_js)
        self.assertIn("variable-role-candidate-panel", self.styles)


if __name__ == "__main__":
    unittest.main()

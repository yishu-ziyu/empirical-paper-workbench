from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class VariableRoleConfirmationApiTests(unittest.TestCase):
    """BDD: VariableRoleSet 必须是可保存、可审计、可驱动 workflow_contract 的产品对象。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="variable-roles-"))
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
                "slug": "variable-roles",
                "title": "Variable Roles Project",
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

    def test_bdd_1_get_variable_roles_returns_draft_from_local_dataset(self) -> None:
        """行为 1：保存前 API 必须返回来自本地数据 schema 的 draft VariableRoleSet。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/variable-roles")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        role_set = body["variable_role_set"]
        self.assertEqual(role_set["status"], "draft")
        self.assertEqual(role_set["evidence_level"], "local_file")
        self.assertEqual(role_set["dataset_path"], "Data/Final/analysis_sample.csv")
        self.assertEqual(role_set["roles"]["outcome"], ["wage"])
        self.assertEqual(role_set["roles"]["treatment"], ["trained"])
        self.assertEqual(role_set["roles"]["controls"], ["edu", "experience"])
        self.assertEqual(role_set["roles"]["instruments"], [])

    def test_bdd_2_put_variable_roles_persists_approved_state_and_decision_event(self) -> None:
        """行为 2：用户保存变量角色后，系统必须写入可审计的 approved VariableRoleSet。"""
        payload = {
            "dataset_path": "Data/Final/analysis_sample.csv",
            "roles": {
                "outcome": ["wage"],
                "treatment": ["trained"],
                "controls": ["edu"],
                "instruments": [],
                "fixed_effects": ["year"],
                "cluster_by": ["person_id"],
            },
            "note": "确认训练变量作为 treatment，教育作为控制变量。",
        }

        response = self.client.put(f"/api/v1/projects/{self.project_id}/variable-roles", json=payload)

        self.assertEqual(response.status_code, 200, msg=response.text)
        role_set = response.json()["variable_role_set"]
        self.assertEqual(role_set["status"], "approved")
        self.assertEqual(role_set["evidence_level"], "local_file")
        self.assertEqual(role_set["version"], 1)
        self.assertEqual(role_set["roles"]["fixed_effects"], ["year"])
        self.assertEqual(role_set["roles"]["cluster_by"], ["person_id"])
        self.assertEqual(role_set["decision_events"][0]["action"], "confirm_variable_roles")
        self.assertEqual(role_set["decision_events"][0]["note"], payload["note"])

        saved_path = self.project_root / "state" / "product" / "variable_roles.json"
        self.assertTrue(saved_path.exists())
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "approved")
        self.assertEqual(saved["roles"]["outcome"], ["wage"])

    def test_bdd_3_workflow_contract_removes_variable_role_blocker_after_approval(self) -> None:
        """行为 3：已确认 VariableRoleSet 必须驱动 workflow_contract 进入研究设计确认。"""
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/analysis_sample.csv",
                "roles": {
                    "outcome": ["wage"],
                    "treatment": ["trained"],
                    "controls": ["edu", "experience"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "变量角色已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

        overview = self.client.get(f"/api/v1/projects/{self.project_id}/overview")

        self.assertEqual(overview.status_code, 200, msg=overview.text)
        contract = overview.json()["workflow_contract"]
        variable_stage = next(stage for stage in contract["canonical_stages"] if stage["id"] == "variable_roles")
        self.assertEqual(variable_stage["status"], "completed")
        self.assertNotIn("variable_roles_unconfirmed", contract["run_readiness"]["blockers"])
        self.assertEqual(contract["next_action"]["id"], "confirm_design_spec")
        self.assertFalse(contract["run_readiness"]["can_start_full_run"])

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: variable-roles\n  title: Variable Roles Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience,year,person_id\n10,1,16,3,2024,1\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class VariableRoleConfirmationFrontendTests(unittest.TestCase):
    """BDD: Data & Variables 必须提供变量角色编辑器和保存动作。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    def test_bdd_4_data_workspace_contains_variable_role_confirmation_editor(self) -> None:
        """行为 4：Data & Variables 页面必须有可编辑的 VariableRoleSet 表单。"""
        self.assertIn("variable-role-confirmation-form", self.index_html)
        self.assertIn("renderVariableRoleEditor", self.app_js)
        for field in ("variable-role-outcome", "variable-role-treatment", "variable-role-controls", "variable-role-instruments", "variable-role-fixed-effects", "variable-role-cluster-by"):
            self.assertIn(field, self.app_js)

    def test_bdd_5_frontend_saves_variable_roles_and_refreshes_contract(self) -> None:
        """行为 5：保存变量角色后必须刷新 VariableRoleSet 和 workflow_contract。"""
        self.assertIn("v2api.variableRoles.save", self.app_js)
        self.assertIn("data-variable-role-save", self.app_js)
        self.assertIn("handleSaveVariableRoles", self.app_js)
        self.assertIn("state.variableRolesData = await v2api.variableRoles.get", self.app_js)
        self.assertIn("state.overviewData = await v2api.overview.get", self.app_js)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_parent_education_wage_p5_variable_role_preflight import seed_p5_project  # noqa: E402
from test_parent_education_wage_p6_variable_role_signoff import COMPLETE_SIGNOFF  # noqa: E402


class ParentEducationWageP7VariableRoleSignoffUiTests(unittest.TestCase):
    """BDD: P7 turns P6 signoff from an API-only action into a Product Control UI path."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p7-signoff-ui-"))
        self.project_root = self.tmp / "project"
        seed_p5_project(self.project_root)
        from Program.workbench.parent_education_wage_variable_role_preflight import (
            run_parent_education_wage_variable_role_preflight,
        )

        run_parent_education_wage_variable_role_preflight(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p7a_signoff_packet_exposes_recommended_decisions_for_ui_defaults(self) -> None:
        """行为 1：P6 packet 必须给页面推荐默认签收值，避免用户猜 JSON payload。"""
        from Program.workbench.parent_education_wage_variable_role_signoff import (
            build_parent_education_wage_variable_role_signoff,
        )

        packet = build_parent_education_wage_variable_role_signoff(self.project_root)

        self.assertEqual(packet["recommended_decisions"], COMPLETE_SIGNOFF)
        self.assertEqual(packet["recommended_decisions"]["approve_before_formal_variable_roles_write"], "draft_only_no_formal_write")
        self.assertFalse(packet["can_write_formal_variable_roles"])

    def test_bdd_p7b_react_panel_contains_five_decision_form_and_no_model_entry(self) -> None:
        """行为 2：React 页面必须提供五项签收输入和草稿按钮，而不是模型执行入口。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("确认并生成可编辑草稿", component)
        self.assertIn("promoteProductControlP6VariableRoleSignoff", component)
        self.assertIn("confirm_preferred_cfps_wave", component)
        self.assertIn("confirm_parent_education_construction", component)
        self.assertIn("confirm_hukou_role", component)
        self.assertIn("confirm_outcome_and_controls", component)
        self.assertIn("approve_before_formal_variable_roles_write", component)
        self.assertIn("draft_only_no_formal_write", component)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p7c_api_promotes_ui_default_decisions_to_editable_draft_only(self) -> None:
        """行为 3：页面默认值完整提交后，只提升到可编辑草稿，不改正式变量表。"""
        original_product_root = product_app.PRODUCT_ROOT
        original_repo_root = product_app.REPO_ROOT
        repo_root = self.tmp / "repo"
        product_root = repo_root / "Product"
        product_root.mkdir(parents=True)
        ensure_registry(product_root, repo_root)
        product_app.PRODUCT_ROOT = product_root
        product_app.REPO_ROOT = repo_root
        client = TestClient(product_app.app)
        try:
            response = client.post(
                "/api/v1/projects",
                json={
                    "slug": "parent-education-wage",
                    "title": "Parent Education Wage",
                    "project_root": str(self.project_root),
                    "language": "zh",
                },
            )
            self.assertEqual(response.status_code, 201, msg=response.text)
            project_id = response.json()["id"]
            created = client.post(f"/api/v1/projects/{project_id}/product-control/p6-variable-role-signoff")
            self.assertEqual(created.status_code, 201, msg=created.text)
            defaults = created.json()["recommended_decisions"]
            formal_path = self.project_root / "state/product/variable_roles.json"
            design_path = self.project_root / "state/product/design_spec.json"
            run_plan_path = self.project_root / "state/product/run_plan.json"
            data_path = self.project_root / "Data/Final/p7_guard_sample.csv"
            data_path.parent.mkdir(parents=True, exist_ok=True)
            data_path.write_text("ln_wage,parent_education,age\n10,12,20\n", encoding="utf-8")
            formal_before = self._sha256(formal_path)
            design_before = self._sha256(design_path)
            run_plan_before = self._sha256(run_plan_path)

            promoted = client.post(
                f"/api/v1/projects/{project_id}/product-control/p6-variable-role-signoff/promote",
                json={
                    "promotion_target": "editable_draft",
                    "allow_formal_write": False,
                    "decisions": defaults,
                    "note": "P7 页面按推荐默认值签收，只生成可编辑草稿。",
                },
            )

            self.assertEqual(promoted.status_code, 201, msg=promoted.text)
            body = promoted.json()
            self.assertEqual(body["status"], "variable_role_draft_promoted_for_editing")
            self.assertFalse(body["can_write_formal_variable_roles"])
            self.assertEqual(body["variable_role_set_draft"]["roles"]["outcome"], ["ln_wage"])
            self.assertTrue((self.project_root / "state/product/variable_roles_drafts.json").exists())
            self.assertEqual(self._sha256(formal_path), formal_before)

            formal_save = client.put(
                f"/api/v1/projects/{project_id}/variable-roles",
                json={
                    "dataset_path": "Data/Final/p7_guard_sample.csv",
                    "roles": {"outcome": ["ln_wage"], "treatment": ["parent_education"], "controls": ["age"]},
                    "note": "P7 draft promotion must not unlock formal VariableRoleSet writes.",
                },
            )

            self.assertEqual(formal_save.status_code, 409, msg=formal_save.text)
            self.assertEqual(formal_save.json()["error"]["code"], "p6_variable_role_draft_required")
            self.assertEqual(self._sha256(formal_path), formal_before)
            self.assertEqual(self._sha256(design_path), design_before)
            self.assertEqual(self._sha256(run_plan_path), run_plan_before)
        finally:
            product_app.PRODUCT_ROOT = original_product_root
            product_app.REPO_ROOT = original_repo_root

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)

from __future__ import annotations

import hashlib
import json
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


COMPLETE_SIGNOFF = {
    "confirm_preferred_cfps_wave": "confirmed_current_p4_sources",
    "confirm_parent_education_construction": "max(father_education, mother_education)",
    "confirm_hukou_role": "control_or_heterogeneity_candidate",
    "confirm_outcome_and_controls": "ln_wage_with_age_female_urban_edu_last_experience",
    "approve_before_formal_variable_roles_write": "draft_only_no_formal_write",
}


class ParentEducationWageP6VariableRoleSignoffTests(unittest.TestCase):
    """BDD: P6 records human signoff before promoting P5 preflight into an editable draft."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p6-variable-role-"))
        self.project_root = self.tmp / "project"
        seed_p5_project(self.project_root)
        from Program.workbench.parent_education_wage_variable_role_preflight import (
            run_parent_education_wage_variable_role_preflight,
        )

        run_parent_education_wage_variable_role_preflight(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p6a_builds_signoff_packet_from_p5_without_formal_write(self) -> None:
        """行为 1：P6 读取 P5 草案并生成待签收清单，不写正式变量角色。"""
        from Program.workbench.parent_education_wage_variable_role_signoff import (
            build_parent_education_wage_variable_role_signoff,
        )

        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        packet = build_parent_education_wage_variable_role_signoff(self.project_root)

        self.assertEqual(packet["schema_version"], "p6.parent_education_wage_variable_role_signoff.v1")
        self.assertEqual(packet["status"], "variable_role_signoff_required")
        self.assertEqual(packet["source_preflight"]["status"], "variable_role_preflight_ready_for_review")
        self.assertEqual(packet["required_decisions"], list(COMPLETE_SIGNOFF))
        self.assertFalse(packet["can_write_formal_variable_roles"])
        self.assertFalse(packet["boundary_flags"]["modified_formal_variable_roles"])
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p6b_incomplete_signoff_cannot_promote_or_write_draft(self) -> None:
        """行为 2：签收项不完整时不能提升，也不能写草稿或正式状态。"""
        from Program.workbench.parent_education_wage_variable_role_signoff import (
            promote_parent_education_wage_variable_role_signoff,
        )

        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        result = promote_parent_education_wage_variable_role_signoff(
            self.project_root,
            {
                "promotion_target": "editable_draft",
                "decisions": {"confirm_parent_education_construction": "max(father_education, mother_education)"},
                "note": "只确认了一项。",
            },
        )

        self.assertEqual(result["status"], "variable_role_signoff_incomplete")
        self.assertIn("confirm_preferred_cfps_wave", result["missing_decisions"])
        self.assertFalse((self.project_root / "state/product/variable_roles_drafts.json").exists())
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p6c_complete_signoff_promotes_only_to_editable_draft(self) -> None:
        """行为 3：完整签收后只写可编辑 draft，不覆盖正式 VariableRoleSet。"""
        from Program.workbench.parent_education_wage_variable_role_signoff import (
            promote_parent_education_wage_variable_role_signoff,
        )

        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        result = promote_parent_education_wage_variable_role_signoff(
            self.project_root,
            {
                "promotion_target": "editable_draft",
                "decisions": COMPLETE_SIGNOFF,
                "note": "人工确认后进入可编辑草稿。",
            },
        )

        self.assertEqual(result["status"], "variable_role_draft_promoted_for_editing")
        draft = result["variable_role_set_draft"]
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["source_preflight_path"], "Results/json/parent_education_wage_p5_variable_role_preflight.json")
        self.assertEqual(draft["roles"]["outcome"], ["ln_wage"])
        self.assertEqual(draft["roles"]["treatment"], ["parent_education"])
        self.assertIn("age", draft["roles"]["controls"])
        self.assertEqual(draft["write_boundary"], "draft_only_until_formal_variable_role_approval")
        self.assertEqual(self._sha256(formal_path), formal_before)

        draft_state = json.loads((self.project_root / "state/product/variable_roles_drafts.json").read_text(encoding="utf-8"))
        self.assertEqual(draft_state["pending_variable_roles_draft"]["id"], draft["id"])

    def test_bdd_p6d_formal_target_is_blocked_without_stronger_authorization(self) -> None:
        """行为 4：请求正式写回必须被稳定阻断，即使 payload 带 allow_formal_write。"""
        from Program.workbench.parent_education_wage_variable_role_signoff import (
            promote_parent_education_wage_variable_role_signoff,
        )

        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        result = promote_parent_education_wage_variable_role_signoff(
            self.project_root,
            {
                "promotion_target": "formal_variable_roles",
                "allow_formal_write": True,
                "decisions": COMPLETE_SIGNOFF,
                "note": "尝试正式写回。",
            },
        )

        self.assertEqual(result["status"], "formal_variable_roles_write_blocked")
        self.assertFalse(result["boundary_flags"]["modified_formal_variable_roles"])
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p6e_repeated_promotion_preserves_existing_drafts(self) -> None:
        """审查闭环：重复 promotion 不能用固定 draft id 覆盖旧草稿。"""
        from Program.workbench.parent_education_wage_variable_role_signoff import (
            promote_parent_education_wage_variable_role_signoff,
        )

        first = promote_parent_education_wage_variable_role_signoff(
            self.project_root,
            {"promotion_target": "editable_draft", "decisions": COMPLETE_SIGNOFF, "note": "第一次签收。"},
        )
        second = promote_parent_education_wage_variable_role_signoff(
            self.project_root,
            {"promotion_target": "editable_draft", "decisions": COMPLETE_SIGNOFF, "note": "第二次签收。"},
        )

        first_id = first["variable_role_set_draft"]["id"]
        second_id = second["variable_role_set_draft"]["id"]
        self.assertNotEqual(first_id, second_id)
        draft_state = json.loads((self.project_root / "state/product/variable_roles_drafts.json").read_text(encoding="utf-8"))
        self.assertIn(first_id, draft_state["drafts"])
        self.assertIn(second_id, draft_state["drafts"])
        self.assertEqual(draft_state["latest_draft_id"], second_id)

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


class ProductControlP6VariableRoleSignoffApiAndReactTests(unittest.TestCase):
    """BDD: Product Control exposes P6 signoff and draft promotion without model execution."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p6-variable-role-api-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.product_root.mkdir(parents=True)
        seed_p5_project(self.project_root)
        from Program.workbench.parent_education_wage_variable_role_preflight import (
            run_parent_education_wage_variable_role_preflight,
        )

        run_parent_education_wage_variable_role_preflight(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "parent-education-wage",
                "title": "Parent Education Wage",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.tmp)

    def test_bdd_p6_api_get_post_and_promote_to_draft(self) -> None:
        """行为 5：GET 只读，POST 生成签收包，完整签收才 promotion 到 draft。"""
        missing = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p6-variable-role-signoff")
        self.assertEqual(missing.status_code, 200, msg=missing.text)
        self.assertEqual(missing.json()["status"], "p6_variable_role_signoff_missing")

        created = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p6-variable-role-signoff")
        self.assertEqual(created.status_code, 201, msg=created.text)
        self.assertEqual(created.json()["status"], "variable_role_signoff_required")

        promoted = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p6-variable-role-signoff/promote",
            json={
                "promotion_target": "editable_draft",
                "allow_formal_write": False,
                "decisions": COMPLETE_SIGNOFF,
                "note": "人工签收后进入可编辑草稿。",
            },
        )

        self.assertEqual(promoted.status_code, 201, msg=promoted.text)
        self.assertEqual(promoted.json()["status"], "variable_role_draft_promoted_for_editing")
        self.assertTrue((self.project_root / "state/product/variable_roles_drafts.json").exists())

    def test_bdd_p6_api_blocks_legacy_formal_variable_roles_save_before_p6_draft(self) -> None:
        """审查闭环：父母教育工资链路不能绕过 P6 直接 PUT 正式变量角色。"""
        data_path = self.project_root / "Data/Final/p6_guard_sample.csv"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text("ln_wage,parent_education,age\n10,12,20\n", encoding="utf-8")
        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/p6_guard_sample.csv",
                "roles": {"outcome": ["ln_wage"], "treatment": ["parent_education"], "controls": ["age"]},
                "note": "尝试绕过 P6 保存正式变量角色。",
            },
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "p6_variable_role_draft_required")
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p6_react_product_control_panel_exposes_signoff_state(self) -> None:
        """行为 6：React 产品控制面必须展示 P6 签收，而不是模型执行入口。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p6-variable-role-signoff", component)
        self.assertIn("P6 签收状态", component)
        self.assertIn("editable_draft", component)
        self.assertIn("formal write", component)
        self.assertIn("不跑模型", component)
        self.assertIn("刷新 P6", component)

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)

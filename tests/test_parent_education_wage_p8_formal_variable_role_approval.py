from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_parent_education_wage_p5_variable_role_preflight import seed_p5_project  # noqa: E402
from test_parent_education_wage_p6_variable_role_signoff import COMPLETE_SIGNOFF  # noqa: E402


class ParentEducationWageP8FormalVariableRoleApprovalTests(unittest.TestCase):
    """BDD: P8 records explicit formal VariableRoleSet approval after P7 editable draft."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p8-formal-approval-"))
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
        created = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p6-variable-role-signoff")
        self.assertEqual(created.status_code, 201, msg=created.text)

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.tmp)

    def test_bdd_p8a_get_blocks_without_p7_editable_draft(self) -> None:
        """行为 1：没有 P7 draft 时不能进入 P8 正式批准。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p8-variable-role-approval")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_missing_p7_variable_role_draft")
        self.assertFalse(body["can_approve_formal_variable_roles"])
        self.assertFalse(body["can_write_formal_variable_roles"])
        self.assertFalse((self.project_root / "state/product/variable_role_formal_approvals.json").exists())

    def test_bdd_p8b_get_exposes_latest_p7_draft_for_formal_review(self) -> None:
        """行为 2：P7 draft 存在后，P8 返回待批准包但仍不写正式变量表。"""
        draft = self._promote_p7_draft()
        formal_before = self._sha256(self.project_root / "state/product/variable_roles.json")

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p8-variable-role-approval")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "formal_variable_role_approval_required")
        self.assertTrue(body["can_approve_formal_variable_roles"])
        self.assertFalse(body["can_write_formal_variable_roles"])
        self.assertEqual(body["latest_draft"]["id"], draft["id"])
        self.assertEqual(body["latest_draft"]["roles"]["outcome"], ["ln_wage"])
        self.assertIn("approve_formal_variable_roles_after_review", body["required_confirmations"])
        self.assertEqual(self._sha256(self.project_root / "state/product/variable_roles.json"), formal_before)

    def test_bdd_p8c_missing_approval_metadata_does_not_unlock_formal_save(self) -> None:
        """行为 3：缺 reviewer、note 或确认短语时不能批准，也不能写正式变量表。"""
        draft = self._promote_p7_draft()
        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p8-variable-role-approval",
            json={
                "decision": "approve_formal_variable_roles",
                "reviewer": "",
                "note": "",
                "confirmation": "",
            },
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["status"], "formal_variable_role_approval_incomplete")
        self.assertFalse((self.project_root / "state/product/variable_role_formal_approvals.json").exists())
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p8d_approval_unlocks_only_formal_variable_roles_save(self) -> None:
        """行为 4：P8 approve 后才允许正式变量角色保存，但不写 RunPlan/DesignSpec。"""
        draft = self._promote_p7_draft()
        formal_path = self.project_root / "state/product/variable_roles.json"
        design_path = self.project_root / "state/product/design_spec.json"
        run_plan_path = self.project_root / "state/product/run_plan.json"
        data_path = self.project_root / "Data/Final/p8_guard_sample.csv"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(
            "ln_wage,parent_education,age,female,urban,edu_last,experience\n10,12,20,1,1,16,2\n",
            encoding="utf-8",
        )
        formal_before = self._sha256(formal_path)
        design_before = self._sha256(design_path)
        run_plan_before = self._sha256(run_plan_path)

        approved = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p8-variable-role-approval",
            json={
                "decision": "approve_formal_variable_roles",
                "reviewer": "human_reviewer",
                "note": "确认 P7 草稿可进入正式变量角色保存；不批准 RunPlan 或模型执行。",
                "confirmation": "approve_formal_variable_roles_after_review",
            },
        )

        self.assertEqual(approved.status_code, 201, msg=approved.text)
        approval = approved.json()
        self.assertEqual(approval["status"], "formal_variable_role_approval_recorded")
        self.assertTrue(approval["can_write_formal_variable_roles"])
        self.assertEqual(self._sha256(formal_path), formal_before)
        self.assertTrue((self.project_root / "state/product/variable_role_formal_approvals.json").exists())

        saved = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/p8_guard_sample.csv",
                "roles": draft["roles"],
                "note": "P8 approval is effective for formal VariableRoleSet only.",
            },
        )

        self.assertEqual(saved.status_code, 200, msg=saved.text)
        self.assertNotEqual(self._sha256(formal_path), formal_before)
        self.assertEqual(self._sha256(design_path), design_before)
        self.assertEqual(self._sha256(run_plan_path), run_plan_before)
        role_set = saved.json()["variable_role_set"]
        self.assertEqual(role_set["status"], "approved")
        self.assertEqual(role_set["roles"]["treatment"], ["parent_education"])
        self.assertEqual(role_set["roles"]["controls"], draft["roles"]["controls"])

    def test_bdd_p8f_stale_approval_cannot_unlock_newer_p7_draft(self) -> None:
        """审查闭环：审批 draft A 后再生成 draft B，旧 approval 不能解锁正式保存。"""
        draft_a = self._promote_p7_draft()
        self._approve_p8()
        time.sleep(0.001)
        draft_b = self._promote_p7_draft(note="P8 stale approval regression: newer editable draft.")
        self.assertNotEqual(draft_a["id"], draft_b["id"])
        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)
        p8_status = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p8-variable-role-approval")
        self.assertEqual(p8_status.status_code, 200, msg=p8_status.text)
        self.assertEqual(p8_status.json()["status"], "formal_variable_role_approval_required")

        saved = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/p8_guard_sample.csv",
                "roles": draft_b["roles"],
                "note": "旧 P8 approval 不应解锁新 draft。",
            },
        )

        self.assertEqual(saved.status_code, 409, msg=saved.text)
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p8g_approval_does_not_unlock_roles_that_differ_from_approved_draft(self) -> None:
        """审查闭环：审批的 draft roles 与 PUT roles 不一致时不能正式保存。"""
        self._promote_p7_draft()
        self._approve_p8()
        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        saved = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/p8_guard_sample.csv",
                "roles": {"outcome": ["fake_y"], "treatment": ["fake_x"], "controls": ["age"]},
                "note": "尝试用已批准 draft 之外的角色写正式变量表。",
            },
        )

        self.assertEqual(saved.status_code, 409, msg=saved.text)
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p8h_same_draft_id_role_mutation_invalidates_approval(self) -> None:
        """审查闭环：同一 draft id 的 roles 被篡改后，原 P8 approval 失效。"""
        draft = self._promote_p7_draft()
        self._approve_p8()
        mutated_roles = {"outcome": ["fake_y"], "treatment": ["fake_x"], "controls": ["age"]}
        self._mutate_latest_draft_roles_preserving_id(draft["id"], mutated_roles)
        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        p8_status = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p8-variable-role-approval")
        self.assertEqual(p8_status.status_code, 200, msg=p8_status.text)
        self.assertEqual(p8_status.json()["status"], "formal_variable_role_approval_required")

        saved = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/p8_guard_sample.csv",
                "roles": mutated_roles,
                "note": "尝试利用同 id draft 篡改绕过 P8 approval 快照。",
            },
        )

        self.assertEqual(saved.status_code, 409, msg=saved.text)
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p8e_react_panel_contains_formal_approval_controls_and_no_model_entry(self) -> None:
        """行为 5：React 页面必须显示 P8 审批路径，不提供模型执行入口。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("P8 正式变量角色审批", component)
        self.assertIn("approveProductControlP8VariableRoleApproval", component)
        self.assertIn("approve_formal_variable_roles_after_review", component)
        self.assertIn("reviewer", component)
        self.assertIn("note", component)
        self.assertIn("不写 RunPlan；不跑模型", component)
        self.assertNotIn(">运行模型<", component)

    def _promote_p7_draft(self, note: str = "P8 test seed: create editable draft only.") -> dict:
        data_path = self.project_root / "Data/Final/p8_guard_sample.csv"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(
            "ln_wage,parent_education,age,female,urban,edu_last,experience\n10,12,20,1,1,16,2\n",
            encoding="utf-8",
        )
        promoted = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p6-variable-role-signoff/promote",
            json={
                "promotion_target": "editable_draft",
                "allow_formal_write": False,
                "decisions": COMPLETE_SIGNOFF,
                "note": note,
            },
        )
        self.assertEqual(promoted.status_code, 201, msg=promoted.text)
        return promoted.json()["variable_role_set_draft"]

    def _mutate_latest_draft_roles_preserving_id(self, draft_id: str, roles: dict) -> None:
        path = self.project_root / "state/product/variable_roles_drafts.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["drafts"][draft_id]["roles"] = roles
        pending = state.get("pending_variable_roles_draft")
        if isinstance(pending, dict) and pending.get("id") == draft_id:
            pending["roles"] = roles
            state["pending_variable_roles_draft"] = pending
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _approve_p8(self) -> dict:
        approved = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p8-variable-role-approval",
            json={
                "decision": "approve_formal_variable_roles",
                "reviewer": "human_reviewer",
                "note": "确认 P7 草稿可进入正式变量角色保存；不批准 RunPlan 或模型执行。",
                "confirmation": "approve_formal_variable_roles_after_review",
            },
        )
        self.assertEqual(approved.status_code, 201, msg=approved.text)
        return approved.json()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)

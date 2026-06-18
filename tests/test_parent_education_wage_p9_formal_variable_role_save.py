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
from test_parent_education_wage_p6_variable_role_signoff import COMPLETE_SIGNOFF  # noqa: E402


class ParentEducationWageP9FormalVariableRoleSaveTests(unittest.TestCase):
    """BDD: P9 saves formal VariableRoleSet only after P8 and source metadata contract."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p9-formal-save-"))
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
        self.draft = self._promote_p7_draft()

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.tmp)

    def test_bdd_p9a_get_blocks_before_p8_approval(self) -> None:
        """行为 1：P7 draft 之后，没有 P8 approval 仍不能正式保存。"""
        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_missing_p8_formal_approval")
        self.assertFalse(body["can_save_formal_variable_roles"])
        self.assertFalse(body["can_enter_design_spec_preflight"])
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p9b_get_blocks_when_dataset_source_metadata_is_incomplete(self) -> None:
        """行为 2：P8 approval 存在但 dataset/source metadata 不完整时仍阻断。"""
        self._approve_p8()

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_missing_dataset_source_metadata")
        self.assertFalse(body["can_save_formal_variable_roles"])
        self.assertIn("ln_wage", body["missing_source_metadata_fields"])
        self.assertIn("age", body["missing_source_metadata_fields"])
        self.assertFalse(body["can_enter_design_spec_preflight"])

    def test_bdd_p9c_save_requires_confirmation_and_does_not_write_any_formal_state(self) -> None:
        """行为 3：P9 save 缺 reviewer、note 或确认短语时不能保存。"""
        draft = self._attach_complete_source_contract()
        self._approve_p8()
        formal_path = self.project_root / "state/product/variable_roles.json"
        design_path = self.project_root / "state/product/design_spec.json"
        run_plan_path = self.project_root / "state/product/run_plan.json"
        formal_before = self._sha256(formal_path)
        design_before = self._sha256(design_path)
        run_plan_before = self._sha256(run_plan_path)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save",
            json={
                "decision": "",
                "reviewer": "",
                "note": "",
                "confirmation": "",
                "source_draft_id": draft["id"],
                "dataset_path": "Data/Final/p9_guard_sample.csv",
                "roles": draft["roles"],
            },
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["status"], "formal_variable_role_save_incomplete")
        self.assertEqual(self._sha256(formal_path), formal_before)
        self.assertEqual(self._sha256(design_path), design_before)
        self.assertEqual(self._sha256(run_plan_path), run_plan_before)

    def test_bdd_p9c2_blocks_name_only_bindings_without_auditable_source_metadata(self) -> None:
        """审查回归：只有 dataset_column 不能算完整字段来源证据。"""
        draft = self._attach_complete_source_contract()
        state_path = self.project_root / "state/product/variable_roles_drafts.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        draft_id = state["latest_draft_id"]
        weak_draft = state["drafts"][draft_id]
        weak_draft["source_contract"]["field_bindings"] = {
            field: {"dataset_column": field}
            for field in [
                "ln_wage",
                "parent_education",
                "age",
                "female",
                "urban",
                "edu_last",
                "experience",
                "father_education",
                "mother_education",
            ]
        }
        state["drafts"][draft_id] = weak_draft
        state["pending_variable_roles_draft"] = weak_draft
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        self._approve_p8()
        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_missing_dataset_source_metadata")
        self.assertFalse(body["can_save_formal_variable_roles"])
        self.assertIn("ln_wage", body["missing_source_metadata_fields"])
        self.assertIn("parent_education", body["missing_source_metadata_fields"])
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p9d_save_writes_formal_variable_roles_only_from_approved_draft(self) -> None:
        """行为 4：P9 save 只写正式 VariableRoleSet，不写 DesignSpec/RunPlan。"""
        draft = self._attach_complete_source_contract()
        self._approve_p8()
        formal_path = self.project_root / "state/product/variable_roles.json"
        design_path = self.project_root / "state/product/design_spec.json"
        run_plan_path = self.project_root / "state/product/run_plan.json"
        formal_before = self._sha256(formal_path)
        design_before = self._sha256(design_path)
        run_plan_before = self._sha256(run_plan_path)

        ready = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save")
        self.assertEqual(ready.status_code, 200, msg=ready.text)
        self.assertEqual(ready.json()["status"], "formal_variable_role_save_ready")

        saved = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save",
            json={
                "decision": "save_formal_variable_roles",
                "reviewer": "human_reviewer",
                "note": "确认 P8 已批准草稿和 source metadata，可写正式 VariableRoleSet。",
                "confirmation": "save_formal_variable_roles_from_p8_approved_draft",
                "source_draft_id": draft["id"],
                "dataset_path": "Data/Final/p9_guard_sample.csv",
                "roles": draft["roles"],
            },
        )

        self.assertEqual(saved.status_code, 201, msg=saved.text)
        body = saved.json()
        self.assertEqual(body["status"], "formal_variable_roles_saved")
        self.assertTrue(body["can_enter_design_spec_preflight"])
        self.assertFalse(body["can_create_run_id"])
        self.assertFalse(body["can_execute_model"])
        self.assertNotEqual(self._sha256(formal_path), formal_before)
        self.assertEqual(self._sha256(design_path), design_before)
        self.assertEqual(self._sha256(run_plan_path), run_plan_before)
        role_set = json.loads(formal_path.read_text(encoding="utf-8"))
        self.assertEqual(role_set["roles"], draft["roles"])
        self.assertEqual(role_set["dataset_path"], "Data/Final/p9_guard_sample.csv")
        self.assertEqual(role_set["source_contract"]["source_draft_id"], draft["id"])
        self.assertEqual(role_set["p8_approval"]["source_draft_id"], draft["id"])

        reloaded = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save")
        self.assertEqual(reloaded.status_code, 200, msg=reloaded.text)
        reloaded_body = reloaded.json()
        self.assertEqual(reloaded_body["status"], "formal_variable_roles_saved")
        self.assertFalse(reloaded_body["can_save_formal_variable_roles"])
        self.assertTrue(reloaded_body["can_enter_design_spec_preflight"])
        self.assertFalse(reloaded_body["can_create_run_id"])
        self.assertFalse(reloaded_body["can_execute_model"])
        self.assertEqual(reloaded_body["variable_role_set"]["dataset_path"], "Data/Final/p9_guard_sample.csv")
        self.assertEqual(reloaded_body["variable_role_set"]["roles"], draft["roles"])

    def test_bdd_p9e_save_rejects_payload_that_changes_roles_or_dataset(self) -> None:
        """行为 5：P9 payload 不能替换已批准 roles 或 dataset path。"""
        draft = self._attach_complete_source_contract()
        self._approve_p8()
        formal_path = self.project_root / "state/product/variable_roles.json"
        formal_before = self._sha256(formal_path)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save",
            json={
                "decision": "save_formal_variable_roles",
                "reviewer": "human_reviewer",
                "note": "尝试替换已批准 draft 之外的 roles 和 dataset。",
                "confirmation": "save_formal_variable_roles_from_p8_approved_draft",
                "source_draft_id": draft["id"],
                "dataset_path": "Data/Final/fake.csv",
                "roles": {"outcome": ["fake_y"], "treatment": ["fake_x"], "controls": ["age"]},
            },
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["status"], "formal_variable_role_save_payload_mismatch")
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p9f_react_panel_contains_formal_save_controls_and_no_model_entry(self) -> None:
        """行为 6：React 页面必须显示 P9 正式保存路径，不提供模型执行入口。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("P9 正式变量表保存", component)
        self.assertIn("saveProductControlP9FormalVariableRoles", component)
        self.assertIn("save_formal_variable_roles_from_p8_approved_draft", component)
        self.assertIn("missing_source_metadata_fields", component)
        self.assertIn("不写 DesignSpec；不写 RunPlan；不跑模型", component)
        self.assertNotIn(">运行模型<", component)

    def _promote_p7_draft(self) -> dict:
        promoted = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p6-variable-role-signoff/promote",
            json={
                "promotion_target": "editable_draft",
                "allow_formal_write": False,
                "decisions": COMPLETE_SIGNOFF,
                "note": "P9 test seed: create editable draft only.",
            },
        )
        self.assertEqual(promoted.status_code, 201, msg=promoted.text)
        return promoted.json()["variable_role_set_draft"]

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

    def _attach_complete_source_contract(self) -> dict:
        data_path = self.project_root / "Data/Final/p9_guard_sample.csv"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(
            "ln_wage,parent_education,age,female,urban,edu_last,experience,father_education,mother_education\n"
            "10,12,20,1,1,16,2,12,10\n",
            encoding="utf-8",
        )
        state_path = self.project_root / "state/product/variable_roles_drafts.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        draft_id = state["latest_draft_id"]
        draft = state["drafts"][draft_id]
        role_fields = [
            "ln_wage",
            "parent_education",
            "age",
            "female",
            "urban",
            "edu_last",
            "experience",
            "father_education",
            "mother_education",
        ]
        draft["dataset_path"] = "Data/Final/p9_guard_sample.csv"
        draft["dataset_name"] = "p9_guard_sample.csv"
        draft["source_contract"] = {
            "status": "complete",
            "dataset_path": "Data/Final/p9_guard_sample.csv",
            "dataset_name": "p9_guard_sample.csv",
            "analysis_dataset_available": True,
            "source_draft_id": draft_id,
            "field_bindings": {
                field: {
                    "dataset_column": field,
                    "source_field": field,
                    "evidence_level": "local_file",
                    "source_path": "Data/Final/p9_guard_sample.csv",
                }
                for field in role_fields
            },
            "derived_variables": {
                "parent_education": {
                    "source_fields": ["father_education", "mother_education"],
                    "construction": "max(father_education, mother_education)",
                }
            },
        }
        state["drafts"][draft_id] = draft
        state["pending_variable_roles_draft"] = draft
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return draft

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)

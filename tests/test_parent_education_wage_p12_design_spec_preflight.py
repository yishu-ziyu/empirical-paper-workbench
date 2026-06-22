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


class ParentEducationWageP12DesignSpecPreflightTests(unittest.TestCase):
    """BDD: P12 turns saved formal roles into a reviewable DesignSpec preflight only."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p12-design-preflight-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.product_root.mkdir(parents=True)
        seed_p5_project(self.project_root)
        from Program.workbench.parent_education_wage_variable_role_preflight import (
            run_parent_education_wage_variable_role_preflight,
        )

        run_parent_education_wage_variable_role_preflight(self.project_root)
        formal_role_path = self.project_root / "state/product/variable_roles.json"
        if formal_role_path.exists():
            formal_role_path.unlink()
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

    def test_bdd_p12a_get_blocks_before_formal_variable_roles_are_saved(self) -> None:
        """行为 1：没有 P9 正式变量表时，P12 必须阻断。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p12-design-spec-preflight")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_missing_formal_variable_roles")
        self.assertFalse(body["can_write_design_spec"])
        self.assertFalse(body["can_write_run_plan"])
        self.assertFalse(body["can_create_run_id"])
        self.assertFalse(body["can_execute_model"])
        self.assertIn("complete_p9_formal_variable_role_save", body["blocking_reasons"])

    def test_bdd_p12b_post_generates_design_spec_preflight_without_formal_state_writes(self) -> None:
        """行为 2/4：P12 生成预检产物，但不写正式 DesignSpec/RunPlan。"""
        self._save_formal_variable_roles()
        design_path = self.project_root / "state/product/design_spec.json"
        run_plan_path = self.project_root / "state/product/run_plan.json"
        design_before = self._sha256(design_path)
        run_plan_before = self._sha256(run_plan_path)

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p12-design-spec-preflight")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "design_spec_preflight_ready_for_review")
        self.assertEqual(body["draft_design_spec"]["status"], "preflight_draft")
        self.assertEqual(body["draft_design_spec"]["model"]["formula"], "ln_wage ~ parent_education + age + female + urban + edu_last + experience")
        self.assertEqual(body["draft_design_spec"]["model"]["estimator"], "ols")
        self.assertEqual(body["draft_design_spec"]["dataset_path"], "Data/Final/p12_guard_sample.csv")
        self.assertFalse(body["can_write_design_spec"])
        self.assertTrue(body["can_request_human_design_spec_confirmation"])
        self.assertFalse(body["can_write_run_plan"])
        self.assertFalse(body["can_create_run_id"])
        self.assertFalse(body["can_execute_model"])
        self.assertEqual(self._sha256(design_path), design_before)
        self.assertEqual(self._sha256(run_plan_path), run_plan_before)
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_p12_design_spec_preflight.json").exists())
        self.assertTrue((self.project_root / "Reviews/parent_education_wage_p12_design_spec_preflight.md").exists())

    def test_bdd_p12c_method_catalog_marks_ready_and_blocked_methods(self) -> None:
        """行为 3：P12 方法清单必须说明哪些方法可预检、哪些被阻断。"""
        self._save_formal_variable_roles()
        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p12-design-spec-preflight")

        self.assertEqual(response.status_code, 201, msg=response.text)
        methods = {item["id"]: item for item in response.json()["method_catalog"]["methods"]}
        self.assertEqual(methods["ols"]["readiness_status"], "ready")
        self.assertEqual(methods["psm"]["readiness_status"], "ready")
        self.assertEqual(methods["dml"]["readiness_status"], "ready")
        self.assertEqual(methods["did"]["readiness_status"], "blocked")
        self.assertIn("missing_panel_time", methods["did"]["blockers"])
        self.assertEqual(methods["iv"]["readiness_status"], "blocked")
        self.assertIn("missing_instrument", methods["iv"]["blockers"])
        self.assertEqual(methods["rdd"]["readiness_status"], "blocked")
        self.assertIn("missing_running_variable", methods["rdd"]["blockers"])
        self.assertFalse(response.json()["boundary_flags"]["created_run_id"])
        self.assertFalse(response.json()["boundary_flags"]["executed_regression"])

    def test_bdd_p12d_get_reads_existing_preflight_after_post(self) -> None:
        """行为 5：GET 必须读取现有 P12 预检，而不是要求重复生成。"""
        self._save_formal_variable_roles()
        posted = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p12-design-spec-preflight")
        self.assertEqual(posted.status_code, 201, msg=posted.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p12-design-spec-preflight")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "design_spec_preflight_ready_for_review")
        self.assertEqual(body["outputs"]["json"], "Results/json/parent_education_wage_p12_design_spec_preflight.json")
        self.assertEqual(body["product_control_signal"]["phase"], "P12")
        self.assertEqual(body["product_control_signal"]["next_action"], "human_review_design_spec_preflight")

    def _save_formal_variable_roles(self) -> None:
        draft = self._attach_complete_source_contract()
        self._approve_p8()
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save",
            json={
                "decision": "save_formal_variable_roles",
                "reviewer": "human_reviewer",
                "note": "P12 seed: save formal roles only.",
                "confirmation": "save_formal_variable_roles_from_p8_approved_draft",
                "source_draft_id": draft["id"],
                "dataset_path": "Data/Final/p12_guard_sample.csv",
                "roles": draft["roles"],
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)

    def _promote_p7_draft(self) -> dict:
        promoted = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p6-variable-role-signoff/promote",
            json={
                "promotion_target": "editable_draft",
                "allow_formal_write": False,
                "decisions": COMPLETE_SIGNOFF,
                "note": "P12 test seed: create editable draft only.",
            },
        )
        self.assertEqual(promoted.status_code, 201, msg=promoted.text)
        return promoted.json()["variable_role_set_draft"]

    def _approve_p8(self) -> None:
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

    def _attach_complete_source_contract(self) -> dict:
        data_path = self.project_root / "Data/Final/p12_guard_sample.csv"
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
        fields = [
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
        draft["dataset_path"] = "Data/Final/p12_guard_sample.csv"
        draft["dataset_name"] = "p12_guard_sample.csv"
        draft["roles"]["controls"] = ["age", "female", "urban", "edu_last", "experience"]
        draft["source_contract"] = {
            "status": "complete",
            "dataset_path": "Data/Final/p12_guard_sample.csv",
            "dataset_name": "p12_guard_sample.csv",
            "analysis_dataset_available": True,
            "source_draft_id": draft_id,
            "field_bindings": {
                field: {
                    "dataset_column": field,
                    "source_field": field,
                    "source_path": "Data/Final/p12_guard_sample.csv",
                    "evidence_level": "local_file",
                }
                for field in fields
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
        if not path.exists():
            return "missing"
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)

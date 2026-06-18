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


class ParentEducationWageP11SourceMetadataContractTests(unittest.TestCase):
    """BDD: P11 completes source metadata before P9 formal save, without writing formal state."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p11-source-contract-"))
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
        self._approve_p8()

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.tmp)

    def test_bdd_p11a_get_lists_missing_source_contract_fields(self) -> None:
        """行为 1：P11 GET 告诉用户需要补哪些 source metadata。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p11-source-metadata-contract")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "source_metadata_contract_required")
        self.assertEqual(body["latest_draft"]["id"], self.draft["id"])
        self.assertFalse(body["can_save_formal_variable_roles"])
        self.assertFalse(body["can_enter_design_spec_preflight"])
        self.assertFalse(body["can_create_run_id"])
        self.assertFalse(body["can_execute_model"])
        for field in ["dataset_path", "ln_wage", "parent_education", "age", "female", "urban", "edu_last", "experience"]:
            self.assertIn(field, body["missing_source_metadata_fields"])
        self.assertIn("ln_wage", body["required_source_fields"])
        self.assertIn("parent_education", body["required_source_fields"])

    def test_bdd_p11b_incomplete_contract_does_not_write_formal_state_or_unlock_p9(self) -> None:
        """行为 2：source contract 不完整时，P11 不写正式层，P9 仍阻断。"""
        formal_path = self.project_root / "state/product/variable_roles.json"
        design_path = self.project_root / "state/product/design_spec.json"
        run_plan_path = self.project_root / "state/product/run_plan.json"
        formal_before = self._sha256(formal_path)
        design_before = self._sha256(design_path)
        run_plan_before = self._sha256(run_plan_path)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p11-source-metadata-contract",
            json={
                "decision": "save_source_metadata_contract",
                "reviewer": "human_reviewer",
                "note": "故意提交不完整 source contract。",
                "confirmation": "save_source_metadata_contract_for_p9_formal_save",
                "dataset_path": "",
                "field_bindings": {},
                "derived_variables": {},
            },
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "source_metadata_contract_incomplete")
        self.assertIn("dataset_path", body["missing_source_metadata_fields"])
        self.assertEqual(self._sha256(formal_path), formal_before)
        self.assertEqual(self._sha256(design_path), design_before)
        self.assertEqual(self._sha256(run_plan_path), run_plan_before)
        p9 = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save")
        self.assertEqual(p9.status_code, 200, msg=p9.text)
        self.assertEqual(p9.json()["status"], "blocked_missing_dataset_source_metadata")

    def test_bdd_p11c_complete_contract_updates_draft_only_and_unlocks_p9(self) -> None:
        """行为 3：完整 source contract 只更新 draft，并让 P9 进入 ready。"""
        dataset_path = self._write_analysis_dataset()
        formal_path = self.project_root / "state/product/variable_roles.json"
        design_path = self.project_root / "state/product/design_spec.json"
        run_plan_path = self.project_root / "state/product/run_plan.json"
        formal_before = self._sha256(formal_path)
        design_before = self._sha256(design_path)
        run_plan_before = self._sha256(run_plan_path)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p11-source-metadata-contract",
            json={
                "decision": "save_source_metadata_contract",
                "reviewer": "human_reviewer",
                "note": "确认 dataset path 和字段来源，只解锁 P9 保存门禁。",
                "confirmation": "save_source_metadata_contract_for_p9_formal_save",
                "dataset_path": dataset_path,
                "field_bindings": self._complete_field_bindings(dataset_path),
                "derived_variables": {
                    "parent_education": {
                        "source_fields": ["father_education", "mother_education"],
                        "construction": "max(father_education, mother_education)",
                    }
                },
            },
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "source_metadata_contract_ready_for_p9_save")
        self.assertTrue(body["can_return_to_p9_formal_save"])
        self.assertFalse(body["can_enter_design_spec_preflight"])
        self.assertFalse(body["can_create_run_id"])
        self.assertFalse(body["can_execute_model"])
        self.assertEqual(self._sha256(formal_path), formal_before)
        self.assertEqual(self._sha256(design_path), design_before)
        self.assertEqual(self._sha256(run_plan_path), run_plan_before)

        state = json.loads((self.project_root / "state/product/variable_roles_drafts.json").read_text(encoding="utf-8"))
        latest = state["drafts"][state["latest_draft_id"]]
        self.assertEqual(latest["source_contract"]["status"], "complete")
        self.assertEqual(latest["source_contract"]["dataset_path"], dataset_path)
        self.assertEqual(latest["source_contract"]["derived_variables"]["parent_education"]["construction"], "max(father_education, mother_education)")

        p9 = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p9-variable-role-formal-save")
        self.assertEqual(p9.status_code, 200, msg=p9.text)
        self.assertEqual(p9.json()["status"], "formal_variable_role_save_ready")
        self.assertTrue(p9.json()["can_save_formal_variable_roles"])
        self.assertEqual(self._sha256(formal_path), formal_before)

    def test_bdd_p11d_react_panel_exposes_source_metadata_form_and_no_model_entry(self) -> None:
        """行为 4：React 页面提供 P11 补证入口，但没有模型执行入口。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("P11 Source Metadata", component)
        self.assertIn("saveProductControlP11SourceMetadataContract", component)
        self.assertIn("save_source_metadata_contract_for_p9_formal_save", component)
        self.assertIn("field_bindings", component)
        self.assertIn("parent_education construction", component)
        self.assertIn("不写正式 VariableRoleSet；不写 DesignSpec；不写 RunPlan；不跑模型", component)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p11a_review_kit_returns_candidate_context_without_unlocking_model(self) -> None:
        """行为 5：P11A 返回候选签收包，帮助人工确认但不越权。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p11-source-metadata-contract")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        review_kit = body["source_contract_review_kit"]
        self.assertEqual(review_kit["status"], "needs_human_source_contract_review")
        self.assertFalse(review_kit["can_save_without_human_review"])
        self.assertFalse(review_kit["can_execute_model"])
        self.assertEqual(review_kit["recommended_parent_education_construction"], "max(father_education, mother_education)")
        self.assertIn("Data/Final/cfps_robot_reallocation.csv", review_kit["dataset_path_candidates"])

        field_items = {item["field"]: item for item in review_kit["field_review_items"]}
        self.assertIn("father_education", field_items)
        self.assertEqual(field_items["father_education"]["review_status"], "needs_human_confirmation")
        self.assertEqual(field_items["father_education"]["recommended_source"]["evidence_level"], "local_stata_metadata")
        self.assertIn("cfps", field_items["father_education"]["recommended_source"]["source_path"])
        self.assertIn("ln_wage", field_items)
        self.assertIn(field_items["ln_wage"]["review_status"], {"missing_recommended_source", "needs_human_confirmation"})

    def test_bdd_p11a_react_panel_exposes_source_review_kit(self) -> None:
        """行为 6：React P11 面板展示候选签收包，不让用户只面对 JSON。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("source_contract_review_kit", component)
        self.assertIn("Source review kit", component)
        self.assertIn("recommended dataset path", component)
        self.assertIn("field review items", component)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p11b_react_panel_exposes_per_field_source_confirmation_editor(self) -> None:
        """行为 7：React P11 面板把 field_bindings 拆成逐字段确认控件。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("Per-field source confirmation", component)
        self.assertIn("p11 per-field source confirmation editor", component)
        self.assertIn("sourceFieldRows", component)
        self.assertIn("handleP11SourceFieldRowChange", component)
        self.assertIn("p11FieldBindingsFromRows", component)
        self.assertIn("field_bindings JSON preview", component)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p11c_react_panel_exposes_source_contract_readiness_check(self) -> None:
        """行为 8：React P11 面板保存前显示 source contract 完整性自检。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("Source contract readiness", component)
        self.assertIn("p11 source contract readiness check", component)
        self.assertIn("p11SourceContractMissingItems", component)
        self.assertIn("p11SourceContractReady", component)
        self.assertIn("ready_to_save_source_contract", component)
        self.assertIn("needs_source_metadata_review", component)
        self.assertIn("p11ReadinessMissingItems", component)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p11d_react_panel_requires_explicit_row_human_confirmation(self) -> None:
        """行为 9：React P11 面板要求每个字段来源行被人工确认后才能保存。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("confirmedSourceFieldRows", component)
        self.assertIn("handleP11SourceFieldRowConfirmChange", component)
        self.assertIn("human_confirmation", component)
        self.assertIn("confirmed rows", component)
        self.assertIn("p11 row human confirmation", component)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p11e_react_panel_keeps_row_field_labels_visible_for_human_signoff(self) -> None:
        """行为 10：React P11 字段来源行在移动端也保留可见标签，方便人工签收。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")
        styles = (root / "Product/web-react/src/styles.css").read_text(encoding="utf-8")

        self.assertIn("product-control-p0-panel__p11-row-field", component)
        self.assertIn("product-control-p0-panel__p11-row-field-label", component)
        for label in ["dataset column", "source field", "source path", "evidence level"]:
            self.assertIn(f"<span>{label}</span>", component)
        self.assertIn("p11 readable source row labels", component)
        self.assertIn(".product-control-p0-panel__p11-row-field", styles)
        self.assertIn(".product-control-p0-panel__p11-row-field-label", styles)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p11f_react_panel_exposes_human_signoff_review_queue(self) -> None:
        """行为 11：React P11 在长表单前展示逐字段人工签收审核队列。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")
        styles = (root / "Product/web-react/src/styles.css").read_text(encoding="utf-8")

        self.assertIn("Human signoff review queue", component)
        self.assertIn("p11 human signoff review queue", component)
        self.assertIn("p11SourceRowReviewItems", component)
        self.assertIn("p11SourceRowMissingItems", component)
        self.assertIn("needs_human_confirmation", component)
        self.assertIn("ready_for_human_confirmation", component)
        self.assertIn("confirmed_source_row", component)
        self.assertIn(".product-control-p0-panel__p11-review-queue", styles)
        self.assertIn(".product-control-p0-panel__p11-review-queue-item", styles)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p11g_react_panel_renders_source_contract_signoff_workspace(self) -> None:
        """行为 12：React P11 以签收工作台组织队列、表单和保存动作。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")
        styles = (root / "Product/web-react/src/styles.css").read_text(encoding="utf-8")

        self.assertIn("Source Contract Signoff", component)
        self.assertIn("Review queue", component)
        self.assertIn("Source contract form", component)
        self.assertIn("product-control-p0-panel__p11-workspace", component)
        self.assertIn("product-control-p0-panel__p11-status-strip", component)
        self.assertIn("product-control-p0-panel__p11-workspace-grid", component)
        self.assertIn("product-control-p0-panel__p11-action-bar", component)
        self.assertIn("No model run", component)
        self.assertIn(".product-control-p0-panel__p11-workspace", styles)
        self.assertIn(".product-control-p0-panel__p11-workspace-grid", styles)
        self.assertIn(".product-control-p0-panel__p11-action-bar", styles)
        self.assertNotIn(">运行模型<", component)

    def test_bdd_p11h_react_panel_shows_saved_next_step_without_model_entry(self) -> None:
        """行为 13：P11 保存成功态必须把用户交回 P9，而不是暗示可以跑模型。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")
        styles = (root / "Product/web-react/src/styles.css").read_text(encoding="utf-8")

        self.assertIn("sourceContractSaved", component)
        self.assertIn("P11 已签收", component)
        self.assertIn("已解锁 P9 正式变量表保存", component)
        self.assertIn("下一步：回到 P9 正式保存", component)
        self.assertIn("仍不能进入 P12", component)
        self.assertIn("仍不能创建 run id", component)
        self.assertIn("仍不能运行模型", component)
        self.assertIn("product-control-p0-panel__p11-saved-next-step", component)
        self.assertIn(".product-control-p0-panel__p11-saved-next-step", styles)
        self.assertNotIn(">运行模型<", component)

    def _promote_p7_draft(self) -> dict:
        promoted = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p6-variable-role-signoff/promote",
            json={
                "promotion_target": "editable_draft",
                "allow_formal_write": False,
                "decisions": COMPLETE_SIGNOFF,
                "note": "P11 test seed: create editable draft only.",
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

    def _write_analysis_dataset(self) -> str:
        relative = "Data/Final/p11_source_contract_sample.csv"
        data_path = self.project_root / relative
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(
            "ln_wage,parent_education,age,female,urban,edu_last,experience,father_education,mother_education\n"
            "10,12,20,1,1,16,2,12,10\n",
            encoding="utf-8",
        )
        return relative

    @staticmethod
    def _complete_field_bindings(dataset_path: str) -> dict[str, dict[str, str]]:
        return {
            field: {
                "dataset_column": field,
                "source_field": field,
                "source_path": dataset_path,
                "evidence_level": "local_file",
            }
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

    @staticmethod
    def _sha256(path: Path) -> str:
        if not path.exists():
            return "MISSING"
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)

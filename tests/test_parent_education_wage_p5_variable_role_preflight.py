from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageP5VariableRolePreflightTests(unittest.TestCase):
    """BDD: P5 turns P4 field candidates into a reviewable VariableRoleSet draft preflight."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p5-variable-role-"))
        self.project_root = self.tmp / "project"
        self._seed_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p5a_builds_reviewable_variable_role_preflight_from_p4(self) -> None:
        """行为 1：P5 必须消费 P4 候选，形成可审阅变量角色草案。"""
        from Program.workbench.parent_education_wage_variable_role_preflight import (
            build_parent_education_wage_variable_role_preflight,
        )

        preflight = build_parent_education_wage_variable_role_preflight(self.project_root)

        self.assertEqual(preflight["schema_version"], "p5.parent_education_wage_variable_role_preflight.v1")
        self.assertEqual(preflight["status"], "variable_role_preflight_ready_for_review")
        self.assertEqual(preflight["draft_variable_roles"]["outcome"]["preferred"], "ln_wage")
        self.assertEqual(preflight["draft_variable_roles"]["treatment"]["preferred"], "parent_education")
        self.assertIn("age", preflight["draft_variable_roles"]["controls"]["preferred"])
        by_binding = {item["dataset_column"]: item for item in preflight["role_bindings"]}
        self.assertEqual(by_binding["father_education"]["binding_status"], "candidate_selected_for_review")
        self.assertEqual(by_binding["father_education"]["preferred_candidate"]["name"], "tb4_a_f")
        self.assertEqual(by_binding["mother_education"]["preferred_candidate"]["name"], "tb4_a_m")
        self.assertEqual(by_binding["hukou"]["preferred_candidate"]["name"], "qa2")

    def test_bdd_p5b_parent_education_construction_requires_human_confirmation(self) -> None:
        """行为 2：父母教育只能形成构造草案，不能自动成为正式变量。"""
        from Program.workbench.parent_education_wage_variable_role_preflight import (
            build_parent_education_wage_variable_role_preflight,
        )

        preflight = build_parent_education_wage_variable_role_preflight(self.project_root)
        construction = preflight["draft_variable_roles"]["treatment"]["construction"]

        self.assertEqual(construction["derived_variable"], "parent_education")
        self.assertEqual(construction["recommended_default"], "max(father_education, mother_education)")
        self.assertEqual(construction["decision_status"], "requires_human_confirmation")
        self.assertFalse(preflight["can_write_formal_variable_roles"])
        self.assertIn("confirm_parent_education_construction", preflight["human_review_required"])

    def test_bdd_p5c_writes_only_review_layer_and_preserves_formal_state(self) -> None:
        """行为 3：P5 不得覆盖正式 VariableRoleSet、DesignSpec、RunPlan 或创建 run id。"""
        from Program.workbench.parent_education_wage_variable_role_preflight import (
            run_parent_education_wage_variable_role_preflight,
        )

        formal_before = (self.project_root / "state/product/variable_roles.json").read_text(encoding="utf-8")
        design_before = (self.project_root / "state/product/design_spec.json").read_text(encoding="utf-8")
        run_plan_before = (self.project_root / "state/product/run_plan.json").read_text(encoding="utf-8")

        preflight, json_path, review_path = run_parent_education_wage_variable_role_preflight(self.project_root)

        self.assertTrue(json_path.exists())
        self.assertTrue(review_path.exists())
        self.assertEqual((self.project_root / "state/product/variable_roles.json").read_text(encoding="utf-8"), formal_before)
        self.assertEqual((self.project_root / "state/product/design_spec.json").read_text(encoding="utf-8"), design_before)
        self.assertEqual((self.project_root / "state/product/run_plan.json").read_text(encoding="utf-8"), run_plan_before)
        self.assertIsNone(preflight["run_id"])
        self.assertFalse(preflight["boundary_flags"]["modified_formal_variable_roles"])
        self.assertFalse(preflight["boundary_flags"]["executed_regression"])

    def test_bdd_p5d_missing_data_context_is_explicit_warning_not_silent_default(self) -> None:
        """审查闭环：缺少 P1-B/P2 输入时，P5 不能静默给出完整 outcome 草案。"""
        from Program.workbench.parent_education_wage_variable_role_preflight import (
            build_parent_education_wage_variable_role_preflight,
        )

        (self.project_root / "Results/json/parent_education_wage_data_field_binding_ledger.json").unlink()
        (self.project_root / "Results/json/parent_education_wage_p2_execution_readiness.json").unlink()

        preflight = build_parent_education_wage_variable_role_preflight(self.project_root)
        warning_ids = {item["id"] for item in preflight["input_warnings"]}

        self.assertEqual(preflight["status"], "variable_role_preflight_ready_with_input_warnings")
        self.assertIn("missing_p1b_data_field_binding_ledger", warning_ids)
        self.assertIn("missing_p2_execution_readiness", warning_ids)
        self.assertIsNone(preflight["draft_variable_roles"]["outcome"]["preferred"])
        self.assertEqual(
            preflight["draft_variable_roles"]["outcome"]["decision_status"],
            "source_ledger_missing_needs_review",
        )

    def _seed_project(self, root: Path) -> None:
        seed_p5_project(root)

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ProductControlP5VariableRolePreflightApiAndReactTests(unittest.TestCase):
    """BDD: Product Control exposes P5 VariableRoleSet draft preflight."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p5-variable-role-api-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.product_root.mkdir(parents=True)
        self._seed_project(self.project_root)
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

    def test_bdd_p5_api_get_reports_missing_and_post_generates_preflight(self) -> None:
        """行为 4：GET 不隐式生成；POST 才生成 P5 草案预检。"""
        missing = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p5-variable-role-preflight")
        self.assertEqual(missing.status_code, 200, msg=missing.text)
        self.assertEqual(missing.json()["status"], "p5_variable_role_preflight_missing")

        created = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p5-variable-role-preflight")

        self.assertEqual(created.status_code, 201, msg=created.text)
        body = created.json()
        self.assertEqual(body["status"], "variable_role_preflight_ready_for_review")
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_p5_variable_role_preflight.json").exists())

    def test_bdd_p5_react_product_control_panel_exposes_preflight(self) -> None:
        """行为 5：React 产品控制面必须展示 P5 VariableRoleSet 草案预检。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p5-variable-role-preflight", component)
        self.assertIn("P5 VariableRoleSet", component)
        self.assertIn("parent_education", component)
        self.assertIn("requires_human_confirmation", component)
        self.assertIn("刷新 P5", component)

    def _seed_project(self, root: Path) -> None:
        seed_p5_project(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)


def seed_p5_project(root: Path) -> None:
    def write_text(relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(relative_path: str, payload: dict) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    write_text("paper.yaml", "research:\n  question: 父母受教育水平对子女工资收入的影响\n")
    write_text("Program/run_paper.py", "print('ok')\n")
    write_json(
        "Results/json/parent_education_wage_p4_field_source_candidates.json",
        {
            "schema_version": "p4.parent_education_wage_field_source_candidates.v1",
            "status": "field_source_candidates_ready_for_review",
            "field_source_candidates": [
                {
                    "dataset_column": "father_education",
                    "candidate_status": "candidate_found",
                    "candidates": [
                        {
                            "name": "tb4_a_f",
                            "label": "父亲最高学历",
                            "source_path": "2018cfps/cfps2018famconf_test.dta",
                            "source_type": "stata_variable_label",
                            "evidence_level": "local_stata_metadata",
                        }
                    ],
                },
                {
                    "dataset_column": "mother_education",
                    "candidate_status": "candidate_found",
                    "candidates": [
                        {
                            "name": "tb4_a_m",
                            "label": "母亲最高学历",
                            "source_path": "2018cfps/cfps2018famconf_test.dta",
                            "source_type": "stata_variable_label",
                            "evidence_level": "local_stata_metadata",
                        }
                    ],
                },
                {
                    "dataset_column": "parent_education",
                    "candidate_status": "constructable_needs_review",
                    "construction_draft": {
                        "source_fields": ["father_education", "mother_education"],
                        "options": [
                            "max(father_education, mother_education)",
                            "mean(father_education, mother_education)",
                            "separate father/mother coefficients",
                        ],
                        "decision_status": "requires_human_confirmation",
                    },
                },
                {
                    "dataset_column": "hukou",
                    "candidate_status": "candidate_found",
                    "candidates": [
                        {
                            "name": "qa2",
                            "label": "户口状况",
                            "source_path": "2018cfps/cfps2018adult_test.dta",
                            "source_type": "stata_variable_label",
                            "evidence_level": "local_stata_metadata",
                        }
                    ],
                },
            ],
        },
    )
    write_json(
        "Results/json/parent_education_wage_data_field_binding_ledger.json",
        {
            "field_bindings": [
                {"role": "Y", "dataset_column": "ln_wage", "binding_status": "matched"},
                {"role": "Y", "dataset_column": "wage", "binding_status": "matched"},
                {"role": "control", "dataset_column": "age", "binding_status": "matched"},
                {"role": "control", "dataset_column": "female", "binding_status": "matched"},
                {"role": "control", "dataset_column": "urban", "binding_status": "matched"},
                {"role": "control", "dataset_column": "edu_last", "binding_status": "matched"},
            ]
        },
    )
    write_json(
        "Results/json/parent_education_wage_p2_execution_readiness.json",
        {"status": "blocked_missing_parent_education_fields", "execution_preflight_allowed": False},
    )
    write_json("state/product/variable_roles.json", {"status": "approved", "roles": {"treatment": ["trained"]}})
    write_json("state/product/design_spec.json", {"status": "approved", "topic": "old"})
    write_json("state/product/run_plan.json", {"status": "approved", "method": "OLS"})

from __future__ import annotations

import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry
from Program.workbench.parent_education_wage_data_field_binding_ledger import (
    build_parent_education_wage_data_field_binding_ledger,
    write_parent_education_wage_data_field_binding_ledger,
)


class ParentEducationWageDataFieldBindingLedgerTests(unittest.TestCase):
    """BDD: P1-B variable candidates must be checked against real fields before formal use."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-data-binding-"))
        self.project_root = self.tmp / "project"
        self._seed_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p1b_matches_candidate_variables_to_real_field_sources(self) -> None:
        """行为 1：候选变量必须记录真实字段来源、匹配状态和证据等级。"""
        ledger = build_parent_education_wage_data_field_binding_ledger(self.project_root)

        self.assertEqual(ledger["schema_version"], "p1b.parent_education_wage_data_field_binding_ledger.v1")
        self.assertEqual(ledger["status"], "blocked_missing_parent_education_fields")
        self.assertGreaterEqual(ledger["candidate_variable_count"], 5)
        bindings = {item["dataset_column"]: item for item in ledger["field_bindings"]}
        self.assertEqual(bindings["ln_wage"]["binding_status"], "matched")
        self.assertEqual(bindings["wage"]["binding_status"], "matched")
        self.assertEqual(bindings["edu_last"]["binding_status"], "matched")
        self.assertEqual(bindings["father_education"]["binding_status"], "missing")
        self.assertEqual(bindings["mother_education"]["binding_status"], "missing")
        self.assertIn("missing_parent_education_source_fields", ledger["blocking_reasons"])
        self.assertTrue(all(item["evidence_level"] == "local_file" for item in ledger["field_bindings"]))

    def test_bdd_p1b_does_not_overwrite_formal_variable_roles(self) -> None:
        """行为 2：字段绑定证据只能进入审阅层，不能覆盖正式 VariableRoleSet。"""
        formal_roles = self.project_root / "state/product/variable_roles.json"
        before = formal_roles.read_text(encoding="utf-8")

        ledger = build_parent_education_wage_data_field_binding_ledger(self.project_root)
        write_parent_education_wage_data_field_binding_ledger(self.project_root, ledger)

        self.assertFalse(ledger["promotion"]["allowed"])
        self.assertFalse(ledger["boundary_flags"]["modified_formal_variable_roles"])
        self.assertFalse(ledger["boundary_flags"]["modified_design_spec"])
        self.assertFalse(ledger["boundary_flags"]["modified_run_plan"])
        self.assertEqual(before, formal_roles.read_text(encoding="utf-8"))

    def test_bdd_p1b_writes_json_and_review_outputs(self) -> None:
        """行为 3：P1-B 字段绑定账本必须有 JSON 和人工审阅 Markdown。"""
        ledger = build_parent_education_wage_data_field_binding_ledger(self.project_root)
        json_path, review_path = write_parent_education_wage_data_field_binding_ledger(self.project_root, ledger)

        self.assertTrue(json_path.exists())
        self.assertTrue(review_path.exists())
        body = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(body["status"], "blocked_missing_parent_education_fields")
        review = review_path.read_text(encoding="utf-8")
        self.assertIn("P1-B 数据字段绑定账本", review)
        self.assertIn("不写正式变量角色", review)
        self.assertIn("father_education", review)

    def _seed_project(self, root: Path) -> None:
        self._write_text(root, "state/product/variable_roles.json", json.dumps({"status": "approved", "roles": {"outcome": ["old_y"]}}, ensure_ascii=False))
        self._write_text(
            root,
            "Tasks/parent-education-wage/variables.yaml",
            """variables:
- role: Y
  dataset_column: ln_wage
  semantic_label: 对数工资收入
  review_status: candidate_needs_dataset_check
- role: Y
  dataset_column: wage
  semantic_label: 工资收入
  review_status: candidate_needs_dataset_check
- role: X
  dataset_column: father_education
  semantic_label: 父亲受教育水平
  review_status: candidate_needs_dataset_check
- role: X
  dataset_column: mother_education
  semantic_label: 母亲受教育水平
  review_status: candidate_needs_dataset_check
- role: control
  dataset_column: edu_last
  semantic_label: 子女受教育年限
  review_status: candidate_needs_dataset_check
""",
        )
        self._write_csv(root / "Data/Final/cfps_robot_reallocation.csv", ["pid", "ln_wage", "edu_last", "age", "female"])
        self._write_csv(root / "Data/Final/analysis_sample.csv", ["trained", "wage", "edu", "experience"])

    def _write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_csv(self, path: Path, header: list[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerow([1 for _ in header])


class ProductControlP1DataFieldApiAndReactTests(unittest.TestCase):
    """BDD: Product Control must expose P1-B data field binding status."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p1-data-api-"))
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

    def test_bdd_p1b_api_get_reports_missing_and_post_generates_ledger(self) -> None:
        """行为 4：GET 不隐式生成；POST 才生成 P1-B 数据字段绑定账本。"""
        missing = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p1-data-field-binding")
        self.assertEqual(missing.status_code, 200, msg=missing.text)
        self.assertEqual(missing.json()["status"], "p1b_data_field_binding_missing")

        created = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p1-data-field-binding")

        self.assertEqual(created.status_code, 201, msg=created.text)
        body = created.json()
        self.assertEqual(body["status"], "blocked_missing_parent_education_fields")
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_data_field_binding_ledger.json").exists())

    def test_bdd_p1b_react_product_control_panel_exposes_p1b_status(self) -> None:
        """行为 5：React 产品控制面必须展示 P1-B 数据字段绑定状态。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p1-data-field-binding", component)
        self.assertIn("P1-B 数据字段", component)
        self.assertIn("blocked_missing_parent_education_fields", component)
        self.assertIn("变量字段", component)

    def _seed_project(self, root: Path) -> None:
        self._write_text(root, "paper.yaml", "research:\n  question: 父母受教育水平对子女工资收入的影响\n")
        self._write_text(root, "Program/run_paper.py", "print('ok')\n")
        self._write_text(root, "state/product/variable_roles.json", json.dumps({"status": "approved", "roles": {"outcome": ["old_y"]}}, ensure_ascii=False))
        self._write_json(
            root,
            "state/product/topic_binding.json",
            {
                "expected_topic": "父母受教育水平对子女工资收入的影响",
                "expected_slug": "parent-education-wage",
            },
        )
        self._write_text(
            root,
            "Tasks/parent-education-wage/variables.yaml",
            "variables:\n- role: Y\n  dataset_column: ln_wage\n  semantic_label: 对数工资收入\n- role: X\n  dataset_column: father_education\n  semantic_label: 父亲受教育水平\n",
        )
        self._write_csv(root / "Data/Final/cfps_robot_reallocation.csv", ["pid", "ln_wage", "edu_last"])

    def _write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        self._write_text(root, relative_path, json.dumps(payload, ensure_ascii=False, indent=2))

    def _write_csv(self, path: Path, header: list[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerow([1 for _ in header])


if __name__ == "__main__":
    unittest.main(verbosity=2)

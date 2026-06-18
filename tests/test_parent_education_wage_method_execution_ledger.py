from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry
from Program.workbench.parent_education_wage_method_execution_ledger import (
    build_parent_education_wage_method_execution_ledger,
    write_parent_education_wage_method_execution_ledger,
)


class ParentEducationWageMethodExecutionLedgerTests(unittest.TestCase):
    """BDD: P1-C must create an execution ledger even when methods are blocked."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-method-ledger-"))
        self.project_root = self.tmp / "project"
        self._seed_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p1c_blocks_execution_when_required_fields_are_missing(self) -> None:
        """行为 1：核心字段缺失时不能创建 run id 或伪造回归结果。"""
        ledger = build_parent_education_wage_method_execution_ledger(self.project_root)

        self.assertEqual(ledger["schema_version"], "p1c.parent_education_wage_method_execution_ledger.v1")
        self.assertEqual(ledger["status"], "blocked_missing_required_fields")
        self.assertIsNone(ledger["run_id"])
        self.assertFalse(ledger["execution_allowed"])
        self.assertIn("father_education", ledger["missing_required_fields"])
        self.assertIn("mother_education", ledger["missing_required_fields"])
        self.assertIn("missing_required_fields", ledger["blocking_reasons"])
        self.assertTrue(all(method["status"] == "blocked" for method in ledger["method_candidates"]))

    def test_bdd_p1c_records_design_contamination_and_statspai_boundary(self) -> None:
        """行为 2：方法账本必须记录旧 robot code_stub 污染和 StatsPAI 使用边界。"""
        ledger = build_parent_education_wage_method_execution_ledger(self.project_root)

        self.assertIn("design_code_stub_topic_contamination", ledger["blocking_reasons"])
        self.assertFalse(ledger["boundary_flags"]["called_statspai_paper"])
        self.assertFalse(ledger["boundary_flags"]["modified_formal_run_plan"])
        self.assertEqual(ledger["statspai_boundary"]["allowed_after"], "analysis_ready_dataframe")
        self.assertIn("sp.paper", ledger["statspai_boundary"]["forbidden_calls"])

    def test_bdd_p1c_writes_blocked_run_json_and_review(self) -> None:
        """行为 3：即使不能执行，也要写出 failure/blocked ledger。"""
        ledger = build_parent_education_wage_method_execution_ledger(self.project_root)
        json_path, review_path = write_parent_education_wage_method_execution_ledger(self.project_root, ledger)

        self.assertTrue(json_path.exists())
        self.assertTrue(review_path.exists())
        body = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(body["status"], "blocked_missing_required_fields")
        review = review_path.read_text(encoding="utf-8")
        self.assertIn("P1-C 方法执行账本", review)
        self.assertIn("run id：未创建", review)
        self.assertIn("father_education", review)

    def _seed_project(self, root: Path) -> None:
        self._write_json(
            root,
            "Results/json/parent_education_wage_data_field_binding_ledger.json",
            {
                "status": "blocked_missing_parent_education_fields",
                "missing_fields": [
                    {"dataset_column": "father_education"},
                    {"dataset_column": "mother_education"},
                ],
                "matched_fields": [
                    {"dataset_column": "ln_wage"},
                    {"dataset_column": "edu_last"},
                ],
            },
        )
        self._write_json(
            root,
            "Tasks/parent-education-wage/design.json",
            {
                "candidates": [{"method": "IV"}, {"method": "DID"}, {"method": "DML"}],
                "recommended": "IV",
                "code_stub": "endog = df['robot_exposure']\nmodel = IV2SLS(df['ln_wage'], exog, endog, instruments)",
            },
        )

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ProductControlP1MethodApiAndReactTests(unittest.TestCase):
    """BDD: Product Control must expose P1-C method execution ledger status."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p1-method-api-"))
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

    def test_bdd_p1c_api_get_reports_missing_and_post_generates_ledger(self) -> None:
        """行为 4：GET 不隐式生成；POST 才生成 P1-C 方法执行账本。"""
        missing = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p1-method-execution")
        self.assertEqual(missing.status_code, 200, msg=missing.text)
        self.assertEqual(missing.json()["status"], "p1c_method_execution_ledger_missing")

        created = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p1-method-execution")

        self.assertEqual(created.status_code, 201, msg=created.text)
        body = created.json()
        self.assertEqual(body["status"], "blocked_missing_required_fields")
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_method_execution_ledger.json").exists())

    def test_bdd_p1c_react_product_control_panel_exposes_p1c_status(self) -> None:
        """行为 5：React 产品控制面必须展示 P1-C 方法执行状态。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p1-method-execution", component)
        self.assertIn("P1-C 方法执行", component)
        self.assertIn("blocked_missing_required_fields", component)
        self.assertIn("run id", component)

    def _seed_project(self, root: Path) -> None:
        self._write_text(root, "paper.yaml", "research:\n  question: 父母受教育水平对子女工资收入的影响\n")
        self._write_text(root, "Program/run_paper.py", "print('ok')\n")
        self._write_json(root, "state/product/topic_binding.json", {"expected_slug": "parent-education-wage"})
        self._write_json(
            root,
            "Results/json/parent_education_wage_data_field_binding_ledger.json",
            {
                "status": "blocked_missing_parent_education_fields",
                "missing_fields": [{"dataset_column": "father_education"}],
                "matched_fields": [{"dataset_column": "ln_wage"}],
            },
        )
        self._write_json(
            root,
            "Tasks/parent-education-wage/design.json",
            {"candidates": [{"method": "IV"}], "recommended": "IV", "code_stub": "df['robot_exposure']"},
        )

    def _write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        self._write_text(root, relative_path, json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    unittest.main(verbosity=2)

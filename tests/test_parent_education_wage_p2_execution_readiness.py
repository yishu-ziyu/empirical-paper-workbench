from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageP2ExecutionReadinessTests(unittest.TestCase):
    """BDD: P2 must turn P1-C blockers into an auditable execution-readiness ledger."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p2-readiness-"))
        self.project_root = self.tmp / "project"
        self._seed_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p2a_field_supplementation_records_candidates_without_formal_write(self) -> None:
        """行为 1：字段补证只生成候选，不直接写正式变量角色。"""
        from Program.workbench.parent_education_wage_execution_readiness import (
            build_parent_education_wage_execution_readiness_ledger,
        )

        ledger = build_parent_education_wage_execution_readiness_ledger(self.project_root)

        self.assertEqual(ledger["schema_version"], "p2.parent_education_wage_execution_readiness.v1")
        self.assertEqual(ledger["status"], "blocked_missing_parent_education_fields")
        self.assertFalse(ledger["boundary_flags"]["modified_formal_variable_roles"])
        by_field = {item["dataset_column"]: item for item in ledger["field_supplementation"]}
        self.assertEqual(by_field["hukou"]["supplement_status"], "candidate_found")
        self.assertEqual(by_field["father_education"]["supplement_status"], "missing")
        self.assertIn("qa2", [candidate["name"] for candidate in by_field["hukou"]["candidates"]])

    def test_bdd_p2b_variable_operationalization_is_draft_only(self) -> None:
        """行为 2：变量口径建议只能进入 draft，父母教育合成规则必须等待人工确认。"""
        from Program.workbench.parent_education_wage_execution_readiness import (
            build_parent_education_wage_execution_readiness_ledger,
        )

        ledger = build_parent_education_wage_execution_readiness_ledger(self.project_root)
        draft = ledger["variable_operationalization_draft"]

        self.assertEqual(draft["outcome"]["preferred"], "ln_wage")
        self.assertEqual(draft["treatment"]["status"], "blocked_missing_parent_education_fields")
        self.assertEqual(draft["parent_education_construction"]["decision_status"], "requires_human_confirmation")
        self.assertFalse(draft["can_write_formal_variable_roles"])

    def test_bdd_p2c_repairs_design_stub_without_writing_formal_designspec(self) -> None:
        """行为 3：设计草案必须清理旧 robot 题目污染，但不写正式 DesignSpec。"""
        from Program.workbench.parent_education_wage_execution_readiness import (
            repair_parent_education_wage_design_draft,
        )

        repair = repair_parent_education_wage_design_draft(self.project_root)

        self.assertTrue(repair["repaired"])
        self.assertFalse(repair["modified_formal_design_spec"])
        design_text = (self.project_root / "Tasks/parent-education-wage/design.json").read_text(encoding="utf-8")
        self.assertNotIn("robot_exposure", design_text)
        self.assertNotIn("bartik_iv", design_text)
        self.assertNotIn("robot_density", design_text)
        self.assertIn("parent_education", design_text)

    def test_bdd_p2d_writes_blocked_execution_readiness_ledger(self) -> None:
        """行为 4：字段仍缺失时，P2 输出 blocked ledger，不创建 run id。"""
        from Program.workbench.parent_education_wage_execution_readiness import (
            run_parent_education_wage_execution_readiness,
        )

        ledger, json_path, review_path = run_parent_education_wage_execution_readiness(self.project_root)

        self.assertEqual(ledger["status"], "blocked_missing_parent_education_fields")
        self.assertFalse(ledger["execution_preflight_allowed"])
        self.assertIsNone(ledger["run_id"])
        self.assertIn("missing_parent_education_fields", ledger["blocking_reasons"])
        self.assertTrue(json_path.exists())
        self.assertTrue(review_path.exists())
        self.assertIn("P2 执行准入账本", review_path.read_text(encoding="utf-8"))

    def _seed_project(self, root: Path) -> None:
        self._write_json(
            root,
            "Results/json/parent_education_wage_data_field_binding_ledger.json",
            {
                "status": "blocked_missing_parent_education_fields",
                "matched_fields": [
                    {"dataset_column": "ln_wage"},
                    {"dataset_column": "wage"},
                    {"dataset_column": "edu_last"},
                    {"dataset_column": "age"},
                    {"dataset_column": "female"},
                    {"dataset_column": "urban"},
                ],
                "missing_fields": [
                    {"dataset_column": "father_education", "semantic_label": "父亲受教育水平"},
                    {"dataset_column": "mother_education", "semantic_label": "母亲受教育水平"},
                    {"dataset_column": "parent_education", "semantic_label": "父母受教育水平"},
                    {"dataset_column": "hukou", "semantic_label": "户口状态"},
                ],
            },
        )
        self._write_json(
            root,
            "Tasks/parent-education-wage/design.json",
            {
                "candidates": [{"method": "IV"}, {"method": "DID"}, {"method": "DML"}],
                "recommended": "IV",
                "code_stub": "endog = df['robot_exposure']\ninstruments = df['bartik_iv']\nrobot_density = df['robot_density']",
            },
        )
        self._write_json(
            root,
            "state/product/variable_role_candidates.json",
            {
                "candidates": {
                    "candidate_hukou": {
                        "source": {
                            "name": "cfps2011adult.dta",
                            "path": "/external/cfps2011adult.dta",
                            "file_type": "dta",
                            "evidence_level": "local_file",
                        },
                        "field_options": [
                            {"name": "qa2", "label": "您现在的户口状况是以下哪类？"},
                            {"name": "qc1", "label": "请问，到目前为止，您已完成（毕业）的最高学历是？"},
                        ],
                    }
                }
            },
        )

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ProductControlP2ExecutionReadinessApiAndReactTests(unittest.TestCase):
    """BDD: Product Control must expose P2 execution-readiness status."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p2-readiness-api-"))
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

    def test_bdd_p2_api_get_reports_missing_and_post_generates_readiness_ledger(self) -> None:
        """行为 5：GET 不隐式生成；POST 才生成 P2 执行准入账本。"""
        missing = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p2-execution-readiness")
        self.assertEqual(missing.status_code, 200, msg=missing.text)
        self.assertEqual(missing.json()["status"], "p2_execution_readiness_missing")

        created = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p2-execution-readiness")

        self.assertEqual(created.status_code, 201, msg=created.text)
        body = created.json()
        self.assertEqual(body["status"], "blocked_missing_parent_education_fields")
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_p2_execution_readiness.json").exists())

    def test_bdd_p2_react_product_control_panel_exposes_next_stage_status(self) -> None:
        """行为 5：React 产品控制面必须展示 P2 执行准入状态。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p2-execution-readiness", component)
        self.assertIn("P2 执行准入", component)
        self.assertIn("execution_preflight_allowed", component)
        self.assertIn("刷新 P2", component)

    def _seed_project(self, root: Path) -> None:
        self._write_text(root, "paper.yaml", "research:\n  question: 父母受教育水平对子女工资收入的影响\n")
        self._write_text(root, "Program/run_paper.py", "print('ok')\n")
        self._write_json(root, "state/product/topic_binding.json", {"expected_slug": "parent-education-wage"})
        self._write_json(
            root,
            "Results/json/parent_education_wage_data_field_binding_ledger.json",
            {
                "status": "blocked_missing_parent_education_fields",
                "matched_fields": [{"dataset_column": "ln_wage"}],
                "missing_fields": [{"dataset_column": "father_education"}],
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

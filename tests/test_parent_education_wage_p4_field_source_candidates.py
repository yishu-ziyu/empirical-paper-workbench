from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageP4FieldSourceCandidateTests(unittest.TestCase):
    """BDD: P4 discovers auditable parent-education field source candidates."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p4-fields-"))
        self.project_root = self.tmp / "project"
        self.cfps_root = self.tmp / "cfps"
        self._seed_project(self.project_root)
        self._seed_cfps_data(self.cfps_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p4a_scans_live_cfps_root_and_records_stale_paths(self) -> None:
        """行为 1：P4 必须使用存在的 CFPS 根目录，并记录旧路径为 stale source。"""
        from Program.workbench.parent_education_wage_field_source_candidates import (
            build_parent_education_wage_field_source_candidates,
        )

        ledger = build_parent_education_wage_field_source_candidates(self.project_root, data_root=self.cfps_root)

        self.assertEqual(ledger["schema_version"], "p4.parent_education_wage_field_source_candidates.v1")
        self.assertEqual(ledger["status"], "field_source_candidates_ready_for_review")
        self.assertEqual(Path(ledger["source_roots"]["selected_root"]), self.cfps_root.resolve())
        self.assertGreaterEqual(ledger["source_roots"]["scanned_file_count"], 1)
        self.assertIn("/missing/cfps2011adult.dta", ledger["source_roots"]["stale_source_paths"])

    def test_bdd_p4b_discovers_father_and_mother_education_from_stata_labels(self) -> None:
        """行为 2：Stata 标签里的父亲/母亲最高学历必须形成字段候选。"""
        from Program.workbench.parent_education_wage_field_source_candidates import (
            build_parent_education_wage_field_source_candidates,
        )

        ledger = build_parent_education_wage_field_source_candidates(self.project_root, data_root=self.cfps_root)
        by_field = {item["dataset_column"]: item for item in ledger["field_source_candidates"]}

        self.assertEqual(by_field["father_education"]["candidate_status"], "candidate_found")
        self.assertEqual(by_field["mother_education"]["candidate_status"], "candidate_found")
        father_names = {candidate["name"] for candidate in by_field["father_education"]["candidates"]}
        mother_names = {candidate["name"] for candidate in by_field["mother_education"]["candidates"]}
        self.assertIn("tb4_a_f", father_names)
        self.assertIn("tb4_a_m", mother_names)
        first_father = by_field["father_education"]["candidates"][0]
        self.assertIn("父亲最高学历", first_father["label"])
        self.assertEqual(first_father["source_type"], "stata_variable_label")

    def test_bdd_p4c_parent_education_is_constructable_but_not_formal(self) -> None:
        """行为 3/4：parent_education 只能进入构造草案，不得写正式变量角色。"""
        from Program.workbench.parent_education_wage_field_source_candidates import (
            run_parent_education_wage_field_source_candidates,
        )

        ledger, json_path, review_path = run_parent_education_wage_field_source_candidates(
            self.project_root,
            data_root=self.cfps_root,
        )
        by_field = {item["dataset_column"]: item for item in ledger["field_source_candidates"]}

        self.assertEqual(by_field["parent_education"]["candidate_status"], "constructable_needs_review")
        self.assertFalse(by_field["parent_education"]["can_write_formal_variable_roles"])
        self.assertFalse(ledger["boundary_flags"]["modified_formal_variable_roles"])
        self.assertFalse(ledger["boundary_flags"]["executed_regression"])
        self.assertIsNone(ledger["run_id"])
        self.assertTrue(json_path.exists())
        self.assertTrue(review_path.exists())
        self.assertFalse((self.project_root / "state/product/variable_roles.json").exists())
        self.assertFalse((self.project_root / "state/product/design_spec.json").exists())
        self.assertFalse((self.project_root / "state/product/run_plan.json").exists())

    def _seed_project(self, root: Path) -> None:
        self._write_json(
            root,
            "state/product/variable_role_candidates.json",
            {
                "candidates": {
                    "candidate_hukou": {
                        "source": {"path": "/missing/cfps2011adult.dta", "file_type": "dta"},
                        "field_options": [{"name": "qa2", "label": "户口状况"}],
                    }
                }
            },
        )

    def _seed_cfps_data(self, root: Path) -> None:
        data_dir = root / "2018cfps"
        data_dir.mkdir(parents=True)
        frame = pd.DataFrame(
            {
                "pid": [1, 2, 3],
                "tb4_a_f": [1, 2, 3],
                "tb4_a_m": [2, 3, 4],
                "hukou": [1, 2, 1],
            }
        )
        frame.to_stata(
            data_dir / "cfps2018famconf_test.dta",
            write_index=False,
            version=118,
            variable_labels={
                "pid": "样本编码",
                "tb4_a_f": "父亲最高学历",
                "tb4_a_m": "母亲最高学历",
                "hukou": "户口状况",
            },
        )

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ProductControlP4FieldSourceApiAndReactTests(unittest.TestCase):
    """BDD: Product Control exposes P4 field source candidate generation."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p4-fields-api-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.cfps_root = self.tmp / "cfps"
        self.product_root.mkdir(parents=True)
        self._seed_project(self.project_root)
        self._seed_cfps_data(self.cfps_root)
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

    def test_bdd_p4_api_get_reports_missing_and_post_generates_candidates(self) -> None:
        """行为 5：GET 不隐式生成；POST 才生成 P4 字段来源候选账本。"""
        missing = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p4-field-source-candidates")
        self.assertEqual(missing.status_code, 200, msg=missing.text)
        self.assertEqual(missing.json()["status"], "p4_field_source_candidates_missing")

        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p4-field-source-candidates",
            params={"data_root": str(self.cfps_root)},
        )

        self.assertEqual(created.status_code, 201, msg=created.text)
        body = created.json()
        self.assertEqual(body["status"], "field_source_candidates_ready_for_review")
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_p4_field_source_candidates.json").exists())

    def test_bdd_p4_react_product_control_panel_exposes_field_source_status(self) -> None:
        """行为 5：React 产品控制面必须展示 P4 字段来源和父母教育状态。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p4-field-source-candidates", component)
        self.assertIn("P4 字段来源", component)
        self.assertIn("father_education", component)
        self.assertIn("mother_education", component)
        self.assertIn("刷新 P4", component)

    def _seed_project(self, root: Path) -> None:
        self._write_text(root, "paper.yaml", "research:\n  question: 父母受教育水平对子女工资收入的影响\n")
        self._write_text(root, "Program/run_paper.py", "print('ok')\n")
        self._write_json(root, "state/product/topic_binding.json", {"expected_slug": "parent-education-wage"})

    def _seed_cfps_data(self, root: Path) -> None:
        data_dir = root / "2018cfps"
        data_dir.mkdir(parents=True)
        frame = pd.DataFrame({"pid": [1], "tb4_a_f": [1], "tb4_a_m": [2], "hukou": [1]})
        frame.to_stata(
            data_dir / "cfps2018famconf_test.dta",
            write_index=False,
            version=118,
            variable_labels={
                "pid": "样本编码",
                "tb4_a_f": "父亲最高学历",
                "tb4_a_m": "母亲最高学历",
                "hukou": "户口状况",
            },
        )

    def _write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        self._write_text(root, relative_path, json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    unittest.main(verbosity=2)

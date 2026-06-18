from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from docx import Document
from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageP3DraftPackageTests(unittest.TestCase):
    """BDD: P3 turns a blocked execution state into a user-visible DraftPackage."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p3-draft-"))
        self.project_root = self.tmp / "project"
        self._seed_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p3a_blocked_readiness_generates_partial_draft_package(self) -> None:
        """行为 1：P2 阻断态必须转成半成品 DraftPackage，而不是只返回诊断账本。"""
        from Program.workbench.parent_education_wage_draft_package import (
            build_parent_education_wage_draft_package,
        )

        package = build_parent_education_wage_draft_package(self.project_root)

        self.assertEqual(package["schema_version"], "p3.parent_education_wage_draft_package.v1")
        self.assertEqual(package["status"], "blocked_draft_package_ready")
        self.assertFalse(package["full_draft_ready"])
        self.assertEqual(package["draft_kind"], "partial_red_flagged_draft")
        self.assertIn("missing_parent_education_fields", package["blocking_reasons"])
        self.assertGreaterEqual(package["issue_count"], 3)
        self.assertEqual(package["product_control_signal"]["phase"], "P3")

    def test_bdd_p3b_writes_docx_markdown_issue_audit_and_manifest(self) -> None:
        """行为 2/3：P3 必须写出用户能打开的 docx，并同步问题清单和审计报告。"""
        from Program.workbench.parent_education_wage_draft_package import (
            run_parent_education_wage_draft_package,
        )

        package, json_path = run_parent_education_wage_draft_package(self.project_root)

        self.assertTrue(json_path.exists())
        outputs = package["outputs"]
        docx_path = self.project_root / outputs["docx"]
        markdown_path = self.project_root / outputs["markdown"]
        issue_path = self.project_root / outputs["issue_list"]
        audit_path = self.project_root / outputs["audit_report"]
        self.assertTrue(docx_path.exists(), outputs)
        self.assertTrue(markdown_path.exists(), outputs)
        self.assertTrue(issue_path.exists(), outputs)
        self.assertTrue(audit_path.exists(), outputs)

        issue_text = issue_path.read_text(encoding="utf-8")
        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn("father_education", issue_text)
        self.assertIn("mother_education", issue_text)
        self.assertIn("missing_parent_education_fields", issue_text)
        self.assertIn("未执行回归", audit_text)
        self.assertIn("正式层写回：否", audit_text)

        doc = Document(docx_path)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        self.assertIn("父母受教育水平对子女工资收入的影响", text)
        self.assertIn("【红标】", text)
        self.assertIn("父母教育字段尚未绑定", text)

    def test_bdd_p3c_does_not_write_formal_state_or_create_run_id(self) -> None:
        """行为 4：P3 只生成草稿交付包，不写正式变量、设计、RunPlan 或 run id。"""
        from Program.workbench.parent_education_wage_draft_package import (
            run_parent_education_wage_draft_package,
        )

        package, _ = run_parent_education_wage_draft_package(self.project_root)

        self.assertFalse((self.project_root / "state/product/variable_roles.json").exists())
        self.assertFalse((self.project_root / "state/product/design_spec.json").exists())
        self.assertFalse((self.project_root / "state/product/run_plan.json").exists())
        self.assertIsNone(package["run_id"])
        self.assertFalse(package["boundary_flags"]["modified_formal_variable_roles"])
        self.assertFalse(package["boundary_flags"]["modified_formal_design_spec"])
        self.assertFalse(package["boundary_flags"]["modified_formal_run_plan"])
        self.assertFalse(package["boundary_flags"]["executed_regression"])

    def _seed_project(self, root: Path) -> None:
        self._write_json(
            root,
            "Results/json/parent_education_wage_p2_execution_readiness.json",
            {
                "schema_version": "p2.parent_education_wage_execution_readiness.v1",
                "topic": "父母受教育水平对子女工资收入的影响",
                "topic_slug": "parent-education-wage",
                "status": "blocked_missing_parent_education_fields",
                "execution_preflight_allowed": False,
                "run_id": None,
                "blocking_reasons": [
                    "missing_parent_education_fields",
                    "human_variable_operationalization_required",
                ],
                "field_supplementation": [
                    {"dataset_column": "father_education", "supplement_status": "missing", "candidates": []},
                    {"dataset_column": "mother_education", "supplement_status": "missing", "candidates": []},
                    {"dataset_column": "parent_education", "supplement_status": "missing", "candidates": []},
                    {
                        "dataset_column": "hukou",
                        "supplement_status": "candidate_found",
                        "candidates": [{"name": "qa2", "label": "户口状况"}],
                    },
                ],
                "variable_operationalization_draft": {
                    "outcome": {"preferred": "ln_wage"},
                    "treatment": {
                        "preferred": "parent_education",
                        "status": "blocked_missing_parent_education_fields",
                    },
                },
                "method_execution_gate": {
                    "allowed": False,
                    "blocked_methods": [
                        {"method": "IV", "status": "blocked"},
                        {"method": "DID", "status": "blocked"},
                        {"method": "DML", "status": "blocked"},
                    ],
                },
            },
        )

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ProductControlP3DraftPackageApiAndReactTests(unittest.TestCase):
    """BDD: Product Control exposes P3 DraftPackage generation."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p3-draft-api-"))
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

    def test_bdd_p3_api_get_reports_missing_and_post_generates_draft_package(self) -> None:
        """行为 5：GET 不隐式生成；POST 才生成 P3 DraftPackage。"""
        missing = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p3-draft-package")
        self.assertEqual(missing.status_code, 200, msg=missing.text)
        self.assertEqual(missing.json()["status"], "p3_draft_package_missing")

        created = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p3-draft-package")

        self.assertEqual(created.status_code, 201, msg=created.text)
        body = created.json()
        self.assertEqual(body["status"], "blocked_draft_package_ready")
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertTrue((self.project_root / "Submissions/parent_education_wage_paper_draft.docx").exists())

    def test_bdd_p3_react_product_control_panel_exposes_draft_package(self) -> None:
        """行为 6：React 产品控制面必须展示 P3 DraftPackage 和 paper_draft.docx。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p3-draft-package", component)
        self.assertIn("P3 DraftPackage", component)
        self.assertIn("paper_draft.docx", component)
        self.assertIn("半成品", component)
        self.assertIn("刷新 P3", component)

    def _seed_project(self, root: Path) -> None:
        self._write_text(root, "paper.yaml", "research:\n  question: 父母受教育水平对子女工资收入的影响\n")
        self._write_text(root, "Program/run_paper.py", "print('ok')\n")
        self._write_json(root, "state/product/topic_binding.json", {"expected_slug": "parent-education-wage"})
        self._write_json(
            root,
            "Results/json/parent_education_wage_p2_execution_readiness.json",
            {
                "topic": "父母受教育水平对子女工资收入的影响",
                "topic_slug": "parent-education-wage",
                "status": "blocked_missing_parent_education_fields",
                "execution_preflight_allowed": False,
                "run_id": None,
                "blocking_reasons": ["missing_parent_education_fields"],
                "field_supplementation": [
                    {"dataset_column": "father_education", "supplement_status": "missing", "candidates": []}
                ],
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

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class MethodWorkflowChecklistApiTests(unittest.TestCase):
    """BDD: 实证方法必须通过前置条件清单和诊断要求才能进入执行计划。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="method-workflow-checklist-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "method-workflow-checklist",
                "title": "Method Workflow Checklist Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self._approve_variable_roles()
        self._approve_design_spec()

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_ols_ready_when_outcome_and_treatment_exist(self) -> None:
        """行为 1：OLS 具备 outcome/treatment 时 ready，并声明基础诊断证据。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/method-workflows")

        self.assertEqual(response.status_code, 200, msg=response.text)
        methods = self._methods_by_id(response)
        ols = methods["ols"]
        self.assertEqual(ols["label"], "OLS：可执行")
        self.assertEqual(ols["readiness_status"], "ready")
        self.assertEqual(ols["required_inputs"], ["outcome", "treatment"])
        self.assertEqual(
            ols["required_diagnostics"],
            ["sample_size", "missingness", "coefficient_table", "residual_diagnostics"],
        )
        self.assertEqual(ols["blockers"], [])

    def test_bdd_2_did_blocked_without_panel_time_and_treatment_timing(self) -> None:
        """行为 2：DID 缺少时间变量和处理时点时必须阻塞。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/method-workflows")

        self.assertEqual(response.status_code, 200, msg=response.text)
        did = self._methods_by_id(response)["did"]
        self.assertEqual(did["label"], "DID：缺少时间变量、处理时点")
        self.assertEqual(did["readiness_status"], "blocked")
        self.assertEqual(
            did["required_inputs"],
            ["outcome", "treatment", "unit_id", "time_variable", "treatment_timing"],
        )
        self.assertIn("time_variable_required", did["blockers"])
        self.assertIn("treatment_timing_required", did["blockers"])
        self.assertIn("parallel_trends", did["required_diagnostics"])
        self.assertIn("heterogeneous_treatment_effects", did["required_diagnostics"])

    def test_bdd_3_iv_blocked_without_instruments(self) -> None:
        """行为 3：IV 缺少 instruments 时必须阻塞。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/method-workflows")

        self.assertEqual(response.status_code, 200, msg=response.text)
        iv = self._methods_by_id(response)["iv"]
        self.assertEqual(iv["label"], "IV：缺少工具变量")
        self.assertEqual(iv["readiness_status"], "blocked")
        self.assertIn("instrument_required", iv["blockers"])
        self.assertIn("first_stage", iv["required_diagnostics"])
        self.assertIn("exclusion_restriction_review", iv["required_diagnostics"])

    def test_bdd_4_blocked_method_cannot_be_approved_for_run_plan(self) -> None:
        """行为 4：blocked 方法不能被保存成 approved RunPlan。"""
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        did_tasks = [dict(task, method_id="did", estimator="did") for task in draft["tasks"]]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={
                "tasks": did_tasks,
                "outputs": draft["outputs"],
                "note": "尝试将 DID 直接放入执行计划。",
            },
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "method_workflow_blocked")
        self.assertFalse((self.project_root / "state" / "product" / "run_plan.json").exists())

    def _approve_variable_roles(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/analysis_sample.csv",
                "roles": {
                    "outcome": ["wage"],
                    "treatment": ["trained"],
                    "controls": ["edu", "experience"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "变量角色已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_design_spec(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "培训是否影响工资？",
                "identification_strategy": {
                    "name": "baseline_ols",
                    "summary": "在已确认控制变量下估计培训对工资的相关关系。",
                    "assumptions": ["控制教育和经验后，处理变量外生。"],
                    "threats": ["遗漏变量偏误", "样本选择偏误"],
                },
                "model": {
                    "estimator": "ols",
                    "formula": "wage ~ trained + edu + experience",
                    "fixed_effects": [],
                    "cluster_by": [],
                    "sample_filter": "all",
                },
                "note": "研究设计已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    @staticmethod
    def _methods_by_id(response) -> dict[str, dict]:
        return {method["id"]: method for method in response.json()["methods"]}

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: method-workflow-checklist\n  title: Method Workflow Checklist Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n12,0,14,5\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class MethodWorkflowChecklistFrontendTests(unittest.TestCase):
    """BDD: 前端必须把方法工作流做成低噪声的可展开清单。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_frontend_shows_method_workflow_requirements(self) -> None:
        """行为 5：前端默认显示状态摘要，详细要求放在折叠区。"""
        self.assertIn("method-workflow-panel", self.index_html)
        self.assertIn("method-workflow-body", self.index_html)
        self.assertIn("renderMethodWorkflows", self.app_js)
        self.assertIn("查看方法要求", self.app_js)
        self.assertIn("OLS：可执行", self.app_js)
        self.assertIn("DID：缺少时间变量、处理时点", self.app_js)
        self.assertIn("method-workflow-card", self.styles)


if __name__ == "__main__":
    unittest.main()

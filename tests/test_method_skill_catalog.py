from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class MethodSkillCatalogApiTests(unittest.TestCase):
    """BDD: RunPlan 必须先展示 CoPaper/StatsPAI 式方法技能集前置条件。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="method-skill-catalog-"))
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
                "slug": "method-skill-catalog",
                "title": "Method Skill Catalog Project",
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

    def test_bdd_1_run_plan_returns_local_file_method_catalog(self) -> None:
        """行为 1：RunPlan draft 必须返回本地文件证据级方法技能集目录。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan")

        self.assertEqual(response.status_code, 200, msg=response.text)
        run_plan = response.json()["run_plan"]
        catalog = run_plan["method_catalog"]
        self.assertEqual(catalog["evidence_level"], "local_file")
        self.assertEqual(catalog["source"], "StatsPAI/CoPaper methodology index")
        self.assertEqual(
            [method["id"] for method in catalog["methods"]],
            ["ols", "did", "iv", "rdd", "psm", "dml"],
        )

    def test_bdd_2_method_catalog_marks_missing_prerequisites_as_blocked(self) -> None:
        """行为 2：方法目录必须说明每种方法的前置要求和阻塞原因。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan")

        self.assertEqual(response.status_code, 200, msg=response.text)
        methods = {
            method["id"]: method
            for method in response.json()["run_plan"]["method_catalog"]["methods"]
        }
        self.assertEqual(methods["ols"]["readiness_status"], "ready")
        self.assertEqual(methods["iv"]["readiness_status"], "blocked")
        self.assertIn("missing_instrument", methods["iv"]["blockers"])
        self.assertEqual(methods["did"]["readiness_status"], "blocked")
        self.assertIn("missing_panel_time", methods["did"]["blockers"])
        self.assertEqual(methods["rdd"]["readiness_status"], "blocked")
        self.assertIn("missing_running_variable", methods["rdd"]["blockers"])
        self.assertIn("结果变量", methods["ols"]["requirements"][0]["label"])

    def test_bdd_3_run_plan_default_tasks_only_include_ready_baseline_method(self) -> None:
        """行为 3：默认 RunPlan 只能包含当前 ready 的基准方法任务。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan")

        self.assertEqual(response.status_code, 200, msg=response.text)
        tasks = response.json()["run_plan"]["tasks"]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "baseline_regression")
        self.assertEqual(tasks[0]["method_id"], "ols")
        self.assertNotIn("iv_regression", [task["id"] for task in tasks])
        self.assertNotIn("did_regression", [task["id"] for task in tasks])

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
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: method-skill-catalog\n  title: Method Skill Catalog Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n12,0,14,5\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class MethodSkillCatalogFrontendTests(unittest.TestCase):
    """BDD: 研究设计页必须把方法目录作为可读产品面板展示。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_4_frontend_contains_method_skill_catalog_panel(self) -> None:
        """行为 4：研究设计页必须展示方法技能集、状态、要求和阻塞原因。"""
        self.assertIn("method-skill-catalog-panel", self.index_html)
        self.assertIn("method-skill-catalog-body", self.index_html)
        self.assertIn("renderMethodSkillCatalog", self.app_js)
        self.assertIn("方法技能集", self.app_js)
        self.assertIn("readiness_status", self.app_js)
        self.assertIn("method-skill-card", self.styles)


if __name__ == "__main__":
    unittest.main()

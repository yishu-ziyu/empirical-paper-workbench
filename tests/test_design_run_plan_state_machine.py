from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class DesignRunPlanStateMachineApiTests(unittest.TestCase):
    """BDD: DesignSpec 与 RunPlan 必须成为 full run 前的可审计产品状态。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="design-run-plan-"))
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
                "slug": "design-run-plan",
                "title": "Design RunPlan Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self._approve_variable_roles()

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_get_design_spec_returns_draft_from_approved_variable_roles(self) -> None:
        """行为 1：DesignSpec draft 必须读取已确认 VariableRoleSet。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/design-spec")

        self.assertEqual(response.status_code, 200, msg=response.text)
        design_spec = response.json()["design_spec"]
        self.assertEqual(design_spec["status"], "draft")
        self.assertEqual(design_spec["evidence_level"], "local_file")
        self.assertEqual(design_spec["variable_role_set_version"], 1)
        self.assertEqual(design_spec["research_question"], "培训是否影响工资？")
        self.assertEqual(design_spec["variables"]["outcome"], ["wage"])
        self.assertEqual(design_spec["variables"]["treatment"], ["trained"])
        self.assertEqual(design_spec["variables"]["controls"], ["edu", "experience"])
        self.assertEqual(design_spec["model"]["estimator"], "ols")
        self.assertEqual(design_spec["model"]["formula"], "wage ~ trained + edu + experience")

    def test_bdd_2_put_design_spec_persists_approved_state_and_decision_event(self) -> None:
        """行为 2：保存 DesignSpec 必须写入可审计项目状态。"""
        payload = self._design_payload(note="确认 OLS 作为第一版识别设计。")

        response = self.client.put(f"/api/v1/projects/{self.project_id}/design-spec", json=payload)

        self.assertEqual(response.status_code, 200, msg=response.text)
        design_spec = response.json()["design_spec"]
        self.assertEqual(design_spec["status"], "approved")
        self.assertEqual(design_spec["evidence_level"], "local_file")
        self.assertEqual(design_spec["version"], 1)
        self.assertEqual(design_spec["identification_strategy"]["name"], "baseline_ols")
        self.assertEqual(design_spec["decision_events"][0]["action"], "confirm_design_spec")
        self.assertEqual(design_spec["decision_events"][0]["note"], payload["note"])

        saved_path = self.project_root / "state" / "product" / "design_spec.json"
        self.assertTrue(saved_path.exists())
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "approved")
        self.assertEqual(saved["model"]["formula"], payload["model"]["formula"])

    def test_bdd_3_design_spec_approval_moves_workflow_to_run_plan(self) -> None:
        """行为 3：DesignSpec approved 后 workflow_contract 必须进入 RunPlan。"""
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json=self._design_payload(note="研究设计已确认。"),
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

        overview = self.client.get(f"/api/v1/projects/{self.project_id}/overview")

        self.assertEqual(overview.status_code, 200, msg=overview.text)
        contract = overview.json()["workflow_contract"]
        design_stage = next(stage for stage in contract["canonical_stages"] if stage["id"] == "design_spec")
        run_plan_stage = next(stage for stage in contract["canonical_stages"] if stage["id"] == "run_plan")
        self.assertEqual(design_stage["status"], "completed")
        self.assertEqual(run_plan_stage["status"], "requires_confirmation")
        self.assertEqual(contract["next_action"]["id"], "confirm_run_plan")
        self.assertNotIn("design_unconfirmed", contract["run_readiness"]["blockers"])
        self.assertEqual(contract["run_readiness"]["blockers"], ["run_plan_missing"])
        self.assertFalse(contract["run_readiness"]["can_start_full_run"])

    def test_bdd_4_get_run_plan_returns_draft_from_approved_design_spec(self) -> None:
        """行为 4：RunPlan draft 必须读取已确认 DesignSpec。"""
        design_response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json=self._design_payload(note="研究设计已确认。"),
        )
        self.assertEqual(design_response.status_code, 200, msg=design_response.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan")

        self.assertEqual(response.status_code, 200, msg=response.text)
        run_plan = response.json()["run_plan"]
        self.assertEqual(run_plan["status"], "draft")
        self.assertEqual(run_plan["evidence_level"], "local_file")
        self.assertEqual(run_plan["design_spec_version"], 1)
        self.assertEqual(run_plan["dataset_path"], "Data/Final/analysis_sample.csv")
        self.assertEqual(run_plan["tasks"][0]["id"], "baseline_regression")
        self.assertEqual(run_plan["tasks"][0]["formula"], "wage ~ trained + edu + experience")
        self.assertIn("regression_table", run_plan["outputs"])

    def test_bdd_5_run_plan_approval_allows_full_run(self) -> None:
        """行为 5：保存 RunPlan 后 full run 才能启动。"""
        design_response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json=self._design_payload(note="研究设计已确认。"),
        )
        self.assertEqual(design_response.status_code, 200, msg=design_response.text)
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={
                "tasks": draft["tasks"],
                "outputs": draft["outputs"],
                "note": "确认第一版 RunPlan。",
            },
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        run_plan = response.json()["run_plan"]
        self.assertEqual(run_plan["status"], "approved")
        self.assertEqual(run_plan["decision_events"][0]["action"], "confirm_run_plan")
        self.assertTrue((self.project_root / "state" / "product" / "run_plan.json").exists())

        overview = self.client.get(f"/api/v1/projects/{self.project_id}/overview")
        contract = overview.json()["workflow_contract"]
        run_plan_stage = next(stage for stage in contract["canonical_stages"] if stage["id"] == "run_plan")
        self.assertEqual(run_plan_stage["status"], "completed")
        self.assertTrue(contract["run_readiness"]["can_start_full_run"])
        self.assertEqual(contract["run_readiness"]["blockers"], [])
        self.assertEqual(contract["next_action"]["id"], "start_full_run")

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

    @staticmethod
    def _design_payload(note: str) -> dict:
        return {
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
            "note": note,
        }

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: design-run-plan\n  title: Design RunPlan Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class DesignRunPlanStateMachineFrontendTests(unittest.TestCase):
    """BDD: 前端必须提供 DesignSpec 与 RunPlan 确认入口。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    def test_bdd_6_frontend_contains_design_spec_confirmation_editor(self) -> None:
        """行为 6A：Research Design 页面必须有 DesignSpec 确认表单。"""
        self.assertIn("design-spec-confirmation-form", self.index_html)
        self.assertIn("renderDesignSpecEditor", self.app_js)
        self.assertIn("v2api.designSpec.save", self.app_js)
        for field in (
            "design-spec-question",
            "design-spec-strategy",
            "design-spec-formula",
            "design-spec-estimator",
            "design-spec-note",
        ):
            self.assertIn(field, self.app_js)

    def test_bdd_7_frontend_contains_run_plan_confirmation_editor(self) -> None:
        """行为 6B：Execution 页面必须有 RunPlan 确认表单。"""
        self.assertIn("run-plan-confirmation-form", self.index_html)
        self.assertIn("renderRunPlanEditor", self.app_js)
        self.assertIn("v2api.runPlan.save", self.app_js)
        self.assertIn("handleSaveRunPlan", self.app_js)
        self.assertIn("state.runPlanData = await v2api.runPlan.get", self.app_js)


if __name__ == "__main__":
    unittest.main()

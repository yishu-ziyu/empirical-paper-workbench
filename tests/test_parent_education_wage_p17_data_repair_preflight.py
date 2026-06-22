from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageP17DataRepairPreflightTests(unittest.TestCase):
    """BDD: P17 lets the UI review data repair candidates without mutating formal data."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p17-data-repair-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.product_root.mkdir(parents=True)
        self.project_root.mkdir(parents=True)
        self._seed_minimal_project_shape()
        self._seed_p16_blocked_project()
        self._seed_repair_source_tables()
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

    def test_bdd_post_writes_reviewable_preflight_without_changing_formal_dataset(self) -> None:
        """行为 1-5：POST 只写 P17 预检产物，并明确不能创建 run id 或运行模型。"""
        dataset_path = self.project_root / "Data/Final/cfps_robot_reallocation.csv"
        before_hash = self._sha256(dataset_path)

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p17-data-repair-preflight")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "data_repair_preflight_ready_for_review")
        self.assertTrue(body["artifact_exists"])
        self.assertEqual(body["current_dataset"]["path"], "Data/Final/cfps_robot_reallocation.csv")
        self.assertIn("parent_education", body["missing_fields"])
        self.assertIn("experience", body["missing_fields"])
        self.assertEqual(body["recommended_parent_education_source"], "famconf_parent_highest_education")
        self.assertIn("famconf_parent_highest_education", [item["id"] for item in body["parent_education_candidates"]])
        self.assertIn("person_age14_parent_education", [item["id"] for item in body["parent_education_candidates"]])
        self.assertEqual(body["experience_candidate"]["status"], "derivable_needs_review")
        self.assertTrue(body["experience_candidate"]["requires_education_years_mapping"])
        self.assertFalse(body["can_modify_final_dataset"])
        self.assertFalse(body["can_create_run_id"])
        self.assertFalse(body["can_execute_model"])
        self.assertEqual(body["suggested_repaired_dataset_path"], "Data/Interim/parent_education_wage_repaired.csv")
        self.assertEqual(before_hash, self._sha256(dataset_path))
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_p17_data_repair_preflight.json").exists())
        self.assertTrue((self.project_root / "Reviews/parent_education_wage_p17_data_repair_preflight.md").exists())
        self.assertFalse((self.project_root / "Data/Interim/parent_education_wage_repaired.csv").exists())

    def test_bdd_get_before_post_builds_preview_without_claiming_artifact(self) -> None:
        """行为 1：GET 可供 UI 首屏读取，但不能谎称已经写出 P17 产物。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p17-data-repair-preflight")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "data_repair_preflight_ready_for_review")
        self.assertFalse(body["artifact_exists"])
        self.assertIn("parent_education", body["missing_fields"])
        self.assertFalse((self.project_root / "Results/json/parent_education_wage_p17_data_repair_preflight.json").exists())

    def test_bdd_get_after_post_reads_existing_p17_artifact_for_ui(self) -> None:
        """行为 6：UI 刷新后再次读取时，必须显示已有 P17 审阅账本。"""
        posted = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p17-data-repair-preflight")
        self.assertEqual(posted.status_code, 201, msg=posted.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p17-data-repair-preflight")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertTrue(body["artifact_exists"])
        self.assertEqual(body["refresh_endpoint"], f"/api/v1/projects/{self.project_id}/product-control/p17-data-repair-preflight")
        self.assertEqual(body["product_control_signal"]["phase"], "P17")
        self.assertIn("review_data_repair_preflight", body["next_action"])

    def test_bdd_react_product_control_panel_exposes_p17_refreshable_ui(self) -> None:
        """行为 6：产品控制台必须有 P17 可点击入口，而不是只靠后端文件。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p17-data-repair-preflight", component)
        self.assertIn("ProductControlP17DataRepairPreflightReport", component)
        self.assertIn("product-control-p17-data-repair-preflight", component)
        self.assertIn("handleRefreshProductControlP17DataRepairPreflight", component)
        self.assertIn("刷新 P17", component)
        self.assertIn("Data Repair Preflight", component)
        self.assertIn("No model run", component)

    def _seed_minimal_project_shape(self) -> None:
        (self.project_root / "Program").mkdir(parents=True)
        (self.project_root / "Program/run_paper.py").write_text("print('stub')\n", encoding="utf-8")
        (self.project_root / "paper.yaml").write_text(
            "project:\n"
            "  slug: parent-education-wage\n"
            "  title: Parent Education Wage\n"
            "research:\n"
            "  question: 父母受教育水平对子女工资收入的影响\n",
            encoding="utf-8",
        )

    def _seed_p16_blocked_project(self) -> None:
        (self.project_root / "Data/Final").mkdir(parents=True)
        (self.project_root / "Data/Final/cfps_robot_reallocation.csv").write_text(
            "pid,year,age,edu_last,ln_wage,female,urban\n"
            "1,2020,31,4,10.1,0,1\n"
            "2,2020,42,5,11.2,1,0\n"
            "3,2022,28,4,9.8,0,1\n"
            "4,2022,36,6,12.0,1,1\n",
            encoding="utf-8",
        )
        self._write_json(
            "Results/json/parent_education_wage_p12_design_spec_preflight.json",
            {
                "status": "design_spec_preflight_ready_for_review",
                "topic": "父母受教育水平对子女工资收入的影响",
                "draft_design_spec": {
                    "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                    "research_question": "父母受教育水平对子女工资收入的影响",
                    "variables": {
                        "outcome": ["ln_wage"],
                        "treatment": ["parent_education"],
                        "controls": ["age", "female", "urban", "edu_last", "experience"],
                    },
                    "model": {
                        "estimator": "ols",
                        "formula": "ln_wage ~ parent_education + age + female + urban + edu_last + experience",
                    },
                },
            },
        )
        self._write_json(
            "Results/json/parent_education_wage_p13_run_plan_approval.json",
            {
                "status": "blocked_missing_dataset_columns_for_run_plan",
                "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                "missing_dataset_columns": ["parent_education", "experience"],
                "can_create_run_id": False,
                "can_execute_model": False,
            },
        )
        self._write_json(
            "Results/json/parent_education_wage_p16_user_acceptance_packet.json",
            {
                "status": "demo_closure_blocked_branch_ready",
                "can_claim_complete_paper": False,
                "can_claim_model_result": False,
                "next_actions": [
                    "在真实分析数据中补齐 parent_education。",
                    "在真实分析数据中补齐或构造 experience。",
                ],
            },
        )

    def _seed_repair_source_tables(self) -> None:
        source_root = self.project_root / "Data/Raw/cfps_source"
        (source_root / "2020cfps/STATA版本").mkdir(parents=True)
        (source_root / "2022CFPS").mkdir(parents=True)
        (source_root / "2020cfps/STATA版本/cfps2020famconf_202301.csv").write_text(
            "pid,tb4_a20_f,tb4_a20_m\n"
            "1,3,4\n"
            "2,5,-8\n",
            encoding="utf-8",
        )
        (source_root / "2022CFPS/cfps2022famconf_202410.csv").write_text(
            "pid,tb4_a22_f,tb4_a22_m\n"
            "3,2,4\n"
            "4,6,79\n",
            encoding="utf-8",
        )
        (source_root / "2020cfps/STATA版本/cfps2020person_202112.csv").write_text(
            "pid,qv102,qv202\n"
            "1,1,2\n"
            "2,79,3\n",
            encoding="utf-8",
        )
        (source_root / "2022CFPS/cfps2022person_202410.csv").write_text(
            "pid,qv102,qv202\n"
            "3,-8,2\n"
            "4,3,4\n",
            encoding="utf-8",
        )

    def _write_json(self, relative_path: str, payload: dict) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _sha256(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)

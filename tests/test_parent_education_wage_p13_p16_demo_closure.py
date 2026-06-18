from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageP13P16DemoClosureTests(unittest.TestCase):
    """BDD: P13-P16 closes the demo line honestly, including blocked delivery."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p13-p16-closure-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.product_root.mkdir(parents=True)
        self.project_root.mkdir(parents=True)
        self._seed_minimal_project_shape()
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
        self._seed_p12_ready_with_missing_dataset_columns()

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.tmp)

    def test_bdd_p13_p16_closure_blocks_missing_columns_and_delivers_issue_package(self) -> None:
        """行为 1-5：缺真实字段时，闭环必须归档旧状态、阻断执行并交付问题清单。"""
        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p13-p16-demo-closure")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "demo_closure_blocked_branch_ready")
        self.assertEqual(body["p13_run_plan_approval"]["status"], "blocked_missing_dataset_columns_for_run_plan")
        self.assertIn("parent_education", body["p13_run_plan_approval"]["missing_dataset_columns"])
        self.assertIn("experience", body["p13_run_plan_approval"]["missing_dataset_columns"])
        self.assertFalse(body["p13_run_plan_approval"]["can_write_run_plan"])
        self.assertFalse(body["p13_run_plan_approval"]["can_create_run_id"])
        self.assertEqual(body["p14_execution_ledger"]["status"], "execution_blocked_missing_dataset_columns")
        self.assertIsNone(body["p14_execution_ledger"]["run_id"])
        self.assertFalse(body["p14_execution_ledger"]["executed_regression"])
        self.assertTrue(body["p15_draft_package"]["paper_draft_docx"].endswith("parent_education_wage_paper_draft.docx"))
        self.assertIn("parent_education", body["p15_draft_package"]["red_flag_issues"][0]["missing_columns"])
        self.assertFalse(body["p16_acceptance_packet"]["can_claim_complete_paper"])
        self.assertTrue(body["p16_acceptance_packet"]["can_accept_blocked_package"])
        self.assertTrue((self.project_root / "state/product/archive/p13_p16_stale_formal_state/design_spec.json").exists())
        self.assertTrue((self.project_root / "state/product/archive/p13_p16_stale_formal_state/run_plan.json").exists())
        self.assertFalse((self.project_root / "state/product/design_spec.json").exists())
        self.assertFalse((self.project_root / "state/product/run_plan.json").exists())
        self.assertTrue((self.project_root / "Manuscripts/generated/parent_education_wage_p15_issue_list.md").exists())
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_p16_user_acceptance_packet.json").exists())

    def test_bdd_get_before_post_does_not_claim_p16_artifacts(self) -> None:
        """行为 5：未执行 P13-P16 前，GET 不能凭空宣称 P16 已完成。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p13-p16-demo-closure")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "p13_p16_closure_not_run")
        self.assertFalse(body["artifact_exists"])
        self.assertNotEqual(body.get("completed_stage"), "P16")
        self.assertFalse((self.project_root / "Results/json/parent_education_wage_p16_user_acceptance_packet.json").exists())

    def test_bdd_p13_p16_get_reads_existing_closure(self) -> None:
        """行为 5：GET 必须读取已有 P16 验收包，避免用户看不到闭环状态。"""
        posted = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p13-p16-demo-closure")
        self.assertEqual(posted.status_code, 201, msg=posted.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p13-p16-demo-closure")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "demo_closure_blocked_branch_ready")
        self.assertEqual(body["p16_acceptance_packet"]["current_user_outcome"], "半成品论文 + 红标问题清单")
        self.assertFalse(body["p16_acceptance_packet"]["can_claim_complete_paper"])

    def test_bdd_stale_p12_robot_preflight_is_rejected(self) -> None:
        """行为 1-2：P13 不能把旧机器人 P12 预检改名成父母教育闭环。"""
        self._write_json(
            "Results/json/parent_education_wage_p12_design_spec_preflight.json",
            {
                "status": "design_spec_preflight_ready_for_review",
                "topic": "工业机器人暴露是否改变劳动者工资回报？",
                "draft_design_spec": {
                    "id": "robot_design_spec_preflight",
                    "status": "preflight_draft",
                    "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                    "research_question": "工业机器人暴露是否改变劳动者工资回报？",
                    "topic_slug": "robot-wage",
                    "variables": {
                        "outcome": ["ln_wage"],
                        "treatment": ["ln_robot"],
                        "controls": ["age", "female", "urban", "edu_last"],
                    },
                    "identification_strategy": {"name": "baseline_ols"},
                    "model": {"estimator": "ols", "formula": "ln_wage ~ ln_robot + age + female + urban + edu_last"},
                },
            },
        )

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p13-p16-demo-closure")

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_stale_p12_preflight_for_topic")
        self.assertEqual(body["p13_run_plan_approval"]["status"], "blocked_stale_p12_preflight_for_topic")
        self.assertFalse(body["p13_run_plan_approval"]["can_execute_model"])
        self.assertFalse(body["p16_acceptance_packet"]["can_claim_complete_paper"])

    def test_bdd_complete_columns_execute_minimal_ols_before_run_id_claim(self) -> None:
        """行为 3：字段齐全时，P14 必须实际执行最小 OLS 后才允许返回 run_id。"""
        self._seed_complete_dataset_columns()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p13-p16-demo-closure")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "demo_closure_model_results_ready")
        self.assertEqual(body["p13_run_plan_approval"]["status"], "run_plan_approved_for_baseline_ols")
        self.assertEqual(body["p14_execution_ledger"]["status"], "execution_completed_minimal_ols")
        self.assertIsNotNone(body["p14_execution_ledger"]["run_id"])
        self.assertTrue(body["p14_execution_ledger"]["executed_regression"])
        self.assertEqual(body["p14_execution_ledger"]["model_results"]["treatment_variable"], "parent_education")
        self.assertTrue(body["p16_acceptance_packet"]["can_claim_model_result"])

    def test_bdd_dashboard_speaks_plain_project_language(self) -> None:
        """行为 6：控制台必须先回答能交付什么、还缺什么、下一步做什么。"""
        state_path = Path(__file__).resolve().parents[1] / "docs/product-control/workflow-dashboard-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        html = (Path(__file__).resolve().parents[1] / "docs/product-control/workflow-dashboard.html").read_text(encoding="utf-8")

        for phrase in ["现在能交付什么", "还缺什么", "下一步做什么"]:
            self.assertIn(phrase, html)
        self.assertIn("plain_summary", state)
        self.assertEqual(["现在能交付什么", "还缺什么", "下一步做什么"], [item["label"] for item in state["plain_summary"]])

    def _seed_p12_ready_with_missing_dataset_columns(self) -> None:
        (self.project_root / "Data/Final").mkdir(parents=True)
        (self.project_root / "Data/Final/cfps_robot_reallocation.csv").write_text(
            "ln_wage,age,female,urban,edu_last\n"
            "10,20,1,1,16\n"
            "11,30,0,0,12\n",
            encoding="utf-8",
        )
        (self.project_root / "Submissions").mkdir(parents=True)
        (self.project_root / "Submissions/parent_education_wage_paper_draft.docx").write_text(
            "blocked draft placeholder",
            encoding="utf-8",
        )
        self._write_json(
            "Results/json/parent_education_wage_p12_design_spec_preflight.json",
            {
                "status": "design_spec_preflight_ready_for_review",
                "topic": "父母受教育水平对子女工资收入的影响",
                "draft_design_spec": {
                    "id": "design_spec_preflight_parent_education_wage",
                    "status": "preflight_draft",
                    "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                    "research_question": "父母受教育水平对子女工资收入的影响",
                    "variables": {
                        "outcome": ["ln_wage"],
                        "treatment": ["parent_education"],
                        "controls": ["age", "female", "urban", "edu_last", "experience"],
                    },
                    "identification_strategy": {"name": "baseline_ols"},
                    "model": {
                        "estimator": "ols",
                        "formula": "ln_wage ~ parent_education + age + female + urban + edu_last + experience",
                    },
                },
            },
        )
        self._write_json(
            "state/product/design_spec.json",
            {"status": "approved", "research_question": "工业机器人暴露是否改变劳动者工资回报？", "model": {"formula": "ln_wage ~ ln_robot"}},
        )
        self._write_json(
            "state/product/run_plan.json",
            {"status": "approved", "tasks": [{"id": "robot_wage_iv_baseline", "estimator": "iv"}]},
        )

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

    def _seed_complete_dataset_columns(self) -> None:
        rows = ["ln_wage,parent_education,age,female,urban,edu_last,experience"]
        for i in range(1, 13):
            parent = i
            age = 20 + i
            female = i % 2
            urban = (i // 2) % 2
            edu_last = 8 + (i % 5)
            experience = (i * i) % 13
            ln_wage = 2 + 0.3 * parent + 0.01 * age - 0.1 * female + 0.05 * urban + 0.02 * edu_last + 0.005 * experience
            rows.append(f"{ln_wage:.4f},{parent},{age},{female},{urban},{edu_last},{experience}")
        (self.project_root / "Data/Final/cfps_robot_reallocation.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    def _write_json(self, relative_path: str, payload: dict) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main(verbosity=2)

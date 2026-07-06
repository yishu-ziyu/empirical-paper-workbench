from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ProductControlHeadlessStateTests(unittest.TestCase):
    """BDD: UI can consume product capabilities without layout-specific state."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="headless-state-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.product_root.mkdir(parents=True)
        self.project_root.mkdir(parents=True)
        self._seed_project()
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

    def test_headless_state_exposes_components_without_layout_contract(self) -> None:
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/headless-state")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["schema_version"], "product_control_headless_state.v1")
        self.assertEqual(body["status"], "pdf_export_smoke_ready")
        self.assertNotIn("layout", body)
        components = {item["component_id"]: item for item in body["components"]}
        for component_id in [
            "data_repair",
            "execution_run",
            "draft_package",
            "final_pdf",
            "course_paper_quality",
            "review_export",
        ]:
            self.assertIn(component_id, components)
            self.assertIn("status", components[component_id])
            self.assertIn("user_summary", components[component_id])
            self.assertIn("primary_action", components[component_id])
            self.assertIn("blockers", components[component_id])
            self.assertIn("artifacts", components[component_id])
            self.assertIn("evidence", components[component_id])
        self.assertEqual(components["draft_package"]["status"], "completed")
        self.assertEqual(components["final_pdf"]["status"], "completed")
        self.assertEqual(components["course_paper_quality"]["status"], "blocked")
        self.assertEqual(
            components["course_paper_quality"]["primary_action"]["id"],
            "run_course_paper_review_report",
        )
        self.assertEqual(components["review_export"]["primary_action"]["id"], "human_review_complete_draft")

    def test_course_paper_quality_gate_uses_current_final_pdf_markdown(self) -> None:
        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/course-paper-quality")

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["draft_path"], "Manuscripts/generated/parent_education_wage_complete_paper_draft.md")
        self.assertFalse(body["can_claim_course_paper_ready"])
        self.assertIn("too_thin", body["verdict"])
        report_path = self.project_root / "Results/json/course_paper_quality_report.json"
        self.assertTrue(report_path.exists())

        headless = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/headless-state").json()
        components = {item["component_id"]: item for item in headless["components"]}
        self.assertEqual(components["course_paper_quality"]["status"], "needs_revision")

    def test_ready_verdict_with_revision_decision_fails_safe_to_needs_revision(self) -> None:
        self._write_json(
            "Results/json/course_paper_quality_report.json",
            {
                "status": "course_paper_quality_ready_for_review",
                "draft_path": "Manuscripts/generated/parent_education_wage_complete_paper_draft.md",
                "verdict": ["ready_for_review"],
                "review_summary": {
                    "decision": "needs_revision",
                    "headline": "审阅摘要仍要求修订。",
                    "top_priorities": [
                        {
                            "id": "repair_method_section",
                            "title": "补齐方法说明",
                            "detail": "ready verdict 与摘要冲突时，必须先回到修订队列。",
                            "owner": "ReviewerAgent",
                        }
                    ],
                },
            },
        )

        headless = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/headless-state")
        self.assertEqual(headless.status_code, 200, msg=headless.text)
        components = {item["component_id"]: item for item in headless.json()["components"]}
        quality = components["course_paper_quality"]
        self.assertEqual(quality["status"], "needs_revision")
        self.assertEqual(quality["primary_action"]["id"], "route_quality_revisions")
        self.assertEqual(quality["quality_report_path"], "Results/json/course_paper_quality_report.json")
        self.assertEqual(quality["top_priorities"][0]["title"], "补齐方法说明")

    def _seed_project(self) -> None:
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
        self._write_json(
            "Results/json/parent_education_wage_p18_data_repair_apply.json",
            {
                "status": "data_repair_applied_ready_for_p13_p16",
                "repaired_dataset_path": "Data/Interim/parent_education_wage_repaired.csv",
            },
        )
        self._write_json(
            "Results/json/parent_education_wage_p14_execution_evidence_ledger.json",
            {
                "status": "execution_completed_minimal_ols",
                "run_id": "run_1",
                "executed_regression": True,
            },
        )
        self._write_json(
            "Results/json/parent_education_wage_p15_draft_export_package.json",
            {
                "status": "complete_paper_draft_package_ready",
                "paper_draft_docx": "Submissions/parent_education_wage_paper_draft.docx",
                "paper_draft_markdown": "Manuscripts/generated/parent_education_wage_complete_paper_draft.md",
                "can_export_complete_paper": True,
            },
        )
        self._write_json(
            "Results/json/parent_education_wage_p16_user_acceptance_packet.json",
            {
                "status": "demo_closure_complete_paper_draft_ready",
                "can_claim_complete_paper": True,
                "can_claim_submission_ready": False,
            },
        )
        self._write_json(
            "Results/json/parent_education_wage_final_pdf_export.json",
            {
                "status": "final_pdf_ready",
                "source_markdown": "Manuscripts/generated/parent_education_wage_complete_paper_draft.md",
                "final_pdf": "Submissions/parent_education_wage_final_paper.pdf",
                "paper_quality_status": "pdf_export_smoke_only",
            },
        )
        draft = self.project_root / "Manuscripts/generated/parent_education_wage_complete_paper_draft.md"
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_text("# 摘要\n\n这是一份过薄的测试草稿。\n\n# 数据与变量\n\n样本说明。\n", encoding="utf-8")

    def _write_json(self, relative_path: str, payload: dict) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main(verbosity=2)

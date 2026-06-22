from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageFinalPdfExportTests(unittest.TestCase):
    """BDD: a complete draft can be exported to a final PDF artifact."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-final-pdf-"))
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

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.tmp)

    def test_final_pdf_blocks_when_complete_draft_is_not_ready(self) -> None:
        self._write_json(
            "Results/json/parent_education_wage_p16_user_acceptance_packet.json",
            {"status": "demo_closure_blocked_branch_ready", "can_claim_complete_paper": False},
        )

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/final-pdf")

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_complete_draft_not_ready")
        self.assertFalse((self.project_root / "Submissions/parent_education_wage_final_paper.pdf").exists())

    def test_final_pdf_writes_pdf_html_report_and_review(self) -> None:
        self._seed_complete_draft_artifacts()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/final-pdf")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "final_pdf_ready")
        self.assertTrue(body["can_claim_final_pdf_ready"])
        self.assertFalse(body["can_claim_submission_ready"])
        self.assertEqual(body["paper_quality_status"], "pdf_export_smoke_only")
        self.assertIn("draft_too_thin_for_course_paper", body["not_submission_ready_reasons"])
        self.assertEqual(body["final_pdf"], "Submissions/parent_education_wage_final_paper.pdf")
        self.assertGreater(body["final_pdf_size"], 1000)
        self.assertRegex(body["final_pdf_sha256"], r"^[0-9a-f]{64}$")
        pdf_path = self.project_root / body["final_pdf"]
        html_path = self.project_root / body["final_html"]
        report_path = self.project_root / "Results/json/parent_education_wage_final_pdf_export.json"
        review_path = self.project_root / "Reviews/parent_education_wage_final_pdf_export.md"
        self.assertTrue(pdf_path.exists())
        self.assertTrue(html_path.exists())
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertEqual(pdf_path.read_bytes()[:4], b"%PDF")
        self.assertIn("父母受教育水平", html_path.read_text(encoding="utf-8"))

    def test_get_final_pdf_returns_existing_export(self) -> None:
        self._seed_complete_draft_artifacts()
        generated = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/final-pdf")
        self.assertEqual(generated.status_code, 201, msg=generated.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/final-pdf")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "final_pdf_ready")
        self.assertTrue(body["artifact_exists"])

    def test_headless_state_includes_completed_final_pdf_component(self) -> None:
        self._seed_complete_draft_artifacts()
        generated = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/final-pdf")
        self.assertEqual(generated.status_code, 201, msg=generated.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/headless-state")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        components = {item["component_id"]: item for item in body["components"]}
        self.assertIn("final_pdf", components)
        self.assertEqual(components["final_pdf"]["status"], "completed")
        self.assertNotIn("layout", components["final_pdf"])

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

    def _seed_complete_draft_artifacts(self) -> None:
        markdown = (
            "# 父母受教育水平如何影响子女的工资水平？\n\n"
            "## 摘要\n\n"
            "本文使用修复后的 CFPS 分析数据，估计父母教育水平与子女工资水平之间的关系。\n\n"
            "## 结果\n\n"
            "模型样本量为 `12582`，`parent_education` 的估计系数为 `0.05915833`。\n"
        )
        path = self.project_root / "Manuscripts/generated/parent_education_wage_complete_paper_draft.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        self._write_json(
            "Results/json/parent_education_wage_p16_user_acceptance_packet.json",
            {
                "status": "demo_closure_complete_paper_draft_ready",
                "can_claim_complete_paper": True,
                "can_claim_submission_ready": False,
            },
        )
        self._write_json(
            "Results/json/parent_education_wage_p14_execution_evidence_ledger.json",
            {
                "status": "execution_completed_minimal_ols",
                "run_id": "test-run",
                "model_results": {"nobs": 12582},
            },
        )

    def _write_json(self, relative_path: str, payload: dict) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main(verbosity=2)

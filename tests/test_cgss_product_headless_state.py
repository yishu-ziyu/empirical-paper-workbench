from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

import Product.app as product_app


class CgssProductHeadlessStateTests(unittest.TestCase):
    """BDD: CGSS 题目进入产品层后，交付状态必须指向 CGSS 产物。"""

    def setUp(self) -> None:
        self.client = TestClient(product_app.app)
        self.project_id = "proj_cgss_social_capital_happiness"

    def test_cgss_project_is_registered_for_browser_workbench(self) -> None:
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/headless-state")
        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertIn("CGSS", body["project"]["title"])

    def test_cgss_headless_state_uses_cgss_pdf_not_parent_demo_pdf(self) -> None:
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/headless-state")
        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "pdf_export_smoke_ready")
        self.assertIn("PDF 导出样稿", body["user_summary"])
        self.assertIn("论文审阅", body["user_summary"])
        self.assertNotIn("质量门", json_dumps(body))
        self.assertNotIn("数据已修复", body["user_summary"])
        final_pdf = next(component for component in body["components"] if component["component_id"] == "final_pdf")
        self.assertIn("Submissions/cgss_social_capital_happiness/paper.pdf", final_pdf["user_summary"])
        self.assertNotIn("parent_education_wage", final_pdf["user_summary"])
        component_paths = [
            item["path"]
            for component in body["components"]
            for field in ("artifacts", "evidence")
            for item in component.get(field, [])
        ]
        self.assertIn("Submissions/cgss_social_capital_happiness/paper.pdf", component_paths)
        self.assertNotIn(
            "parent_education_wage",
            "\n".join(component_paths),
        )
        artifact_paths = [artifact["path"] for artifact in body["artifacts"]]
        self.assertIn("Results/json/cgss_social_capital_happiness_pdf_preflight.json", artifact_paths)

    def test_cgss_quality_gate_uses_cgss_markdown_source(self) -> None:
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/course-paper-quality")
        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(
            body["draft_path"],
            "Manuscripts/generated/cgss_social_capital_happiness_paper.md",
        )
        self.assertEqual(
            body["quality_report_path"],
            "Results/json/cgss_social_capital_happiness_course_paper_quality_report.json",
        )

    def test_cgss_review_report_uses_only_cgss_evidence_and_summarizes_revisions(self) -> None:
        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/course-paper-quality")
        self.assertIn(response.status_code, {200, 409}, msg=response.text)
        body = response.json()
        body_text = json_dumps(body)
        self.assertIn("Results/json/cgss_social_capital_happiness_results_evidence_package.json", body_text)
        self.assertIn("Results/json/cgss_social_capital_happiness_method_gate.json", body_text)
        self.assertNotIn("parent_education_wage", body_text)
        self.assertNotIn("Tasks/parent-education-wage", body_text)
        self.assertNotIn("missing_iv_diagnostics", body_text)
        self.assertNotIn("undefined_iv_strategy", body_text)
        summary = body["review_summary"]
        self.assertEqual(summary["decision"], "needs_revision")
        self.assertGreaterEqual(summary["current_chinese_chars"], 5000)
        self.assertIn("扩写核心章节", summary["top_priorities"][0]["title"])
        self.assertTrue(summary["section_gaps"])

    def test_cgss_headless_state_exposes_review_report_contract_after_generation(self) -> None:
        """BDD 行为 4：审阅报告生成后，headless 组件必须直接暴露可读修订合同。"""

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/course-paper-quality")
        self.assertIn(response.status_code, {200, 409}, msg=response.text)

        headless_response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/headless-state")
        self.assertEqual(headless_response.status_code, 200, msg=headless_response.text)
        body = headless_response.json()
        component = next(item for item in body["components"] if item["component_id"] == "course_paper_quality")

        self.assertEqual(component["status"], "needs_revision")
        self.assertEqual(
            component["quality_report_path"],
            "Results/json/cgss_social_capital_happiness_course_paper_quality_report.json",
        )
        self.assertEqual(component["review_summary"]["decision"], "needs_revision")
        self.assertEqual(component["top_priorities"], component["review_summary"]["top_priorities"])
        self.assertTrue(component["top_priorities"])
        self.assertEqual(component["primary_action"]["id"], "route_quality_revisions")
        self.assertNotIn("论文审阅尚未完成", component["user_summary"])


def json_dumps(value: object) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()

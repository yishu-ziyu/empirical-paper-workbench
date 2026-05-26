from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class FormalSubmissionPackageSummaryApiTests(unittest.TestCase):
    """BDD 40: 产品 API 必须只读暴露正式包验收摘要。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-summary-api-"))
        self.repo_root = self.temp_dir / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "formal-summary-api",
                "title": "Formal Summary API Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_40_reads_formal_summary_without_mutating_state(self) -> None:
        """行为 40：API 返回验收摘要，并保持状态文件字节级不变。"""
        summary_path = self.project_root / "state" / "product" / "formal_submission_package_summary.json"
        summary_path.parent.mkdir(parents=True)
        summary = {
            "schema_version": "p6.formal_submission_package_summary.v1",
            "status": "ready_for_manual_acceptance",
            "ready_for_manual_acceptance": True,
            "visible_summary": [{"id": "package_status", "label": "正式包状态", "value": "可进入人工验收"}],
            "open_targets": [
                {
                    "id": "paper_pdf",
                    "label": "打开 PDF",
                    "path": "Submissions/formal_package/paper.pdf",
                    "type": "pdf",
                    "exists": True,
                }
            ],
            "manual_acceptance": {"status": "pending_manual_acceptance"},
            "source_manifest": {"path": "Results/json/formal_submission_package_manifest.json", "exists": True},
            "consistency_checks": [{"id": "paper_pdf_sha256", "status": "passed"}],
            "blocking_reasons": [],
            "command_boundaries": {
                "this_command_rendered_pdf": False,
                "this_command_rendered_docx": False,
                "this_command_wrote_final_outputs": False,
            },
        }
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        before = summary_path.read_bytes()

        response = self.client.get(f"/api/v1/projects/{self.project_id}/formal-submission-package-summary")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["service"], "formal_submission_package_service")
        self.assertEqual(body["_meta"]["mode"], "read_only")
        self.assertEqual(body["project_id"], self.project_id)
        self.assertEqual(body["summary_path"], "state/product/formal_submission_package_summary.json")
        self.assertEqual(body["status"], "ready_for_manual_acceptance")
        self.assertTrue(body["ready_for_manual_acceptance"])
        self.assertEqual(body["visible_summary"], summary["visible_summary"])
        self.assertEqual(body["open_targets"], summary["open_targets"])
        self.assertEqual(body["manual_acceptance"], summary["manual_acceptance"])
        self.assertEqual(body["source_manifest"], summary["source_manifest"])
        self.assertEqual(body["consistency_checks"], summary["consistency_checks"])
        self.assertEqual(body["blocking_reasons"], [])
        self.assertEqual(summary_path.read_bytes(), before)

    def test_bdd_40_missing_summary_returns_structured_409(self) -> None:
        """行为 40：缺少 P6-E1 summary 时，API 明确阻断而不是返回空壳。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/formal-submission-package-summary")

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["error"]["code"], "formal_submission_package_summary_required")
        self.assertIn("formal_submission_package_summary.py", body["error"]["message"])

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n"
            "  slug: formal-summary-api\n"
            "  title: Formal Summary API Project\n"
            "research:\n"
            "  question: 培训是否影响工资？\n"
            "data:\n"
            "  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageDeliveryPackageTests(unittest.TestCase):
    """BDD: complete draft artifacts can be packaged for delivery without UI work."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-delivery-package-"))
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

    def test_delivery_package_blocks_when_complete_draft_is_not_ready(self) -> None:
        self._write_json(
            "Results/json/parent_education_wage_p16_user_acceptance_packet.json",
            {"status": "demo_closure_blocked_branch_ready", "can_claim_complete_paper": False},
        )

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/delivery-package")

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_complete_draft_not_ready")
        self.assertFalse((self.project_root / "Submissions/parent_education_wage_delivery_package.zip").exists())

    def test_delivery_package_writes_manifest_readme_and_zip(self) -> None:
        self._seed_complete_delivery_artifacts()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/delivery-package")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "delivery_package_ready_for_human_review")
        self.assertTrue(body["can_deliver_reviewable_package"])
        self.assertFalse(body["can_claim_submission_ready"])
        self.assertGreaterEqual(len(body["files"]), 10)
        for item in body["files"]:
            self.assertIn("path", item)
            self.assertGreater(item["size"], 0)
            self.assertRegex(item["sha256"], r"^[0-9a-f]{64}$")
        manifest_path = self.project_root / "Submissions/parent_education_wage_delivery_manifest.json"
        readme_path = self.project_root / "Submissions/parent_education_wage_delivery_README.md"
        zip_path = self.project_root / "Submissions/parent_education_wage_delivery_package.zip"
        self.assertTrue(manifest_path.exists())
        self.assertTrue(readme_path.exists())
        self.assertTrue(zip_path.exists())
        with zipfile.ZipFile(zip_path) as archive:
            names = set(archive.namelist())
        self.assertIn("Submissions/parent_education_wage_delivery_manifest.json", names)
        self.assertIn("Submissions/parent_education_wage_paper_draft.docx", names)
        self.assertIn("Data/Interim/parent_education_wage_repaired.csv", names)

    def test_headless_state_includes_completed_delivery_package_component(self) -> None:
        self._seed_complete_delivery_artifacts()
        generated = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/delivery-package")
        self.assertEqual(generated.status_code, 201, msg=generated.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/headless-state")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        components = {item["component_id"]: item for item in body["components"]}
        self.assertIn("delivery_package", components)
        self.assertEqual(components["delivery_package"]["status"], "completed")
        self.assertNotIn("layout", components["delivery_package"])

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

    def _seed_complete_delivery_artifacts(self) -> None:
        files = {
            "Submissions/parent_education_wage_paper_draft.docx": "docx bytes placeholder",
            "Manuscripts/generated/parent_education_wage_complete_paper_draft.md": "# draft\n",
            "Data/Interim/parent_education_wage_repaired.csv": "pid,parent_education,experience\n1,4,10\n",
            "Reviews/parent_education_wage_p13_run_plan_approval.md": "p13",
            "Reviews/parent_education_wage_p14_execution_evidence_ledger.md": "p14",
            "Reviews/parent_education_wage_p15_draft_export_package.md": "p15",
            "Reviews/parent_education_wage_p16_user_acceptance_packet.md": "p16",
            "Reviews/parent_education_wage_p17_data_repair_preflight.md": "p17",
            "Reviews/parent_education_wage_p18_data_repair_apply.md": "p18",
        }
        for relative_path, content in files.items():
            path = self.project_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        json_files = {
            "Results/json/parent_education_wage_p13_run_plan_approval.json": {"status": "run_plan_approved_for_baseline_ols"},
            "Results/json/parent_education_wage_p14_execution_evidence_ledger.json": {"status": "execution_completed_minimal_ols"},
            "Results/json/parent_education_wage_p15_draft_export_package.json": {"status": "complete_paper_draft_package_ready"},
            "Results/json/parent_education_wage_p16_user_acceptance_packet.json": {
                "status": "demo_closure_complete_paper_draft_ready",
                "can_claim_complete_paper": True,
                "can_claim_submission_ready": False,
            },
            "Results/json/parent_education_wage_p17_data_repair_preflight.json": {"status": "data_repair_preflight_ready_for_review"},
            "Results/json/parent_education_wage_p18_data_repair_apply.json": {"status": "data_repair_applied_ready_for_p13_p16"},
        }
        for relative_path, payload in json_files.items():
            self._write_json(relative_path, payload)

    def _write_json(self, relative_path: str, payload: dict) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main(verbosity=2)


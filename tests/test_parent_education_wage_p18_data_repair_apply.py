from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ParentEducationWageP18DataRepairApplyTests(unittest.TestCase):
    """BDD: P18 applies reviewed repair candidates without touching final data."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-p18-data-repair-"))
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

    def test_bdd_p18_requires_p17_preflight_before_apply(self) -> None:
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p18-data-repair-apply",
            json=self._valid_apply_payload(),
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_missing_p17_data_repair_preflight")
        self.assertFalse((self.project_root / "Data/Interim/parent_education_wage_repaired.csv").exists())

    def test_bdd_p18_requires_human_confirmation_and_mapping_confirmation(self) -> None:
        p17 = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p17-data-repair-preflight")
        self.assertEqual(p17.status_code, 201, msg=p17.text)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p18-data-repair-apply",
            json={"reviewer": "", "note": "", "confirm_apply": False},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "blocked_missing_human_apply_confirmation")
        self.assertIn("missing_reviewer", body["blocking_reasons"])
        self.assertIn("missing_confirm_education_years_mapping", body["blocking_reasons"])
        self.assertFalse((self.project_root / "Data/Interim/parent_education_wage_repaired.csv").exists())
        p12 = self._load_json("Results/json/parent_education_wage_p12_design_spec_preflight.json")
        self.assertEqual(p12["draft_design_spec"]["dataset_path"], "Data/Final/cfps_robot_reallocation.csv")

    def test_bdd_p18_writes_interim_repaired_dataset_and_preserves_final_dataset(self) -> None:
        p17 = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p17-data-repair-preflight")
        self.assertEqual(p17.status_code, 201, msg=p17.text)
        final_path = self.project_root / "Data/Final/cfps_robot_reallocation.csv"
        before_hash = self._sha256(final_path)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p18-data-repair-apply",
            json=self._valid_apply_payload(),
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "data_repair_applied_ready_for_p13_p16")
        self.assertEqual(body["repaired_dataset_path"], "Data/Interim/parent_education_wage_repaired.csv")
        self.assertEqual(before_hash, self._sha256(final_path))
        repaired_path = self.project_root / "Data/Interim/parent_education_wage_repaired.csv"
        self.assertTrue(repaired_path.exists())
        with repaired_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertIn("parent_education", reader.fieldnames or [])
            self.assertIn("education_years", reader.fieldnames or [])
            self.assertIn("experience", reader.fieldnames or [])
            rows = list(reader)
        self.assertGreaterEqual(len(rows), 12)
        self.assertTrue(any(row["parent_education"] for row in rows))
        self.assertTrue(any(row["experience"] for row in rows))
        p12 = self._load_json("Results/json/parent_education_wage_p12_design_spec_preflight.json")
        self.assertEqual(p12["draft_design_spec"]["dataset_path"], "Data/Interim/parent_education_wage_repaired.csv")
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_p18_data_repair_apply.json").exists())
        self.assertTrue((self.project_root / "Reviews/parent_education_wage_p18_data_repair_apply.md").exists())

    def test_bdd_p18_then_p13_p16_executes_real_minimal_ols(self) -> None:
        p17 = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p17-data-repair-preflight")
        self.assertEqual(p17.status_code, 201, msg=p17.text)
        p18 = self.client.post(
            f"/api/v1/projects/{self.project_id}/product-control/p18-data-repair-apply",
            json=self._valid_apply_payload(),
        )
        self.assertEqual(p18.status_code, 201, msg=p18.text)

        response = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p13-p16-demo-closure")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "demo_closure_complete_paper_draft_ready")
        self.assertEqual(body["p13_run_plan_approval"]["dataset_path"], "Data/Interim/parent_education_wage_repaired.csv")
        self.assertEqual(body["p14_execution_ledger"]["status"], "execution_completed_minimal_ols")
        self.assertTrue(body["p14_execution_ledger"]["executed_regression"])
        self.assertIsNotNone(body["p14_execution_ledger"]["run_id"])
        self.assertEqual(body["p14_execution_ledger"]["model_results"]["treatment_variable"], "parent_education")
        self.assertEqual(body["p15_draft_package"]["status"], "complete_paper_draft_package_ready")
        self.assertTrue(body["p15_draft_package"]["can_export_complete_paper"])
        self.assertTrue(body["p16_acceptance_packet"]["can_claim_model_result"])
        self.assertTrue(body["p16_acceptance_packet"]["can_claim_complete_paper"])
        self.assertFalse(body["p16_acceptance_packet"]["can_claim_submission_ready"])
        self.assertTrue((self.project_root / "Manuscripts/generated/parent_education_wage_complete_paper_draft.md").exists())
        self.assertTrue((self.project_root / "Submissions/parent_education_wage_paper_draft.docx").exists())

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
        rows = ["pid,year,age,edu_last,ln_wage,female,urban"]
        for i in range(1, 15):
            year = 2020 if i <= 7 else 2022
            age = 24 + i
            edu_last = 2 + (i % 5)
            parent = 2 + (i % 6)
            female = i % 2
            urban = (i // 2) % 2
            experience = max(age - {2: 6, 3: 9, 4: 12, 5: 15, 6: 16}[edu_last] - 6, 0)
            ln_wage = 2 + 0.2 * parent + 0.03 * age - 0.1 * female + 0.07 * urban + 0.01 * edu_last + 0.004 * experience
            rows.append(f"{i},{year},{age},{edu_last},{ln_wage:.4f},{female},{urban}")
        (self.project_root / "Data/Final/cfps_robot_reallocation.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
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
            {"status": "demo_closure_blocked_branch_ready", "can_claim_complete_paper": False},
        )

    def _seed_repair_source_tables(self) -> None:
        source_root = self.project_root / "Data/Raw/cfps_source"
        (source_root / "2020cfps/STATA版本").mkdir(parents=True)
        (source_root / "2022CFPS").mkdir(parents=True)
        rows_2020 = ["pid,tb4_a20_f,tb4_a20_m"]
        rows_2022 = ["pid,tb4_a22_f,tb4_a22_m"]
        person_2020 = ["pid,qv102,qv202"]
        person_2022 = ["pid,qv102,qv202"]
        for i in range(1, 15):
            father = 2 + (i % 6)
            mother = 1 + (i % 5)
            if i <= 7:
                rows_2020.append(f"{i},{father},{mother}")
                person_2020.append(f"{i},{mother},{father}")
            else:
                rows_2022.append(f"{i},{father},{mother}")
                person_2022.append(f"{i},{mother},{father}")
        (source_root / "2020cfps/STATA版本/cfps2020famconf_202301.csv").write_text("\n".join(rows_2020) + "\n", encoding="utf-8")
        (source_root / "2022CFPS/cfps2022famconf_202410.csv").write_text("\n".join(rows_2022) + "\n", encoding="utf-8")
        (source_root / "2020cfps/STATA版本/cfps2020person_202112.csv").write_text("\n".join(person_2020) + "\n", encoding="utf-8")
        (source_root / "2022CFPS/cfps2022person_202410.csv").write_text("\n".join(person_2022) + "\n", encoding="utf-8")

    def _valid_apply_payload(self) -> dict:
        return {
            "reviewer": "tester",
            "note": "确认使用 P17 推荐来源，并采用默认教育年限映射。",
            "confirm_apply": True,
            "confirm_education_years_mapping": True,
        }

    def _write_json(self, relative_path: str, payload: dict) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.project_root / relative_path).read_text(encoding="utf-8"))

    def _sha256(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)

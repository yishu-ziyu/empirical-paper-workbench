from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ResultsDraftEvidenceBindingApiTests(unittest.TestCase):
    """BDD: Results & Draft 必须从成功 full run 绑定真实证据。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="results-draft-binding-"))
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
                "slug": "results-draft-binding",
                "title": "Results Draft Binding Project",
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

    def test_bdd_1_results_draft_requires_successful_full_run(self) -> None:
        """行为 1：没有成功 full run 时不得伪造 finding。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/results-draft")

        self.assertEqual(response.status_code, 409, msg=response.text)
        body = response.json()
        self.assertEqual(body["error"]["code"], "full_run_required")

    def test_bdd_2_successful_full_run_returns_finding_card_bound_to_result_artifact(self) -> None:
        """行为 2：成功 full run 后必须生成绑定结果 JSON 的 FindingCard。"""
        self._write_successful_full_run("run_test_full_001")

        response = self.client.get(f"/api/v1/projects/{self.project_id}/results-draft")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "local_execution")
        self.assertEqual(body["latest_run_id"], "run_test_full_001")
        self.assertEqual(len(body["findings"]), 1)
        finding = body["findings"][0]
        self.assertEqual(finding["evidence_level"], "local_execution")
        self.assertEqual(finding["run_id"], "run_test_full_001")
        self.assertEqual(finding["run_plan_version"], 1)
        self.assertEqual(finding["artifact_path"], "Results/json/analysis_result.json")
        self.assertEqual(finding["treatment"], "trained")
        self.assertEqual(finding["dependent_var"], "wage")
        self.assertEqual(finding["model_type"], "OLS")
        self.assertEqual(finding["sample_size"], 12)
        self.assertAlmostEqual(finding["estimate"], 1.8505, places=4)
        self.assertAlmostEqual(finding["std_error"], 0.0573, places=4)
        self.assertLess(finding["p_value"], 0.001)
        self.assertEqual(finding["review_status"], "needs_review")
        self.assertFalse(finding["can_write_to_draft"])

    def test_bdd_5_approve_finding_persists_claim_review_and_allows_draft_use(self) -> None:
        """行为 5：approve 后 FindingCard 才能进入正文写作。"""
        self._write_successful_full_run("run_test_full_001")

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/results-draft/findings/finding_trained_effect/review",
            json={"action": "approve", "note": "系数、标准误和样本量已核对，可以写入结果段。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        review = response.json()["review"]
        self.assertEqual(review["finding_id"], "finding_trained_effect")
        self.assertEqual(review["review_status"], "approved")
        self.assertEqual(review["evidence_level"], "local_file")
        self.assertEqual(review["run_id"], "run_test_full_001")
        self.assertEqual(review["artifact_path"], "Results/json/analysis_result.json")

        state_path = self.project_root / "state" / "product" / "finding_reviews.json"
        self.assertTrue(state_path.exists())
        persisted = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertIn("finding_trained_effect", persisted["reviews"])

        refreshed = self.client.get(f"/api/v1/projects/{self.project_id}/results-draft")
        finding = refreshed.json()["findings"][0]
        self.assertEqual(finding["review_status"], "approved")
        self.assertTrue(finding["can_write_to_draft"])
        self.assertEqual(finding["review"]["note"], "系数、标准误和样本量已核对，可以写入结果段。")

    def test_bdd_6_reject_or_revision_keeps_finding_out_of_draft(self) -> None:
        """行为 6：reject / needs_revision 都不能进入正文。"""
        self._write_successful_full_run("run_test_full_001")

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/results-draft/findings/finding_trained_effect/review",
            json={"action": "needs_revision", "note": "解释还需要补充稳健性证据。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        refreshed = self.client.get(f"/api/v1/projects/{self.project_id}/results-draft")
        finding = refreshed.json()["findings"][0]
        self.assertEqual(finding["review_status"], "needs_revision")
        self.assertFalse(finding["can_write_to_draft"])
        self.assertEqual(finding["review"]["note"], "解释还需要补充稳健性证据。")

    def test_bdd_7_claim_review_rejects_unknown_finding_and_invalid_action(self) -> None:
        """行为 7：非法 finding 或非法 action 必须被拒绝。"""
        self._write_successful_full_run("run_test_full_001")

        unknown = self.client.put(
            f"/api/v1/projects/{self.project_id}/results-draft/findings/finding_missing/review",
            json={"action": "approve", "note": "missing"},
        )
        invalid = self.client.put(
            f"/api/v1/projects/{self.project_id}/results-draft/findings/finding_trained_effect/review",
            json={"action": "maybe", "note": "bad action"},
        )

        self.assertEqual(unknown.status_code, 404, msg=unknown.text)
        self.assertEqual(unknown.json()["error"]["code"], "finding_not_found")
        self.assertEqual(invalid.status_code, 400, msg=invalid.text)
        self.assertEqual(invalid.json()["error"]["code"], "invalid_review_action")

    def test_bdd_3_draft_sections_bind_local_file_to_execution_evidence(self) -> None:
        """行为 3：DraftSection 必须同时暴露 local_file 和 local_execution 证据。"""
        self._write_successful_full_run("run_test_full_001")

        response = self.client.get(f"/api/v1/projects/{self.project_id}/results-draft")

        self.assertEqual(response.status_code, 200, msg=response.text)
        sections = response.json()["draft_sections"]
        section_titles = {section["title"] for section in sections}
        self.assertIn("Results", section_titles)
        results_section = next(section for section in sections if section["title"] == "Results")
        self.assertEqual(results_section["source_path"], "Manuscripts/generated/paper_draft.md")
        self.assertEqual(results_section["source_evidence_level"], "local_file")
        self.assertEqual(results_section["evidence_binding"]["run_id"], "run_test_full_001")
        self.assertEqual(results_section["evidence_binding"]["artifact_path"], "Results/json/analysis_result.json")
        self.assertEqual(results_section["evidence_binding"]["claim_evidence_level"], "local_execution")

    def test_bdd_9_finding_card_binds_method_execution_evidence(self) -> None:
        """行为 9：FindingCard 必须绑定 OLS 方法执行适配器产物。"""
        self._write_successful_full_run("run_test_full_001")

        response = self.client.get(f"/api/v1/projects/{self.project_id}/results-draft")

        self.assertEqual(response.status_code, 200, msg=response.text)
        finding = response.json()["findings"][0]
        method_evidence = finding["method_evidence"]
        self.assertEqual(method_evidence["artifact_path"], "Results/json/method_execution_result.json")
        self.assertEqual(method_evidence["evidence_level"], "local_execution")
        self.assertEqual(method_evidence["engine"], "python_ols_adapter")
        self.assertEqual(method_evidence["method_id"], "ols")
        self.assertEqual(method_evidence["formula"], "wage ~ trained + edu + experience")
        self.assertEqual(method_evidence["nobs"], 12)
        self.assertAlmostEqual(method_evidence["treatment_coefficient"], 1.8505, places=4)

    def _write_successful_full_run(self, run_id: str) -> None:
        runs_root = self.project_root / "state" / "runs"
        runs_root.mkdir(parents=True)
        run = {
            "id": run_id,
            "project_id": self.project_id,
            "mode": "full-run",
            "status": "succeeded",
            "started_at": "2026-05-13T00:00:00+00:00",
            "finished_at": "2026-05-13T00:01:00+00:00",
            "results_index_path": "Results/index.json",
            "artifact_count": 2,
            "artifact_paths": [
                "Results/json/analysis_result.json",
                "Results/json/method_execution_result.json",
                "Manuscripts/generated/paper_draft.md",
            ],
            "plan_binding": {"run_plan_version": 1},
            "execution_evidence_level": "local_execution",
            "method_execution": self._method_execution_payload(run_id),
        }
        (runs_root / f"{run_id}.json").write_text(json.dumps(run), encoding="utf-8")
        (runs_root / "index.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "id": run_id,
                            "project_id": self.project_id,
                            "mode": "full-run",
                            "status": "succeeded",
                            "started_at": run["started_at"],
                            "finished_at": run["finished_at"],
                            "results_index_path": "Results/index.json",
                            "artifact_count": 2,
                            "error": None,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        run_root = runs_root / run_id
        run_root.mkdir()
        (run_root / "run_manifest.json").write_text(
            json.dumps(
                {
                    "_meta": {"evidence_level": "local_execution"},
                    "run_id": run_id,
                    "run_plan_binding": {"run_plan_version": 1, "evidence_level": "local_file"},
                    "execution_evidence_level": "local_execution",
                    "method_execution": self._method_execution_payload(run_id),
                }
            ),
            encoding="utf-8",
        )
        (self.project_root / "Results" / "json" / "method_execution_result.json").write_text(
            json.dumps(self._method_execution_payload(run_id)),
            encoding="utf-8",
        )

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: results-draft-binding\n  title: Results Draft Binding Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "Results" / "index.json").write_text(
            json.dumps(
                {
                    "artifacts": [
                        {
                            "kind": "json",
                            "path": "Results/json/analysis_result.json",
                            "description": "StatsPAI paper workflow output",
                            "exists": True,
                        },
                        {
                            "kind": "markdown",
                            "path": "Manuscripts/generated/paper_draft.md",
                            "description": "Generated draft in Markdown",
                            "exists": True,
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        (project_root / "Results" / "json" / "analysis_result.json").write_text(
            json.dumps(
                {
                    "result_payload": {
                        "model_type": "OLS",
                        "dependent_var": "wage",
                        "n_obs": 12,
                        "coefficients": {
                            "Intercept": {"estimate": 8.3546, "std_error": 0.7470, "p_value": 0.00001},
                            "trained": {
                                "estimate": 1.8505,
                                "std_error": 0.0573,
                                "p_value": 0.000000001,
                                "conf_low": 1.7184,
                                "conf_high": 1.9826,
                            },
                        },
                    },
                    "draft": {
                        "parsed_hints": {"treatment": "trained", "y": "wage"},
                        "sections": {
                            "Results": "- **trained**: 1.8505 (SE = 0.0573)",
                            "Robustness": "- Estimate: 1.8505",
                        },
                    },
                }
            ),
            encoding="utf-8",
        )
        (project_root / "Results" / "json" / "method_execution_result.json").write_text(
            json.dumps(ResultsDraftEvidenceBindingApiTests._method_execution_payload("run_test_full_001")),
            encoding="utf-8",
        )
        (project_root / "Manuscripts" / "generated" / "paper_draft.md").write_text(
            "## Results\n\n- **trained**: 1.8505 (SE = 0.0573)\n\n## Robustness\n\n- Estimate: 1.8505\n",
            encoding="utf-8",
        )

    @staticmethod
    def _method_execution_payload(run_id: str) -> dict:
        return {
            "artifact_path": "Results/json/method_execution_result.json",
            "engine": "python_ols_adapter",
            "evidence_level": "local_execution",
            "methods": [
                {
                    "run_id": run_id,
                    "task_id": "baseline_regression",
                    "method_id": "ols",
                    "formula": "wage ~ trained + edu + experience",
                    "dataset_path": "Data/Final/analysis_sample.csv",
                    "run_plan_version": 1,
                    "nobs": 12,
                    "treatment": "trained",
                    "treatment_coefficient": 1.8505,
                    "evidence_level": "local_execution",
                }
            ],
        }


class ResultsDraftEvidenceBindingFrontendTests(unittest.TestCase):
    """BDD: Results & Draft 页面必须展示 findings 和 draft evidence binding。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    def test_bdd_4_results_draft_workspace_renders_findings_and_draft_bindings(self) -> None:
        """行为 4：前端必须有 FindingCard 和 DraftSection evidence binding 容器与渲染函数。"""
        self.assertIn("results-findings-list", self.index_html)
        self.assertIn("draft-evidence-sections", self.index_html)
        self.assertIn("v2api.resultsDraft.get", self.app_js)
        self.assertIn("renderResultsDraftEvidence", self.app_js)
        self.assertIn("local_execution", self.app_js)
        self.assertIn("local_file", self.app_js)

    def test_bdd_8_results_draft_workspace_exposes_claim_review_actions(self) -> None:
        """行为 8：前端 FindingCard 必须提供 claim review 操作。"""
        self.assertIn("reviewFinding", self.app_js)
        self.assertIn("data-finding-review-action", self.app_js)
        self.assertIn("data-finding-review-note", self.app_js)
        self.assertIn("claim-review-actions", self.app_js)
        self.assertIn("can_write_to_draft", self.app_js)
        self.assertIn("可写入正文", self.app_js)
        self.assertIn("run_plan_version", self.app_js)

    def test_bdd_10_results_draft_workspace_shows_method_execution_evidence(self) -> None:
        """行为 10：前端 FindingCard 必须展示方法执行证据来源。"""
        self.assertIn("method_evidence", self.app_js)
        self.assertIn("renderFindingMethodEvidence", self.app_js)
        self.assertIn("方法执行证据", self.app_js)
        self.assertIn("methodEvidence.method_id", self.app_js)
        self.assertIn("methodEvidence.formula", self.app_js)
        self.assertIn("methodEvidence.treatment_coefficient", self.app_js)


if __name__ == "__main__":
    unittest.main()

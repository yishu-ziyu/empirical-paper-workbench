from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ManuscriptConsumptionApiTests(unittest.TestCase):
    """BDD: Manuscript 只能消费 approved FindingCard。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="manuscript-consumption-"))
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
                "slug": "manuscript-consumption",
                "title": "Manuscript Consumption Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self._write_successful_full_run("run_test_full_001")

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_unapproved_finding_does_not_generate_candidate_or_mutate_draft(self) -> None:
        """行为 1：没有 approved FindingCard 时不得生成正文候选，也不得改写草稿。"""
        draft_path = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        before = draft_path.read_text(encoding="utf-8")

        response = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["items"], [])
        self.assertEqual(body["empty_state"]["code"], "approved_finding_required")
        self.assertEqual(draft_path.read_text(encoding="utf-8"), before)

    def test_bdd_2_approved_finding_generates_draft_candidate(self) -> None:
        """行为 2：approved FindingCard 必须生成可审阅正文候选。"""
        self._approve_finding()

        response = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "local_file")
        self.assertEqual(len(body["items"]), 1)
        candidate = body["items"][0]
        self.assertEqual(candidate["id"], "manuscript_candidate_finding_trained_effect_results")
        self.assertEqual(candidate["status"], "draft")
        self.assertEqual(candidate["section"], "Results")
        self.assertEqual(candidate["finding_id"], "finding_trained_effect")
        self.assertEqual(candidate["run_id"], "run_test_full_001")
        self.assertEqual(candidate["run_plan_version"], 1)
        self.assertIn("trained", candidate["body"])
        self.assertIn("wage", candidate["body"])
        self.assertIn("1.8505", candidate["body"])
        self.assertIn("0.0573", candidate["body"])
        self.assertIn("p", candidate["body"])
        self.assertIn("12", candidate["body"])

    def test_bdd_3_candidate_binds_source_result_and_review_provenance(self) -> None:
        """行为 3：正文候选必须绑定草稿、结果文件和人工审阅决定。"""
        self._approve_finding()

        response = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")

        self.assertEqual(response.status_code, 200, msg=response.text)
        provenance = response.json()["items"][0]["provenance"]
        self.assertEqual(provenance["source_draft"]["path"], "Manuscripts/generated/paper_draft.md")
        self.assertEqual(provenance["source_draft"]["evidence_level"], "local_file")
        self.assertEqual(provenance["result_artifact"]["path"], "Results/json/analysis_result.json")
        self.assertEqual(provenance["result_artifact"]["evidence_level"], "local_execution")
        self.assertEqual(provenance["review_decision"]["path"], "state/product/finding_reviews.json")
        self.assertEqual(provenance["review_decision"]["evidence_level"], "local_file")

    def test_bdd_4_rejected_finding_does_not_generate_candidate(self) -> None:
        """行为 4：rejected / needs_revision finding 不能进入正文候选。"""
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/results-draft/findings/finding_trained_effect/review",
            json={"action": "reject", "note": "证据不足。"},
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

        candidates = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")

        self.assertEqual(candidates.status_code, 200, msg=candidates.text)
        self.assertEqual(candidates.json()["items"], [])

    def test_bdd_6_candidate_defaults_to_needs_review_before_promote(self) -> None:
        """行为 6：正文候选默认需要人工审阅，不能直接 promote。"""
        draft_path = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        before = draft_path.read_text(encoding="utf-8")
        self._approve_finding()

        response = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")

        self.assertEqual(response.status_code, 200, msg=response.text)
        candidate = response.json()["items"][0]
        self.assertEqual(candidate["review_status"], "needs_review")
        self.assertFalse(candidate["can_promote"])
        self.assertEqual(draft_path.read_text(encoding="utf-8"), before)

    def test_bdd_7_approve_candidate_persists_review_and_allows_promote(self) -> None:
        """行为 7：approve 正文候选后写入本地审阅证据并允许后续 promote。"""
        self._approve_finding()

        review = self.client.put(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/review",
            json={"action": "approve", "note": "段落表述可以进入结果部分。"},
        )

        self.assertEqual(review.status_code, 200, msg=review.text)
        review_body = review.json()
        self.assertEqual(review_body["review_status"], "approved")
        self.assertEqual(review_body["evidence_level"], "local_file")
        self.assertTrue(review_body["can_promote"])
        review_path = self.project_root / "state" / "product" / "manuscript_candidate_reviews.json"
        self.assertTrue(review_path.exists())

        candidates = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")
        self.assertEqual(candidates.status_code, 200, msg=candidates.text)
        candidate = candidates.json()["items"][0]
        self.assertEqual(candidate["review_status"], "approved")
        self.assertTrue(candidate["can_promote"])
        self.assertEqual(candidate["review"]["note"], "段落表述可以进入结果部分。")
        self.assertEqual(
            candidate["provenance"]["candidate_review"]["path"],
            "state/product/manuscript_candidate_reviews.json",
        )
        self.assertEqual(candidate["provenance"]["candidate_review"]["evidence_level"], "local_file")

    def test_bdd_8_rejected_candidate_cannot_promote(self) -> None:
        """行为 8：reject / needs_revision 正文候选不能进入 promote。"""
        self._approve_finding()

        review = self.client.put(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/review",
            json={"action": "needs_revision", "note": "需要补充稳健性上下文。"},
        )

        self.assertEqual(review.status_code, 200, msg=review.text)
        candidates = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")
        candidate = candidates.json()["items"][0]
        self.assertEqual(candidate["review_status"], "needs_revision")
        self.assertFalse(candidate["can_promote"])
        self.assertEqual(candidate["review"]["note"], "需要补充稳健性上下文。")

    def test_bdd_9_invalid_candidate_review_is_rejected(self) -> None:
        """行为 9：非法 candidate 或非法 action 必须被结构化拒绝。"""
        self._approve_finding()

        invalid_action = self.client.put(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/review",
            json={"action": "publish", "note": "bad"},
        )
        missing_candidate = self.client.put(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/missing_candidate/review",
            json={"action": "approve", "note": "bad"},
        )

        self.assertEqual(invalid_action.status_code, 400, msg=invalid_action.text)
        self.assertEqual(invalid_action.json()["error"]["code"], "invalid_candidate_review_action")
        self.assertEqual(missing_candidate.status_code, 404, msg=missing_candidate.text)
        self.assertEqual(missing_candidate.json()["error"]["code"], "manuscript_candidate_not_found")

    def test_bdd_11_unreviewed_candidate_cannot_promote_or_mutate_draft(self) -> None:
        """行为 11：未审阅正文候选不能 promote，也不得改写草稿。"""
        self._approve_finding()
        draft_path = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        before = draft_path.read_text(encoding="utf-8")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/promote",
            json={"note": "尝试进入导出前检查。"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "candidate_review_required")
        self.assertEqual(draft_path.read_text(encoding="utf-8"), before)

    def test_bdd_12_approved_candidate_generates_promotion_preflight_without_writeback(self) -> None:
        """行为 12：approved 正文候选可以生成 promote preflight，但不能直接写回草稿。"""
        self._approve_finding()
        self._approve_candidate()
        draft_path = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        before = draft_path.read_text(encoding="utf-8")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/promote",
            json={"note": "进入导出前检查，不直接覆盖草稿。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["promotion_status"], "ready_for_export")
        self.assertEqual(body["evidence_level"], "local_file")
        self.assertTrue(body["can_export"])
        self.assertFalse(body["can_write_back"])
        self.assertEqual(body["promotion"]["candidate_review_path"], "state/product/manuscript_candidate_reviews.json")
        self.assertEqual(body["promotion"]["promotion_path"], "state/product/manuscript_candidate_promotions.json")
        self.assertEqual(draft_path.read_text(encoding="utf-8"), before)

        promotion_path = self.project_root / "state" / "product" / "manuscript_candidate_promotions.json"
        self.assertTrue(promotion_path.exists())
        candidates = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")
        candidate = candidates.json()["items"][0]
        self.assertEqual(candidate["promotion_status"], "ready_for_export")
        self.assertTrue(candidate["can_export"])
        self.assertFalse(candidate["can_write_back"])
        self.assertEqual(
            candidate["provenance"]["promotion_state"]["path"],
            "state/product/manuscript_candidate_promotions.json",
        )

    def test_bdd_13_rejected_candidate_cannot_promote(self) -> None:
        """行为 13：rejected / needs_revision candidate 不能 promote。"""
        self._approve_finding()
        review = self.client.put(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/review",
            json={"action": "reject", "note": "段落不适合进入正文。"},
        )
        self.assertEqual(review.status_code, 200, msg=review.text)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/promote",
            json={"note": "bad"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "candidate_review_required")
        promotion_path = self.project_root / "state" / "product" / "manuscript_candidate_promotions.json"
        self.assertFalse(promotion_path.exists())

    def test_bdd_14_missing_candidate_promote_is_rejected(self) -> None:
        """行为 14：不存在的正文候选不能创建 promote 状态。"""
        self._approve_finding()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/missing_candidate/promote",
            json={"note": "bad"},
        )

        self.assertEqual(response.status_code, 404, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "manuscript_candidate_not_found")

    def test_bdd_16_unpromoted_candidate_cannot_generate_export_preflight(self) -> None:
        """行为 16：未进入 ready_for_export 的 candidate 不能生成导出预览。"""
        self._approve_finding()
        self._approve_candidate()
        draft_path = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        before = draft_path.read_text(encoding="utf-8")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/export-preflight",
            json={"note": "bad"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "candidate_promotion_required")
        self.assertEqual(draft_path.read_text(encoding="utf-8"), before)

    def test_bdd_17_ready_candidate_generates_writeback_preview_and_manifest(self) -> None:
        """行为 17：ready_for_export candidate 生成写回预览和 export manifest，但不覆盖源草稿。"""
        self._approve_finding()
        self._approve_candidate()
        self._promote_candidate()
        draft_path = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        before = draft_path.read_text(encoding="utf-8")

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/export-preflight",
            json={"note": "生成写回预览。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["export_status"], "preview_ready")
        self.assertEqual(body["evidence_level"], "local_file")
        self.assertFalse(body["can_write_back"])
        self.assertEqual(body["preview_path"], "Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md")
        self.assertEqual(body["manifest_path"], "state/product/export_package_manifest.json")
        self.assertEqual(draft_path.read_text(encoding="utf-8"), before)

        preview_path = self.project_root / body["preview_path"]
        manifest_path = self.project_root / body["manifest_path"]
        self.assertTrue(preview_path.exists())
        self.assertTrue(manifest_path.exists())
        preview = preview_path.read_text(encoding="utf-8")
        self.assertIn("trained", preview)
        self.assertIn("wage", preview)
        self.assertIn("source_draft: Manuscripts/generated/paper_draft.md", preview)

        candidates = self.client.get(f"/api/v1/projects/{self.project_id}/manuscript-candidates")
        candidate = candidates.json()["items"][0]
        self.assertEqual(candidate["export_status"], "preview_ready")
        self.assertEqual(candidate["writeback_preview_path"], body["preview_path"])
        self.assertEqual(candidate["provenance"]["export_package"]["path"], "state/product/export_package_manifest.json")

    def test_bdd_18_missing_candidate_export_preflight_is_rejected(self) -> None:
        """行为 18：不存在的 candidate 不能生成 export preflight。"""
        self._approve_finding()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/missing_candidate/export-preflight",
            json={"note": "bad"},
        )

        self.assertEqual(response.status_code, 404, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "manuscript_candidate_not_found")

    def _approve_finding(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/results-draft/findings/finding_trained_effect/review",
            json={"action": "approve", "note": "可以进入结果段候选。"},
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_candidate(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/review",
            json={"action": "approve", "note": "段落可以进入导出前检查。"},
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _promote_candidate(self) -> None:
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/promote",
            json={"note": "进入导出前检查。"},
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

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
                "Manuscripts/generated/paper_draft.md",
            ],
            "plan_binding": {"run_plan_version": 1},
            "execution_evidence_level": "local_execution",
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
                }
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: manuscript-consumption\n  title: Manuscript Consumption Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
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
                    },
                }
            ),
            encoding="utf-8",
        )
        (project_root / "Manuscripts" / "generated" / "paper_draft.md").write_text(
            "## Results\n\n- **trained**: 1.8505 (SE = 0.0573)\n",
            encoding="utf-8",
        )


class ManuscriptConsumptionFrontendTests(unittest.TestCase):
    """BDD: Results & Draft 页面必须展示 Manuscript candidates。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    def test_bdd_5_results_draft_workspace_renders_manuscript_candidates(self) -> None:
        """行为 5：前端必须有正文候选容器、API 客户端和渲染函数。"""
        self.assertIn("manuscript-candidates-list", self.index_html)
        self.assertIn("v2api.manuscriptCandidates.get", self.app_js)
        self.assertIn("renderManuscriptCandidates", self.app_js)
        self.assertIn("approved_finding_required", self.app_js)
        self.assertIn("source_draft", self.app_js)
        self.assertIn("review_decision", self.app_js)
        self.assertNotIn("overwrite-paper-draft", self.app_js)

    def test_bdd_10_results_draft_workspace_exposes_candidate_review_actions(self) -> None:
        """行为 10：前端必须提供正文候选的独立审阅操作。"""
        self.assertIn("review_status", self.app_js)
        self.assertIn("可进入导出", self.app_js)
        self.assertIn("candidate_review", self.app_js)
        self.assertIn("v2api.manuscriptCandidates.reviewCandidate", self.app_js)
        self.assertIn("reviewManuscriptCandidate", self.app_js)
        self.assertIn("data-candidate-review-action", self.app_js)

    def test_bdd_15_results_draft_workspace_exposes_candidate_promote_preflight(self) -> None:
        """行为 15：前端必须提供 promote preflight，且不能提供直接覆盖草稿。"""
        self.assertIn("promotion_status", self.app_js)
        self.assertIn("ready_for_export", self.app_js)
        self.assertIn("can_write_back", self.app_js)
        self.assertIn("v2api.manuscriptCandidates.promoteCandidate", self.app_js)
        self.assertIn("promoteManuscriptCandidate", self.app_js)
        self.assertIn("data-candidate-promote-action", self.app_js)
        self.assertNotIn("overwrite-paper-draft", self.app_js)

    def test_bdd_19_results_draft_workspace_exposes_export_preflight_preview(self) -> None:
        """行为 19：前端必须提供 export preflight 预览操作和状态展示。"""
        self.assertIn("export_status", self.app_js)
        self.assertIn("preview_ready", self.app_js)
        self.assertIn("writeback_preview_path", self.app_js)
        self.assertIn("v2api.manuscriptCandidates.exportPreflightCandidate", self.app_js)
        self.assertIn("exportPreflightManuscriptCandidate", self.app_js)
        self.assertIn("data-candidate-export-preflight-action", self.app_js)
        self.assertIn("export_package", self.app_js)
        self.assertNotIn("overwrite-paper-draft", self.app_js)

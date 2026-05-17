from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ReviewerScorecardApiTests(unittest.TestCase):
    """BDD: 审稿意见必须结构化为评分、证据和人工接受的后续任务。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="reviewer-scorecard-"))
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
                "slug": "reviewer-scorecard",
                "title": "Reviewer Scorecard Project",
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

    def test_bdd_1_scorecard_requires_successful_full_run(self) -> None:
        """行为 1：没有 successful full run 时不能生成评分卡。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/reviewer-scorecard")

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "full_run_required")
        self.assertFalse((self.project_root / "state" / "product" / "reviewer_scorecard.json").exists())

    def test_bdd_2_scorecard_has_five_dimensions_with_evidence(self) -> None:
        """行为 2：评分卡必须覆盖五个审稿维度，并绑定证据。"""
        self._write_successful_full_run("run_reviewer_score_001")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/reviewer-scorecard", json={})

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "local_file")
        self.assertEqual(body["reviewer_backend"], "deterministic_baseline")
        self.assertEqual(body["source_run_id"], "run_reviewer_score_001")
        dimensions = {item["id"]: item for item in body["dimensions"]}
        self.assertEqual(
            set(dimensions),
            {"novelty", "identification_credibility", "data_quality", "clarity", "policy_relevance"},
        )
        for dimension in dimensions.values():
            self.assertIsInstance(dimension["score"], (int, float))
            self.assertGreaterEqual(dimension["score"], 0)
            self.assertLessEqual(dimension["score"], 10)
            self.assertTrue(dimension["rationale"])
            self.assertTrue(dimension["evidence"])
            self.assertIsInstance(dimension["suggested_tasks"], list)

    def test_bdd_3_low_score_creates_follow_up_task_suggestions_not_queue_mutations(self) -> None:
        """行为 3：低分建议不能自动改写 Agent Task Queue。"""
        self._write_successful_full_run("run_reviewer_score_002")
        queue_path = self.project_root / "state" / "product" / "agent_task_queue.json"
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        original_queue = {
            "id": "agent_task_queue",
            "version": 1,
            "status": "ready_for_dispatch",
            "tasks": [{"id": "existing_task", "title": "保持不变"}],
        }
        queue_path.write_text(json.dumps(original_queue, ensure_ascii=False, indent=2), encoding="utf-8")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/reviewer-scorecard", json={})

        self.assertEqual(response.status_code, 201, msg=response.text)
        dimensions = {item["id"]: item for item in response.json()["dimensions"]}
        identification = dimensions["identification_credibility"]
        self.assertLess(identification["score"], 6)
        self.assertTrue(identification["suggested_tasks"])
        self.assertTrue(all(task["requires_human_acceptance"] for task in identification["suggested_tasks"]))
        self.assertEqual(json.loads(queue_path.read_text(encoding="utf-8")), original_queue)

    def _write_successful_full_run(self, run_id: str) -> None:
        runs_root = self.project_root / "state" / "runs"
        runs_root.mkdir(parents=True)
        run = {
            "id": run_id,
            "project_id": self.project_id,
            "mode": "full-run",
            "status": "succeeded",
            "started_at": "2026-05-17T00:00:00+00:00",
            "finished_at": "2026-05-17T00:01:00+00:00",
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
            "project:\n  slug: reviewer-scorecard\n  title: Reviewer Scorecard Project\n"
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
                            "trained": {
                                "estimate": 1.8505,
                                "std_error": 0.0573,
                                "p_value": 0.000000001,
                                "conf_low": 1.7184,
                                "conf_high": 1.9826,
                            },
                        },
                    },
                    "draft": {"parsed_hints": {"treatment": "trained", "y": "wage"}},
                }
            ),
            encoding="utf-8",
        )
        (project_root / "Manuscripts" / "generated" / "paper_draft.md").write_text(
            "## Results\n\n- **trained**: 1.8505 (SE = 0.0573)\n",
            encoding="utf-8",
        )


class ReviewerScorecardFrontendTests(unittest.TestCase):
    """BDD: Review & Export 页面必须摘要优先展示审稿评分卡。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_4_frontend_shows_compact_scorecard_with_folded_details(self) -> None:
        """行为 4：评分理由和后续任务默认折叠，任务建议必须显式接受。"""
        self.assertIn("reviewer-scorecard-panel", self.index_html)
        self.assertIn("reviewer-scorecard-body", self.index_html)
        self.assertIn("v2api.reviewerScorecard.get", self.app_js)
        self.assertIn("v2api.reviewerScorecard.generate", self.app_js)
        self.assertIn("renderReviewerScorecard", self.app_js)
        self.assertIn("查看理由与后续任务", self.app_js)
        self.assertIn("加入任务队列草案", self.app_js)
        self.assertIn("data-accept-reviewer-task-suggestion", self.app_js)
        self.assertIn("reviewer-scorecard-row", self.styles_css)

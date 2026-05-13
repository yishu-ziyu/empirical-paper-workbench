from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ReviewExportPackageApiTests(unittest.TestCase):
    """BDD: Review & Export 必须展示可验收的导出包闭环。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="review-export-package-"))
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
                "slug": "review-export",
                "title": "Review Export Package Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self._write_successful_full_run("run_review_export_001")
        self._prepare_preview_ready_candidate()

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_export_package_returns_preview_ready_candidate(self) -> None:
        """行为 1：API 必须只把 preview_ready candidate 暴露为导出包。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/export-package")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "local_file")
        self.assertEqual(len(body["packages"]), 1)
        package = body["packages"][0]
        self.assertEqual(package["candidate_id"], "manuscript_candidate_finding_trained_effect_results")
        self.assertEqual(package["export_status"], "preview_ready")
        self.assertFalse(package["can_write_back"])
        self.assertEqual(
            package["writeback_preview_path"],
            "Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md",
        )
        self.assertEqual(package["manifest_path"], "state/product/export_package_manifest.json")

    def test_bdd_2_export_package_includes_frontier_evaluator_checks(self) -> None:
        """行为 2：导出包必须包含 Frontier-Eng 式 evaluator checks。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/export-package")

        self.assertEqual(response.status_code, 200, msg=response.text)
        package = response.json()["packages"][0]
        checks = {check["id"]: check for check in package["evaluator_checks"]}
        self.assertEqual(package["evaluator_status"], "passed")
        self.assertEqual(checks["writeback_preview_exists"]["status"], "passed")
        self.assertEqual(checks["export_manifest_exists"]["status"], "passed")
        self.assertEqual(checks["result_artifact_bound"]["evidence_level"], "local_execution")
        self.assertEqual(checks["promotion_decision_present"]["path"], "state/product/manuscript_candidate_promotions.json")
        self.assertEqual(checks["source_draft_not_overwritten"]["detail"], "can_write_back=false")

    def test_bdd_3_export_package_records_iteration_log(self) -> None:
        """行为 3：Review & Export 必须记录 objective -> baseline -> evaluator -> feedback -> next_iteration。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/export-package")

        self.assertEqual(response.status_code, 200, msg=response.text)
        package = response.json()["packages"][0]
        phases = [entry["phase"] for entry in package["frontier_iteration_log"]]
        self.assertEqual(phases, ["objective", "baseline", "evaluator", "feedback", "next_iteration"])
        self.assertEqual(package["frontier_loop"]["reference"], "Frontier-Eng")
        self.assertEqual(package["frontier_loop"]["feedback"], "evaluator_status=passed")
        self.assertIn("人工确认", package["next_manual_action"])

    def _prepare_preview_ready_candidate(self) -> None:
        finding = self.client.put(
            f"/api/v1/projects/{self.project_id}/results-draft/findings/finding_trained_effect/review",
            json={"action": "approve", "note": "可以进入结果段候选。"},
        )
        self.assertEqual(finding.status_code, 200, msg=finding.text)
        candidate = self.client.put(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/review",
            json={"action": "approve", "note": "段落可以进入导出前检查。"},
        )
        self.assertEqual(candidate.status_code, 200, msg=candidate.text)
        promotion = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/promote",
            json={"note": "进入导出前检查。"},
        )
        self.assertEqual(promotion.status_code, 200, msg=promotion.text)
        export = self.client.post(
            f"/api/v1/projects/{self.project_id}/manuscript-candidates/"
            "manuscript_candidate_finding_trained_effect_results/export-preflight",
            json={"note": "生成写回预览。"},
        )
        self.assertEqual(export.status_code, 200, msg=export.text)

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
            "project:\n  slug: review-export\n  title: Review Export Package Project\n"
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


class ReviewExportPackageFrontendTests(unittest.TestCase):
    """BDD: Review & Export 页面必须有可视化导出包验收入口。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    def test_bdd_4_frontend_exposes_export_package_workbench(self) -> None:
        """行为 4：前端必须展示导出包、evaluator checks 和迭代日志。"""
        self.assertIn("export-package-workbench", self.index_html)
        self.assertIn("v2api.exportPackage.get", self.app_js)
        self.assertIn("renderExportPackageWorkbench", self.app_js)
        self.assertIn("export-evaluator-checks", self.app_js)
        self.assertIn("frontier-iteration-log", self.app_js)
        self.assertIn("写回预览路径", self.app_js)
        self.assertIn("可写回正文", self.app_js)
        self.assertIn("data-open-results-draft", self.app_js)
        self.assertNotIn("overwrite-paper-draft", self.app_js)

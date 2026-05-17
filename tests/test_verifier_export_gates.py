from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class VerifierExportGatesTests(unittest.TestCase):
    """BDD: Review & Export 必须通过 verifier gates 才能进入 docx 导出。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="verifier-export-gates-"))
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
                "slug": "verifier-export",
                "title": "Verifier Export Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self._write_successful_full_run("run_verifier_001")

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_verifier_requires_export_candidate(self) -> None:
        """行为 1：没有 ready_for_export 正文候选时，不得生成 verifier state。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/verifier-checks")

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "export_candidate_required")
        self.assertFalse((self.project_root / "state" / "product" / "verifier_checks.json").exists())

    def test_bdd_2_verifier_checks_result_binding(self) -> None:
        """行为 2：结果绑定必须连接 FindingCard、正文候选和结果产物。"""
        self._prepare_preview_ready_candidate()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/verifier-checks/run")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "local_file")
        checks = {check["id"]: check for check in body["checks"]}
        self.assertEqual(checks["result_binding"]["status"], "passed")
        self.assertEqual(checks["result_binding"]["evidence_level"], "local_execution")
        self.assertIn("Results/json/analysis_result.json", checks["result_binding"]["artifact_paths"])
        self.assertEqual(checks["result_binding"]["candidate_id"], "manuscript_candidate_finding_trained_effect_results")
        self.assertEqual(checks["result_binding"]["finding_id"], "finding_trained_effect")

    def test_bdd_3_verifier_checks_reproducibility_package_artifacts(self) -> None:
        """行为 3：核验清单必须覆盖复现包关键产物。"""
        self._prepare_preview_ready_candidate()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/verifier-checks/run")

        self.assertEqual(response.status_code, 201, msg=response.text)
        checks = {check["id"]: check for check in response.json()["checks"]}
        for check_id in [
            "repro_manifest",
            "run_plan_artifact",
            "analysis_result_artifact",
            "method_execution_artifact",
            "draft_preview_exists",
            "evidence_levels_valid",
            "docx_export_preflight",
        ]:
            self.assertIn(check_id, checks)
            self.assertIn(checks[check_id]["status"], {"passed", "failed", "blocked"})
            self.assertTrue(checks[check_id]["artifact_paths"], msg=check_id)
        self.assertEqual(checks["method_execution_artifact"]["artifact_paths"], ["Results/json/method_execution_result.json"])
        self.assertTrue((self.project_root / "state" / "product" / "verifier_checks.json").exists())

    def test_bdd_4_docx_export_blocked_until_verifier_passes(self) -> None:
        """行为 4：存在失败项时 docx 最终导出必须被 verifier gate 阻断。"""
        self._prepare_preview_ready_candidate()
        (self.project_root / "Manuscripts" / "generated" / "previews" / "manuscript_candidate_finding_trained_effect_results.md").unlink()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/verifier-checks/run")

        self.assertEqual(response.status_code, 201, msg=response.text)
        body = response.json()
        checks = {check["id"]: check for check in body["checks"]}
        self.assertEqual(body["status"], "failed")
        self.assertFalse(body["can_export_docx"])
        self.assertEqual(body["docx_export_preflight"]["status"], "blocked")
        self.assertEqual(checks["draft_preview_exists"]["status"], "failed")

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
        method_execution = self._method_execution_payload(run_id)
        run = {
            "id": run_id,
            "project_id": self.project_id,
            "mode": "full-run",
            "status": "succeeded",
            "started_at": "2026-05-13T00:00:00+00:00",
            "finished_at": "2026-05-13T00:01:00+00:00",
            "results_index_path": "Results/index.json",
            "artifact_count": 4,
            "artifact_paths": [
                "Results/json/analysis_result.json",
                "Results/json/method_execution_result.json",
                "Manuscripts/generated/paper_draft.md",
                "state/product/run_plan.json",
            ],
            "plan_binding": {"run_plan_version": 1},
            "method_execution": method_execution,
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
                            "artifact_count": 4,
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
                    "method_execution": method_execution,
                    "execution_evidence_level": "local_execution",
                }
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _method_execution_payload(run_id: str) -> dict:
        return {
            "artifact_path": "Results/json/method_execution_result.json",
            "engine": "python",
            "evidence_level": "local_execution",
            "methods": [
                {
                    "id": "baseline_ols",
                    "method": "OLS",
                    "status": "succeeded",
                    "run_id": run_id,
                    "run_plan_version": 1,
                    "evidence_level": "local_execution",
                }
            ],
        }

    def _create_minimal_project(self, project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "state" / "product").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: verifier-export\n  title: Verifier Export Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "state" / "product" / "run_plan.json").write_text(
            json.dumps(
                {
                    "status": "approved",
                    "version": 1,
                    "evidence_level": "local_file",
                    "tasks": [{"id": "baseline_regression", "method": "OLS"}],
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
        (project_root / "Results" / "json" / "method_execution_result.json").write_text(
            json.dumps(self._method_execution_payload("run_verifier_001")),
            encoding="utf-8",
        )
        (project_root / "Manuscripts" / "generated" / "paper_draft.md").write_text(
            "## Results\n\n- **trained**: 1.8505 (SE = 0.0573)\n",
            encoding="utf-8",
        )


class VerifierExportGatesFrontendTests(unittest.TestCase):
    """BDD: Review & Export 页面必须先显示 verifier gates，再显示最终导出动作。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_frontend_shows_verifier_gates_before_export_actions(self) -> None:
        """行为 5：前端必须把验证闸门放在导出包动作之前，并由 can_export_docx 控制按钮。"""
        self.assertIn("verifier-gate-panel", self.index_html)
        self.assertLess(self.index_html.index("verifier-gate-panel"), self.index_html.index("export-package-panel"))
        self.assertIn("v2api.verifierChecks.get", self.app_js)
        self.assertIn("v2api.verifierChecks.run", self.app_js)
        self.assertIn("renderVerifierGates", self.app_js)
        self.assertIn("verifier-gate-row", self.app_js)
        self.assertIn("data-run-verifier-checks", self.app_js)
        self.assertIn("data-docx-final-export", self.app_js)
        self.assertIn("verifier-final-export-button", self.app_js)
        self.assertIn("!state.verifierChecksData?.can_export_docx", self.app_js)
        self.assertIn("verifier-gate-panel", self.styles_css)
        self.assertIn("verifier-gate-row", self.styles_css)

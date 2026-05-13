from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class FullRunFromRunPlanApiTests(unittest.TestCase):
    """BDD: 完整执行必须从 approved RunPlan 启动，并保留 provenance。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="full-run-plan-"))
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
                "slug": "full-run-plan",
                "title": "Full RunPlan Project",
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

    def test_bdd_1_full_run_requires_approved_run_plan(self) -> None:
        """行为 1：缺少 approved RunPlan 时禁止 full run。"""
        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "run_plan_required")
        runs = self.client.get(f"/api/v1/projects/{self.project_id}/runs")
        self.assertEqual(runs.json()["items"], [])

    def test_bdd_2_full_run_reads_run_plan_and_creates_observable_execution(self) -> None:
        """行为 2：full run 必须读取 approved RunPlan 并创建可观察执行。"""
        self._approve_variable_roles()
        self._approve_design_spec()
        self._approve_run_plan()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        run = response.json()
        self.assertEqual(run["mode"], "full-run")
        self.assertEqual(run["status"], "succeeded")
        self.assertEqual(run["execution_evidence_level"], "local_execution")
        self.assertEqual(run["dataset_source"]["path"], "Data/Final/analysis_sample.csv")
        self.assertEqual(run["plan_binding"]["evidence_level"], "local_file")
        self.assertEqual(run["plan_binding"]["run_plan_version"], 1)
        self.assertEqual(run["plan_binding"]["design_spec_version"], 1)
        self.assertEqual(run["plan_binding"]["variable_role_set_version"], 1)

        manifest_path = self.project_root / "state" / "runs" / run["id"] / "run_manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["run_plan_binding"]["run_plan_version"], 1)
        self.assertEqual(manifest["run_plan_binding"]["dataset_path"], "Data/Final/analysis_sample.csv")
        self.assertEqual(manifest["run_plan_binding"]["evidence_level"], "local_file")
        self.assertEqual(manifest["research_engine"]["name"], "Feynman-compatible research engine")
        self.assertFalse(manifest["research_engine"]["embedded"])
        self.assertEqual(manifest["research_engine"]["integration_mode"], "callable_external")

        observability = self.client.get(
            f"/api/v1/projects/{self.project_id}/runs/{run['id']}/observability"
        )
        self.assertEqual(observability.status_code, 200, msg=observability.text)
        self.assertEqual(observability.json()["_meta"]["evidence_level"], "local_execution")
        self.assertEqual(
            observability.json()["manifest"]["run_plan_binding"]["evidence_level"],
            "local_file",
        )

    def _approve_variable_roles(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/analysis_sample.csv",
                "roles": {
                    "outcome": ["wage"],
                    "treatment": ["trained"],
                    "controls": ["edu", "experience"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "变量角色已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_design_spec(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "培训是否影响工资？",
                "identification_strategy": {
                    "name": "baseline_ols",
                    "summary": "在控制教育和经验后估计培训与工资的关系。",
                    "assumptions": [],
                    "threats": [],
                },
                "model": {
                    "estimator": "ols",
                    "formula": "wage ~ trained + edu + experience",
                    "fixed_effects": [],
                    "cluster_by": [],
                    "sample_filter": "all",
                },
                "note": "研究设计已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_run_plan(self) -> None:
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={
                "tasks": draft["tasks"],
                "outputs": draft["outputs"],
                "note": "RunPlan 已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Results").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: full-run-plan\n  title: Full RunPlan Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n12,0,14,5\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text(
            """from __future__ import annotations
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--project-root', default='.')
parser.add_argument('--run-id', required=True)
args = parser.parse_args()
root = Path(args.project_root).resolve()
run_root = root / 'state' / 'runs' / args.run_id
run_root.mkdir(parents=True, exist_ok=True)
(root / 'Results').mkdir(parents=True, exist_ok=True)
(root / 'state').mkdir(parents=True, exist_ok=True)
(root / 'Manuscripts' / 'generated').mkdir(parents=True, exist_ok=True)
(root / 'state' / 'project_state.json').write_text(json.dumps({'current_stage': 'execution', 'last_run_mode': 'live', 'dataset_exists': True}), encoding='utf-8')
(root / 'Results' / 'index.json').write_text(json.dumps({'artifacts': [{'path': 'Manuscripts/generated/paper_draft.md', 'exists': True}]}), encoding='utf-8')
(root / 'Manuscripts' / 'generated' / 'paper_draft.md').write_text('# Draft\\n', encoding='utf-8')
(run_root / 'run_manifest.json').write_text(json.dumps({'run_id': args.run_id, 'mode': 'live', 'human_in_loop': {'open_gate_count': 0}}), encoding='utf-8')
(run_root / 'run_steps.json').write_text(json.dumps({'_meta': {'evidence_level': 'local_execution'}, 'items': []}), encoding='utf-8')
(run_root / 'gates.json').write_text(json.dumps({'_meta': {'evidence_level': 'local_execution'}, 'items': []}), encoding='utf-8')
(run_root / 'run_events.jsonl').write_text(json.dumps({'sequence': 1, 'run_id': args.run_id, 'type': 'run_started', 'evidence_level': 'local_execution'}) + '\\n', encoding='utf-8')
print('ok')
""",
            encoding="utf-8",
        )


class FullRunFromRunPlanFrontendTests(unittest.TestCase):
    """BDD: 前端 ready 后必须把 full run 作为 Execution 主行动。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    def test_bdd_4_execution_page_contains_start_full_run_action(self) -> None:
        """行为 4：Execution 页面必须有 full run 主行动按钮。"""
        self.assertIn("observable-run-full-button", self.index_html)
        self.assertIn("v2api.runs.startFull", self.app_js)
        self.assertIn("createFullRunFromPlan", self.app_js)
        self.assertIn("start_full_run", self.app_js)
        self.assertIn("/runs/full", self.app_js)


if __name__ == "__main__":
    unittest.main()

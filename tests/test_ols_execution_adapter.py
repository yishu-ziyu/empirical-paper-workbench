from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class OlsExecutionAdapterApiTests(unittest.TestCase):
    """BDD: ready 的 OLS RunPlan 必须产生真实 local_execution 方法结果。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ols-execution-adapter-"))
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
                "slug": "ols-execution-adapter",
                "title": "OLS Execution Adapter Project",
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

    def test_bdd_1_full_run_writes_local_execution_ols_result(self) -> None:
        """行为 1：approved OLS RunPlan 生成本地执行结果。"""
        self._approve_variable_roles()
        self._approve_design_spec()
        self._approve_run_plan()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        run = response.json()
        result_path = self.project_root / "Results" / "json" / "method_execution_result.json"
        self.assertTrue(result_path.exists())
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["evidence_level"], "local_execution")
        self.assertEqual(result["engine"], "python_ols_adapter")
        self.assertEqual(result["methods"][0]["method_id"], "ols")
        self.assertEqual(result["methods"][0]["task_id"], "baseline_regression")
        self.assertEqual(run["method_execution"]["artifact_path"], "Results/json/method_execution_result.json")
        self.assertEqual(run["method_execution"]["evidence_level"], "local_execution")

    def test_bdd_2_ols_result_binds_run_plan_dataset_formula_and_coefficient(self) -> None:
        """行为 2：OLS 结果必须绑定 RunPlan、数据集、公式和 treatment 系数。"""
        self._approve_variable_roles()
        self._approve_design_spec()
        self._approve_run_plan()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        method = response.json()["method_execution"]["methods"][0]
        self.assertEqual(method["run_plan_version"], 1)
        self.assertEqual(method["dataset_path"], "Data/Final/analysis_sample.csv")
        self.assertEqual(method["formula"], "wage ~ trained + edu + experience")
        self.assertEqual(method["method_id"], "ols")
        self.assertEqual(method["nobs"], 8)
        self.assertIn("trained", method["coefficients"])
        self.assertIsInstance(method["coefficients"]["trained"], float)

    def test_bdd_3_manifest_records_method_execution_artifact(self) -> None:
        """行为 3：run manifest 必须记录方法执行产物。"""
        self._approve_variable_roles()
        self._approve_design_spec()
        self._approve_run_plan()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        run_id = response.json()["id"]
        manifest_path = self.project_root / "state" / "runs" / run_id / "run_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["method_execution"]["artifact_path"], "Results/json/method_execution_result.json")
        self.assertEqual(manifest["method_execution"]["evidence_level"], "local_execution")
        self.assertEqual(manifest["method_execution"]["methods"][0]["method_id"], "ols")

    def test_bdd_4_unsupported_method_is_rejected_before_execution(self) -> None:
        """行为 4：unsupported 方法不能被静默执行。"""
        self._approve_variable_roles()
        self._approve_design_spec()
        self._approve_run_plan(method_id="iv")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "unsupported_run_plan_method")
        self.assertFalse((self.project_root / "Results" / "json" / "method_execution_result.json").exists())

    def test_bdd_5_insufficient_ols_data_returns_structured_failure(self) -> None:
        """行为 5：OLS 数据不足时返回结构化失败，不能暴露 500。"""
        (self.project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n"
            "10,1,16,3\n"
            "12,0,14,5\n",
            encoding="utf-8",
        )
        self._approve_variable_roles()
        self._approve_design_spec()
        self._approve_run_plan()

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "method_execution_failed")
        self.assertIn("not_enough_numeric_observations", response.json()["error"]["message"])
        self.assertFalse((self.project_root / "Results" / "json" / "method_execution_result.json").exists())

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

    def _approve_run_plan(self, method_id: str = "ols") -> None:
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        tasks = [dict(task, method_id=method_id) for task in draft["tasks"]]
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={
                "tasks": tasks,
                "outputs": draft["outputs"],
                "note": "RunPlan 已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: ols-execution-adapter\n  title: OLS Execution Adapter Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n"
            "10,1,16,3\n"
            "12,0,14,5\n"
            "13,1,15,6\n"
            "15,0,17,8\n"
            "18,1,18,10\n"
            "16,0,16,4\n"
            "20,1,20,12\n"
            "14,0,15,7\n",
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


if __name__ == "__main__":
    unittest.main()

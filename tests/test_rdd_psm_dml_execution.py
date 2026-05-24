from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class RddPsmDmlExecutionAdapterApiTests(unittest.TestCase):
    """BDD: StatsPAI 后端支持 RDD、PSM 和 DML 方法执行。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="rdd-psm-dml-execution-adapter-"))
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
                "slug": "rdd-psm-dml-execution-adapter",
                "title": "RDD PSM DML Execution Adapter Project",
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

    def test_bdd_1_rdd_run_plan_is_accepted_when_running_variable_present(self) -> None:
        """行为 1：RDD RunPlan 在具备断点运行变量时被接受。"""
        self._approve_variable_roles_rdd()
        self._approve_design_spec_rdd()
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        tasks = [dict(task, method_id="rdd", estimator="rdd") for task in draft["tasks"]]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={"tasks": tasks, "outputs": draft["outputs"], "note": "RDD RunPlan 已确认。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_bdd_2_rdd_full_run_produces_local_execution_result(self) -> None:
        """行为 2：RDD full run 生成本地执行结果。"""
        self._approve_variable_roles_rdd()
        self._approve_design_spec_rdd()
        self._approve_run_plan("rdd")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        result_path = self.project_root / "Results" / "json" / "method_execution_result.json"
        self.assertTrue(result_path.exists())
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["engine"], "statspai")
        method = result["methods"][0]
        self.assertEqual(method["method_id"], "rdd")
        self.assertIn("y=outcome", method["formula"])
        self.assertIn("running=score", method["formula"])
        self.assertEqual(method["nobs"], 50)

    def test_bdd_3_psm_run_plan_is_accepted_when_covariates_present(self) -> None:
        """行为 3：PSM RunPlan 在具备协变量时被接受。"""
        self._approve_variable_roles_psm()
        self._approve_design_spec_psm()
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        tasks = [dict(task, method_id="psm", estimator="psm") for task in draft["tasks"]]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={"tasks": tasks, "outputs": draft["outputs"], "note": "PSM RunPlan 已确认。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_bdd_4_psm_full_run_produces_local_execution_result(self) -> None:
        """行为 4：PSM full run 生成本地执行结果。"""
        self._approve_variable_roles_psm()
        self._approve_design_spec_psm()
        self._approve_run_plan("psm")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        result_path = self.project_root / "Results" / "json" / "method_execution_result.json"
        self.assertTrue(result_path.exists())
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["engine"], "statspai")
        method = result["methods"][0]
        self.assertEqual(method["method_id"], "psm")
        self.assertIn("y=outcome", method["formula"])
        self.assertIn("treat=treatment", method["formula"])
        self.assertEqual(method["nobs"], 50)

    def test_bdd_5_dml_run_plan_is_accepted_when_covariates_present(self) -> None:
        """行为 5：DML RunPlan 在具备协变量时被接受。"""
        self._approve_variable_roles_dml()
        self._approve_design_spec_dml()
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        tasks = [dict(task, method_id="dml", estimator="dml") for task in draft["tasks"]]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={"tasks": tasks, "outputs": draft["outputs"], "note": "DML RunPlan 已确认。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_bdd_6_dml_full_run_produces_local_execution_result(self) -> None:
        """行为 6：DML full run 生成本地执行结果。"""
        self._approve_variable_roles_dml()
        self._approve_design_spec_dml()
        self._approve_run_plan("dml")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        result_path = self.project_root / "Results" / "json" / "method_execution_result.json"
        self.assertTrue(result_path.exists())
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["engine"], "statspai")
        method = result["methods"][0]
        self.assertEqual(method["method_id"], "dml")
        self.assertIn("y=outcome", method["formula"])
        self.assertIn("treat=treatment", method["formula"])
        self.assertEqual(method["nobs"], 50)

    def _approve_variable_roles_rdd(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/rdd_sample.csv",
                "roles": {
                    "outcome": ["outcome"],
                    "treatment": ["treatment"],
                    "controls": ["cov1", "cov2"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                    "running_variable": ["score"],
                },
                "note": "RDD 变量角色已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_design_spec_rdd(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "奖学金对学业表现的影响（RDD）",
                "identification_strategy": {
                    "name": "rdd_baseline",
                    "summary": "用断点回归估计奖学金门槛对学业表现的影响。",
                    "assumptions": [],
                    "threats": [],
                },
                "model": {
                    "estimator": "rdd",
                    "running_variable": "score",
                    "cutoff": 0.0,
                    "fixed_effects": [],
                    "cluster_by": [],
                    "sample_filter": "all",
                },
                "note": "研究设计已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_variable_roles_psm(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/psm_sample.csv",
                "roles": {
                    "outcome": ["outcome"],
                    "treatment": ["treatment"],
                    "controls": ["age", "income", "edu"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "PSM 变量角色已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_design_spec_psm(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "培训项目对收入的影响（PSM）",
                "identification_strategy": {
                    "name": "psm_baseline",
                    "summary": "用倾向得分匹配估计培训项目对收入的影响。",
                    "assumptions": [],
                    "threats": [],
                },
                "model": {
                    "estimator": "psm",
                    "fixed_effects": [],
                    "cluster_by": [],
                    "sample_filter": "all",
                },
                "note": "研究设计已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_variable_roles_dml(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/dml_sample.csv",
                "roles": {
                    "outcome": ["outcome"],
                    "treatment": ["treatment"],
                    "controls": ["x1", "x2", "x3", "x4"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "DML 变量角色已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_design_spec_dml(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "广告曝光对购买行为的影响（DML）",
                "identification_strategy": {
                    "name": "dml_baseline",
                    "summary": "用双机器学习估计广告曝光对购买行为的影响。",
                    "assumptions": [],
                    "threats": [],
                },
                "model": {
                    "estimator": "dml",
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
            json={"tasks": tasks, "outputs": draft["outputs"], "note": "RunPlan 已确认。"},
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _create_minimal_project(self, project_root: Path) -> None:
        import pandas as pd
        import numpy as np

        project_root.mkdir(parents=True)
        for sub in ["Data/Raw", "Data/Final", "Results/json", "Results/logs", "Manuscripts/generated", "Program/temp", "Submissions", "state/product", "state/runs", "Tasks", "docs", "Reference"]:
            (project_root / sub).mkdir(parents=True, exist_ok=True)

        # RDD sample: score around cutoff=0, with clear left/right separation
        np.random.seed(42)
        rdd_left = np.random.uniform(-40, -5, 25)   # well below cutoff
        rdd_right = np.random.uniform(5, 40, 25)    # well above cutoff
        rdd_df = pd.DataFrame({
            "outcome": np.random.normal(50, 10, 50),
            "score": np.concatenate([rdd_left, rdd_right]),
            "treatment": [0] * 25 + [1] * 25,
            "cov1": np.random.normal(0, 1, 50),
            "cov2": np.random.normal(0, 1, 50),
        })
        rdd_df.to_csv(project_root / "Data/Final/rdd_sample.csv", index=False)

        # PSM sample
        psm_df = pd.DataFrame({
            "outcome": np.random.normal(50, 10, 50),
            "treatment": np.random.binomial(1, 0.4, 50),
            "age": np.random.normal(35, 10, 50),
            "income": np.random.normal(50000, 15000, 50),
            "edu": np.random.normal(14, 3, 50),
        })
        psm_df.to_csv(project_root / "Data/Final/psm_sample.csv", index=False)

        # DML sample
        dml_df = pd.DataFrame({
            "outcome": np.random.normal(50, 10, 50),
            "treatment": np.random.binomial(1, 0.4, 50),
            "x1": np.random.normal(0, 1, 50),
            "x2": np.random.normal(0, 1, 50),
            "x3": np.random.normal(0, 1, 50),
            "x4": np.random.normal(0, 1, 50),
        })
        dml_df.to_csv(project_root / "Data/Final/dml_sample.csv", index=False)

        # Minimal paper.yaml
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: test\n  title: Test\n  language: zh\n"
            "research:\n  question: Test question\n  design: experimental\n"
            "data:\n  source: synthetic\n  key_variables:\n    outcome: [y]\n    treatment: [d]\n    controls: []\n"
            "methods:\n  baseline:\n    candidates: [ols, iv, did, rdd, psm, dml]\n"
            "manuscript:\n  target_journal: 华侨大学学报\n",
            encoding="utf-8",
        )
        (project_root / "README.md").write_text("# Test", encoding="utf-8")
        (project_root / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
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

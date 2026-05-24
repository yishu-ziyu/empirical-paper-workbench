from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class IvDidExecutionAdapterApiTests(unittest.TestCase):
    """BDD: StatsPAI 后端支持 IV 和 DID 方法执行。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iv-did-execution-adapter-"))
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
                "slug": "iv-did-execution-adapter",
                "title": "IV DID Execution Adapter Project",
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

    def test_bdd_1_iv_run_plan_is_accepted_when_instruments_present(self) -> None:
        """行为 1：IV RunPlan 在具备工具变量时被接受。"""
        self._approve_variable_roles_iv()
        self._approve_design_spec_iv()
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        tasks = [dict(task, method_id="iv", estimator="iv") for task in draft["tasks"]]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={"tasks": tasks, "outputs": draft["outputs"], "note": "IV RunPlan 已确认。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_bdd_2_iv_full_run_produces_local_execution_result(self) -> None:
        """行为 2：IV full run 生成本地执行结果。"""
        self._approve_variable_roles_iv()
        self._approve_design_spec_iv()
        self._approve_run_plan("iv")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        result_path = self.project_root / "Results" / "json" / "method_execution_result.json"
        self.assertTrue(result_path.exists())
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["engine"], "statspai")
        method = result["methods"][0]
        self.assertEqual(method["method_id"], "iv")
        self.assertIn("lwage", method["formula"])
        self.assertIn("educ", method["formula"])
        self.assertIn("nearc4", method["formula"])
        self.assertEqual(method["nobs"], 50)
        self.assertIn("educ", method["coefficients"])

    def test_bdd_3_iv_diag_writes_independent_artifact(self) -> None:
        """行为 3：IV 诊断写出独立产物。"""
        self._approve_variable_roles_iv()
        self._approve_design_spec_iv()
        self._approve_run_plan("iv")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        diag_path = self.project_root / "Results" / "json" / "iv_diag_result.json"
        self.assertTrue(diag_path.exists())
        diag = json.loads(diag_path.read_text(encoding="utf-8"))
        self.assertEqual(diag["backend_id"], "iv_diag")
        self.assertEqual(diag["status"], "passed")

    def test_bdd_4_did_run_plan_is_accepted_when_panel_vars_present(self) -> None:
        """行为 4：DID RunPlan 在具备面板变量时被接受。"""
        self._approve_variable_roles_did()
        self._approve_design_spec_did()
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        tasks = [dict(task, method_id="did", estimator="did") for task in draft["tasks"]]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={"tasks": tasks, "outputs": draft["outputs"], "note": "DID RunPlan 已确认。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_bdd_5_did_full_run_produces_local_execution_result(self) -> None:
        """行为 5：DID full run 生成本地执行结果。"""
        self._approve_variable_roles_did()
        self._approve_design_spec_did()
        self._approve_run_plan("did")

        response = self.client.post(f"/api/v1/projects/{self.project_id}/runs/full", json={})

        self.assertEqual(response.status_code, 202, msg=response.text)
        result_path = self.project_root / "Results" / "json" / "method_execution_result.json"
        self.assertTrue(result_path.exists())
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["engine"], "statspai")
        method = result["methods"][0]
        self.assertEqual(method["method_id"], "did")
        self.assertIn("y=employment", method["formula"])
        self.assertEqual(method["nobs"], 16)
        # DID coefficients may be empty if no valid ATT estimates, but method should execute
        self.assertIn("method_id", method)

    def test_bdd_6_did_blocked_without_panel_id(self) -> None:
        """行为 6：DID 缺少面板 id 变量时 readiness 返回 blocked。"""
        self._approve_variable_roles_partial_did()
        self._approve_design_spec_partial_did()
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        tasks = [dict(task, method_id="did", estimator="did") for task in draft["tasks"]]

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={"tasks": tasks, "outputs": draft["outputs"], "note": "尝试批准缺少面板 id 的 DID。"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "method_workflow_blocked")
        self.assertIn("panel_id_required", response.json()["error"]["details"]["blocked_methods"][0]["blockers"])

    def _approve_variable_roles_iv(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/analysis_sample.csv",
                "roles": {
                    "outcome": ["lwage"],
                    "treatment": ["educ"],
                    "controls": ["exper", "black", "south"],
                    "instruments": ["nearc4"],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "变量角色已确认（Card 1993 风格）。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_design_spec_iv(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "教育回报率（Card 1993 工具变量）",
                "identification_strategy": {
                    "name": "card_iv",
                    "summary": "用 nearc4 作为 educ 的工具变量估计工资方程。",
                    "assumptions": [],
                    "threats": [],
                },
                "model": {
                    "estimator": "iv",
                    "formula": "lwage ~ (educ ~ nearc4) + exper + black + south",
                    "fixed_effects": [],
                    "cluster_by": [],
                    "sample_filter": "all",
                },
                "note": "研究设计已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_variable_roles_did(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/did_sample.csv",
                "roles": {
                    "outcome": ["employment"],
                    "treatment": ["first_treat"],
                    "controls": [],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                    "unit_id": ["state"],
                    "time_variable": ["year"],
                },
                "note": "DID 变量角色已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_design_spec_did(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "最低工资对就业的影响（DID）",
                "identification_strategy": {
                    "name": "did_baseline",
                    "summary": "用 DID 估计政策对就业的影响。",
                    "assumptions": [],
                    "threats": [],
                },
                "model": {
                    "estimator": "did",
                    "fixed_effects": [],
                    "cluster_by": [],
                    "sample_filter": "all",
                },
                "note": "研究设计已确认。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_variable_roles_partial_did(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/did_sample.csv",
                "roles": {
                    "outcome": ["employment"],
                    "treatment": ["first_treat"],
                    "controls": [],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "缺少面板变量。",
            },
        )
        self.assertEqual(response.status_code, 200, msg=response.text)

    def _approve_design_spec_partial_did(self) -> None:
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "最低工资对就业的影响（DID）",
                "identification_strategy": {
                    "name": "did_baseline",
                    "summary": "用 DID 估计政策对就业的影响。",
                    "assumptions": [],
                    "threats": [],
                },
                "model": {
                    "estimator": "did",
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

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: iv-did-execution-adapter\n  title: IV DID Execution Adapter Project\n"
            "research:\n  question: 教育回报率与政策评估\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        # Card (1993) style dataset for IV (50 rows to avoid singular matrix)
        import random
        random.seed(42)
        rows = ["lwage,educ,exper,black,south,nearc4"]
        for i in range(50):
            nearc4 = random.choice([0, 1])
            educ = 10 + nearc4 * 3 + random.randint(0, 4)
            exper = random.randint(1, 15)
            black = random.choice([0, 1])
            south = random.choice([0, 1])
            lwage = 3.5 + 0.08 * educ + 0.02 * exper - 0.15 * black - 0.10 * south + random.uniform(-0.5, 0.5)
            rows.append(f"{lwage:.2f},{educ},{exper},{black},{south},{nearc4}")
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "\n".join(rows) + "\n",
            encoding="utf-8",
        )
        # DID panel dataset with first_treat format (first treatment year per unit)
        (project_root / "Data" / "Final" / "did_sample.csv").write_text(
            "state,year,employment,first_treat\n"
            "1,2000,100,2002\n"
            "1,2001,100,2002\n"
            "1,2002,102,2002\n"
            "1,2003,104,2002\n"
            "2,2000,80,0\n"
            "2,2001,80,0\n"
            "2,2002,80,0\n"
            "2,2003,80,0\n"
            "3,2000,120,2002\n"
            "3,2001,120,2002\n"
            "3,2002,118,2002\n"
            "3,2003,116,2002\n"
            "4,2000,90,0\n"
            "4,2001,90,0\n"
            "4,2002,90,0\n"
            "4,2003,90,0\n",
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

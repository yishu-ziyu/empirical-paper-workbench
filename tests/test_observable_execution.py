import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")
SCRIPT_PATH = REPO_ROOT / "Program" / "run_paper.py"


class ObservableExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="observable-execution-"))
        self.project_dir = self.temp_dir / "project"
        self._copy_minimal_project(self.project_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_run_paper_writes_observable_manifest_steps_events_and_gates(self) -> None:
        """行为 1：一次研究执行必须留下可被 UI 观察的运行清单、阶段状态、事件流和 HITL gate。"""
        run_id = "run_observable_contract"

        result = subprocess.run(
            [
                "python3",
                str(SCRIPT_PATH),
                "--project-root",
                str(self.project_dir),
                "--dry-run",
                "--run-id",
                run_id,
            ],
            cwd=self.project_dir,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)

        observable_root = self.project_dir / "state" / "runs" / run_id
        manifest = self._read_json(observable_root / "run_manifest.json")
        steps = self._read_json(observable_root / "run_steps.json")
        gates = self._read_json(observable_root / "gates.json")
        events = self._read_events(observable_root / "run_events.jsonl")

        self.assertEqual(manifest["run_id"], run_id)
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(manifest["mode"], "dry-run")
        self.assertEqual(manifest["_meta"]["evidence_level"], "local_execution")
        self.assertIn("human_in_loop", manifest)
        self.assertGreaterEqual(manifest["human_in_loop"]["open_gate_count"], 1)

        step_ids = {step["id"] for step in steps["items"]}
        self.assertTrue(
            {
                "config_load",
                "dataset_intake",
                "topic_confirmation",
                "analysis_execution",
                "draft_generation",
                "state_index",
                "finalization",
            }.issubset(step_ids),
            msg=steps,
        )
        self.assertTrue(all(step["status"] in {"completed", "skipped"} for step in steps["items"]), msg=steps)

        self.assertGreaterEqual(len(events), 8)
        self.assertEqual(events[0]["type"], "run_started")
        self.assertEqual(events[-1]["type"], "run_succeeded")
        self.assertTrue(any(event["type"] == "hitl_gate_opened" for event in events), msg=events)
        self.assertTrue(any(event["type"] == "artifact_written" for event in events), msg=events)

        self.assertGreaterEqual(len(gates["items"]), 1)
        first_gate = gates["items"][0]
        self.assertEqual(first_gate["status"], "open")
        self.assertIn("required_by", first_gate)
        self.assertIn("options", first_gate)

    def test_bdd_2_product_api_exposes_run_observability_for_frontend_polling(self) -> None:
        """行为 2：前端必须能通过 API 读取某次运行的清单、阶段、事件和待用户介入点。"""
        original_product_root = product_app.PRODUCT_ROOT
        original_repo_root = product_app.REPO_ROOT
        product_root = self.temp_dir / "repo" / "Product"
        repo_root = self.temp_dir / "repo"
        product_root.mkdir(parents=True)
        ensure_registry(product_root, repo_root)
        product_app.PRODUCT_ROOT = product_root
        product_app.REPO_ROOT = repo_root
        client = TestClient(product_app.app)

        try:
            response = client.post(
                "/api/v1/projects",
                json={
                    "slug": "observable-project",
                    "title": "Observable Project",
                    "project_root": str(self.project_dir),
                    "language": "zh",
                },
            )
            self.assertEqual(response.status_code, 201, msg=response.text)
            project_id = response.json()["id"]

            response = client.post(f"/api/v1/projects/{project_id}/runs", json={"mode": "dry-run"})
            self.assertEqual(response.status_code, 202, msg=response.text)
            run_id = response.json()["id"]

            response = client.get(f"/api/v1/projects/{project_id}/runs/{run_id}/observability")
            self.assertEqual(response.status_code, 200, msg=response.text)
            body = response.json()
            self.assertEqual(body["manifest"]["run_id"], run_id)
            self.assertGreaterEqual(len(body["steps"]["items"]), 1)
            self.assertGreaterEqual(len(body["events"]["items"]), 1)
            self.assertGreaterEqual(len(body["gates"]["items"]), 1)

            response = client.get(f"/api/v1/projects/{project_id}/runs/{run_id}/events")
            self.assertEqual(response.status_code, 200, msg=response.text)
            event_body = response.json()
            self.assertEqual(event_body["_meta"]["evidence_level"], "local_execution")
            self.assertEqual(event_body["run_id"], run_id)
            self.assertTrue(any(event["type"] == "run_succeeded" for event in event_body["items"]))
        finally:
            product_app.PRODUCT_ROOT = original_product_root
            product_app.REPO_ROOT = original_repo_root

    def test_bdd_3_observability_exposes_dataset_source_as_run_evidence(self) -> None:
        """行为 3：observability API 必须把本次 run 的数据来源作为一等证据暴露给前端。"""
        original_product_root = product_app.PRODUCT_ROOT
        original_repo_root = product_app.REPO_ROOT
        product_root = self.temp_dir / "repo" / "Product"
        repo_root = self.temp_dir / "repo"
        product_root.mkdir(parents=True)
        ensure_registry(product_root, repo_root)
        product_app.PRODUCT_ROOT = product_root
        product_app.REPO_ROOT = repo_root
        client = TestClient(product_app.app)

        try:
            response = client.post(
                "/api/v1/projects",
                json={
                    "slug": "observable-dataset-source-project",
                    "title": "Observable Dataset Source Project",
                    "project_root": str(self.project_dir),
                    "language": "zh",
                },
            )
            self.assertEqual(response.status_code, 201, msg=response.text)
            project_id = response.json()["id"]

            response = client.post(
                f"/api/v1/projects/{project_id}/runs",
                json={"mode": "dry-run", "dataset_path": "Data/Final/analysis_sample.csv"},
            )
            self.assertEqual(response.status_code, 202, msg=response.text)
            run_id = response.json()["id"]

            response = client.get(f"/api/v1/projects/{project_id}/runs/{run_id}/observability")
            self.assertEqual(response.status_code, 200, msg=response.text)
            observability = response.json()

            self.assertIn("dataset_source", observability)
            self.assertEqual(observability["dataset_source"], observability["manifest"]["dataset_source"])
            self.assertEqual(observability["dataset_source"]["path"], "Data/Final/analysis_sample.csv")
            self.assertEqual(observability["dataset_source"]["evidence_level"], "local_file")
            self.assertEqual(observability["dataset_source"]["row_count"], 12)
            self.assertEqual(observability["dataset_source"]["column_count"], 4)
        finally:
            product_app.PRODUCT_ROOT = original_product_root
            product_app.REPO_ROOT = original_repo_root

    def test_bdd_4_gate_resolve_api_updates_gate_event_and_manifest(self) -> None:
        """行为 4：HITL gate resolve 必须写回 gates、追加事件并更新 manifest。"""
        original_product_root = product_app.PRODUCT_ROOT
        original_repo_root = product_app.REPO_ROOT
        product_root = self.temp_dir / "repo" / "Product"
        repo_root = self.temp_dir / "repo"
        product_root.mkdir(parents=True)
        ensure_registry(product_root, repo_root)
        product_app.PRODUCT_ROOT = product_root
        product_app.REPO_ROOT = repo_root
        client = TestClient(product_app.app)

        try:
            response = client.post(
                "/api/v1/projects",
                json={
                    "slug": "gate-resolve-project",
                    "title": "Gate Resolve Project",
                    "project_root": str(self.project_dir),
                    "language": "zh",
                },
            )
            self.assertEqual(response.status_code, 201, msg=response.text)
            project_id = response.json()["id"]

            response = client.post(f"/api/v1/projects/{project_id}/runs", json={"mode": "dry-run"})
            self.assertEqual(response.status_code, 202, msg=response.text)
            run_id = response.json()["id"]

            response = client.get(f"/api/v1/projects/{project_id}/runs/{run_id}/observability")
            self.assertEqual(response.status_code, 200, msg=response.text)
            gate = response.json()["gates"]["items"][0]
            gate_id = gate["id"]
            original_event_count = len(response.json()["events"]["items"])

            response = client.post(
                f"/api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve",
                json={"action": "confirm", "note": "变量识别已人工确认"},
            )
            self.assertEqual(response.status_code, 200, msg=response.text)
            body = response.json()
            self.assertEqual(body["_meta"]["evidence_level"], "local_execution")
            self.assertEqual(body["gate"]["status"], "resolved")
            self.assertEqual(body["gate"]["resolution"]["action"], "confirm")
            self.assertEqual(body["gate"]["resolution"]["note"], "变量识别已人工确认")
            self.assertIsNotNone(body["gate"]["resolved_at"])

            response = client.get(f"/api/v1/projects/{project_id}/runs/{run_id}/observability")
            self.assertEqual(response.status_code, 200, msg=response.text)
            observability = response.json()
            resolved_gate = next(item for item in observability["gates"]["items"] if item["id"] == gate_id)
            self.assertEqual(resolved_gate["status"], "resolved")
            self.assertEqual(observability["manifest"]["human_in_loop"]["open_gate_count"], len(observability["gates"]["items"]) - 1)
            self.assertGreater(len(observability["events"]["items"]), original_event_count)
            self.assertEqual(observability["events"]["items"][-1]["type"], "hitl_gate_resolved")
            self.assertEqual(observability["events"]["items"][-1]["evidence_level"], "local_execution")

            response = client.post(
                f"/api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve",
                json={"action": "delete", "note": "非法动作"},
            )
            self.assertEqual(response.status_code, 400, msg=response.text)
            self.assertEqual(response.json()["error"]["code"], "invalid_gate_action")
        finally:
            product_app.PRODUCT_ROOT = original_product_root
            product_app.REPO_ROOT = original_repo_root

    def test_bdd_5_observability_exposes_variable_roles_and_confirmation_gate(self) -> None:
        """行为 5：observability API 必须把变量角色和字段确认 gate 作为一等执行证据暴露。"""
        original_product_root = product_app.PRODUCT_ROOT
        original_repo_root = product_app.REPO_ROOT
        product_root = self.temp_dir / "repo" / "Product"
        repo_root = self.temp_dir / "repo"
        product_root.mkdir(parents=True)
        ensure_registry(product_root, repo_root)
        product_app.PRODUCT_ROOT = product_root
        product_app.REPO_ROOT = repo_root
        client = TestClient(product_app.app)

        try:
            response = client.post(
                "/api/v1/projects",
                json={
                    "slug": "observable-variable-roles-project",
                    "title": "Observable Variable Roles Project",
                    "project_root": str(self.project_dir),
                    "language": "zh",
                },
            )
            self.assertEqual(response.status_code, 201, msg=response.text)
            project_id = response.json()["id"]

            response = client.post(
                f"/api/v1/projects/{project_id}/runs",
                json={"mode": "dry-run", "dataset_path": "Data/Final/analysis_sample.csv"},
            )
            self.assertEqual(response.status_code, 202, msg=response.text)
            run_id = response.json()["id"]

            response = client.get(f"/api/v1/projects/{project_id}/runs/{run_id}/observability")
            self.assertEqual(response.status_code, 200, msg=response.text)
            variable_roles = response.json()["variable_roles"]

            self.assertEqual(variable_roles["evidence_level"], "local_execution")
            self.assertEqual(variable_roles["source_step_id"], "dataset_intake")
            self.assertEqual(variable_roles["confirmation_gate_id"], "gate_dataset_fields")
            self.assertEqual(variable_roles["confirmation_status"], "open")
            self.assertEqual(variable_roles["roles"]["outcome"], ["wage"])
            self.assertEqual(variable_roles["roles"]["treatment"], ["trained"])
            self.assertEqual(variable_roles["roles"]["controls"], ["edu", "experience"])
            self.assertEqual(variable_roles["roles"]["instruments"], [])
        finally:
            product_app.PRODUCT_ROOT = original_product_root
            product_app.REPO_ROOT = original_repo_root

    def test_bdd_6_observability_exposes_method_execution_as_run_evidence(self) -> None:
        """行为 6：observability API 必须把方法执行结果作为一等执行证据暴露。"""
        original_product_root = product_app.PRODUCT_ROOT
        original_repo_root = product_app.REPO_ROOT
        product_root = self.temp_dir / "repo" / "Product"
        repo_root = self.temp_dir / "repo"
        product_root.mkdir(parents=True)
        ensure_registry(product_root, repo_root)
        product_app.PRODUCT_ROOT = product_root
        product_app.REPO_ROOT = repo_root
        client = TestClient(product_app.app)

        try:
            response = client.post(
                "/api/v1/projects",
                json={
                    "slug": "observable-method-execution-project",
                    "title": "Observable Method Execution Project",
                    "project_root": str(self.project_dir),
                    "language": "zh",
                },
            )
            self.assertEqual(response.status_code, 201, msg=response.text)
            project_id = response.json()["id"]

            response = client.post(
                f"/api/v1/projects/{project_id}/runs",
                json={"mode": "dry-run", "dataset_path": "Data/Final/analysis_sample.csv"},
            )
            self.assertEqual(response.status_code, 202, msg=response.text)
            run_id = response.json()["id"]

            method_execution = {
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
                        "treatment_coefficient": 1.8505076803,
                        "evidence_level": "local_execution",
                    }
                ],
            }
            run_root = self.project_dir / "state" / "runs" / run_id
            manifest_path = run_root / "run_manifest.json"
            manifest = self._read_json(manifest_path)
            manifest["method_execution"] = method_execution
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            result_path = self.project_dir / "Results" / "json" / "method_execution_result.json"
            result_path.parent.mkdir(parents=True, exist_ok=True)
            result_path.write_text(json.dumps({"run_id": run_id, **method_execution}), encoding="utf-8")

            response = client.get(f"/api/v1/projects/{project_id}/runs/{run_id}/observability")
            self.assertEqual(response.status_code, 200, msg=response.text)
            method = response.json()["method_execution"]

            self.assertEqual(method["evidence_level"], "local_execution")
            self.assertEqual(method["engine"], "python_ols_adapter")
            self.assertEqual(method["artifact_path"], "Results/json/method_execution_result.json")
            self.assertEqual(method["methods"][0]["method_id"], "ols")
            self.assertEqual(method["methods"][0]["formula"], "wage ~ trained + edu + experience")
            self.assertEqual(method["methods"][0]["nobs"], 12)
            self.assertAlmostEqual(method["methods"][0]["treatment_coefficient"], 1.8505076803, places=8)
        finally:
            product_app.PRODUCT_ROOT = original_product_root
            product_app.REPO_ROOT = original_repo_root

    @staticmethod
    def _copy_minimal_project(target: Path) -> None:
        target.mkdir(parents=True)
        shutil.copytree(REPO_ROOT / "Program", target / "Program", dirs_exist_ok=True)
        shutil.copytree(REPO_ROOT / "Manuscripts" / "templates", target / "Manuscripts" / "templates", dirs_exist_ok=True)
        shutil.copy2(REPO_ROOT / "paper.yaml", target / "paper.yaml")
        (target / "Data" / "Final").mkdir(parents=True)
        shutil.copy2(REPO_ROOT / "Data" / "Final" / "analysis_sample.csv", target / "Data" / "Final" / "analysis_sample.csv")

    @staticmethod
    def _read_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _read_events(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()

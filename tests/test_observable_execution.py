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

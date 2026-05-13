import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from Product.app import app


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")


class ProductV1LocalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="product-v1-local-"))
        self.project_dir = self.temp_dir / "project"
        shutil.copytree(REPO_ROOT, self.project_dir, dirs_exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_health_and_project_registration_and_run_flow(self) -> None:
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

        payload = {
            "slug": "v1-local-project",
            "title": "V1 Local Project",
            "project_root": str(self.project_dir),
            "language": "zh",
        }
        response = self.client.post("/api/v1/projects", json=payload)
        self.assertEqual(response.status_code, 201, msg=response.text)
        project = response.json()
        project_id = project["id"]

        response = self.client.post(f"/api/v1/projects/{project_id}/runs", json={"mode": "dry-run"})
        self.assertEqual(response.status_code, 202, msg=response.text)
        run = response.json()
        self.assertEqual(run["status"], "succeeded")
        self.assertEqual(run["mode"], "dry-run")
        self.assertIn("Results/index.json", run["artifact_paths"])

        response = self.client.get(f"/api/v1/projects/{project_id}/runs/{run['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], run["id"])

        response = self.client.get(f"/api/v1/projects/{project_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("paper", response.json())

    def test_run_endpoint_records_selected_dataset_source(self) -> None:
        payload = {
            "slug": "v1-dataset-run-project",
            "title": "V1 Dataset Run Project",
            "project_root": str(self.project_dir),
            "language": "zh",
        }
        response = self.client.post("/api/v1/projects", json=payload)
        self.assertEqual(response.status_code, 201, msg=response.text)
        project_id = response.json()["id"]

        response = self.client.post(
            f"/api/v1/projects/{project_id}/runs",
            json={"mode": "dry-run", "dataset_path": "Data/Final/analysis_sample.csv"},
        )
        self.assertEqual(response.status_code, 202, msg=response.text)
        run = response.json()
        self.assertEqual(run["dataset_source"]["path"], "Data/Final/analysis_sample.csv")
        self.assertEqual(run["dataset_source"]["evidence_level"], "local_file")
        self.assertTrue(run["dataset_source"]["exists"])

        manifest_path = self.project_dir / "state" / "runs" / run["id"] / "run_manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["dataset_source"]["path"], "Data/Final/analysis_sample.csv")
        self.assertEqual(manifest["dataset_source"]["evidence_level"], "local_file")

    def test_run_endpoint_rejects_invalid_dataset_source(self) -> None:
        payload = {
            "slug": "v1-invalid-dataset-project",
            "title": "V1 Invalid Dataset Project",
            "project_root": str(self.project_dir),
            "language": "zh",
        }
        response = self.client.post("/api/v1/projects", json=payload)
        self.assertEqual(response.status_code, 201, msg=response.text)
        project_id = response.json()["id"]

        response = self.client.post(
            f"/api/v1/projects/{project_id}/runs",
            json={"mode": "dry-run", "dataset_path": "../outside.csv"},
        )
        self.assertEqual(response.status_code, 400, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "invalid_dataset_path")

        response = self.client.post(
            f"/api/v1/projects/{project_id}/runs",
            json={"mode": "dry-run", "dataset_path": "Data/Final/missing.csv"},
        )
        self.assertEqual(response.status_code, 400, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "dataset_not_found")

    def test_orchestrate_and_export_v1_endpoints(self) -> None:
        payload = {
            "slug": "v1-orchestrate-project",
            "title": "V1 Orchestrate Project",
            "project_root": str(self.project_dir),
            "language": "zh",
        }
        project = self.client.post("/api/v1/projects", json=payload).json()
        project_id = project["id"]

        response = self.client.post(f"/api/v1/projects/{project_id}/orchestrate?mode=dry-run")
        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(
            [agent["name"] for agent in body["orchestration"]["manifest"]["agents"]],
            [
                "PreparationAgent",
                "LiteratureAgent",
                "ResearchStrategistAgent",
                "ModelingAgent",
                "VisualizationAgent",
                "WritingAgent",
                "ReviewerAgent",
                "FormatterAgent",
            ],
        )

        response = self.client.post(f"/api/v1/projects/{project_id}/export")
        self.assertEqual(response.status_code, 200, msg=response.text)
        export_body = response.json()
        self.assertEqual(export_body["execution"]["returncode"], 0)
        self.assertTrue(export_body["snapshot"]["artifacts"]["docx"])

    def test_workbench_run_endpoint_creates_observable_run_folder(self) -> None:
        payload = {
            "slug": "v1-workbench-project",
            "title": "V1 Workbench Project",
            "project_root": str(self.project_dir),
            "language": "zh",
        }
        project = self.client.post("/api/v1/projects", json=payload).json()
        project_id = project["id"]

        response = self.client.post(
            f"/api/v1/projects/{project_id}/workbench-runs",
            json={"mode": "dry-run", "user_goal": "体验Codex内部CoPaper流程"},
        )
        self.assertEqual(response.status_code, 202, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "completed")
        self.assertTrue(body["run_root"].endswith(body["run_id"]))

        response = self.client.get(f"/api/v1/projects/{project_id}/workbench-runs/{body['run_id']}")
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(response.json()["run_id"], body["run_id"])


if __name__ == "__main__":
    unittest.main()

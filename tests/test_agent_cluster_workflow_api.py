import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class AgentClusterWorkflowApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="agent-cluster-api-"))
        self.repo_root = self.temp_dir / "repo"
        self.product_root = self.repo_root / "Product"
        self.product_root.mkdir(parents=True)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_workflow_lifecycle_generates_tasks_artifacts_and_report(self) -> None:
        response = self.client.post(
            "/api/v1/workflows",
            json={"title": "工业机器人影响劳动力市场匹配效率"},
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        created = response.json()
        workflow = created["workflow"]
        workflow_id = workflow["id"]
        self.assertEqual(workflow["status"], "queued")
        self.assertEqual(workflow["execution_provider"], "local_codex")
        self.assertEqual(workflow["provider_status"]["provider"], "local_codex")
        self.assertEqual(len(created["tasks"]), 10)
        self.assertEqual(created["tasks"][0]["agent_name"], "ResearchIntentAgent")
        self.assertEqual(created["tasks"][-1]["agent_name"], "ExportAgent")
        self.assertEqual(created["artifacts"], [])

        response = self.client.post(f"/api/v1/workflows/{workflow_id}/start")
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(response.json()["workflow"]["status"], "running")

        bundle = {}
        for _ in range(4):
            response = self.client.get(f"/api/v1/workflows/{workflow_id}")
            self.assertEqual(response.status_code, 200, msg=response.text)
            bundle = response.json()
            if bundle["workflow"]["status"] == "completed":
                break

        self.assertEqual(bundle["workflow"]["status"], "completed")
        self.assertEqual(len(bundle["tasks"]), 10)
        self.assertTrue(all(task["status"] == "completed" for task in bundle["tasks"]))
        self.assertEqual(
            [task["agent_name"] for task in bundle["tasks"]],
            [
                "ResearchIntentAgent",
                "LiteratureAgent",
                "DataAgent",
                "MethodAgent",
                "ExecutionAgent",
                "RobustnessAgent",
                "ManuscriptAgent",
                "ReviewerAgent",
                "ReplicationAgent",
                "ExportAgent",
            ],
        )
        self.assertEqual(len(bundle["artifacts"]), 10)

        task_id = bundle["tasks"][0]["id"]
        response = self.client.get(f"/api/v1/workflows/{workflow_id}/tasks/{task_id}")
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(response.json()["task"]["id"], task_id)

        artifact_id = bundle["artifacts"][0]["id"]
        response = self.client.get(f"/api/v1/artifacts/{artifact_id}")
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(response.json()["artifact"]["evidence_level"], "pipeline_contract")
        self.assertIn("Evidence level: pipeline_contract", response.json()["content"])

        response = self.client.get(f"/api/v1/workflows/{workflow_id}/report")
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertTrue(response.json()["path"].endswith("final_research_report.md"))
        self.assertIn("Paper Pipeline Contract", response.json()["content"])

        response = self.client.post(
            f"/api/v1/artifacts/{artifact_id}/promote",
            json={"target": "manuscripts"},
        )
        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "promotion_blocked")

    def test_local_codex_provider_status_endpoint(self) -> None:
        response = self.client.get("/api/v1/providers/local-codex")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["provider"], "local_codex")
        self.assertIn("available", body)
        self.assertIn("execution_enabled", body)

    def test_unknown_workflow_returns_structured_error(self) -> None:
        response = self.client.get("/api/v1/workflows/wf_missing")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "workflow_not_found")


if __name__ == "__main__":
    unittest.main()

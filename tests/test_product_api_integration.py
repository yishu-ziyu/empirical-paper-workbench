import json
import os
import shlex
import shutil
import subprocess
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from urllib import error, request


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")
BASE_URL = os.environ.get("PRODUCT_API_BASE_URL")
START_CMD = os.environ.get("PRODUCT_API_START_CMD")
STARTUP_TIMEOUT = float(os.environ.get("PRODUCT_API_STARTUP_TIMEOUT", "20"))
POLL_TIMEOUT = float(os.environ.get("PRODUCT_API_POLL_TIMEOUT", "30"))
POLL_INTERVAL = float(os.environ.get("PRODUCT_API_POLL_INTERVAL", "0.5"))
HEALTH_PATH = "/api/v1/health"


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def request_json(self, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"

        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers=headers,
        )
        try:
            with request.urlopen(req, timeout=5) as response:
                raw = response.read()
                return response.status, self._decode_json(raw)
        except error.HTTPError as exc:
            raw = exc.read()
            return exc.code, self._decode_json(raw)

    @staticmethod
    def _decode_json(raw: bytes) -> dict:
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))


class ManagedServer:
    def __init__(self, command: str | None) -> None:
        self.command = command
        self.process: subprocess.Popen[str] | None = None

    def start(self) -> None:
        if not self.command:
            return
        self.process = subprocess.Popen(
            shlex.split(self.command),
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def stop(self) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)


class ProductApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not BASE_URL:
            raise unittest.SkipTest("Set PRODUCT_API_BASE_URL to enable product API integration tests.")

        cls.client = ApiClient(BASE_URL)
        cls.server = ManagedServer(START_CMD)
        cls.server.start()
        cls._wait_for_health()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()

    @classmethod
    def _wait_for_health(cls) -> None:
        deadline = time.time() + STARTUP_TIMEOUT
        last_status = None
        last_payload = None
        while time.time() < deadline:
            try:
                status, payload = cls.client.request_json("GET", HEALTH_PATH)
            except error.URLError:
                time.sleep(POLL_INTERVAL)
                continue

            last_status = status
            last_payload = payload
            if status == 200 and payload.get("status") == "ok":
                return
            time.sleep(POLL_INTERVAL)

        raise AssertionError(
            f"Health check did not become ready within {STARTUP_TIMEOUT}s: "
            f"status={last_status}, payload={last_payload}"
        )

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="product-api-test-"))
        self.project_dir = self.temp_dir / "project"
        shutil.copytree(REPO_ROOT, self.project_dir, dirs_exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_health_endpoint_returns_ok(self) -> None:
        status, payload = self.client.request_json("GET", HEALTH_PATH)

        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertIn("service", payload)

    def test_project_round_trip_and_dry_run_execution(self) -> None:
        slug = f"api-contract-{uuid.uuid4().hex[:8]}"
        create_payload = {
            "slug": slug,
            "title": "API contract integration test project",
            "project_root": str(self.project_dir),
            "language": "zh",
        }

        status, project = self.client.request_json("POST", "/api/v1/projects", create_payload)
        self.assertEqual(status, 201, msg=project)
        project_id = project["id"]

        status, listed = self.client.request_json("GET", "/api/v1/projects")
        self.assertEqual(status, 200, msg=listed)
        self.assertIn(project_id, {item["id"] for item in listed["items"]})

        status, project_detail = self.client.request_json("GET", f"/api/v1/projects/{project_id}")
        self.assertEqual(status, 200, msg=project_detail)
        self.assertEqual(project_detail["slug"], slug)
        self.assertEqual(project_detail["project_root"], str(self.project_dir))

        status, run = self.client.request_json(
            "POST",
            f"/api/v1/projects/{project_id}/runs",
            {"mode": "dry-run"},
        )
        self.assertEqual(status, 202, msg=run)
        run_id = run["id"]

        final_run = self._poll_run(project_id, run_id)
        self.assertEqual(final_run["status"], "succeeded", msg=final_run)
        self.assertEqual(final_run["mode"], "dry-run")
        self.assertEqual(final_run["state"]["current_stage"], "question-definition")
        self.assertEqual(final_run["results"]["mode"], "dry-run")

        artifact_paths = set(final_run["artifact_paths"])
        self.assertTrue(
            {
                "state/project_state.json",
                "Results/index.json",
                "Results/json/project_snapshot.json",
                "Manuscripts/generated/paper_draft.md",
                "Manuscripts/generated/paper_draft.tex",
            }.issubset(artifact_paths),
            msg=final_run,
        )

        self.assertTrue((self.project_dir / "state" / "project_state.json").exists())
        self.assertTrue((self.project_dir / "Results" / "index.json").exists())

        status, run_list = self.client.request_json("GET", f"/api/v1/projects/{project_id}/runs")
        self.assertEqual(status, 200, msg=run_list)
        self.assertIn(run_id, {item["id"] for item in run_list["items"]})

    def test_unknown_project_returns_structured_404(self) -> None:
        status, payload = self.client.request_json("GET", "/api/v1/projects/proj_missing")

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["code"], "project_not_found")
        self.assertIn("message", payload["error"])

    def _poll_run(self, project_id: str, run_id: str) -> dict:
        deadline = time.time() + POLL_TIMEOUT
        last_payload = None
        while time.time() < deadline:
            status, payload = self.client.request_json(
                "GET",
                f"/api/v1/projects/{project_id}/runs/{run_id}",
            )
            self.assertEqual(status, 200, msg=payload)
            last_payload = payload
            if payload["status"] in {"succeeded", "failed"}:
                return payload
            time.sleep(POLL_INTERVAL)

        raise AssertionError(f"Run did not finish within {POLL_TIMEOUT}s: payload={last_payload}")


if __name__ == "__main__":
    unittest.main()

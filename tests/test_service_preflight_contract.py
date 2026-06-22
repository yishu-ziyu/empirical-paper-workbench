from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend import llm_client


ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_SRC = ROOT / "Product" / "web-react" / "src"


class ServicePreflightContractTests(unittest.TestCase):
    """BDD: 服务连接失败时，产品必须告诉用户真实卡点。"""

    def setUp(self) -> None:
        self.client = TestClient(product_app.app)
        self.previous_env = {
            key: os.environ.get(key)
            for key in (
                "EMPIRICAL_LLM_PROVIDER",
                "EMPIRICAL_LLM_MODEL",
                "OPENAI_API_KEY",
                "OPENAI_MODEL",
                "STEPFUN_API_KEY",
                "STEPFUN_MODEL",
                "MIMO_API_KEY",
                "MIMO_MODEL",
                "DEEPSEEK_API_KEY",
                "DEEPSEEK_MODEL",
                "MINIMAX_API_KEY",
                "MINIMAX_TOKEN_PLAN_KEY",
                "MINIMAX_MODEL",
                "OPENROUTER_API_KEY",
                "OPENROUTER_MODEL",
                "KIMI_CODE_API_KEY",
                "KIMI_CODE_MODEL",
                "ANTHROPIC_AUTH_TOKEN",
                "MOONSHOT_API_KEY",
                "MOONSHOT_MODEL",
                "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC",
                "CODEX_LOCAL_MODEL",
            )
        }
        for key in self.previous_env:
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key, value in self.previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_bdd_backend_preflight_reports_fastapi_service_and_llm_readiness(self) -> None:
        """行为 1：后端在线时，预检接口要同时报告服务和 LLM Supervisor 状态。"""
        os.environ["OPENAI_API_KEY"] = "test-openai"
        os.environ["OPENAI_MODEL"] = "gpt-5.5"

        with patch.object(llm_client, "load_local_env_if_present", return_value=None):
            response = self.client.get("/api/v1/service-preflight")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "ready")
        self.assertEqual(body["service"]["kind"], "fastapi")
        self.assertEqual(body["service"]["health_endpoint"], "/api/v1/health")
        self.assertTrue(body["llm_supervisor"]["ready"])
        self.assertEqual(body["llm_supervisor"]["provider_id"], "openai")
        self.assertEqual(body["llm_supervisor"]["model"], "gpt-5.5")
        self.assertIn("当前主模型", body["llm_supervisor"]["reason"])
        self.assertEqual(body["recommended_action"]["id"], "continue")

    def test_bdd_backend_preflight_reports_model_configuration_gate(self) -> None:
        """行为 2：服务在线但模型未接入时，预检要把问题定位到模型配置。"""
        with patch.object(llm_client, "load_local_env_if_present", return_value=None):
            response = self.client.get("/api/v1/service-preflight")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "needs_llm")
        self.assertEqual(body["service"]["kind"], "fastapi")
        self.assertFalse(body["llm_supervisor"]["ready"])
        self.assertEqual(body["recommended_action"]["id"], "configure_llm_supervisor")
        self.assertIn("LLM Supervisor", body["recommended_action"]["label"])

    def test_bdd_frontend_preflight_helper_classifies_wrong_port_static_service(self) -> None:
        """行为 3：前端连到静态服务或错误端口时，不能再只显示泛化失败。"""
        helper = (WEB_REACT_SRC / "lib" / "servicePreflight.ts").read_text(encoding="utf-8")
        system_status = (
            WEB_REACT_SRC / "components" / "SystemStatusBar.tsx"
        ).read_text(encoding="utf-8")
        recovery = (
            WEB_REACT_SRC / "components" / "ServiceConnectionRecovery.tsx"
        ).read_text(encoding="utf-8")

        for token in [
            "classifyServicePreflightFailure",
            "probeLocalServiceReachability",
            "backend_unreachable",
            "wrong_service",
            "cors_blocked",
            "llm_not_configured",
            "status === 501",
            "status === 405",
            "text/html",
            'mode: "no-cors"',
            "当前端口不是研究后端",
            "服务有响应，但浏览器预检失败",
            "后端在线，模型还没准备好",
        ]:
            self.assertIn(token, helper)

        self.assertIn("/api/v1/service-preflight", system_status)
        self.assertIn("servicePreflightMessage", system_status)
        self.assertIn("system-status-bar__error", system_status)
        self.assertIn("preflight", recovery)
        self.assertNotIn("状态暂时没连上，稍后会自动重试。不会影响已保存的研究材料。", system_status)

    def test_bdd_frontend_preflight_classifier_executes_runtime_branches(self) -> None:
        """行为 4：前端预检分类要可执行，覆盖断网、错端口、跨域和模型门。"""
        web_root = ROOT / "Product" / "web-react"
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = Path(temp_dir) / "servicePreflight.mjs"
            bundle = subprocess.run(
                [
                    "node_modules/.bin/esbuild",
                    "src/lib/servicePreflight.ts",
                    "--bundle",
                    "--format=esm",
                    f"--outfile={bundle_path}",
                ],
                cwd=web_root,
                check=True,
                text=True,
                capture_output=True,
            )
            self.assertEqual(bundle.returncode, 0, msg=bundle.stderr)

            probe = subprocess.run(
                [
                    "node",
                    "--input-type=module",
                    "-e",
                    f"""
                    import {{
                      classifyServicePreflightFailure,
                      servicePreflightMessage
                    }} from {str(bundle_path)!r};
                    const cases = [
                      classifyServicePreflightFailure({{}}),
                      classifyServicePreflightFailure({{ status: 501 }}),
                      classifyServicePreflightFailure({{ contentType: "text/html; charset=utf-8" }}),
                      classifyServicePreflightFailure({{ serviceRespondedWithoutCors: true }}),
                      servicePreflightMessage({{
                        status: "needs_llm",
                        llm_supervisor: {{ ready: false, reason: "missing model" }},
                        recommended_action: {{ hint: "configure model" }}
                      }})
                    ].map((item) => [item.kind, item.title]);
                    console.log(JSON.stringify(cases));
                    """,
                ],
                check=True,
                text=True,
                capture_output=True,
            )

        self.assertIn('"backend_unreachable"', probe.stdout)
        self.assertIn('"wrong_service"', probe.stdout)
        self.assertIn('"cors_blocked"', probe.stdout)
        self.assertIn('"llm_not_configured"', probe.stdout)


if __name__ == "__main__":
    unittest.main()

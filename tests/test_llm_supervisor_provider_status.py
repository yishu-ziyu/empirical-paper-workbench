from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend import llm_client


LLM_ENV_KEYS = (
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
    "MINIMAX_MODEL",
    "OPENROUTER_API_KEY",
    "OPENROUTER_MODEL",
)


class LlmSupervisorProviderStatusTests(unittest.TestCase):
    """BDD: Agent 产品必须在实验前暴露 LLM Supervisor 的真实可用性。"""

    def setUp(self) -> None:
        self.client = TestClient(product_app.app)
        self.previous_env = {key: os.environ.get(key) for key in LLM_ENV_KEYS}
        for key in LLM_ENV_KEYS:
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key, value in self.previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_bdd_llm_supervisor_status_lists_configured_gpt55_candidate(self) -> None:
        """行为 1：用户进入实验前，系统必须显示当前 LLM 候选模型与配置状态。"""
        os.environ["OPENAI_API_KEY"] = "test-openai"
        os.environ["OPENAI_MODEL"] = "gpt-5.5"

        with patch.object(llm_client, "load_local_env_if_present", return_value=None):
            response = self.client.get("/api/v1/providers/llm-supervisor")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertTrue(body["ready"])
        self.assertEqual(body["primary_provider"]["provider_id"], "openai")
        self.assertEqual(body["primary_provider"]["model"], "gpt-5.5")
        self.assertTrue(body["primary_provider"]["configured"])
        self.assertIn("LLM Supervisor", body["label"])
        self.assertIn("openai", [item["provider_id"] for item in body["attempts"]])

    def test_bdd_llm_supervisor_status_returns_recovery_action_without_config(self) -> None:
        """行为 2：没有可用模型配置时，系统不能假装可执行，必须给出恢复动作。"""
        with patch.object(llm_client, "load_local_env_if_present", return_value=None):
            response = self.client.get("/api/v1/providers/llm-supervisor")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertFalse(body["ready"])
        self.assertEqual(body["primary_provider"], {})
        self.assertEqual(body["primary_action"]["id"], "configure_llm_provider")
        self.assertIn("OPENAI_API_KEY", body["primary_action"]["hint"])

    def test_bdd_llm_supervisor_probe_uses_real_fallback_call_and_returns_model_metadata(self) -> None:
        """行为 3：用户需要确认真实连通时，探测接口必须触发一次 LLM 调用并回传模型元数据。"""
        os.environ["OPENAI_API_KEY"] = "test-openai"
        os.environ["OPENAI_MODEL"] = "gpt-5.5"
        with patch.object(
            llm_client,
            "chat_completion_with_fallback",
            return_value=(
                '{"status":"ok"}',
                {
                    "provider_id": "openai",
                    "provider_name": "OpenAI",
                    "model": "gpt-5.5",
                    "api_type": "openai-compatible",
                    "input_tokens": 12,
                    "output_tokens": 4,
                },
            ),
        ) as mocked_call:
            response = self.client.post("/api/v1/providers/llm-supervisor/probe")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["provider"]["provider_id"], "openai")
        self.assertEqual(body["provider"]["model"], "gpt-5.5")
        self.assertIn("LLM Supervisor", mocked_call.call_args.args[0][0]["content"])

    def test_bdd_llm_supervisor_probe_returns_actionable_error_when_call_fails(self) -> None:
        """行为 4：探测失败时不能只说服务没连上，要指出这是模型层不可用。"""
        with patch.object(
            llm_client,
            "chat_completion_with_fallback",
            side_effect=llm_client.LLMError("all_attempts_failed", "All providers failed."),
        ):
            response = self.client.post("/api/v1/providers/llm-supervisor/probe")

        self.assertEqual(response.status_code, 503, msg=response.text)
        body = response.json()
        self.assertEqual(body["error"]["code"], "llm_supervisor_unavailable")
        self.assertIn("LLM Supervisor", body["error"]["message"])


class LlmSupervisorProviderFrontendTests(unittest.TestCase):
    """BDD: 顶部状态栏必须把 LLM Supervisor 当成一等状态展示。"""

    def test_bdd_system_status_bar_declares_llm_supervisor_pill_and_probe_endpoint(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "Product"
            / "web-react"
            / "src"
            / "components"
            / "SystemStatusBar.tsx"
        ).read_text(encoding="utf-8")

        self.assertIn("/api/v1/providers/llm-supervisor", source)
        self.assertIn("LLM", source)
        self.assertIn("status-pill-llm", source)
        self.assertIn("status-pill-llm-model", source)
        self.assertIn("status-detail-llm", source)
        self.assertIn("备用链", source)


if __name__ == "__main__":
    unittest.main()

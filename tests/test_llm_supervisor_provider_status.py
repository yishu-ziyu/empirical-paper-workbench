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
    "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC",
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

    def test_bdd_llm_supervisor_status_lists_gpt55_as_selectable_choice_even_when_not_configured(self) -> None:
        """行为 3：GPT-5.5 没接上时，产品仍要显示它是可切换候选以及缺什么配置。"""
        os.environ["STEPFUN_API_KEY"] = "test-stepfun"
        os.environ["STEPFUN_MODEL"] = "step-3.7-flash"

        with patch.object(llm_client, "load_local_env_if_present", return_value=None):
            response = self.client.get("/api/v1/providers/llm-supervisor")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        openai_choice = next(item for item in body["model_choices"] if item["provider_id"] == "openai")
        self.assertEqual(openai_choice["provider_name"], "OpenAI")
        self.assertEqual(openai_choice["default_model"], "gpt-5.5")
        self.assertFalse(openai_choice["configured"])
        self.assertEqual(openai_choice["api_key_env"], "OPENAI_API_KEY")
        self.assertIn("EMPIRICAL_LLM_PROVIDER=openai", openai_choice["activation_hint"])
        self.assertEqual(body["selection"]["current_provider_id"], "stepfun")
        self.assertIn("切换", body["selection"]["change_hint"])

    def test_bdd_llm_supervisor_status_exposes_local_codex_cli_state(self) -> None:
        """行为 4：本地 Codex 不能只在后台存在，状态页要说明是否可作为本地执行型 Supervisor。"""
        with patch.object(llm_client, "load_local_env_if_present", return_value=None), patch(
            "Product.app.local_codex_status",
            return_value={
                "provider": "local_codex",
                "available": True,
                "path": "/opt/homebrew/bin/codex",
                "version": "codex-cli 0.137.0",
                "execution_enabled": False,
                "execution_env": "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC",
            },
        ):
            response = self.client.get("/api/v1/providers/llm-supervisor")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertTrue(body["local_codex"]["available"])
        self.assertFalse(body["local_codex"]["execution_enabled"])
        self.assertEqual(body["local_codex"]["execution_env"], "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC")
        self.assertIn("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1", body["local_codex"]["activation_hint"])

    def test_bdd_llm_supervisor_probe_uses_real_fallback_call_and_returns_model_metadata(self) -> None:
        """行为 5：用户需要确认真实连通时，探测接口必须触发一次 LLM 调用并回传模型元数据。"""
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
        """行为 6：探测失败时不能只说服务没连上，要指出这是模型层不可用。"""
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
        self.assertIn("可选模型", source)
        self.assertIn("本地 Codex", source)
        self.assertIn("model_choices", source)
        self.assertIn("local_codex", source)

    def test_bdd_system_status_bar_exposes_interactive_llm_probe(self) -> None:
        """行为 7：用户必须能在状态栏直接测试当前 LLM，而不是只看到一个接口路径。"""
        source = (
            Path(__file__).resolve().parents[1]
            / "Product"
            / "web-react"
            / "src"
            / "components"
            / "SystemStatusBar.tsx"
        ).read_text(encoding="utf-8")
        styles = (
            Path(__file__).resolve().parents[1]
            / "Product"
            / "web-react"
            / "src"
            / "styles.css"
        ).read_text(encoding="utf-8")

        self.assertIn("probeLlmSupervisor", source)
        self.assertIn("data-testid=\"status-detail-llm-probe\"", source)
        self.assertIn("测试当前 LLM", source)
        self.assertIn("正在测试", source)
        self.assertIn("测试通过", source)
        self.assertIn("测试失败", source)
        self.assertIn("system-status-bar__probe-result", styles)


if __name__ == "__main__":
    unittest.main()

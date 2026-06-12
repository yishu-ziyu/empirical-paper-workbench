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
    "CODEX_BIN",
    "CODEX_LOCAL_MODEL",
    "CODEX_LOCAL_PROJECT_ROOT",
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
                "auth_ready": True,
                "ready": True,
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

    def test_bdd_llm_supervisor_status_lists_codex_cli_as_local_gpt55_choice(self) -> None:
        """行为 7：Codex CLI 要作为本地 GPT-5.5 选择展示，并说明开启方式。"""
        with patch.object(llm_client, "load_local_env_if_present", return_value=None), patch(
            "Product.backend.llm_client.probe_codex_login",
            return_value={
                "ready": True,
                "available": True,
                "path": "/opt/homebrew/bin/codex",
                "auth_ready": True,
                "version": "codex-cli 0.139.0",
                "reason": "",
                "action": "",
            },
        ), patch(
            "Product.app.local_codex_status",
            return_value={
                "provider": "local_codex",
                "available": True,
                "path": "/opt/homebrew/bin/codex",
                "version": "codex-cli 0.139.0",
                "auth_ready": True,
                "ready": True,
                "execution_enabled": False,
                "execution_env": "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC",
            },
        ):
            response = self.client.get("/api/v1/providers/llm-supervisor")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        codex_choice = next(item for item in body["model_choices"] if item["provider_id"] == "codex-cli")
        self.assertEqual(codex_choice["provider_name"], "Codex CLI")
        self.assertEqual(codex_choice["default_model"], "gpt-5.5")
        self.assertFalse(codex_choice["configured"])
        self.assertIn("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1", codex_choice["activation_hint"])
        self.assertIn("EMPIRICAL_LLM_PROVIDER=codex-cli", codex_choice["activation_hint"])

    def test_bdd_llm_supervisor_status_blocks_codex_cli_when_login_is_missing(self) -> None:
        """行为 7a：本机装了 Codex 但未登录时，产品必须提示 codex login，而不是显示已配置。"""
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"

        with patch.object(llm_client, "load_local_env_if_present", return_value=None), patch(
            "Product.backend.llm_client.probe_codex_login",
            return_value={
                "ready": False,
                "available": True,
                "path": "/opt/homebrew/bin/codex",
                "auth_path": "/Users/test/.codex/auth.json",
                "auth_ready": False,
                "version": None,
                "reason": "codex CLI 尚未登录。",
                "action": "在终端运行 codex login，完成 OAuth 后重启本地服务。",
            },
        ), patch(
            "Product.app.local_codex_status",
            return_value={
                "provider": "local_codex",
                "available": True,
                "path": "/opt/homebrew/bin/codex",
                "auth_path": "/Users/test/.codex/auth.json",
                "auth_ready": False,
                "ready": False,
                "reason": "codex CLI 尚未登录。",
                "action": "在终端运行 codex login，完成 OAuth 后重启本地服务。",
                "execution_enabled": True,
                "execution_env": "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC",
            },
        ):
            response = self.client.get("/api/v1/providers/llm-supervisor")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        codex_choice = next(item for item in body["model_choices"] if item["provider_id"] == "codex-cli")
        self.assertFalse(codex_choice["configured"])
        self.assertFalse(body["local_codex"]["ready"])
        self.assertIn("codex login", body["local_codex"]["activation_hint"])

    def test_bdd_llm_supervisor_status_explains_why_codex_gpt55_is_selected(self) -> None:
        """行为 7b：当本地 Codex/GPT-5.5 被选中时，状态接口必须解释选择依据。"""
        os.environ["EMPIRICAL_LLM_PROVIDER"] = "codex-cli"
        os.environ["CODEX_LOCAL_MODEL"] = "gpt-5.5"
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"

        with patch.object(llm_client, "load_local_env_if_present", return_value=None), patch(
            "Product.backend.llm_client.probe_codex_login",
            return_value={
                "ready": True,
                "available": True,
                "path": "/opt/homebrew/bin/codex",
                "auth_ready": True,
                "version": "codex-cli 0.139.0",
                "reason": "",
                "action": "",
            },
        ):
            response = self.client.get("/api/v1/providers/llm-supervisor")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertTrue(body["ready"])
        self.assertEqual(body["primary_provider"]["provider_id"], "codex-cli")
        self.assertEqual(body["primary_provider"]["model"], "gpt-5.5")
        self.assertEqual(body["selection"]["source"], "env_preference")
        self.assertIn("EMPIRICAL_LLM_PROVIDER=codex-cli", body["selection"]["reason"])
        self.assertIn("GPT-5.5", body["selection"]["reason"])

    def test_bdd_codex_cli_provider_requires_execution_gate_before_fallback(self) -> None:
        """行为 8：本地 Codex 只有显式打开执行门后，才会进入 LLM fallback。"""
        os.environ["EMPIRICAL_LLM_PROVIDER"] = "codex-cli"
        os.environ["CODEX_LOCAL_MODEL"] = "gpt-5.5"

        with patch.object(llm_client, "load_local_env_if_present", return_value=None), patch(
            "Product.backend.llm_client.probe_codex_login",
            return_value={
                "ready": True,
                "available": True,
                "path": "/opt/homebrew/bin/codex",
                "auth_ready": True,
                "version": "codex-cli 0.139.0",
                "reason": "",
                "action": "",
            },
        ):
            attempts_without_gate = llm_client.build_default_llm_attempts()
            configured_without_gate = llm_client._provider_has_key("codex-cli", llm_client.resolve_provider("codex-cli"))
            os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"
            attempts_with_gate = llm_client.build_default_llm_attempts()
            configured_with_gate = llm_client._provider_has_key("codex-cli", llm_client.resolve_provider("codex-cli"))

        self.assertEqual(attempts_without_gate[0]["provider_id"], "codex-cli")
        self.assertEqual(attempts_without_gate[0]["env"], "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC")
        self.assertFalse(configured_without_gate)
        self.assertEqual(attempts_with_gate[0]["provider_id"], "codex-cli")
        self.assertEqual(attempts_with_gate[0]["model"], "gpt-5.5")
        self.assertTrue(configured_with_gate)

    def test_bdd_codex_cli_call_uses_read_only_ephemeral_exec_contract(self) -> None:
        """行为 9：真实调用 Codex CLI 时必须走只读、临时、无规则注入的受控命令。"""
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"
        os.environ["CODEX_LOCAL_PROJECT_ROOT"] = "/tmp/empirical-codex-project"

        class Completed:
            returncode = 0
            stdout = ""
            stderr = ""

        def fake_run(command, *, input, check, capture_output, text, timeout):
            output_path = command[command.index("--output-last-message") + 1]
            Path(output_path).write_text('{"status":"ok"}', encoding="utf-8")
            self.assertEqual(input.startswith("[user]"), True)
            return Completed()

        with patch.object(llm_client, "load_local_env_if_present", return_value=None), patch(
            "Product.backend.llm_client._codex_bin",
            return_value="/opt/homebrew/bin/codex",
        ), patch("Product.backend.llm_client.subprocess.run", side_effect=fake_run) as mocked_run:
            text, usage = llm_client.chat_completion(
                [{"role": "user", "content": "连通性测试"}],
                provider_id="codex-cli",
                model="gpt-5.5",
                temperature=0,
            )

        command = mocked_run.call_args.args[0]
        self.assertEqual(text, '{"status":"ok"}')
        self.assertIn("-a", command)
        self.assertIn("never", command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("--ephemeral", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn("--sandbox", command)
        self.assertIn("read-only", command)
        self.assertIn("--model", command)
        self.assertIn("gpt-5.5", command)
        self.assertGreater(usage["input_tokens"], 0)


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

    def test_bdd_system_status_bar_makes_current_llm_and_gpt55_state_directly_readable(self) -> None:
        """行为 8：状态栏展开后，用户必须一眼看见当前接入模型和 GPT-5.5 未启用原因。"""
        source = (
            Path(__file__).resolve().parents[1]
            / "Product"
            / "web-react"
            / "src"
            / "components"
            / "SystemStatusBar.tsx"
        ).read_text(encoding="utf-8")

        self.assertIn("status-detail-llm-current-provider", source)
        self.assertIn("status-detail-llm-openai-gpt55", source)
        self.assertIn("当前接入", source)
        self.assertIn("GPT-5.5 状态", source)
        self.assertIn("未启用", source)
        self.assertIn("OPENAI_API_KEY", source)


if __name__ == "__main__":
    unittest.main()

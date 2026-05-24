from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from Product.backend import llm_client
from Product.backend.orchestrator import _estimate_llm_cost, _resolve_project_id


class DualGapFixSpecTests(unittest.TestCase):
    def test_resolve_project_id_prefers_registry_id_for_chinese_title(self) -> None:
        """行为 A2：中文标题项目必须优先使用 registry id，避免 KeyError。"""
        profile = {
            "id": "proj_training_wage",
            "slug": "training-wage",
            "title": "培训是否影响工资",
        }

        self.assertEqual(_resolve_project_id(profile), "proj_training_wage")

    def test_openai_compatible_returns_text_and_usage(self) -> None:
        """行为 B1：OpenAI-compatible 响应必须返回文本和 token usage。"""
        parsed = {
            "choices": [{"message": {"content": "ok"}}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 7},
        }

        with patch.object(llm_client, "_read_response_json", return_value=parsed):
            text, usage = llm_client._call_openai_compatible(
                api_key="test",
                base_url="https://example.test/v1",
                model="test-model",
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.1,
                provider_name="test-provider",
            )

        self.assertEqual(text, "ok")
        self.assertEqual(usage, {"input_tokens": 12, "output_tokens": 7})

    def test_anthropic_compatible_returns_text_and_usage(self) -> None:
        """行为 B1：Anthropic-compatible 响应必须返回文本和 token usage。"""
        parsed = {
            "content": [{"type": "text", "text": "ok"}],
            "usage": {"input_tokens": 20, "output_tokens": 9},
        }

        with patch.object(llm_client, "_read_response_json", return_value=parsed):
            text, usage = llm_client._call_anthropic_compatible(
                api_key="test",
                base_url="https://example.test",
                model="test-model",
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.1,
                provider_name="test-provider",
            )

        self.assertEqual(text, "ok")
        self.assertEqual(usage, {"input_tokens": 20, "output_tokens": 9})

    def test_fallback_metadata_includes_token_usage(self) -> None:
        """行为 B1/B2：fallback metadata 必须携带 token usage 供 cost_service 使用。"""
        with patch.object(
            llm_client,
            "chat_completion",
            return_value=("ok", {"input_tokens": 31, "output_tokens": 13}),
        ):
            text, metadata = llm_client.chat_completion_with_fallback(
                [{"role": "user", "content": "hi"}],
                attempts=({"provider_id": "openrouter", "model": "openai/gpt-4o-mini"},),
            )

        self.assertEqual(text, "ok")
        self.assertEqual(metadata["input_tokens"], 31)
        self.assertEqual(metadata["output_tokens"], 13)

    def test_llm_cost_estimate_uses_input_and_output_tokens(self) -> None:
        """行为 B2：LLM 成本估算必须同时包含输入与输出 token。"""
        estimated = _estimate_llm_cost("openrouter", "openai/gpt-4o-mini", 1_000_000, 1_000_000)

        self.assertEqual(estimated, 0.75)

    def test_frontend_contains_journey_start_run_and_cost_token_ui(self) -> None:
        """行为 A1/B3：前端必须暴露 Journey 启动和成本 token 显示锚点。"""
        root = Path(__file__).resolve().parents[1]
        app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('data-journey-action="start-run"', app_js)
        self.assertIn("void createFullRunFromPlan();", app_js)
        self.assertIn("journeyPrimaryAction", app_js)
        self.assertIn("cost-tokens", app_js)
        self.assertIn("Provider / Model 汇总", app_js)
        self.assertIn(".cost-usd", styles_css)


if __name__ == "__main__":
    unittest.main()

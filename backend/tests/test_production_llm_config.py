"""Production startup uses the same role resolution as the research router.

Subprocesses have an empty HOME and only synthetic credentials. No provider
request is made, and a workstation's SSOT cannot make a broken case pass.
"""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ProductionLLMConfigTests(unittest.TestCase):
    def boot(self, overrides):
        with tempfile.TemporaryDirectory() as isolated:
            env = {
                "PATH": os.defpath,
                "HOME": isolated,
                "ECONPAPER_LOCAL_STATE_ROOT": isolated,
                "DEBUG": "false",
                "JWT_SECRET_KEY": "unit-test-only-jwt-secret-with-32-characters",
                **overrides,
            }
            result = subprocess.run(
                [sys.executable, "-c", "import backend.config"],
                cwd=ROOT, env=env, text=True, capture_output=True, timeout=10,
            )
        # Even failures must not print configuration values.
        self.assertNotIn("synthetic-api-credential", result.stdout + result.stderr)
        return result

    def assert_rejected(self, overrides, role=None):
        result = self.boot(overrides)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("FATAL:", result.stderr)
        if role:
            self.assertIn(role, result.stderr)

    def test_missing_config_and_openai_key_without_selected_provider(self):
        for env in ({}, {"OPENAI_API_KEY": "synthetic-api-credential"}):
            with self.subTest(keys=list(env)):
                self.assert_rejected(env)

    def test_reject_mock_unknown_and_case_mismatch_for_each_role(self):
        for role in ("GENERATE", "REVIEW"):
            for provider in ("mock", "unknown-provider", "OpenAI"):
                with self.subTest(role=role, provider=provider):
                    self.assert_rejected({
                        "MINIMAX_API_KEY": "synthetic-api-credential",
                        f"{role}_LLM_PROVIDER": provider,
                    }, role)

    def test_global_mock_is_rejected(self):
        self.assert_rejected({
            "ECONPAPER_LLM": "mock",
            "MINIMAX_API_KEY": "synthetic-api-credential",
        })

    def test_selected_provider_without_key_is_rejected(self):
        self.assert_rejected({
            "GENERATE_LLM_PROVIDER": "openai",
            "GENERATE_LLM_MODEL": "test-model",
        }, "GENERATE")

    def test_minimax_cannot_inherit_unrelated_openai_key(self):
        self.assert_rejected({
            "GENERATE_LLM_PROVIDER": "minimax",
            "OPENAI_API_KEY": "synthetic-api-credential",
        }, "GENERATE")

    def test_openai_requires_explicit_role_model(self):
        for model in ("", "default"):
            with self.subTest(model=model):
                self.assert_rejected({
                    "GENERATE_LLM_PROVIDER": "openai",
                    "GENERATE_LLM_MODEL": model,
                    "OPENAI_API_KEY": "synthetic-api-credential",
                }, "GENERATE")

    def test_each_role_is_checked_independently(self):
        self.assert_rejected({
            "GENERATE_LLM_PROVIDER": "openai",
            "GENERATE_LLM_MODEL": "test-model",
            "GENERATE_LLM_API_KEY": "synthetic-api-credential",
            "GENERATE_LLM_BASE_URL": "https://example.invalid/v1",
            "REVIEW_LLM_PROVIDER": "openai",
            "REVIEW_LLM_MODEL": "test-model",
        }, "REVIEW")

    def test_explicit_roles_and_minimax_defaults_are_accepted(self):
        explicit = {}
        for role in ("GENERATE", "REVIEW"):
            explicit.update({
                f"{role}_LLM_PROVIDER": "openai",
                f"{role}_LLM_MODEL": "test-model",
                f"{role}_LLM_API_KEY": "synthetic-api-credential",
                f"{role}_LLM_BASE_URL": "https://example.invalid/v1",
            })
        for env in (
            explicit,
            {"MINIMAX_API_KEY": "synthetic-api-credential"},
            {"MINIMAX_TOKEN_PLAN_KEY": "synthetic-api-credential"},
        ):
            with self.subTest(keys=list(env)):
                result = self.boot(env)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

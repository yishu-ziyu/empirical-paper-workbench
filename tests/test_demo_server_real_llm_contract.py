from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import demo_server
from Product.backend import llm_client
from Product.backend.wrapper import brief_stream_service


class DemoServerRealLlmContractTests(unittest.TestCase):
    """BDD: 本地验收服务必须走真实 LLM，不能用固定题目 fixture。"""

    def test_bdd_demo_server_does_not_patch_brief_stream_llm(self) -> None:
        """Given 启动验收服务, When 进入 brief stream, Then 默认调用真实 LLM 入口。"""
        self.assertIs(
            brief_stream_service.chat_completion_stream,
            llm_client.chat_completion_stream,
        )

    def test_bdd_demo_server_source_has_no_hardcoded_research_case(self) -> None:
        """Given 用户输入任意题目, Then demo server 不能内置上一题研究内容。"""
        source = Path(demo_server.__file__).read_text(encoding="utf-8")
        forbidden = [
            "工业机器人",
            "蓝领工资",
            "Bartik IV",
            "Acemoglu",
            "Restrepo",
            "CHUNKS_INITIAL",
            "_fake_stream",
            "LLM mocked",
        ]
        for term in forbidden:
            self.assertNotIn(term, source)

    def test_bdd_local_env_loader_sets_missing_values_without_overriding(self) -> None:
        """Given 本地私有配置, When 启动验收服务, Then 可读取模型配置且不覆盖已有环境。"""
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env.local"
            env_path.write_text(
                "\n".join(
                    [
                        "EXISTING_MODEL=from-file",
                        "NEW_MODEL=from-local-env",
                        "COMMENTED=value # trailing comment",
                    ]
                ),
                encoding="utf-8",
            )
            previous_existing = os.environ.get("EXISTING_MODEL")
            previous_new = os.environ.get("NEW_MODEL")
            previous_commented = os.environ.get("COMMENTED")
            os.environ["EXISTING_MODEL"] = "already-set"
            os.environ.pop("NEW_MODEL", None)
            os.environ.pop("COMMENTED", None)
            try:
                demo_server._load_local_env(env_path)
                self.assertEqual(os.environ["EXISTING_MODEL"], "already-set")
                self.assertEqual(os.environ["NEW_MODEL"], "from-local-env")
                self.assertEqual(os.environ["COMMENTED"], "value")
            finally:
                if previous_existing is None:
                    os.environ.pop("EXISTING_MODEL", None)
                else:
                    os.environ["EXISTING_MODEL"] = previous_existing
                if previous_new is None:
                    os.environ.pop("NEW_MODEL", None)
                else:
                    os.environ["NEW_MODEL"] = previous_new
                if previous_commented is None:
                    os.environ.pop("COMMENTED", None)
                else:
                    os.environ["COMMENTED"] = previous_commented


if __name__ == "__main__":
    unittest.main()

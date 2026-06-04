"""L3-variables: /api/variables 端到端 smoke 测试。

行为覆盖：
- 行为 1: POST /api/variables 返回 200 + 完整 VariablesResponse
- 行为 2: 落盘文件存在且含 frontmatter
- 行为 3: verdict_passed 在 mock LLM 输出合规时为 True
- 行为 4: variables 字段在响应中可被前端直接消费
- 行为 5: dataset_name='custom' 走兜底 stub 路径
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from Product.app import app


SAMPLE_VARIABLES_YAML = """\
variables:
  - role: X
    dataset_column: robot_density
    semantic_label: "工业机器人渗透率"
    description: "Bartik IV 来源"
    reference_papers: ["Acemoglu 2020"]
  - role: Y
    dataset_column: ln_wage
    semantic_label: "对数工资"
    description: "被解释变量"
    reference_papers: ["Acemoglu 2020"]
  - role: control
    dataset_column: age
    semantic_label: "年龄"
    description: "控制"
    reference_papers: []
"""


class VariablesEndpointSmokeTests(unittest.TestCase):
    """/api/variables 端到端 smoke 测试套件。"""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        # 写一个最小 brief.md（route 路径只读不验证内容，但保证存在）
        self.brief_path = self.tmp / "brief.md"
        self.brief_path.write_text(
            "## 研究问题\n工业机器人对就业结构的影响\n## 边际贡献\n1. 新数据\n## 研究边界\n1. 城市\n## 成功标准\np<0.05",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # ============== 行为 1: 端到端 200 + VariablesResponse ==============

    def test_bdd_endpoint_post_returns_200_with_full_response(self) -> None:
        """行为 1: POST /api/variables 返回 200 + 完整 VariablesResponse。"""
        with patch(
            "Product.backend.wrapper.variables_service.chat_completion",
            return_value=(SAMPLE_VARIABLES_YAML, {"input_tokens": 10, "output_tokens": 20}),
        ):
            resp = self.client.post(
                "/api/variables",
                json={
                    "topic_slug": "smoke-vars",
                    "brief_path": str(self.brief_path),
                    "dataset_name": "CFPS",
                },
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("variables_yaml", body)
        self.assertIn("variables_path", body)
        self.assertIn("variables", body)
        self.assertIn("verdict_passed", body)
        self.assertIsInstance(body["variables"], list)
        self.assertGreaterEqual(len(body["variables"]), 3)

    # ============== 行为 2: 落盘文件 + frontmatter ==============

    def test_bdd_endpoint_writes_yaml_with_provenance(self) -> None:
        """行为 2: 落盘文件存在且含 frontmatter (model + topic_slug)。"""
        slug = "smoke-vars-write"
        with patch(
            "Product.backend.wrapper.variables_service.chat_completion",
            return_value=(SAMPLE_VARIABLES_YAML, {"input_tokens": 10, "output_tokens": 20}),
        ):
            resp = self.client.post(
                "/api/variables",
                json={
                    "topic_slug": slug,
                    "brief_path": str(self.brief_path),
                    "dataset_name": "CFPS",
                },
            )
        body = resp.json()
        path = Path(body["variables_path"])
        self.assertTrue(path.exists())
        self.assertEqual(path.name, "variables.yaml")
        content = path.read_text(encoding="utf-8")
        # frontmatter 验证
        self.assertIn("---", content)
        self.assertIn("model: MiniMax-M3", content)
        self.assertIn(f"topic_slug: {slug}", content)
        # YAML body 验证
        self.assertIn("robot_density", content)
        self.assertIn("ln_wage", content)

    # ============== 行为 3: verdict gate ==============

    def test_bdd_endpoint_verdict_passed_when_valid(self) -> None:
        """行为 3: mock LLM 输出合规时 verdict_passed=True。"""
        with patch(
            "Product.backend.wrapper.variables_service.chat_completion",
            return_value=(SAMPLE_VARIABLES_YAML, {"input_tokens": 10, "output_tokens": 20}),
        ):
            resp = self.client.post(
                "/api/variables",
                json={
                    "topic_slug": "smoke-verdict",
                    "brief_path": str(self.brief_path),
                    "dataset_name": "CFPS",
                },
            )
        self.assertTrue(resp.json()["verdict_passed"])

    # ============== 行为 4: 角色 + 列名 ==============

    def test_bdd_endpoint_variables_have_role_and_column(self) -> None:
        """行为 4: 每条 variable 都有 role + dataset_column + semantic_label。"""
        with patch(
            "Product.backend.wrapper.variables_service.chat_completion",
            return_value=(SAMPLE_VARIABLES_YAML, {"input_tokens": 10, "output_tokens": 20}),
        ):
            resp = self.client.post(
                "/api/variables",
                json={
                    "topic_slug": "smoke-shape",
                    "brief_path": str(self.brief_path),
                    "dataset_name": "CFPS",
                },
            )
        variables = resp.json()["variables"]
        for v in variables:
            self.assertIn("role", v)
            self.assertIn("dataset_column", v)
            self.assertIn("semantic_label", v)
            self.assertIn("description", v)
            self.assertIn("reference_papers", v)
        roles = {v["role"] for v in variables}
        self.assertIn("X", roles)
        self.assertIn("Y", roles)
        self.assertIn("control", roles)

    # ============== 行为 5: custom 数据集 ==============

    def test_bdd_endpoint_custom_dataset_falls_back_to_stub(self) -> None:
        """行为 5: dataset_name='custom' 走兜底 stub 路径（无需 schema.yaml）。"""
        with patch(
            "Product.backend.wrapper.variables_service.chat_completion",
            return_value=(SAMPLE_VARIABLES_YAML, {"input_tokens": 10, "output_tokens": 20}),
        ):
            resp = self.client.post(
                "/api/variables",
                json={
                    "topic_slug": "smoke-custom",
                    "brief_path": str(self.brief_path),
                    "dataset_name": "custom",
                    "custom_dataset_path": None,
                },
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["verdict_passed"])


if __name__ == "__main__":
    unittest.main()

"""L4-design 端到端 wire-in 测试：POST /api/design 通过 FastAPI TestClient。

业务含义：验证 5-tab vertical slice 的 design tab 在 FastAPI 端到端可工作：
1. Route /api/design 在 Product.app.app 中注册
2. POST 返回 200 + DesignResponse 所有字段
3. 落盘的 design.json 包含 candidates + recommended + code_stub
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from Product.app import app


SAMPLE_LLM = json.dumps(
    {
        "candidates": [
            {"method": "DID", "rationale": "DID 可控城市固定效应", "fits_data": True},
            {"method": "IV", "rationale": "Bartik 工具变量缓解内生性", "fits_data": True},
            {"method": "PSM", "rationale": "高/低暴露组平衡协变量", "fits_data": True},
        ],
        "recommended": "IV",
    },
    ensure_ascii=False,
)


class DesignWireInTests(unittest.TestCase):
    """L4-design: /api/design 端到端 wire-in 测试。"""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self._tmp = tempfile.TemporaryDirectory()
        self.tasks_root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_bdd_design_route_is_registered(self) -> None:
        """行为 1: /api/design route 在 Product.app.app 中已注册。"""
        paths = {r.path for r in app.routes if hasattr(r, "path")}
        self.assertIn("/api/design", paths)

    def test_bdd_design_post_returns_200_and_full_response(self) -> None:
        """行为 2: POST /api/design → 200 + DesignResponse 含 6 个必需字段。"""
        var_path = self.tasks_root / "industrial-robots-employment" / "variables.yaml"
        var_path.parent.mkdir(parents=True, exist_ok=True)
        var_path.write_text(
            """
variables:
  - role: Y
    dataset_column: ln_wage
    semantic_label: 工资
    description: ""
    reference_papers: []
  - role: X
    dataset_column: robot_exposure
    semantic_label: 机器人
    description: ""
    reference_papers: []
  - role: control
    dataset_column: age
    semantic_label: 年龄
    description: ""
    reference_papers: []
""",
            encoding="utf-8",
        )

        with patch(
            "Product.api.design._TASKS_ROOT",
            self.tasks_root,
        ), patch(
            "Product.backend.wrapper.design_service.chat_completion",
            return_value=(SAMPLE_LLM, {"input_tokens": 50, "output_tokens": 100}),
        ):
            resp = self.client.post(
                "/api/design",
                json={
                    "topic_slug": "industrial-robots-employment",
                    "variables_path": str(var_path),
                    "brief_path": "Tasks/industrial-robots-employment/brief.md",
                },
            )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        # 6 个必需字段
        for field in [
            "design_json",
            "design_path",
            "candidates",
            "recommended",
            "code_stub",
            "verdict_passed",
        ]:
            self.assertIn(field, body, f"missing field: {field}")
        self.assertTrue(body["verdict_passed"])
        self.assertEqual(len(body["candidates"]), 3)
        self.assertEqual(body["recommended"], "IV")
        # 落盘验证
        self.assertTrue(Path(body["design_path"]).exists())
        design_path = Path(body["design_path"])
        self.assertEqual(design_path.name, "design.json")
        payload = json.loads(design_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["recommended"], "IV")
        self.assertIn("import", payload["code_stub"])


if __name__ == "__main__":
    unittest.main()

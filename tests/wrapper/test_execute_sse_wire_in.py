"""L5-execution wire-in smoke test: 端到端 SSE 消费。

行为：POST /api/execute → text/event-stream → 21 events
(start ×1, progress ×9, section_done ×9, paper_ready ×1, done ×1)

这个文件验证 /api/execute endpoint 真的能通过 FastAPI TestClient 流式返回。
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


def _mock_chat_completion(messages, **kwargs):  # noqa: ARG001
    """替代真实 LLM 调用，返回固定 markdown。"""

    return (
        "# Section content\n\nMock body.\n",
        {"input_tokens": 1, "output_tokens": 1},
    )


# 导入 app 但不修改 llm_client.chat_completion（避免污染其他 lane 的测试）
from Product.app import app  # noqa: E402


SAMPLE_BRIEF = """# 研究问题
工业机器人对就业的影响

# 边际贡献
x

# 研究边界
y

# 成功标准
z
"""

SAMPLE_VARIABLES = """
variables:
  - role: Y
    dataset_column: ln_wage
    semantic_label: 工资
    description: ""
    reference_papers: []
  - role: X
    dataset_column: robot
    semantic_label: 机器人
    description: ""
    reference_papers: []
"""

SAMPLE_DESIGN = json.dumps(
    {
        "topic": "smoke test",
        "method": "IV",
        "recommended": "IV",
        "code_stub": "# iv",
    },
    ensure_ascii=False,
)


class ExecuteSseWireInTests(unittest.TestCase):
    """L5 wire-in: /api/execute 端到端 SSE smoke。"""

    def test_sse_end_to_end_yields_21_events(self) -> None:
        """POST /api/execute → 21 events: 1 start + 9 progress + 9 section_done + 1 paper_ready + 1 done."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "brief.md"
            variables_path = tmp_path / "variables.yaml"
            design_path = tmp_path / "design.json"
            brief_path.write_text(SAMPLE_BRIEF, encoding="utf-8")
            variables_path.write_text(SAMPLE_VARIABLES, encoding="utf-8")
            design_path.write_text(SAMPLE_DESIGN, encoding="utf-8")

            req = {
                "topic_slug": "sse-smoke-wire-in",
                "brief_path": str(brief_path),
                "variables_path": str(variables_path),
                "design_path": str(design_path),
            }

            client = TestClient(app)
            events: list[dict] = []
            # 用 patch as context manager 限定 mock 作用域（避免污染其他 lane 的测试）
            with patch(
                "Product.backend.wrapper.execute_service.chat_completion",
                side_effect=_mock_chat_completion,
            ):
                with client.stream("POST", "/api/execute", json=req) as response:
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(
                        response.headers.get("content-type", "").startswith(
                            "text/event-stream"
                        ),
                        f"unexpected content-type: {response.headers.get('content-type')}",
                    )
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            events.append(json.loads(line[6:]))

        event_types = [e["event"] for e in events]
        # 序列断言
        self.assertEqual(event_types[0], "start")
        self.assertEqual(event_types[-1], "done")
        # 类型计数
        self.assertEqual(event_types.count("start"), 1)
        self.assertEqual(event_types.count("progress"), 9)
        self.assertEqual(event_types.count("section_done"), 9)
        self.assertEqual(event_types.count("paper_ready"), 1)
        self.assertEqual(event_types.count("done"), 1)
        # 21 events total
        self.assertEqual(len(events), 21)
        # paper_ready event 必含 paper_pdf_path
        paper_ready = next(e for e in events if e["event"] == "paper_ready")
        self.assertIn("paper_pdf_path", paper_ready)
        self.assertTrue(paper_ready["paper_pdf_path"].endswith("paper.pdf"))
        # done event 必含 results_json_path
        done = next(e for e in events if e["event"] == "done")
        self.assertIn("results_json_path", done)
        self.assertTrue(done["results_json_path"].endswith("results.json"))


if __name__ == "__main__":
    unittest.main()

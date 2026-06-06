from __future__ import annotations

import asyncio
import json
import unittest
from unittest.mock import patch

from Product.api import brief_stream
from Product.backend.wrapper.brief_stream_service import BriefResumeRequest
from Product.types.research import BriefRequest


def _decode_sse_line(line: str) -> dict:
    assert line.startswith("data: ")
    payload = line.removeprefix("data: ").strip()
    return json.loads(payload)


async def _collect_initial(topic: str) -> list[dict]:
    return [_decode_sse_line(line) async for line in brief_stream._stream_initial(BriefRequest(topic=topic))]


async def _collect_resume(topic: str) -> list[dict]:
    request = BriefResumeRequest(topic=topic, action="continue", prior_steps={})
    return [_decode_sse_line(line) async for line in brief_stream._stream_resume(request)]


class BriefStreamErrorContractTests(unittest.TestCase):
    """BDD: LLM 层失败时，任务书页面必须给用户可理解的错误原因。"""

    def test_bdd_initial_stream_emits_error_event_when_model_layer_fails(self) -> None:
        """Given 模型层异常, When 开始任务书, Then SSE 返回 error 事件而不是断流。"""

        def broken_stream(_: str):
            raise RuntimeError("MiniMax API key missing")
            yield  # pragma: no cover

        with patch.object(brief_stream, "run_brief_stream", side_effect=broken_stream):
            events = asyncio.run(_collect_initial("父母教育对子女工资的影响"))

        self.assertEqual(events[-1]["event"], "error")
        self.assertIn("MiniMax API key missing", events[-1]["message"])

    def test_bdd_resume_stream_emits_error_event_when_model_layer_fails(self) -> None:
        """Given 模型层异常, When 人工确认后继续, Then SSE 返回 error 事件而不是断流。"""

        def broken_resume(**_: object):
            raise TimeoutError("model stream timed out")
            yield  # pragma: no cover

        with patch.object(brief_stream, "resume_brief_stream", side_effect=broken_resume):
            events = asyncio.run(_collect_resume("父母教育对子女工资的影响"))

        self.assertEqual(events[-1]["event"], "error")
        self.assertIn("model stream timed out", events[-1]["message"])


if __name__ == "__main__":
    unittest.main()

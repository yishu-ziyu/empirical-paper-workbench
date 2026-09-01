"""MiniMax-compatible typed output contract for chapter review."""
from __future__ import annotations

import asyncio
import json

import pytest
from pydantic import ValidationError
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel

from agent.nodes.review_chapter import (
    ReviewResult,
    _run_review_agent_sync,
    build_review_agent,
)


VALID_REVIEW = {
    "rubric": {
        "endogeneity": 0.7,
        "identification": 0.8,
        "robustness": 0.6,
        "contribution": 0.9,
        "readability": 0.8,
    },
    "feedback": "主张边界清楚。",
    "suggestions": "补充局限说明。",
}


def test_review_result_rejects_missing_rubric_dimension():
    """The old parser silently converted this real failure class to 0.0."""
    malformed = json.loads(json.dumps(VALID_REVIEW, ensure_ascii=False))
    malformed["rubric"].pop("readability")

    with pytest.raises(ValidationError):
        ReviewResult.model_validate(malformed)


def test_review_result_rejects_blank_text():
    malformed = json.loads(json.dumps(VALID_REVIEW, ensure_ascii=False))
    malformed["feedback"] = "   "

    with pytest.raises(ValidationError):
        ReviewResult.model_validate(malformed)


def test_review_result_rejects_out_of_range_score():
    malformed = json.loads(json.dumps(VALID_REVIEW, ensure_ascii=False))
    malformed["rubric"]["robustness"] = 1.2

    with pytest.raises(ValidationError):
        ReviewResult.model_validate(malformed)


def test_review_agent_retries_malformed_then_returns_typed_result():
    calls = {"count": 0}
    malformed = json.loads(json.dumps(VALID_REVIEW, ensure_ascii=False))
    malformed["rubric"].pop("readability")

    def respond(messages, info):
        calls["count"] += 1
        payload = malformed if calls["count"] <= 2 else VALID_REVIEW
        return ModelResponse(
            parts=[TextPart(content=json.dumps(payload, ensure_ascii=False))]
        )

    agent = build_review_agent(model=FunctionModel(respond))
    result = agent.run_sync("评审这一章。")

    assert calls["count"] == 3
    assert isinstance(result.output, ReviewResult)
    assert result.output.rubric.readability == 0.8


def test_paper_draft_review_disables_internal_structured_retries():
    calls = {"count": 0}
    malformed = json.loads(json.dumps(VALID_REVIEW, ensure_ascii=False))
    malformed["rubric"].pop("readability")

    def respond(messages, info):
        calls["count"] += 1
        return ModelResponse(
            parts=[TextPart(content=json.dumps(malformed, ensure_ascii=False))]
        )

    agent = build_review_agent(model=FunctionModel(respond), retries=0)
    with pytest.raises(Exception):
        agent.run_sync("评审这一章。")

    assert calls["count"] == 1


def test_review_agent_sync_bridge_works_inside_running_event_loop():
    class FakeRun:
        output = ReviewResult.model_validate(VALID_REVIEW)

    class FakeAgent:
        def run_sync(self, prompt):
            with pytest.raises(RuntimeError):
                asyncio.get_running_loop()
            return FakeRun()

    async def invoke():
        return _run_review_agent_sync(FakeAgent(), "评审。")

    result = asyncio.run(invoke())
    assert result.output.feedback == VALID_REVIEW["feedback"]

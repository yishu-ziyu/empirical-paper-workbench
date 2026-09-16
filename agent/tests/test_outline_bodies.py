"""Outline body completeness: empty pads and heading-only drafts are missing."""
from __future__ import annotations

from agent.engine.outline_bodies import (
    chapter_has_body,
    missing_outline_specs,
    prose_without_headings,
)
from conftest import make_six_chapter_outline, make_write_ready_state


def test_heading_only_content_is_not_a_body():
    assert prose_without_headings("## 引言\n\n") == ""
    assert chapter_has_body({"type": "intro", "title": "引言", "content": "## 引言\n"}) is False
    assert chapter_has_body({"type": "intro", "title": "引言", "content": "研究背景。"}) is True


def test_missing_outline_specs_skips_empty_pads():
    state = make_write_ready_state(
        outline=make_six_chapter_outline(),
        body_chapters=[
            {"type": "intro", "title": "引言", "content": "研究背景。"},
            {},
            {},
            {"type": "methods", "title": "方法", "content": "## 模型设定\n"},
            {"type": "results", "title": "结果", "content": "主表如下。"},
            {},
        ],
    )
    missing = [spec["type"] for spec in missing_outline_specs(state)]
    assert missing == ["lit_review", "data_desc", "methods", "conclusion"]
